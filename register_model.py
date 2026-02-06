import os
import logging
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential

"""
Register a local model to Azure ML workspace.
You can also do this via Azure ML SDK in Python or Azure Portal.    
"""

# ===========================
# CONFIGURATION
# ===========================
LOCAL_MODEL_PATH = "./path/to/your/local/qwen-folder"  # CHANGE : Path to local model
MODEL_NAME = "qwen-7b-custom"                           # CHANGE : Model name in Azure ML
MODEL_DESCRIPTION = "Pre-trained Qwen 7B from on-prem storage"  # Optional: Model description

# NOTE: For production, consider using environment variables:
# LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "./path/to/model")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_ml_client():
    """Initialize Azure ML Client from config.json file."""
    try:
        logger.info("Loading Azure ML client from config.json...")
        ml_client = MLClient.from_config(credential=DefaultAzureCredential())
        logger.info("Successfully connected to Azure ML workspace")
        return ml_client
    except Exception as e:
        logger.error(f"Could not load from config.json: {e}")
        raise ValueError(
            "Please create config.json with your Azure ML workspace details.\n"
            "Use config.json.template as a reference."
        )

def register_model():
    """Register a local model to Azure ML workspace."""
    try:
        # Validate model path
        if not os.path.exists(LOCAL_MODEL_PATH):
            raise FileNotFoundError(
                f"Model path does not exist: {LOCAL_MODEL_PATH}\n"
                f"Please update LOCAL_MODEL_PATH at the top of this script."
            )
        
        logger.info(f"Model path: {LOCAL_MODEL_PATH}")
        logger.info(f"Model name: {MODEL_NAME}")
        
        # Initialize ML Client
        ml_client = get_ml_client()
        logger.info(f"Connected to workspace: {ml_client.workspace_name}")
        
        # Create model entity
        qwen_model = Model(
            path=LOCAL_MODEL_PATH,
            type="custom_model",
            name=MODEL_NAME,
            description=MODEL_DESCRIPTION
        )
        
        # Register the model
        logger.info("Starting model registration...")
        registered_model = ml_client.models.create_or_update(qwen_model)
        
        logger.info(f"Model registered successfully!")
        logger.info(f"Model name: {registered_model.name}")
        logger.info(f"Model version: {registered_model.version}")
        logger.info(f"Model ID: {registered_model.id}")
        
        return True
        
    except FileNotFoundError as fnf:
        logger.error(f"File Error: {fnf}")
        return False
    except ValueError as ve:
        logger.error(f"Configuration Error: {ve}")
        return False
    except Exception as e:
        logger.error(f"Error during model registration: {e}")
        return False

if __name__ == "__main__":
    success = register_model()
    exit(0 if success else 1)