from pydantic import BaseModel
from typing import List, Optional

# Restaurant-specific models
class RestaurantSearchRequest(BaseModel):
    query: str
    neighborhood: Optional[str] = None
    top_k: int = 20

class Restaurant(BaseModel):
    name: str
    boro: str
    buildings: str
    street: str
    zipcode: float
    cuisine_type: str
    address: str
    rating: Optional[float] = None
    review: Optional[str] = None
    review_clean: Optional[str] = None

class RestaurantRecommendation(BaseModel):
    name: str
    address: str
    cuisine_type: str
    rating: Optional[float] = None
    match_score: float
    zipcode: float
    review_clean: Optional[str] = None
    link: Optional[str] = None
    neighborhood: Optional[str] = None
    llm_rank: Optional[int] = None
    llm_comment: Optional[str] = None

class RestaurantSearchResponse(BaseModel):
    restaurants: List[RestaurantRecommendation]
    query: str
    total_matches: int
    processing_time: float
