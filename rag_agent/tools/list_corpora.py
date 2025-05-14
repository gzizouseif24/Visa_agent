"""
Tool for listing all available Vertex AI RAG corpora.
"""

from typing import Dict, List, Union, Optional

from pydantic import BaseModel
from vertexai import rag

# Define Pydantic models for the output
class CorpusDetail(BaseModel):
    resource_name: str
    display_name: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None

class ListCorporaOutput(BaseModel):
    status: str
    message: str
    corpora: Optional[List[CorpusDetail]] = None

def list_corpora() -> ListCorporaOutput:
    """
    List all available Vertex AI RAG corpora.

    Returns:
        ListCorporaOutput: A list of available corpora and status, with each corpus containing:
            - resource_name: The full resource name to use with other tools
            - display_name: The human-readable name of the corpus
            - create_time: When the corpus was created
            - update_time: When the corpus was last updated
    """
    try:
        # Get the list of corpora
        corpora_response = rag.list_corpora()

        # Process corpus information into a more usable format
        corpus_info_list: List[CorpusDetail] = []
        for corpus_item in corpora_response:
            corpus_data = CorpusDetail(
                resource_name=corpus_item.name,  # Full resource name for use with other tools
                display_name=corpus_item.display_name if hasattr(corpus_item, 'display_name') else "",
                create_time=(
                    str(corpus_item.create_time) if hasattr(corpus_item, "create_time") else ""
                ),
                update_time=(
                    str(corpus_item.update_time) if hasattr(corpus_item, "update_time") else ""
                ),
            )
            corpus_info_list.append(corpus_data)

        return ListCorporaOutput(
            status="success",
            message=f"Found {len(corpus_info_list)} available corpora",
            corpora=corpus_info_list if corpus_info_list else None,
        )
    except Exception as e:
        return ListCorporaOutput(
            status="error",
            message=f"Error listing corpora: {str(e)}",
            corpora=None,
        )

CorpusDetail.model_rebuild()
ListCorporaOutput.model_rebuild()