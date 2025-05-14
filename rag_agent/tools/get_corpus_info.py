"""
Tool for retrieving detailed information about a specific RAG corpus.
"""

from typing import List, Optional

from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel
from vertexai import rag

from .utils import check_corpus_exists, get_corpus_resource_name

# Define Pydantic models for the output
class CorpusFileInfo(BaseModel):
    file_id: str
    display_name: Optional[str] = None
    source_uri: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None

class GetCorpusInfoOutput(BaseModel):
    status: str
    message: str
    corpus_name: str
    corpus_display_name: Optional[str] = None
    file_count: Optional[int] = 0
    files: Optional[List[CorpusFileInfo]] = None

def get_corpus_info(
    corpus_name: str,
    tool_context: ToolContext,
) -> GetCorpusInfoOutput:
    """
    Get detailed information about a specific RAG corpus, including its files.

    Args:
        corpus_name (str): The full resource name of the corpus to get information about.
                           Preferably use the resource_name from list_corpora results.
        tool_context (ToolContext): The tool context

    Returns:
        GetCorpusInfoOutput: Information about the corpus and its files
    """
    try:
        # Check if corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return GetCorpusInfoOutput(
                status="error",
                message=f"Corpus '{corpus_name}' does not exist",
                corpus_name=corpus_name,
            )

        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Try to get corpus details first
        corpus_display_name = corpus_name  # Default if we can't get actual display name

        # Process file information
        file_details: List[CorpusFileInfo] = []
        try:
            # Get the list of files
            files = rag.list_files(corpus_resource_name)
            for rag_file in files:
                # Get document specific details
                try:
                    # Extract the file ID from the name
                    file_id = rag_file.name.split("/")[-1]

                    file_info = CorpusFileInfo(
                        file_id=file_id,
                        display_name=(
                            rag_file.display_name
                            if hasattr(rag_file, "display_name")
                            else ""
                        ),
                        source_uri=(
                            rag_file.source_uri
                            if hasattr(rag_file, "source_uri")
                            else ""
                        ),
                        create_time=(
                            str(rag_file.create_time)
                            if hasattr(rag_file, "create_time")
                            else ""
                        ),
                        update_time=(
                            str(rag_file.update_time)
                            if hasattr(rag_file, "update_time")
                            else ""
                        ),
                    )
                    file_details.append(file_info)
                except Exception:
                    # Continue to the next file
                    continue
        except Exception:
            # Continue without file details
            pass

        # Basic corpus info
        return GetCorpusInfoOutput(
            status="success",
            message=f"Successfully retrieved information for corpus '{corpus_display_name}'",
            corpus_name=corpus_name,
            corpus_display_name=corpus_display_name,
            file_count=len(file_details),
            files=file_details if file_details else None,
        )

    except Exception as e:
        return GetCorpusInfoOutput(
            status="error",
            message=f"Error getting corpus information: {str(e)}",
            corpus_name=corpus_name,
        )

CorpusFileInfo.model_rebuild()
GetCorpusInfoOutput.model_rebuild()