import os
import shelve
from typing import Dict, List, Optional, Set, Tuple
from flask import current_app
from google.cloud import datastore


class DatastoreAdapter:
    @property
    def ds_client(self):
        if not hasattr(current_app, "_datastore_client"):
            config = current_app.config
            current_app._datastore_client = datastore.Client(
                project=config.get("DATASTORE_PROJECT"),
                credentials=config.get("GCP_CREDENTIALS"),
            )
        return current_app._datastore_client


db = DatastoreAdapter()


class CredentialsAdapter:
    @property
    def credentials(self):
        credentials = current_app.config.get("GCP_CREDENTIALS")
        assert credentials is not None
        return credentials


gcp = CredentialsAdapter()
