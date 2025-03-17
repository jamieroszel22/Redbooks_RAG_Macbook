import torch
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_gpu():
    """Check if CUDA is available and return GPU information."""
    if not torch.cuda.is_available():
        logger.info("No GPU detected. Running on CPU.")
        return False, None

    # GPU is available
    gpu_count = torch.cuda.device_count()
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # Convert to GB
    
    logger.info(f"GPU detected: {gpu_name}")
    logger.info(f"Total GPU memory: {gpu_memory:.2f} GB")
    logger.info(f"Number of GPUs available: {gpu_count}")
    
    return True, {
        "name": gpu_name,
        "count": gpu_count,
        "memory_gb": gpu_memory
    }

if __name__ == "__main__":
    has_gpu, gpu_info = check_gpu()
    if has_gpu:
        print(f"GPU detected: {gpu_info['name']}")
        print(f"Total memory: {gpu_info['memory_gb']:.2f} GB")
        sys.exit(0)  # Success exit code
    else:
        print("No GPU detected")
        sys.exit(1)  # Error exit code
