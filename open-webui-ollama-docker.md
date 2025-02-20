# Deploy Docker with Open WebUI Bundled with Ollama and Image Generation

To deploy the Open WebUI bundled with Ollama and image generation capabilities, follow these steps:

1. Run the following command in your terminal:

    ```bash
    docker run -d -p 3000:8080 --gpus=all \
      -v ollama:/root/.ollama \
      -v open-webui:/app/backend/data \
      --name open-webui \
      --restart no ghcr.io/open-webui/open-webui:ollama
    ```

2. Once the container is running, you can access the Open WebUI interface by visiting `http://localhost:3000` in your web browser.

Make sure to have Docker installed on your system before deploying the application.