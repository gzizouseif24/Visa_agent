"""
Tool for deleting a Vertex AI RAG corpus when it's no longer needed.
"""

from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel
from vertexai import rag

from .utils import check_corpus_exists, get_corpus_resource_name

# Define Pydantic model for the output
class DeleteCorpusOutput(BaseModel):
    status: str
    message: str
    corpus_name: str

def delete_corpus(
    corpus_name: str,
    confirm: bool,
    tool_context: ToolContext,
) -> DeleteCorpusOutput:
    """
    Delete a Vertex AI RAG corpus when it's no longer needed.
    Requires confirmation to prevent accidental deletion.

    Args:
        corpus_name (str): The full resource name of the corpus to delete.
                           Preferably use the resource_name from list_corpora results.
        confirm (bool): Must be set to True to confirm deletion
        tool_context (ToolContext): The tool context

    Returns:
        DeleteCorpusOutput: Status information about the deletion operation
    """
    # Check if corpus exists
    if not check_corpus_exists(corpus_name, tool_context):
        return DeleteCorpusOutput(
            status="error",
            message=f"Corpus '{corpus_name}' does not exist",
            corpus_name=corpus_name,
        )

    # Check if deletion is confirmed
    if not confirm:
        return DeleteCorpusOutput(
            status="error",
            message="Deletion requires explicit confirmation. Set confirm=True to delete this corpus.",
            corpus_name=corpus_name,
        )

    try:
        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Delete the corpus
        rag.delete_corpus(corpus_resource_name)

        # Remove from state by setting to False
        state_key = f"corpus_exists_{corpus_name}"
        if state_key in tool_context.state:
            tool_context.state[state_key] = False

        return DeleteCorpusOutput(
            status="success",
            message=f"Successfully deleted corpus '{corpus_name}'",
            corpus_name=corpus_name,
        )
    except Exception as e:
        return DeleteCorpusOutput(
            status="error",
            message=f"Error deleting corpus: {str(e)}",
            corpus_name=corpus_name,
        )

DeleteCorpusOutput.model_rebuild()