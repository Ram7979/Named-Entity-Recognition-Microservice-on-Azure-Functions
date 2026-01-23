import logging
import json
import os
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import spacy
from spacy.cli import download as spacy_download

# Initialize spaCy model (loaded once at cold start)
nlp = None

def load_model():
    """Load spaCy model with error handling"""
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
            logging.info("spaCy model loaded successfully")
        except OSError:
            logging.warning("spaCy model not found locally; downloading en_core_web_sm")
            spacy_download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            logging.exception("Unexpected error while loading spaCy model")
            raise
    return nlp

def extract_entities(text: str):
    """Perform NER on input text"""
    model = load_model()
    doc = model(text)
    
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
            "description": spacy.explain(ent.label_)
        })
    
    return entities

def save_to_blob(data: dict, connection_string: str):
    """Save extraction results to Azure Blob Storage"""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "ner-results"
        
        # Create container if it doesn't exist
        try:
            container_client = blob_service_client.get_container_client(container_name)
            container_client.get_container_properties()
        except:
            container_client = blob_service_client.create_container(container_name)
        
        # Create unique blob name with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        blob_name = f"ner_result_{timestamp}.json"
        
        # Upload data
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        blob_client.upload_blob(json.dumps(data, indent=2))
        
        return blob_name
    except Exception as e:
        logging.error(f"Error saving to blob: {str(e)}")
        return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main Azure Function entry point"""
    logging.info('NER Function triggered')

    try:
        # Parse request body
        req_body = req.get_json()
        text = req_body.get('text')
        
        if not text:
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing 'text' field in request body",
                    "example": {"text": "Apple is looking at buying U.K. startup for $1 billion"}
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Perform NER
        entities = extract_entities(text)
        
        # Prepare response
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "input_text": text,
            "entities_count": len(entities),
            "entities": entities
        }
        
        # Save to Blob Storage
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if connection_string:
            blob_name = save_to_blob(result, connection_string)
            result["blob_storage"] = {
                "saved": blob_name is not None,
                "blob_name": blob_name,
                "container": "ner-results"
            }
        else:
            logging.warning("AZURE_STORAGE_CONNECTION_STRING not configured")
            result["blob_storage"] = {
                "saved": False,
                "message": "Storage connection string not configured"
            }
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )