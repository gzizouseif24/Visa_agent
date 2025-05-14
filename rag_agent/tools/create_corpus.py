"""
Tool for creating a new Vertex AI RAG corpus.
"""

import re
from typing import Optional

from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel
from vertexai import rag

from ..config import (
    DEFAULT_EMBEDDING_MODEL,
)
from .utils import check_corpus_exists

# Define Pydantic model for the output
class CreateCorpusOutput(BaseModel):
    status: str
    message: str
    corpus_name: str
    display_name: Optional[str] = None
    corpus_created: bool

def create_corpus(
    corpus_name: str,
    tool_context: ToolContext,
) -> CreateCorpusOutput:
    """
    Create a new Vertex AI RAG corpus with the specified name.

    Args:
        corpus_name (str): The name for the new corpus
        tool_context (ToolContext): The tool context for state management

    Returns:
        CreateCorpusOutput: Status information about the operation
    """
    # Check if corpus already exists
    if check_corpus_exists(corpus_name, tool_context):
        return CreateCorpusOutput(
            status="info",
            message=f"Corpus '{corpus_name}' already exists",
            corpus_name=corpus_name,
            corpus_created=False,
        )

    try:
        # Clean corpus name for use as display name
        display_name = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_name)

        # Configure embedding model
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model=DEFAULT_EMBEDDING_MODEL
            )
        )

        # Create the corpus
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )

        # Update state to track corpus existence
        tool_context.state[f"corpus_exists_{corpus_name}"] = True

        # Set this as the current corpus
        tool_context.state["current_corpus"] = corpus_name

        return CreateCorpusOutput(
            status="success",
            message=f"Successfully created corpus '{rag_corpus.display_name}' (Resource: {rag_corpus.name})",
            corpus_name=rag_corpus.name,
            display_name=rag_corpus.display_name,
            corpus_created=True,
        )

    except Exception as e:
        return CreateCorpusOutput(
            status="error",
            message=f"Error creating corpus: {str(e)}",
            corpus_name=corpus_name,
            corpus_created=False,
        )

CreateCorpusOutput.model_rebuild()
