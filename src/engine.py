import asyncio
from typing import Dict

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import settings
from src.models import Transaction
from src.vectordb import vector_search

# Initialize embedding model (Requires GOOGLE_API_KEY)
# We use standard models/embedding-001 for embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    google_api_key=settings.google_api_key
)


async def _get_sql_rules(transaction: Transaction) -> str:
    """
    Simulates a fast SQL query for strict deterministic rules (Amounts, limits).
    In a fully operational mode, this uses aiosqlite or asyncpg against the DB.
    """
    # Mocking standard deterministic thresholds
    rules = []
    if transaction.amount > 10000:
        rules.append("SQL_RULE_001: Transactions over $10000 require manual review or FLAG.")
    
    # Sanctions check
    sanctioned_countries = {"KP", "IR", "SY", "CU"}
    if transaction.destination_country in sanctioned_countries:
        rules.append(f"SQL_RULE_002: Destination {transaction.destination_country} is sanctioned. Action must be BLOCK.")
        
    return "\n".join(rules) if rules else "No strict SQL limits encountered."


async def _get_vector_policies(transaction: Transaction) -> str:
    """
    Calls Pinecone to retrieve nuanced subjective policies based on the transaction context.
    Strictly uses asynchronous embedding generation and vector search.
    """
    query_text = (
        f"merchant category: {transaction.merchant_category}, "
        f"description: {transaction.description or 'None'}"
    )
    
    try:
        # Generate embeddings concurrently without blocking the event loop
        embedding_vector = await embeddings.aembed_query(query_text)
        
        # We can optionally use filter_expr={"merchant_category": transaction.merchant_category}
        # to strictly narrow down the search in Pinecone.
        results = await vector_search(query_embedding=embedding_vector, top_k=3)
        
        if not results:
            return "No specific semantic policies retrieved."
            
        policies = []
        for match in results:
            meta = match.get("metadata", {})
            text = meta.get("text", "No context provided.")
            p_id = meta.get("policy_id", "UNKNOWN")
            
            policies.append(f"[Policy {p_id}]: {text}")
            
        return "\n".join(policies)
        
    except Exception as e:
        # Failsafe returning standard error description, logging should occur here
        return f"Warning: Vector search failed. ({str(e)})"


async def retrieve_context(transaction: Transaction) -> Dict[str, str]:
    """
    Executes 'Hybrid Search' in parallel, combining deterministic SQL rules 
    and unstructured Vector policies. This avoids blocking logic and minimizes latency.
    """
    # Execute both retrievers simultaneously
    sql_task = asyncio.create_task(_get_sql_rules(transaction))
    vector_task = asyncio.create_task(_get_vector_policies(transaction))
    
    sql_rules, vector_policies = await asyncio.gather(sql_task, vector_task)
    
    return {
        "sql_deterministic_rules": sql_rules,
        "vector_semantic_policies": vector_policies
    }
