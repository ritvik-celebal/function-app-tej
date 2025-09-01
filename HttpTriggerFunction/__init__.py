import logging
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get resource URLs from environment variables (set by Bicep deployment)
        key_vault_url = os.getenv("KEY_VAULT_URL", "https://your-keyvault.vault.azure.net/")
        storage_account_url = os.getenv("STORAGE_ACCOUNT_URL", "https://yourstorageaccount.blob.core.windows.net")
        
        # Get managed identity credential
        credential = DefaultAzureCredential()
        
        # Example 1: Access Key Vault using managed identity
        secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
        
        # Example 2: Access Storage Account using managed identity
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
        
        # Simulate some operations
        response_data = {
            "message": "Hello from Azure Function with Managed Identity!",
            "status": "success",
            "timestamp": func.DateTime.utcnow().isoformat(),
            "managed_identity": "enabled",
            "environment": os.getenv("AZURE_FUNCTIONS_ENVIRONMENT", "unknown"),
            "function_app_name": os.getenv("WEBSITE_SITE_NAME", "local-development")
        }
        
        # Try to get a sample secret (this will work if Key Vault is configured)
        try:
            secret = secret_client.get_secret("sample-secret")
            response_data["secret_retrieved"] = "success"
            response_data["secret_value"] = secret.value[:10] + "..." if secret.value else "empty"
        except Exception as kv_error:
            logging.warning(f"Key Vault access failed: {str(kv_error)}")
            response_data["key_vault_status"] = f"not accessible: {str(kv_error)}"
        
        # Try to list containers (this will work if Storage Account is configured)
        try:
            containers = list(blob_service_client.list_containers())
            response_data["storage_containers_count"] = len(containers)
            response_data["storage_status"] = "accessible"
        except Exception as storage_error:
            logging.warning(f"Storage access failed: {str(storage_error)}")
            response_data["storage_status"] = f"not accessible: {str(storage_error)}"
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            headers={
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        logging.error(f"Function execution failed: {str(e)}")
        error_response = {
            "message": "Function execution failed",
            "error": str(e),
            "status": "error"
        }
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            headers={
                "Content-Type": "application/json"
            }
        )
