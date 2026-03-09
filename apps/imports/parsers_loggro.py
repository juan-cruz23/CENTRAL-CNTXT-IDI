"""
Loggro Accounting Excel Parser.

Parses the auxiliar contable exported from Loggro (Excel .xlsx format).
Expected columns: Cuenta, NombreCuenta, CentroCosto, NombreCentroCosto,
TipoDocumento, NumeroDocumento, FechaDocumento, Tercero (NIT),
NombreTercero, Descripcion, Debito, Credito, SaldoFinal, etc.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation

import openpyxl


class LoggroAccountingParser:
    """Parses a Loggro accounting Excel file into structured records."""

    # Mapping from column header variants to canonical field names
    COLUMN_MAP = {
        # Account code
        "cuenta": "account_code",
        "código cuenta": "account_code",
        "cod cuenta": "account_code",
        # Account name
        "nombrecuenta": "account_name",
        "nombre cuenta": "account_name",
        "descripción cuenta": "account_name",
        "descripcion cuenta": "account_name",
        # Cost center
        "centrocosto": "cost_center_code",
        "centro costo": "cost_center_code",
        "centro de costo": "cost_center_code",
        "cod centro costo": "cost_center_code",
        "centro": "cost_center_code",
        # Cost center name
        "nombrecentrocosto": "cost_center_name",
        "nombre centro costo": "cost_center_name",
        "nombre centro de costo": "cost_center_name",
        "nombre centro": "cost_center_name",
        # Document type
        "tipodocumento": "document_type",
        "tipo documento": "document_type",
        "tipo doc": "document_type",
        "tipo transaccion": "document_type",
        "tipo transacción": "document_type",
        # Document number
        "numerodocumento": "document_number",
        "numero documento": "document_number",
        "no documento": "document_number",
        "documento": "document_number",
        "cbte.": "document_number",
        "cbte": "document_number",
        # Date
        "fechadocumento": "document_date",
        "fecha documento": "document_date",
        "fecha": "document_date",
        # Third party NIT
        "tercero": "third_party_nit",
        "nit": "third_party_nit",
        "nit tercero": "third_party_nit",
        "contacto": "third_party_nit",
        # Third party name
        "nombretercero": "third_party_name",
        "nombre tercero": "third_party_name",
        "razón social": "third_party_name",
        "nombre contacto": "third_party_name",
        # Description
        "descripcion": "description",
        "descripción": "description",
        "detalle": "description",
        "ref. (#)": "description",
        # Debit / Credit / Balance
        "debito": "debit",
        "débito": "debit",
        "credito": "credit",
        "crédito": "credit",
        "saldofinal": "balance",
        "saldo final": "balance",
        "saldo": "balance",
    }

    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.accounts = {}  # {code: name}
        self.cost_centers = {}  # {code: name}

    def parse(self):
        """
        Parse the Excel file and return structured data.

        Returns:
            dict with keys:
                - records: list of transaction dicts
                - accounts: dict of {code: name} for discovered accounts
                - cost_centers: dict of {code: name} for discovered cost centers
                - errors: list of error strings
                - total_rows: int
        """
        wb = openpyxl.load_workbook(self.file_path, data_only=True)
        ws = wb.active

        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append(tuple(row))
        if not rows:
            return {"records": [], "accounts": {}, "cost_centers": {},
                    "errors": ["Archivo vacío."], "total_rows": 0}

        # Find header row (first row with recognizable column names)
        header_row_idx, column_indices = self._find_headers(rows)
        if header_row_idx is None:
            return {"records": [], "accounts": {}, "cost_centers": {},
                    "errors": ["No se encontraron encabezados reconocidos."],
                    "total_rows": 0}

        records = []
        for row_num, row in enumerate(rows[header_row_idx + 1:], start=header_row_idx + 2):
            if all(cell is None or str(cell).strip() == "" for cell in row):
                continue  # skip blank rows

            record = self._parse_row(row, column_indices, row_num)
            if record:
                records.append(record)

                # Track unique accounts and cost centers
                if record.get("account_code"):
                    self.accounts[record["account_code"]] = record.get("account_name", "")
                if record.get("cost_center_code"):
                    self.cost_centers[record["cost_center_code"]] = record.get("cost_center_name", "")

        wb.close()

        return {
            "records": records,
            "accounts": self.accounts,
            "cost_centers": self.cost_centers,
            "errors": self.errors,
            "total_rows": len(records),
        }

    def _find_headers(self, rows):
        """Find the header row and map columns to indices."""
        for idx, row in enumerate(rows[:10]):  # check first 10 rows
            if row is None:
                continue
            column_indices = {}
            for col_idx, cell in enumerate(row):
                if cell is None:
                    continue
                normalized = str(cell).strip().lower()
                if normalized in self.COLUMN_MAP:
                    canonical = self.COLUMN_MAP[normalized]
                    if canonical not in column_indices:
                        column_indices[canonical] = col_idx

            # Require at least account_code and one financial field
            if "account_code" in column_indices and (
                "debit" in column_indices or "credit" in column_indices
            ):
                return idx, column_indices

        return None, {}

    def _parse_row(self, row, column_indices, row_num):
        """Parse a single data row into a record dict."""
        def get_cell(field_name):
            idx = column_indices.get(field_name)
            if idx is not None and idx < len(row):
                return row[idx]
            return None

        account_code = self._safe_str(get_cell("account_code"))
        if not account_code:
            return None

        document_date = self._safe_date(get_cell("document_date"))
        if not document_date:
            self.errors.append(f"Fila {row_num}: fecha inválida, usando hoy.")
            document_date = datetime.now().date()

        period = document_date.strftime("%Y-%m")

        return {
            "account_code": account_code,
            "account_name": self._safe_str(get_cell("account_name")),
            "cost_center_code": self._safe_str(get_cell("cost_center_code")),
            "cost_center_name": self._safe_str(get_cell("cost_center_name")),
            "document_type": self._safe_str(get_cell("document_type")),
            "document_number": self._safe_str(get_cell("document_number")),
            "document_date": document_date,
            "third_party_nit": self._safe_str(get_cell("third_party_nit")),
            "third_party_name": self._safe_str(get_cell("third_party_name")),
            "description": self._safe_str(get_cell("description")),
            "debit": self._safe_decimal(get_cell("debit")),
            "credit": self._safe_decimal(get_cell("credit")),
            "balance": self._safe_decimal(get_cell("balance")),
            "period": period,
        }

    @staticmethod
    def _safe_str(value):
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def _safe_decimal(value):
        if value is None:
            return Decimal("0")
        try:
            cleaned = str(value).replace(",", "").replace("$", "").replace(" ", "").strip()
            if not cleaned or cleaned == "-":
                return Decimal("0")
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal("0")

    @staticmethod
    def _safe_date(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if hasattr(value, "date"):
            return value.date() if callable(getattr(value, "date")) else value
        try:
            s = str(value).strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    continue
        except (ValueError, TypeError):
            pass
        return None
