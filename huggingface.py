import os
from huggingface_hub import HfApi, create_repo

"""
Upload a local model to Hugging Face Hub as a private repository.
You can do it manually on Hugging Face website as well.
"""

# ===========================
# CONFIGURATION
# ===========================
TOKEN = "hf_your_write_token_here"        # CHANGE : Your HuggingFace write token
USERNAME = "your_hf_username"             # CHANGE : Your HuggingFace username
REPO_NAME = "qwen-7b-private"             # CHANGE : Your HF repository
LOCAL_FOLDER = "./path/to/qwen"           # CHANGE : Path to your local model folder

# NOTE: For production deployments, use environment variables instead of hardcoded values
# Example: TOKEN = os.getenv("HF_TOKEN", "default_value")

def validate_config():
    """Validate required configuration variables."""
    missing = []
    if TOKEN == "hf_your_write_token_here" or not TOKEN:
        missing.append("TOKEN (HuggingFace write token)")
    if USERNAME == "your_hf_username" or not USERNAME:
        missing.append("USERNAME (HuggingFace username)")
    if not os.path.exists(LOCAL_FOLDER):
        print(f"Warning: Local folder '{LOCAL_FOLDER}' does not exist")
        missing.append("LOCAL_FOLDER (path to model files)")
    
    if missing:
        raise ValueError(f"Please configure the following in the script: {', '.join(missing)}")

def upload_model():
    """Upload local model to Hugging Face Hub."""
    try:
        # Validate configuration
        validate_config()
        
        api = HfApi()
        repo_id = f"{USERNAME}/{REPO_NAME}"
        
        print(f"Checking if repository {REPO_NAME} exists...")
        
        # 1. Create the private repository
        create_repo(repo_id=repo_id, token=TOKEN, private=True, exist_ok=True)
        print(f"Repository ready: https://huggingface.co/{repo_id}")

        # 2. Upload the entire folder
        print(f"Starting upload from '{LOCAL_FOLDER}'...")
        print("This may take a while depending on your upload speed...")
        
        api.upload_folder(
            folder_path=LOCAL_FOLDER,
            repo_id=repo_id,
            repo_type="model",
            token=TOKEN
        )
        
        print("Upload Successful!")
        print(f"Model available at: https://huggingface.co/{repo_id}")
        return True
        
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
        print("Please update the configuration values at the top of this script.")
        return False
    except Exception as e:
        print(f"Error occurred during upload: {e}")
        return False

if __name__ == "__main__":
    success = upload_model()
    exit(0 if success else 1)