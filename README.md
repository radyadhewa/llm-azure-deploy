# Deploy Pre-trained LLM Models to Azure ML

A reference repository for deploying pre-trained Large Language Models (LLMs) from local storage to Azure Machine Learning managed online endpoints.

## 📋 Overview

This repository provides scripts and configurations to:
- Upload local LLM models to Hugging Face Hub (optional)
- Register local models to Azure ML workspace
- Deploy models as managed online endpoints with GPU support

## 🏗️ Repository Structure

```
.
├── huggingface.py           # Upload local model to HuggingFace Hub
├── register_model.py        # Register model to Azure ML workspace
├── deployment/
│   ├── deployment.yml       # Deployment configuration
│   └── endpoint.yml         # Endpoint configuration
├── environment/
│   └── conda.yaml          # Python environment dependencies
├── src/
│   └── inference.py        # Scoring script for model inference
├── test_request.json       # Example request payload
├── .env.template           # Environment variables template
├── config.json.template    # Azure ML config template
└── requirements.txt        # Python dependencies
```

## 🚀 Prerequisites

1. **Azure Subscription** with Azure ML workspace
2. **Python 3.10+** installed
3. **Azure CLI** with ML extension:
   ```powershell
   az extension add -n ml
   az login
   ```
4. **GPU-enabled compute** (Standard_NC6s_v3 or higher) in your Azure region
5. **Local model files** (e.g., Qwen, LLaMA, etc.)

## ⚙️ Setup

### 1. Clone and Install Dependencies

```powershell
git clone <your-repo-url>
cd llm-azure-deploy

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Azure ML Workspace

Create `config.json` from template:

```powershell
cp config.json.template config.json
```

Edit `config.json` with your Azure details:

```json
{
    "subscription_id": "your-subscription-id",
    "resource_group": "your-resource-group",
    "workspace_name": "your-workspace-name"
}
```

### 3. Configure Script Variables

Edit the configuration section at the top of each Python script:

**For [huggingface.py](huggingface.py)** (if using HuggingFace upload):
```python
TOKEN = "hf_..."                    # Your HuggingFace write token
USERNAME = "your_username"          # Your HuggingFace username
REPO_NAME = "qwen-7b-private"       # Repository name
LOCAL_FOLDER = "./path/to/qwen"     # Path to local model
```

**For [register_model.py](register_model.py)**:
```python
LOCAL_MODEL_PATH = "./path/to/your/local/qwen-folder"
MODEL_NAME = "qwen-7b-custom"
```

> 💡 **Production Note**: For production deployments, consider using environment variables or Azure Key Vault instead of hardcoded values.

## 📦 Usage

### Option 1: Direct Azure ML Deployment (Recommended)

**Step 1: Register Model**

```powershell
python register_model.py
```

This uploads your local model to Azure ML workspace as a registered model asset.

**Step 2: Create Endpoint**

```powershell
az ml online-endpoint create -f deployment/endpoint.yml
```

**Step 3: Deploy Model**

```powershell
az ml online-deployment create -f deployment/deployment.yml --all-traffic
```

**Step 4: Test Endpoint**

```powershell
# Get endpoint key
$KEY = az ml online-endpoint get-credentials -n qwen-endpoint --query primaryKey -o tsv

# Get scoring URI
$URI = az ml online-endpoint show -n qwen-endpoint --query scoring_uri -o tsv

# Test with example payload
$headers = @{"Authorization"="Bearer $KEY"; "Content-Type"="application/json"}
Invoke-RestMethod -Uri $URI -Method Post -Headers $headers -Body (Get-Content test_request.json)
```

### Option 2: Via HuggingFace Hub

If you want to host on HuggingFace first:

```powershell
# Upload to HuggingFace Hub
python huggingface.py

# Then use HuggingFace model reference in deployment
```

## 🔧 Configuration Details

### Deployment Configuration

Edit [deployment/deployment.yml](deployment/deployment.yml) to customize:

- **instance_type**: GPU SKU (e.g., `Standard_NC6s_v3`, `Standard_NC12s_v3`)
- **instance_count**: Number of instances (default: 1)
- **request_timeout_ms**: Maximum request timeout (default: 90000ms)
- **environment**: Conda dependencies and Docker image

### Inference Configuration

Edit [src/inference.py](src/inference.py) for custom:

- **Generation parameters**: temperature, top_p, top_k
- **Token limits**: max_new_tokens
- **Model loading**: device_map, torch_dtype
- **Pre/post-processing**: custom tokenization logic

### Environment Dependencies

Update [environment/conda.yaml](environment/conda.yaml) based on your model requirements:

```yaml
dependencies:
  - python=3.10
  - pip:
    - torch
    - transformers
    - accelerate
    # Add model-specific dependencies
```

## 🧪 Testing Request Format

The endpoint expects JSON payloads:

```json
{
  "prompt": "Your question or prompt here",
  "max_new_tokens": 512,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 50,
  "do_sample": true
}
```

**Response Format:**

```json
{
  "result": "Generated text response...",
  "prompt_length": 15,
  "generated_length": 247
}
```

## 📊 Monitoring

View logs and metrics:

```powershell
# View deployment logs
az ml online-deployment get-logs -n qwen-deployment-v1 -e qwen-endpoint

# Monitor endpoint
az ml online-endpoint show -n qwen-endpoint
```

## 🛠️ Troubleshooting

### Authentication Issues

```powershell
# Re-authenticate
az login
az account set --subscription <subscription-id>

# Verify credentials
az account show
```

### Model Loading Errors

Check that:
- Model path in `.env` is correct and files exist
- Model format is compatible with `transformers` library
- All required model files are present (config.json, tokenizer files, weights)

### Deployment Timeout

If deployment takes too long:
- Increase `initial_delay` in [deployment.yml](deployment/deployment.yml)
- Check GPU availability in your region
- Review deployment logs for specific errors

### Out of Memory

If encountering OOM errors:
- Use smaller batch sizes
- Enable model quantization (int8/int4)
- Use larger GPU instance type
- Adjust `torch_dtype` to `torch.float16` or `torch.bfloat16`

## 💰 Cost Optimization

- Use **spot instances** for development/testing
- **Scale to zero** when not in use (Azure ML online endpoints support this)
- Monitor with **cost analysis** in Azure Portal
- Consider **batch endpoints** for non-real-time workloads

## 🔐 Security Best Practices

1. **Never commit** `config.json` with real credentials (included in `.gitignore`)
2. **For production**: Use environment variables or Azure Key Vault for secrets
3. **Avoid hardcoding**: The scripts show hardcoded config for simplicity - replace with secure methods in production
4. Enable **managed identity** instead of API keys when possible
5. Restrict **network access** with private endpoints
6. Enable **authentication** on endpoints (key or Azure AD)

## 📚 Additional Resources

- [Azure ML Documentation](https://learn.microsoft.com/azure/machine-learning/)
- [Deploy models online](https://learn.microsoft.com/azure/machine-learning/how-to-deploy-online-endpoints)
- [Managed online endpoints](https://learn.microsoft.com/azure/machine-learning/concept-endpoints)
- [Transformers documentation](https://huggingface.co/docs/transformers)

## 📝 Notes

- **Model Size**: Ensure your model fits in the instance memory (NC6s_v3 has 56GB)
- **Cold Start**: First request after deployment may take longer
- **Concurrency**: Adjust `max_concurrent_requests_per_instance` based on model size
- **Version Control**: Update deployment name for new versions to maintain history

## 🤝 Contributing

This is a reference repository. Feel free to fork and adapt to your needs.

## 📄 License

This project is provided as-is for reference purposes.
