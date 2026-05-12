"""
Seed V.sual service catalog from Excel file.
Reads 'V.sual DATA' sheet and creates:
  - ProjectCategories (V0–V5)
  - ServiceSubCategories (V01–V04) linked to VSUAL operative line
  - ServiceTemplates (22)
  - Deliverables (23)
  - KeyActivities (88)
  - ServiceActivities (141)
"""

import os

from django.core.management.base import BaseCommand

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
EXCEL_PATH = os.path.join(BASE_DIR, "Documentacion", "05. Services_05.25.xlsm")

ROLE_MAP = {
    "VL | Visual Leader": "VL",
    "VS | Visual Support": "VS",
    "PC | Elena": "PC",
    "VM | VisuaL Manager": "VM",
    "Outsoursing": None,
}


def clean(v):
    return " ".join(str(v).strip().split()) if v else ""


class Command(BaseCommand):
    help = "Seed V.sual service catalog from Excel"

    def handle(self, *args, **options):
        try:
            import openpyxl
        except ImportError:
            self.stderr.write("openpyxl not installed")
            return

        from apps.accounts.models import Role
        from apps.organizations.models import OperativeLine
        from apps.services.models import (
            Deliverable,
            KeyActivity,
            ProjectCategory,
            ServiceActivity,
            ServiceSubCategory,
            ServiceTemplate,
        )

        # --- OperativeLine VSUAL ---
        vsual, _ = OperativeLine.objects.get_or_create(
            code="VSUAL",
            defaults={
                "name": "V.sual",
                "business_unit_id": OperativeLine.objects.filter(code="DSIGN").values_list("business_unit_id", flat=True).first(),
                "description": "Línea de Visualización",
                "is_active": True,
            },
        )
        self.stdout.write(f"OperativeLine: {vsual}")

        # --- Parse Excel ---
        wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True, keep_vba=False)
        ws = wb["V.sual DATA"]
        rows = list(ws.iter_rows(values_only=True))
        data_rows = [r for r in rows[3:] if r[1]]

        # Build structured data
        all_rows = []
        for r in data_rows:
            code = clean(r[1])
            cat = clean(r[2])
            subcat = clean(r[3])
            svc_name = clean(r[4])
            deliv = clean(r[5])
            und = clean(r[6])
            kact = clean(r[8])
            act_order = int(r[9]) if r[9] else 0
            action = clean(r[10])
            role_raw = clean(r[11])
            hours = float(r[12]) if r[12] else 0.0

            cat_code = cat.split(".")[0].strip() if "." in cat else cat
            cat_name = cat.split(".", 1)[1].strip() if "." in cat else cat

            subcat_num = subcat.split(".")[0].strip()
            subcat_code = "V" + subcat_num.zfill(2)
            subcat_name = subcat.split(".", 1)[1].strip() if "." in subcat else subcat

            role_code = ROLE_MAP.get(role_raw)

            all_rows.append({
                "svc_code": code,
                "cat_code": cat_code,
                "cat_name": cat_name,
                "subcat_code": subcat_code,
                "subcat_name": subcat_name,
                "svc_name": svc_name,
                "deliv_name": deliv,
                "deliv_und": und,
                "kact_name": kact,
                "act_order": act_order,
                "action_name": action,
                "role_code": role_code,
                "hours": hours,
            })

        self.stdout.write(f"Filas leídas: {len(all_rows)}")

        # --- ProjectCategories ---
        cats_created = 0
        cat_map = {}
        seen_cats = {}
        for row in all_rows:
            cc = row["cat_code"]
            if cc not in seen_cats:
                seen_cats[cc] = row["cat_name"]
        for code, name in seen_cats.items():
            obj, created = ProjectCategory.objects.get_or_create(code=code, defaults={"name": name})
            cat_map[code] = obj
            if created:
                cats_created += 1
        self.stdout.write(f"ProjectCategories creadas: {cats_created} | total registradas: {len(cat_map)}")

        # --- ServiceSubCategories ---
        subcats_created = 0
        subcat_map = {}
        seen_subcats = {}
        for row in all_rows:
            sc = row["subcat_code"]
            if sc not in seen_subcats:
                seen_subcats[sc] = row["subcat_name"]
        for code, name in seen_subcats.items():
            obj, created = ServiceSubCategory.objects.get_or_create(
                code=code,
                defaults={"name": name, "operative_line": vsual, "is_active": True},
            )
            if not obj.operative_line:
                obj.operative_line = vsual
                obj.save(update_fields=["operative_line"])
            subcat_map[code] = obj
            if created:
                subcats_created += 1
        self.stdout.write(f"ServiceSubCategories creadas: {subcats_created} | total: {len(subcat_map)}")

        # --- ServiceTemplates ---
        svcs_created = 0
        svc_map = {}
        seen_svcs = {}
        for row in all_rows:
            sc = row["svc_code"]
            if sc not in seen_svcs:
                seen_svcs[sc] = row
        for code, row in seen_svcs.items():
            cat_obj = cat_map.get(row["cat_code"])
            subcat_obj = subcat_map.get(row["subcat_code"])
            obj, created = ServiceTemplate.objects.get_or_create(
                code=code,
                defaults={
                    "name": row["svc_name"],
                    "category": cat_obj,
                    "subcategory": subcat_obj,
                    "operative_line": vsual,
                    "is_active": True,
                },
            )
            svc_map[code] = obj
            if created:
                svcs_created += 1
        self.stdout.write(f"ServiceTemplates creadas: {svcs_created} | total: {len(svc_map)}")

        # --- Deliverables ---
        delivs_created = 0
        deliv_map = {}
        seen_delivs = {}
        for row in all_rows:
            key = (row["svc_code"], row["deliv_name"])
            if key not in seen_delivs:
                seen_delivs[key] = row
        for (svc_code, deliv_name), row in seen_delivs.items():
            svc_obj = svc_map.get(svc_code)
            if not svc_obj:
                continue
            obj, created = Deliverable.objects.get_or_create(
                service_template=svc_obj,
                name=deliv_name,
                defaults={"unit": row["deliv_und"], "order": 1},
            )
            deliv_map[(svc_code, deliv_name)] = obj
            if created:
                delivs_created += 1
        self.stdout.write(f"Deliverables creados: {delivs_created} | total: {len(deliv_map)}")

        # --- KeyActivities ---
        kacts_created = 0
        kact_map = {}
        seen_kacts = {}
        kact_order = {}
        for row in all_rows:
            deliv_key = (row["svc_code"], row["deliv_name"])
            kact_key = (row["svc_code"], row["kact_name"])
            if kact_key not in seen_kacts:
                seen_kacts[kact_key] = deliv_key
                kact_order[kact_key] = row["act_order"]

        for kact_key, deliv_key in seen_kacts.items():
            svc_code, kact_name = kact_key
            deliv_obj = deliv_map.get(deliv_key)
            if not deliv_obj:
                self.stderr.write(f"  [WARN] Deliverable not found for kact: {kact_key}")
                continue
            obj, created = KeyActivity.objects.get_or_create(
                deliverable=deliv_obj,
                name=kact_name,
                defaults={"order": kact_order[kact_key]},
            )
            kact_map[kact_key] = obj
            if created:
                kacts_created += 1
        self.stdout.write(f"KeyActivities creadas: {kacts_created} | total: {len(kact_map)}")

        # --- ServiceActivities ---
        actions_created = 0
        actions_omitted = 0
        for i, row in enumerate(all_rows):
            svc_obj = svc_map.get(row["svc_code"])
            kact_key = (row["svc_code"], row["kact_name"])
            kact_obj = kact_map.get(kact_key)
            role_obj = None
            if row["role_code"]:
                role_obj = Role.objects.filter(code=row["role_code"]).first()

            if not svc_obj or not kact_obj:
                actions_omitted += 1
                self.stderr.write(f"  [OMIT] svc={row['svc_code']} kact={row['kact_name'][:40]}")
                continue

            obj, created = ServiceActivity.objects.get_or_create(
                service_template=svc_obj,
                key_activity=kact_obj,
                name=row["action_name"],
                defaults={
                    "order": row["act_order"],
                    "responsible_role": role_obj,
                    "estimated_hours": row["hours"],
                },
            )
            if created:
                actions_created += 1

        self.stdout.write(f"ServiceActivities creadas: {actions_created} | omitidas: {actions_omitted}")
        self.stdout.write(self.style.SUCCESS("✓ seed_vsual completado"))
