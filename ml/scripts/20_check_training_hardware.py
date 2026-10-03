import platform
import os

import torch


print("=" * 70)
print("BreedVision AI - Phase 5 Training Hardware Check")
print("=" * 70)

print()
print("Operating System :", platform.system(), platform.release())
print("Python Version   :", platform.python_version())
print("PyTorch Version  :", torch.__version__)
print("CPU Threads      :", os.cpu_count())

print()
print("-" * 70)
print("ACCELERATOR CHECK")
print("-" * 70)

cuda_available = torch.cuda.is_available()

print("CUDA Available   :", cuda_available)

if cuda_available:
    print("CUDA Version     :", torch.version.cuda)
    print("GPU Count        :", torch.cuda.device_count())

    for index in range(torch.cuda.device_count()):
        properties = torch.cuda.get_device_properties(index)

        memory_gb = properties.total_memory / (1024 ** 3)

        print()
        print(f"GPU {index}")
        print("Name             :", properties.name)
        print("VRAM             :", round(memory_gb, 2), "GB")

    device = torch.device("cuda")

else:
    print("CUDA GPU         : Not detected")
    device = torch.device("cpu")


print()
print("-" * 70)
print("TRAINING DEVICE")
print("-" * 70)

print("Selected Device  :", device)


# Small PyTorch test

print()
print("Running tensor test...")

x = torch.randn(1000, 1000)
y = torch.randn(1000, 1000)

x = x.to(device)
y = y.to(device)

z = torch.matmul(x, y)

print("Tensor Device    :", z.device)
print("Tensor Shape     :", tuple(z.shape))

print()
print("=" * 70)
print("Hardware check completed successfully.")
print("=" * 70)