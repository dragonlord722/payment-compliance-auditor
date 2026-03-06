import asyncio
from typing import Any, Dict, List, Optional

from pinecone import Pinecone

from src.config import settings

# Initialize synchronous Pinecone client once
# If the API key is not yet set (e.g., during tests without mock envs), 
# this will wait until it's used or we can initialize it lazily.
_pc: Optional[Pinecone] = None

def get_pinecone_client() -> Pinecone:
    global _pc
    if not _pc:
        _pc = Pinecone(api_key=settings.pinecone_api_key)
    return _pc

def get_index(index_name: str = settings.pinecone_index_name) -> Any:
    """
    Returns the Pinecone Index object.
    Type-hinted as Any to avoid deep coupling with Pinecone internals, 
    but strictly used for vector operations.
    """
    client = get_pinecone_client()
    return client.Index(index_name)

async def vector_search(
    query_embedding: List[float], 
    top_k: int = 5, 
    filter_expr: Optional[Dict[str, Any]] = None,
    index_name: str = settings.pinecone_index_name
) -> List[Dict[str, Any]]:
    """
    Perform a vector similarity search in Pinecone.
    Wrapped in asyncio.to_thread to comply with 'Async First' standards and avoid blocking the event loop.
    Strict type checking on inbound and outbound.
    """
    def _search() -> Any:
        idx = get_index(index_name)
        return idx.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_expr
        )
    
    # Run the synchronous Pinecone call in a thread pool
    response = await asyncio.to_thread(_search)
    return response.get("matches", [])

async def upsert_vectors(
    vectors: List[Dict[str, Any]], 
    namespace: str = "",
    index_name: str = settings.pinecone_index_name
) -> None:
    """
    Upsert metadata-rich vectors into Pinecone asynchronously.
    """
    def _upsert() -> None:
        idx = get_index(index_name)
        idx.upsert(vectors=vectors, namespace=namespace)
        
    await asyncio.to_thread(_upsert)
