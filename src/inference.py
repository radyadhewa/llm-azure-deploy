import os
import torch
import json
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer

"""
Inference script for deploying a language model on Azure ML.
This make your endpoint callable for generating text based on prompts.
"""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init():
    """
    Initialize the model and tokenizer when the endpoint starts.
    This function is called once when the deployment is created.
    """
    global model, tokenizer
    
    try:
        # Azure ML puts your registered model in AZUREML_MODEL_DIR
        model_dir = os.getenv("AZUREML_MODEL_DIR")
        logger.info(f"Model directory: {model_dir}")
        
        # List contents to verify structure
        if model_dir and os.path.exists(model_dir):
            contents = os.listdir(model_dir)
            logger.info(f"Model directory contents: {contents}")
            
            # Determine model path 
            # If model files are in a subfolder, use that; otherwise use the root
            if len(contents) == 1 and os.path.isdir(os.path.join(model_dir, contents[0])):
                model_path = os.path.join(model_dir, contents[0])
            else:
                model_path = model_dir
        else:
            raise ValueError(f"Model directory not found or empty: {model_dir}")
        
        logger.info(f"Loading model from: {model_path}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_path, 
            trust_remote_code=True
        )
        logger.info("Tokenizer loaded successfully")
        
        # Load model with optimizations for inference
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        ).eval()
        
        logger.info("Model loaded successfully")
        logger.info(f"Model device: {model.device}")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise

def run(raw_data):
    """
    Process inference requests. You should adjust this based on your model's requirements.
    
    Expected input format:
    {
        "prompt": "Your prompt here",
        "max_new_tokens": 512,  # optional
        "temperature": 0.7,      # optional
        "top_p": 0.9,           # optional
        "top_k": 50             # optional
    }
    
    Returns:
    {
        "result": "Generated text",
        "prompt_length": 10,
        "generated_length": 100
    }
    """
    try:
        # Parse input
        data = json.loads(raw_data)
        prompt = data.get("prompt", "")
        
        if not prompt:
            return {"error": "No prompt provided"}
        
        # Generation parameters with defaults
        max_new_tokens = data.get("max_new_tokens", 512)
        temperature = data.get("temperature", 0.7)
        top_p = data.get("top_p", 0.9)
        top_k = data.get("top_k", 50)
        do_sample = data.get("do_sample", True)
        
        logger.info(f"Generating response for prompt (length: {len(prompt)})")
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
        input_length = inputs.input_ids.shape[1]
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=do_sample,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        output_length = outputs.shape[1]
        
        logger.info(f"Generation complete (tokens: {output_length})")
        
        return {
            "result": response,
            "prompt_length": input_length,
            "generated_length": output_length - input_length
        }
        
    except json.JSONDecodeError as je:
        logger.error(f"JSON decode error: {je}")
        return {"error": f"Invalid JSON format: {str(je)}"}
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return {"error": str(e)}