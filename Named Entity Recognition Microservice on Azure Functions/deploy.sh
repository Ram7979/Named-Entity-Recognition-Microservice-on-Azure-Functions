"""
#!/bin/bash

# Configuration
RESOURCE_GROUP="ner-microservice-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="nerstorage$(date +%s)"
FUNCTION_APP="ner-function-app-$(date +%s)"
PYTHON_VERSION="3.9"

echo "🚀 Deploying NER Microservice to Azure..."

# Login to Azure
echo "📝 Logging in to Azure..."
az login

# Create Resource Group
echo "📦 Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Storage Account
echo "💾 Creating Storage Account..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS

# Get Storage Connection String
echo "🔑 Retrieving Storage Connection String..."
STORAGE_CONNECTION=$(az storage account show-connection-string \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query connectionString \
    --output tsv)

# Create Function App
echo "⚡ Creating Function App..."
az functionapp create \
    --resource-group $RESOURCE_GROUP \
    --consumption-plan-location $LOCATION \
    --runtime python \
    --runtime-version $PYTHON_VERSION \
    --functions-version 4 \
    --name $FUNCTION_APP \
    --storage-account $STORAGE_ACCOUNT \
    --os-type Linux

# Configure App Settings
echo "⚙️  Configuring App Settings..."
az functionapp config appsettings set \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --settings "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION"

# Install spaCy model in Azure (post-deployment script)
echo "📚 Note: After deployment, run the following command to install spaCy model:"
echo "az functionapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $FUNCTION_APP --src <your-zip-file>"

# Deploy Function
echo "🚢 Deploying Function Code..."
func azure functionapp publish $FUNCTION_APP --build remote

echo "✅ Deployment Complete!"
echo "Function URL: https://$FUNCTION_APP.azurewebsites.net/api/NERFunction"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Resource Group: $RESOURCE_GROUP"
"""