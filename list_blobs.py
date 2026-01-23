#!/usr/bin/env python3
"""List and retrieve blobs from Azurite local storage"""
import os
from azure.storage.blob import BlobServiceClient

# Azurite connection string
connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

try:
    # Connect to blob service
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Get container
    container_client = blob_service_client.get_container_client("ner-results")
    
    print("📦 Blobs in 'ner-results' container:\n")
    
    # List all blobs
    blobs = list(container_client.list_blobs())
    
    if not blobs:
        print("⚠️  No blobs found in container")
    else:
        for idx, blob in enumerate(blobs, 1):
            print(f"{idx}. {blob.name}")
            print(f"   Size: {blob.size} bytes")
            print(f"   Created: {blob.creation_time}")
            
            # Download and display content
            blob_client = container_client.get_blob_client(blob.name)
            content = blob_client.download_blob().readall().decode('utf-8')
            print(f"   Preview: {content[:200]}...")
            print()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Make sure Azurite is running:")
    print("   azurite --silent --location /tmp/azurite --blobPort 10000 --skipApiVersionCheck &")
