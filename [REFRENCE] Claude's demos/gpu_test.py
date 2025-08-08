import torch, torchaudio


print(f"PyTorch version: {torch.__version__}")
print(f"PyTorch audio version: {torchaudio.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"Device name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU'}")
print(f"Memory allocated: {torch.cuda.memory_allocated(0)/1024**2:.1f} MB")