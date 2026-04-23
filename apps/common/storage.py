"""GCS storage backend with IAM-signed URLs for Cloud Run.

Cloud Run runtime uses metadata-server credentials without a private key,
so blob.generate_signed_url() raises AttributeError. Passing
service_account_email + access_token routes signing through the IAM
signBlob API, which only requires the runtime SA to have
roles/iam.serviceAccountTokenCreator on itself.
"""
from datetime import timedelta

from google.auth import default as default_credentials
from google.auth.transport import requests as g_requests
from storages.backends.gcloud import GoogleCloudStorage


class IAMSignedGoogleCloudStorage(GoogleCloudStorage):
    def url(self, name):
        credentials, _ = default_credentials()
        credentials.refresh(g_requests.Request())
        blob = self.bucket.blob(self._normalize_name(name))
        return blob.generate_signed_url(
            expiration=timedelta(seconds=self.expiration),
            service_account_email=credentials.service_account_email,
            access_token=credentials.token,
            version="v4",
        )
