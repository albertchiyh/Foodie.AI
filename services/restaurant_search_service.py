import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from models import RestaurantRecommendation
from services.restaurant_service import (
    load_restaurants_from_csv,
    load_faiss_index,
    filter_restaurants_by_zipcode,
    get_zipcodes_for_neighborhood,
    get_neighborhood_by_zipcode
)
from services.llm_ranking_service import rank_restaurants_with_llm
from utils import get_embedding

# Global variables to cache loaded data
_restaurants_cache = None
_faiss_index_cache = None

def initialize_restaurant_data(csv_path: str = "static/manhattan_FoodieAI_new.csv", 
                               index_path: str = "static/text_FoodieAI_index.faiss"):
    """Initialize and cache restaurant data and FAISS index."""
    global _restaurants_cache, _faiss_index_cache
    
    if _restaurants_cache is None:
        print("📖 Loading restaurant data from CSV...")
        _restaurants_cache = load_restaurants_from_csv(csv_path)
        print(f"✅ Loaded {len(_restaurants_cache)} restaurants")
    
    if _faiss_index_cache is None:
        print("📖 Loading FAISS index...")
        _faiss_index_cache = load_faiss_index(index_path)
    
    return _restaurants_cache, _faiss_index_cache

def search_restaurants(query: str, 
                      neighborhood: Optional[str] = None,
                      top_k: int = 10) -> List[RestaurantRecommendation]:
    """
    Search restaurants using FAISS similarity search.
    
    Args:
        query: User query text (food craving description)
        neighborhood: Optional neighborhood filter
        top_k: Number of top results to return
        
    Returns:
        List of restaurant recommendations
    """
    import time
    start_time = time.time()
    
    try:
        # Initialize data
        restaurants, faiss_index = initialize_restaurant_data()
        
        if not restaurants or faiss_index is None:
            print("❌ Failed to load restaurant data or FAISS index")
            return []
        
        # Get zipcodes for neighborhood filter
        zipcodes = get_zipcodes_for_neighborhood(neighborhood)
        
        # Filter restaurants by zipcode if neighborhood is specified
        filtered_indices = filter_restaurants_by_zipcode(restaurants, zipcodes)
        
        if not filtered_indices:
            print(f"⚠️  No restaurants found for neighborhood: {neighborhood}")
            return []
        
        # Generate embedding for user query
        print(f"🔍 Generating embedding for query: {query}")
        query_embedding = get_embedding(query)
        query_vector = np.array([query_embedding], dtype='float32')
        
        # Normalize the query vector for cosine similarity search
        faiss.normalize_L2(query_vector)
        
        # Search in FAISS index
        # Search for more results than needed to account for filtering
        search_k = min(top_k * 5, faiss_index.ntotal) if neighborhood else top_k
        
        distances, indices = faiss_index.search(query_vector, search_k)
        
        # Create recommendations from search results
        recommendations = []
        seen_indices = set()
        
        for dist, idx in zip(distances[0], indices[0]):
            # Skip invalid indices
            if idx < 0 or idx >= len(restaurants):
                continue
            
            # Apply neighborhood filter if specified
            if neighborhood and idx not in filtered_indices:
                continue
            
            # Skip duplicates
            if idx in seen_indices:
                continue
            
            seen_indices.add(idx)
            
            restaurant = restaurants[idx]
            
            # Convert distance to similarity score
            # FAISS with normalized vectors typically uses Inner Product (IP),
            # where 'dist' represents cosine similarity directly (range: -1 to 1)
            # For cosine similarity: normalize from [-1, 1] to [0, 1]
            similarity_score = (dist + 1.0) / 2.0
            similarity_score = max(0.0, min(1.0, similarity_score))  # Clamp to [0, 1]
            
            # Get neighborhood from zipcode
            restaurant_zipcode = restaurant.get("zipcode", 0)
            neighborhood = get_neighborhood_by_zipcode(restaurant_zipcode)
            
            recommendation = RestaurantRecommendation(
                name=restaurant.get("name", ""),
                address=restaurant.get("address", ""),
                cuisine_type=restaurant.get("cuisine_type", ""),
                rating=restaurant.get("rating"),
                match_score=similarity_score,
                zipcode=restaurant_zipcode,
                review_clean=restaurant.get("review_clean"),
                link=restaurant.get("link"),
                neighborhood=neighborhood
            )
            
            recommendations.append(recommendation)
            
            if len(recommendations) >= top_k:
                break
        
        # Sort by match score (descending)
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        
        # Convert recommendations to dict for LLM ranking
        recommendations_dict = []
        for rec in recommendations:
            recommendations_dict.append({
                'name': rec.name,
                'address': rec.address,
                'cuisine_type': rec.cuisine_type,
                'rating': rec.rating,
                'review_clean': rec.review_clean,
                'link': rec.link
            })
        
        # Apply LLM re-ranking
        print("🤖 Applying LLM re-ranking...")
        ranked_restaurants = rank_restaurants_with_llm(query, recommendations_dict, top_k)
        
        # Convert back to RestaurantRecommendation objects with LLM info
        final_recommendations = []
        for ranked_rest in ranked_restaurants:
            # Find the original recommendation to get match_score, zipcode, etc.
            original_rec = next(
                (r for r in recommendations if r.name == ranked_rest['name']),
                None
            )
            
            if original_rec:
                final_rec = RestaurantRecommendation(
                    name=original_rec.name,
                    address=original_rec.address,
                    cuisine_type=original_rec.cuisine_type,
                    rating=original_rec.rating,
                    match_score=original_rec.match_score,
                    zipcode=original_rec.zipcode,
                    review_clean=original_rec.review_clean,
                    link=original_rec.link,
                    neighborhood=original_rec.neighborhood,
                    llm_rank=ranked_rest.get('llm_rank'),
                    llm_comment=ranked_rest.get('llm_comment')
                )
                final_recommendations.append(final_rec)
        
        processing_time = time.time() - start_time
        print(f"✅ Found {len(final_recommendations)} restaurants in {processing_time:.2f}s")
        
        return final_recommendations
        
    except Exception as e:
        print(f"❌ Error in search_restaurants: {e}")
        import traceback
        traceback.print_exc()
        return []

