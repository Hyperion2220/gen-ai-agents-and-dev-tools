# Ubuntu Setup Guide for Ollama and OpenWeb UI

This guide provides instructions on installing Ollama and setting up OpenWeb UI on an Ubuntu system. It also includes steps to run Ollama as a systemd service and create a command shortcut for starting the OpenWeb UI.

## Prerequisites
Windows 11 WSL 2 running Ubuntu 22.04
ffmpeg

## Installation Steps

### Install ffmpeg
You can install ffmpeg by running the following command in your terminal:

```bash
sudo apt update
sudo apt install ffmpeg
```

### Install Ollama
To install Ollama, execute the following command in your terminal:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Install OpenWeb UI with uv
For installing OpenWeb UI using `uv`, use this command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Running OpenWeb UI

Start the Open Web UI by setting up a specific data directory. Ensure you have Python 3.11 installed or adjust the version as needed.

```bash
DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve
```

### Accessing OpenWeb UI
Once started, access the Open Web UI at:

```
http://localhost:8080
```

## Setting Up Ollama as a Systemd Service

To have Ollama start automatically on boot using systemd, follow these steps:

1. **Create a systemd service file for Ollama:**

   ```bash
   sudo nano /etc/systemd/system/ollama.service
   ```
2. **Save and exit** by pressing `CTRL + X`, then `Y`, followed by `Enter`.

4. Reload systemd to recognize the new service:

   ```bash
   sudo systemctl daemon-reload
   ```

5. Enable and start the Ollama service:

   ```bash
   sudo systemctl enable ollama
   sudo systemctl start ollama
   ```

6. **Verify the status** of your service:

   ```bash
   sudo systemctl status ollama
   ```

   You should see output indicating that the `ollama.service` is active and running.

## Creating a Command Shortcut for OpenWeb UI

To run Open Web UI with just the command `openwebui`, follow these steps:

1. **Create a shell script:**

   ```bash
   nano ~/openwebui.sh
   ```

2. Add this content to the script file:

   ```bash
   #!/bin/bash
   export USER_AGENT="OpenWebUI"
   DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve
   ```

3. **Make the script executable:**

   ```bash
   chmod +x ~/openwebui.sh
   ```

4. Move the script to a directory in your PATH, such as `/usr/local/bin`:

   ```bash
   sudo mv ~/openwebui.sh /usr/local/bin/openwebui
   ```

5. **Run OpenWeb UI** by simply typing this command at the Ubuntu terminal:

   ```bash
   openwebui
   ```


## Alternatively, the following is a script thats automates the steps outlined in the guide.

### Instructions for Running the Script:

1. **Save the script**: Copy the script into a file, e.g., `setup.sh`.
2. **Make it executable**: Run `chmod +x setup.sh` to make the script executable.
3. **Execute the script**: Run `./setup.sh` in your terminal.

### Notes:
- This script assumes you have Python 3.11 installed or adjust the version as needed for OpenWeb UI.
- Ensure you have sudo privileges to execute commands that require administrative permissions.
- The systemd service file provided is a basic template; modify it according to Ollama's specific requirements if necessary.
- After running this script, you can start OpenWeb UI by simply typing `openwebui` in your terminal.


```bash
#!/bin/bash

# Update package list
echo "Updating package list..."
sudo apt update

# Install ffmpeg
echo "Installing ffmpeg..."
sudo apt install -y ffmpeg

# Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Install OpenWeb UI using uv
echo "Installing OpenWeb UI with uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Function to setup and start OpenWeb UI
start_openwebui() {
    echo "Starting Open Web UI..."
    DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve &
}

# Create systemd service for Ollama
create_ollama_service() {
    echo "Creating systemd service file for Ollama..."
    cat <<EOF | sudo tee /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Service

[Service]
ExecStart=/usr/local/bin/ollama run
Restart=always

[Install]
WantedBy=default.target
EOF
}

# Reload systemd, enable and start Ollama service
setup_ollama_service() {
    echo "Setting up Ollama as a systemd service..."
    sudo systemctl daemon-reload
    sudo systemctl enable ollama
    sudo systemctl start ollama

    # Verify the status
    sudo systemctl status ollama
}

# Create command shortcut for OpenWeb UI
create_openwebui_command() {
    echo "Creating command shortcut for OpenWeb UI..."
    cat <<'EOF' > ~/openwebui.sh
#!/bin/bash
export USER_AGENT="OpenWebUI"
DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve
EOF

    # Make the script executable and move it to /usr/local/bin
    chmod +x ~/openwebui.sh
    sudo mv ~/openwebui.sh /usr/local/bin/openwebui
}

# Main execution flow
start_openwebui
create_ollama_service
setup_ollama_service
create_openwebui_command

echo "Installation and configuration completed successfully."
```

## Conclusion

By following these steps, you have successfully installed Ollama and OpenWeb UI on your Ubuntu system. You can now manage Ollama as a systemd service and quickly start the Open Web UI using a custom shell command.

For further customization or troubleshooting, consult the respective documentation of Ollama, uv, and systemd.
