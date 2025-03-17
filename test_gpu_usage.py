
import torch
import time
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gpu_performance():
    """Test if GPU is actually being used by running a computation benchmark"""
    
    logger.info("Starting GPU performance test...")
    
    # Check if CUDA is available
    if not torch.cuda.is_available():
        logger.error("CUDA is not available. Check your PyTorch installation.")
        return False
    
    # Get device information
    device = torch.device("cuda")
    logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    logger.info(f"CUDA Version: {torch.version.cuda}")
    logger.info(f"PyTorch Version: {torch.__version__}")
    
    # Print memory stats before test
    logger.info(f"GPU Memory - Total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    logger.info(f"GPU Memory - Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    logger.info(f"GPU Memory - Cached: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
    
    # Create large matrices
    size = 10000
    logger.info(f"Creating {size}x{size} matrices...")
    
    # Time CPU computation
    start_time = time.time()
    a_cpu = torch.randn(size, size)
    b_cpu = torch.randn(size, size)
    c_cpu = a_cpu @ b_cpu  # Matrix multiplication
    cpu_time = time.time() - start_time
    logger.info(f"CPU computation time: {cpu_time:.4f} seconds")
    
    # Time GPU computation
    start_time = time.time()
    a_gpu = torch.randn(size, size, device=device)
    b_gpu = torch.randn(size, size, device=device)
    
    # Force synchronization to ensure accurate timing
    torch.cuda.synchronize()
    start_compute = time.time()
    
    c_gpu = a_gpu @ b_gpu  # Matrix multiplication
    
    # Force synchronization again
    torch.cuda.synchronize()
    gpu_time = time.time() - start_compute
    total_gpu_time = time.time() - start_time
    
    logger.info(f"GPU computation time: {gpu_time:.4f} seconds")
    logger.info(f"GPU total time (including transfers): {total_gpu_time:.4f} seconds")
    logger.info(f"Speedup factor (computation only): {cpu_time / gpu_time:.2f}x")
    
    # Print memory stats after test
    logger.info(f"GPU Memory - Allocated after test: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    logger.info(f"GPU Memory - Cached after test: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
    
    # Clear GPU memory
    del a_gpu, b_gpu, c_gpu
    torch.cuda.empty_cache()
    
    if gpu_time < cpu_time:
        logger.info("✅ GPU is working correctly and providing speedup")
        return True
    else:
        logger.warning("⚠️ GPU is not providing expected speedup. Check configuration.")
        return False

def setup_docling_gpu_env():
    """Set optimal environment variables for Docling GPU usage"""
    
    # Set environment variables
    os.environ["DOCLING_USE_GPU"] = "1"
    os.environ["DOCLING_DEVICE"] = "cuda"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    os.environ["TORCH_CUDA_ARCH_LIST"] = "7.0;7.5;8.0;8.6;8.9;9.0"  # Support most modern GPUs
    
    # Force PyTorch to use TF32 on Ampere (RTX 3000 series) and newer GPUs
    # This provides good speedup with minimal precision loss
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    
    # Enable cuDNN benchmarking for best performance
    torch.backends.cudnn.benchmark = True
    
    logger.info("Set optimal GPU environment variables for Docling")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("GPU PERFORMANCE TEST")
    print("=" * 60)
    
    # First set optimal environment
    setup_docling_gpu_env()
    
    # Test GPU performance
    gpu_working = test_gpu_performance()
    
    print("\n" + "=" * 60)
    if gpu_working:
        print("✅ GPU TEST PASSED: Your GPU is working correctly.")
        print("You should set these environment variables before running Docling:")
        print("  DOCLING_USE_GPU=1")
        print("  DOCLING_DEVICE=cuda")
        print("  CUDA_VISIBLE_DEVICES=0")
        print("  TORCH_CUDA_ARCH_LIST=7.0;7.5;8.0;8.6;8.9;9.0")
    else:
        print("⚠️ GPU TEST WARNING: Your GPU may not be optimally configured.")
        print("Please check your CUDA and PyTorch installation.")
    print("=" * 60)
