# BulkLoadData_Python
Loading multiple datasets by using API on Dataverse


Run these codes on Terminal in workpace 

- Create a virtual environment: 

`python -m venv venv`

- Activate the environment:

`source venv/bin/activate`

- Install pip packages:

`pip install -r requirements.txt`

- Get API token, create new environment variable:

`export DATAVERSE_API_TOKEN="your_token_here"`

- To upload the files, you need 1 json file and 1 zip file in each dataset:

`python BulkLoad_Python.py --base-url https://demo.borealisdata.ca --dataverse-alias yourDataverseAlias --datasets-folder /your/folder/path/Datasets`
