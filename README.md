
# Named Entity Recognition Microservice on Azure Functions

## Overview
Serverless NER microservice using spaCy on Azure Functions with Blob Storage logging.

## Prerequisites
- Azure account with active subscription
- Azure CLI installed
- Azure Functions Core Tools v4
- Python 3.9+
- pip

## Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure local settings:**
   Update `local.settings.json` with your Azure Storage connection string.

3. **Run locally:**
   ```bash
   func start
   ```

4. **Test locally:**
   ```bash
   curl -X POST http://localhost:7071/api/NERFunction \
     -H "Content-Type: application/json" \
     -d '{"text": "Apple Inc. is buying a U.K. startup for $1 billion. Tim Cook will announce it in California."}'
   ```

## Azure Deployment

1. **Make deploy script executable:**
   ```bash
   chmod +x deploy.sh
   ```

2. **Run deployment:**
   ```bash
   ./deploy.sh
   ```

3. **Install spaCy model on Azure:**
   After deployment, the model will be downloaded on first cold start.

## Sample Request

```bash
curl -X POST https://YOUR_FUNCTION_APP.azurewebsites.net/api/NERFunction?code=YOUR_FUNCTION_KEY \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Microsoft was founded by Bill Gates in Seattle. It is now worth over $2 trillion."
  }'
```

## Sample Response

```json
{
  "timestamp": "2024-01-21T10:30:45.123456",
  "input_text": "Microsoft was founded by Bill Gates in Seattle...",
  "entities_count": 4,
  "entities": [
    {
      "text": "Microsoft",
      "label": "ORG",
      "start": 0,
      "end": 9,
      "description": "Companies, agencies, institutions, etc."
    },
    {
      "text": "Bill Gates",
      "label": "PERSON",
      "start": 25,
      "end": 35,
      "description": "People, including fictional"
    },
    {
      "text": "Seattle",
      "label": "GPE",
      "start": 39,
      "end": 46,
      "description": "Countries, cities, states"
    },
    {
      "text": "$2 trillion",
      "label": "MONEY",
      "start": 70,
      "end": 81,
      "description": "Monetary values, including unit"
    }
  ],
  "blob_storage": {
    "saved": true,
    "blob_name": "ner_result_20240121_103045_123456.json",
    "container": "ner-results"
  }
}
```

## Monitoring Results in Blob Storage

View results in Azure Portal:
1. Navigate to Storage Account > Containers > ner-results
2. Download JSON files to view extraction logs

Or use Azure CLI:
```bash
az storage blob list \
  --account-name YOUR_STORAGE_ACCOUNT \
  --container-name ner-results \
  --output table
```

## Cleanup

```bash
az group delete --name ner-microservice-rg --yes
```

## Entity Types Supported

- PERSON: People names
- ORG: Organizations
- GPE: Geopolitical entities (countries, cities)
- MONEY: Monetary values
- DATE: Dates
- TIME: Times
- PERCENT: Percentages
- And 15+ more types

## Notes

- Cold start may take 10-15 seconds for model loading
- Function timeout: 5 minutes (default)
- Max request size: 100MB
- spaCy model: en_core_web_sm (12MB)

