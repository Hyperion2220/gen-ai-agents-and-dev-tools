# ComfyUI and Manager Installation Guide for Windows 11 using Conda and PowerShell 7.5

This guide provides step-by-step instructions to install ComfyUI and ComfyUI-Manager on Windows 11 using Conda via PowerShell 7.5. The setup includes creating a Conda environment, installing dependencies, and configuring PyTorch with support for NVIDIA's Blackwell 50xx series GPUs.

## Prerequisites
- Windows 11
- PowerShell 7.5 installed
- Conda (Anaconda or Miniconda) installed
- Git installed
- NVIDIA GPU (optional, for CUDA support)

## Installation Steps

### 1. Open a Conda PowerShell Terminal
- Launch PowerShell 7.5 with Conda initialized. You can do this by opening PowerShell and ensuring Conda is available (e.g., via `conda init powershell` if not already set up).

### 2. Create a Conda Environment
Run the following command to create a new Conda environment named `comfyui_env` with Python 3.12 and Panda:
```powershell
conda create --name comfyui_env python=3.12 pandas
```
Activate the environment:
```powershell
conda activate comfyui_env
```

### 3. Navigate to User Directory
Change to your user directory (adjust the path if your username differs from "Dallas"):
```powershell
cd C:\Users\Dallas
```

### 4. Clone the ComfyUI Repository
Clone the ComfyUI repository from GitHub:
```powershell
git clone https://github.com/comfyanonymous/ComfyUI.git
```

### 5. Enter the ComfyUI Directory
Navigate into the cloned ComfyUI folder:
```powershell
cd ComfyUI
```

### 6. Install PyTorch Nightly (with Blackwell 50xx GPU Support)
Install the PyTorch nightly build, which includes support for NVIDIA's Blackwell 50xx series GPUs and potential performance improvements. Use the following command:
```powershell
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```
**Note**: This assumes CUDA 12.8 support. Adjust the `--index-url` if you need a different CUDA version (e.g., `cu121` for CUDA 12.1).

### 7. Install ComfyUI Dependencies
Install the remaining dependencies listed in the `requirements.txt` file:
```powershell
pip install -r requirements.txt
```

### 8. Install ComfyUI-Manager
Navigate to the `custom_nodes` directory and clone the ComfyUI-Manager repository:
```powershell
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager comfyui-manager
```

## Post-Installation
- To run ComfyUI, return to the `ComfyUI` directory (`cd ..`) and execute:
  ```powershell
  python main.py
  ```
- The ComfyUI-Manager will be available within the ComfyUI interface once launched.

## Shortcut Files
- Use Anaconda PowerShell ComfyUI and ComfyUI files to create easy shortcuts

## Troubleshooting
- Ensure your Conda environment is activated before running commands (`conda activate comfyui_env`).
- If you encounter GPU-related issues, verify your CUDA version matches the PyTorch nightly build installed.
- Check the GitHub repositories ([ComfyUI](https://github.com/comfyanonymous/ComfyUI) and [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)) for additional documentation or issues.

## License
This guide is provided as-is. Refer to the respective repositories for their licensing terms.

---
Last updated: March 13, 2025
```

This README includes clear sections, code blocks for commands, and additional notes for usability. Let me know if you'd like any adjustments!
