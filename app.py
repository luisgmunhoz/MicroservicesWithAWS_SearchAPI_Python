import os
import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
import uvicorn
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import pybreaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
hotel_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

HOST = os.getenv("host", "localhost")
USERNAME = os.getenv("userName", "user")
PASSWORD = os.getenv("password", "pass")
INDEX_NAME = os.getenv("indexName", "index")


def get_es() -> Elasticsearch:
    """Create and return an Elasticsearch client."""
    es = Elasticsearch(
        [HOST],
        http_auth=(USERNAME, PASSWORD),
    )
    return es


@app.get("/search")
def search(
    city: Optional[str] = None, rating: int = 1, es: Elasticsearch = Depends(get_es)
) -> JSONResponse:
    """Search for hotels."""
    try:
        hotels = search_hotels(city, rating, es)
        response = JSONResponse(
            content=hotels,
            status_code=200,
            headers={
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
            },
            media_type="application/json",
        )
        return response

    except pybreaker.CircuitBreakerError as e:
        logger.error("Circuit is open.")
        raise HTTPException(
            status_code=503, detail="Service temporarily unavailable"
        ) from e


@hotel_breaker  # type: ignore
def search_hotels(city: Optional[str], rating: int, es: Elasticsearch) -> List[Dict]:
    """Search for hotels in Elasticsearch."""
    rating = rating or 1

    search_query = Search(using=es, index=INDEX_NAME)

    if city is None:
        search_query = search_query.query(
            Q("match_all") & Q("range", Rating={"gte": rating})
        )
    else:
        search_query = search_query.query(
            Q("prefix", CityName={"value": city.lower()})
            & Q("range", Rating={"gte": rating})
        )
    try:
        response = search_query.execute()
        hotels = [hit["_source"].to_dict() for hit in response.hits.hits]
        return hotels
    except Exception as e:
        logger.error(f"Failed to execute search: {e}")
        return []


@app.get("/health")
def health_check() -> JSONResponse:
    """Check the health of the application."""
    return JSONResponse(status_code=200, content="OK")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
