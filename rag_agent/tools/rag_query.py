"""
Tool for querying Vertex AI RAG corpora and retrieving relevant information.
"""

import logging
from typing import List, Optional

from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel
from vertexai import rag

from ..config import (
    DEFAULT_DISTANCE_THRESHOLD,
    DEFAULT_TOP_K,
)
from .utils import check_corpus_exists, get_corpus_resource_name


class ResultItem(BaseModel):
    source_uri: Optional[str] = None
    source_name: Optional[str] = None
    text: Optional[str] = None
    score: Optional[float] = None


class RagQueryOutput(BaseModel):
    status: str
    message: str
    query: str
    corpus_name: str
    results: Optional[List[ResultItem]] = None
    results_count: Optional[int] = 0


def rag_query(
    corpus_name: str,
    query: str,
    tool_context: ToolContext,
) -> RagQueryOutput:
    """
    Query a Vertex AI RAG corpus with a user question and return relevant information.

    Args:
        corpus_name (str): The name of the corpus to query. If empty, the current corpus will be used.
                          Preferably use the resource_name from list_corpora results.
        query (str): The text query to search for in the corpus
        tool_context (ToolContext): The tool context

    Returns:
        RagQueryOutput: The query results and status
    """
    try:

        # Check if the corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return RagQueryOutput(
                status="error",
                message=f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
                query=query,
                corpus_name=corpus_name,
            )

        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Configure retrieval parameters
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        # Perform the query
        print("Performing retrieval query...")
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_resource_name,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        # Process the response into a more usable format
        processed_results: List[ResultItem] = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = ResultItem(
                    source_uri=(
                        ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""
                    ),
                    source_name=(
                        ctx_group.source_display_name
                        if hasattr(ctx_group, "source_display_name")
                        else ""
                    ),
                    text=ctx_group.text if hasattr(ctx_group, "text") else "",
                    score=ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                )
                processed_results.append(result)

        # If we didn't find any results
        if not processed_results:
            return RagQueryOutput(
                status="warning",
                message=f"No results found in corpus '{corpus_name}' for query: '{query}'",
                query=query,
                corpus_name=corpus_name,
                results=[],
                results_count=0,
            )

        return RagQueryOutput(
            status="success",
            message=f"Successfully queried corpus '{corpus_name}'",
            query=query,
            corpus_name=corpus_name,
            results=processed_results,
            results_count=len(processed_results),
        )

    except Exception as e:
        error_msg = f"Error querying corpus: {str(e)}"
        logging.error(error_msg)
        return RagQueryOutput(
            status="error",
            message=error_msg,
            query=query,
            corpus_name=corpus_name,
        )

ResultItem.model_rebuild()
RagQueryOutput.model_rebuild()