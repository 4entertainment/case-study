# Case Study

## Overview


### Features:
- **Weaviate Ingest**: Requests sent to the Weaviate server to extract embeddings using the BGE-M3 model.
- **Weaviate Query**: Query-based similarity search to retrieve relevant documents from the Weaviate vector database.

## Prerequisites

Before starting the setup, ensure you have the following:

- Docker installed (for running Weaviate container)
- Conda installed (for managing the Python environment)
- Hugging Face API Token

### Setup Instructions

1. **Create a Conda Environment**:
   ```bash
   conda create --name my_env python==3.10
   conda activate my_env
   ```
2. **Install Required Python Packages**: Navigate to the project directory and install dependencies:

    ```bash
    pip install -r requirements.txt
    ```
3. **Configure Docker**: The Weaviate server is set up as a Docker container. Use the following command to start the container in detached mode:

    ```bash
    docker compose up -d
    ```
4. **API Key Configuration**: In the docker-compose.yml file, replace the placeholder for the Hugging Face API key with your actual API token:

    ```yaml
    HUGGINGFACE_APIKEY: 'your-huggingface-api-key'
    ```
5. **Run the Application**: Depending on the task you want to perform, run one of the following Python scripts:

    - To ingest text and extract embeddings:
        ```bash
        python weaviate-ingest.py
        ```
    - To query and perform similarity search:
        ```bash
        python weaviate-query.py
        ```
    - Alternatively, you can run the main application:
        ```bash
        python weaviate-app.py
        ```
 ### Notes
- **Weaviate Docker Setup**: The Weaviate server runs inside a Docker container, and its configuration is defined in the `docker-compose.yml` file. The server setup is controlled using the command `docker compose up -d`.

- **GPU Limitation**: This version of the project is not recommended for use in environments with limited GPU resources, as it requires significant computational power for effective operation.

- **Weaviate Query and Ingest Communication**: The client-server communication model is implemented via HTTP requests. The client scripts send requests to the Weaviate server for extracting embeddings and performing similarity searches.

- **Known Issues**
    
    - GPU Limitations: Insufficient GPU resources may cause performance bottlenecks.
    
    - Control in Shared Environments: The Weaviate container setup may not work effectively in shared or collaborative environments due to the challenges of container management.
