import os
import json
import time
from pathlib import Path
import click
from pyDataverse.api import NativeApi

# Configuration
API_TOKEN = os.getenv("DATAVERSE_API_TOKEN")  # Read from environment variable
BASE_URL = "https://demo.borealisdata.ca"  # Your Dataverse URL
DATAVERSE_ALIAS = "zeynepcevik"  # The dataverse where datasets will be uploaded
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

def upload_zip_file(persistent_id, zip_path):
    """Upload a ZIP file to the dataset."""
    try:
        # Ensure we pass a filesystem path string to pyDataverse, which
        # will open the file itself. If a Path object was provided, cast
        # to str so pyDataverse can open it.
        filepath = str(zip_path)
        response = api.upload_datafile(persistent_id, filepath)

        filename = os.path.basename(filepath)
        if response.status_code in [200, 201]:
            print(f"✓ Uploaded file: {filename}")
            return True
        else:
            print(f"✗ Failed to upload {filename}: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error uploading {zip_path}: {e}")
        return False

def process_dataset_folder(dataset_folder_path):
    """Process a single dataset folder (JSON + ZIP)."""
    print(f"\n{'='*60}")
    print(f"Processing: {dataset_folder_path.name}")
    print(f"{'='*60}")

    # Find JSON and ZIP files
    json_files = list(dataset_folder_path.glob("*.json"))
    zip_files = list(dataset_folder_path.glob("*.zip"))

    if not json_files:
        print(f"✗ No JSON file found in {dataset_folder_path.name}")
        return False

    if not zip_files:
        print(f"⚠ No ZIP file found in {dataset_folder_path.name}")
        # Continue anyway - some datasets might not have files

    # Use the first JSON file found
    json_file = json_files[0]

    # Load metadata
    metadata = load_json_metadata(json_file)
    if not metadata:
        return False

    # Create dataset
    persistent_id = create_dataset(metadata, DATAVERSE_ALIAS)
    if not persistent_id:
        return False

    # Upload ZIP file if exists
    if zip_files:
        zip_file = zip_files[0]
        upload_success = upload_zip_file(persistent_id, zip_file)
        if not upload_success:
            print(f"⚠ Dataset created but file upload failed")

    # Wait a bit to avoid overwhelming the server
    time.sleep(1)

    print(f"✓ Completed: {dataset_folder_path.name}")
    return True


@click.command()
@click.option('--api-token', envvar='DATAVERSE_API_TOKEN', help='Dataverse API token')
@click.option('--base-url', default='https://demo.borealisdata.ca', help='Dataverse base URL')
@click.option('--dataverse-alias', default='root', help='Dataverse alias for dataset upload')
@click.option('--datasets-folder', default='/Destop/Datasets', help='Path to datasets folder')
def main(api_token, base_url, dataverse_alias, datasets_folder):
    """Bulk load datasets to Dataverse."""
    if not api_token:
        click.echo("Error: API token not provided. Set DATAVERSE_API_TOKEN environment variable or use --api-token option.")
        raise click.Exit(1)
    
    click.echo(f"Starting bulk load...")
    click.echo(f"Base URL: {base_url}")
    click.echo(f"Dataverse Alias: {dataverse_alias}")
    click.echo(f"Datasets Folder: {datasets_folder}")
    
    # Initialize globals from CLI options so other functions use the correct values
    global api, API_TOKEN, BASE_URL, DATAVERSE_ALIAS, DATASETS_FOLDER
    API_TOKEN = api_token
    BASE_URL = base_url
    DATAVERSE_ALIAS = dataverse_alias
    DATASETS_FOLDER = datasets_folder
    api = NativeApi(BASE_URL, API_TOKEN)

    datasets_path = Path(DATASETS_FOLDER).expanduser()
    if not datasets_path.exists():
        click.echo(f"Error: datasets folder '{datasets_path}' does not exist.")
        raise click.Exit(1)

    # Iterate over subdirectories and process each dataset folder
    for entry in sorted(datasets_path.iterdir()):
        if entry.is_dir():
            process_dataset_folder(entry)

if __name__ == '__main__':
    main()

#python BulkLoad_Python.py --base-url https://demo.borealisdata.ca --dataverse-alias zeynepcevik --datasets-folder /workspaces/BulkLoadData_Python/Datasets