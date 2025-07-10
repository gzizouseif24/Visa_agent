# Vertex AI RAG VISA Agent 

https://rag-agent-app-387445599024.us-central1.run.app

This project implements a Retrieval Augmented Generation (RAG) agent using Google Cloud Vertex AI RAG capabilities, fronted by a simple Flask web application with a chat interface.

The agent is designed to assist with visa-related information, particularly for Tunisian applicants, by querying specialized document corpora and using web search for general information.

## Features

*   **RAG Core**: Leverages Vertex AI for managing document corpora (creating, adding data, querying, deleting) and performing RAG queries.
*   **Web Search**: Integrates a search sub-agent for general knowledge lookups.
*   **Flask API**: Exposes agent functionality via a local web server.
*   **Chat Interface**: A simple HTML/CSS/JS frontend for interacting with the agent in a conversational manner, with streaming responses.
*   **Configurable**: Uses environment variables for Google Cloud Project ID and Location.

## Project Structure

```
.
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION) - DO NOT COMMIT IF IT CONTAINS SECRETS
├── .gitignore            # Specifies intentionally untracked files that Git should ignore
├── rag_agent/            # Core RAG agent package
│   ├── __init__.py       # Package initializer (handles Vertex AI init)
│   ├── agent.py          # Main agent definition (root_agent)
│   ├── config.py         # Configuration for RAG tools (chunk size, embedding models etc.)
│   ├── sub_agents/       # Sub-agents (e.g., for web search)
│   │   └── search_agent/
│   │       ├── __init__.py
│   │       └── agent.py
│   └── tools/            # Custom tools for the RAG agent (corpus management, querying)
│       ├── __init__.py
│       ├── add_data.py
│       ├── create_corpus.py
│       ├── delete_corpus.py
│       ├── delete_document.py
│       ├── get_corpus_info.py
│       ├── list_corpora.py
│       ├── rag_query.py
│       └── utils.py
├── templates/
│   └── index.html        # HTML for the chat frontend
└── README.md             # This file
```

## Setup and Installation

1.  **Prerequisites**:
    *   Python 3.9+ (Python 3.12 was used during development of some parts)
    *   Access to a Google Cloud Platform project with the Vertex AI API enabled.
    *   `gcloud` CLI authenticated and configured with application default credentials, or a service account key with appropriate permissions for Vertex AI (especially RAG and AI Platform services).

2.  **Clone the Repository (if applicable once on GitHub)**:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

3.  **Set up Python Environment**:
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Environment Variables**:
    Create a `.env` file in the project root directory with your Google Cloud project details:
    ```env
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="your-gcp-region" # e.g., us-central1
    # GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json" # Optional: if not using ADC
    ```
    *   Replace `your-gcp-project-id` and `your-gcp-region` with your actual GCP project ID and region.
    *   If you are using a service account key, ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set (either in `.env` or your system environment) and points to the JSON key file. **Important**: Do not commit service account keys to Git. Ensure `.env` is in your `.gitignore` if it contains secrets.

## Running the Application

1.  **Ensure Configuration**: Make sure your `.env` file is correctly set up and your Google Cloud authentication is in place.

2.  **Start the Flask Server**:
    From the project root directory, run:
    ```bash
    python app.py
    ```

3.  **Access the Chat Interface**:
    Open your web browser and navigate to `http://127.0.0.1:5000/` (or the address shown in your terminal).

    You can now interact with the RAG agent through the chat interface.

## How the Agent Works

The agent uses a set of custom tools defined in the `rag_agent/tools/` directory to interact with Vertex AI RAG services. These tools allow it to:
*   Create and delete document corpora.
*   Add data (files from Google Drive or GCS) to corpora.
*   List available corpora and get information about specific ones.
*   Perform RAG queries against a corpus to answer questions.
*   Utilize a web search sub-agent for information not found in its specialized corpora.

The Flask application (`app.py`) provides a simple API endpoint (`/query`) that takes user input and streams it to the agent. The frontend (`templates/index.html`) displays the conversation in a chat format and handles the streaming responses for a dynamic feel.

## Deployment (Conceptual)

While currently set up for local execution, this application can be containerized using Docker and deployed to cloud platforms.

1.  **Docker**: A `Dockerfile` can be created to package the application and its dependencies.
    *   The Docker image would need to include the Python environment, application code, and a mechanism to provide Google Cloud credentials (e.g., by mounting a service account key or using the runtime identity if deployed on GCP).

2.  **Google Cloud Run**: A good target for deploying this Docker container would be Google Cloud Run, which provides a serverless, scalable environment for running containers.
    *   Cloud Run can provide a public URL and can be configured with custom domains.
    *   Authentication with Vertex AI services would typically be handled by assigning an appropriate service account to the Cloud Run service with the necessary IAM permissions.

## Notes
*   The application uses a fixed `user_id` and creates a single ADK session at startup for simplicity. For a multi-user or production scenario, proper session management would be required.
*   Error handling is basic; a production application would need more robust error management and user feedback. 
