import os
import json
import time
from pathlib import Path
from pyDataverse.api import NativeApi

# Configuration
API_TOKEN = os.getenv("DATAVERSE_API_TOKEN")  # Read from environment variable
BASE_URL = "https://demo.borealisdata.ca"  # Your Dataverse URL
DATAVERSE_ALIAS = "root"  # The dataverse where datasets will be uploaded
DATASETS_FOLDER = "/Destop/Datasets"  # Main folder containing all dataset folders

# Initialize API
api = NativeApi(BASE_URL, API_TOKEN)

def load_json_metadata(json_path):
    """Load and parse JSON metadata file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"✓ Loaded metadata from {json_path}")
        return metadata
    except Exception as e:
        print(f"✗ Error loading {json_path}: {e}")
        return None

def create_dataset(metadata, dataverse_alias):
    """Create a new dataset in Dataverse."""
    try:
        # Extract just the dataset version metadata for creation
        if 'datasetVersion' in metadata:
            dataset_json = {
                "datasetVersion": metadata['datasetVersion']
            }
        else:
            dataset_json = metadata

        response = api.create_dataset(dataverse_alias, dataset_json)

        if response.status_code == 201:
            data = response.json()
            dataset_id = data['data']['id']
            persistent_id = data['data']['persistentId']
            print(f"✓ Created dataset: {persistent_id}")
            return persistent_id
        else:
            print(f"✗ Failed to create dataset: {response.status_code}")
            print(f"  Response: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Error creating dataset: {e}")
        return None

