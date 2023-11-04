import os
import logging
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


def get_es():
    es = Elasticsearch(
        [os.getenv("host")],
        http_auth=(os.getenv("userName"), os.getenv("password")),
    )
    return es


@app.get("/search")
def search(city: str = None, rating: int = 1, es: Elasticsearch = Depends(get_es)):
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


@hotel_breaker
def search_hotels(city: str, rating: int, es: Elasticsearch):
    rating = rating or 1

    s = Search(using=es, index=os.getenv("indexName"))

    if city is None:
        s = s.query(Q("match_all") & Q("range", Rating={"gte": rating}))
    else:
        s = s.query(
            Q("prefix", CityName={"value": city.lower()})
            & Q("range", Rating={"gte": rating})
        )
    response = s.execute()
    hotels = [hit["_source"].to_dict() for hit in response.hits.hits]
    return hotels


@app.get("/health")
def health_check():
    return JSONResponse(status_code=200, content="OK")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
