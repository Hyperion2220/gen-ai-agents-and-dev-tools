# Fooocus

Fooocus is a powerful tool for advanced image generation and manipulation. Below are the steps to get it up and running using Docker.

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/lllyasviel/Fooocus.git
   ```

2. **Navigate to the Fooocus Directory**
   ```bash
   cd Foocus
   ```

3. **Build the Docker Image**
   ```bash
   docker build . -t fooocus
   ```

4. **Start Services Using Docker Compose**
   Ensure you have a `docker-compose.yml` file in the directory.
   ```bash
   docker compose up -d
   ```

5. **Run the Fooocus Container**

   Run the container with GPU support and necessary environment variables:

   ```bash
   docker run -d -p 7865:7865 \
     -v fooocus-data:/content/data \
     --name fooocus \
     --gpus all \
     -e CMDARGS=--listen \
     -e DATADIR=/content/data \
     -e config_path=/content/data/config.txt \
     -e config_example_path=/content/data/config_modification_tutorial.txt \
     -e path_checkpoints=/content/data/models/checkpoints/ \
     -e path_loras=/content/data/models/loras/ \
     -e path_embeddings=/content/data/models/embeddings/ \
     -e path_vae_approx=/content/data/models/vae_approx/ \
     -e path_upscale_models=/content/data/models/upscale_models/ \
     -e path_inpaint=/content/data/models/inpaint/ \
     -e path_controlnet=/content/data/models/controlnet/ \
     -e path_clip_vision=/content/data/models/clip_vision/ \
     -e path_fooocus_expansion=/content/data/models/prompt_expansion/fooocus_expansion/ \
     -e path_outputs=/content/app/outputs/ \
     ghcr.io/lllyasviel/fooocus
   ```

## Configuration

- **DATADIR**: Directory where all data is stored.
- **config_path**: Path to the configuration file.
- **config_example_path**: Path to a sample configuration for modification tutorials.

## Model Directories

- **path_checkpoints**: Directory containing model checkpoints.
- **path_loras**: Location of LoRA models.
- **path_embeddings**: Embeddings models directory.
- **path_vae_approx**: Variational Autoencoder approximation models.
- **path_upscale_models**: Models used for upscaling images.
- **path_inpaint**: Inpainting models directory.
- **path_controlnet**: ControlNet models path.
- **path_clip_vision**: CLIP vision models location.
- **path_fooocus_expansion**: Prompt expansion models.

## Output

- **path_outputs**: Directory where output files will be saved.

For further customization and advanced usage, refer to the configuration files in the `fooocus-data` directory.