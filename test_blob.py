import json
import os
import importlib
from azure.functions import HttpRequest

# Set Azurite connection string
os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

# Import function
app = importlib.import_module("NERFunction.__init__")

# Create request
body = json.dumps({"text": "Apple Inc. bought a U.K. startup for $1 billion."}).encode()
req = HttpRequest(method="POST", url="http://localhost/api/NERFunction", body=body)

# Call function
res = app.main(req)
result = json.loads(res.get_body().decode())

# Display results
print(f"✅ Status: {res.status_code}")
print(f"📊 Entities found: {result['entities_count']}")
print(f"💾 Blob saved: {result['blob_storage']['saved']}")
if result['blob_storage']['saved']:
    print(f"📁 Blob name: {result['blob_storage']['blob_name']}")
    print(f"📦 Container: {result['blob_storage']['container']}")
