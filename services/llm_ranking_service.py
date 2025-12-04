"""
LLM-based restaurant ranking service using Mistral AI.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

# Initialize Mistral client
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=MISTRAL_API_KEY)

def rank_restaurants_with_llm(
    query: str,
    restaurants: List[Dict[str, Any]],
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Use Mistral AI to re-rank restaurants based on the user query.
    
    Args:
        query: User's food craving/query
        restaurants: List of restaurant candidates to rank
        top_k: Number of top restaurants to return after ranking
        
    Returns:
        List of restaurants sorted by LLM ranking with comments
    """
    if not restaurants:
        return []
    
    if not MISTRAL_API_KEY:
        print("⚠️  MISTRAL_API_KEY not set, skipping LLM ranking")
        return restaurants
    
    try:
        # Prepare restaurant information for the LLM
        restaurant_list = []
        for i, rest in enumerate(restaurants, 1):
            rest_info = (
                f"{i}. {rest['name']} - {rest['cuisine_type']} cuisine\n"
                f"   Address: {rest['address']}\n"
                f"   Review: {rest.get('review_clean', 'No review available')}\n"
                f"   Rating: {rest.get('rating', 'N/A')}"
            )
            restaurant_list.append(rest_info)
        
        restaurants_text = "\n\n".join(restaurant_list)
        
        # Create the prompt for LLM ranking
        prompt = f"""You are a New York food expert. The user is looking for: "{query}"

Here is the recommended restaurant list:

{restaurants_text}

Please rank these restaurants based on the user's needs. Consider:
1. Whether the cuisine matches the user's requirements
2. Restaurant ratings and review quality
3. Overall match quality

Please respond in JSON format with:
- ranking: List of ranked restaurant numbers (e.g.: [2, 1, 3])
- comments: Brief comments for each restaurant (explaining user preference), format as {{"restaurant_number": "comment"}}

Example:
{{
    "ranking": [2, 1, 3],
    "comments": {{
        "2": "Perfectly matches your needs, excellent ratings",
        "1": "Great alternative choice",
        "3": "Good but slightly lower ranking"
    }}
}}

Respond ONLY with JSON, no other text."""

        # Call Mistral API
        message = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        response_text = message.choices[0].message.content.strip()
        
        # Parse JSON response
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_json = json.loads(json_match.group())
        else:
            response_json = json.loads(response_text)
        
        ranking = response_json.get("ranking", list(range(1, len(restaurants) + 1)))
        comments = response_json.get("comments", {})
        
        # Re-order restaurants based on LLM ranking
        ranked_restaurants = []
        for rank, original_idx in enumerate(ranking, 1):
            if 1 <= original_idx <= len(restaurants):
                rest = restaurants[original_idx - 1].copy()
                rest['llm_rank'] = rank
                rest['llm_comment'] = comments.get(str(original_idx), "")
                ranked_restaurants.append(rest)
        
        # Add remaining restaurants that weren't ranked
        ranked_indices = set(ranking)
        for idx, rest in enumerate(restaurants, 1):
            if idx not in ranked_indices:
                rest_copy = rest.copy()
                rest_copy['llm_rank'] = len(ranked_restaurants) + 1
                rest_copy['llm_comment'] = ""
                ranked_restaurants.append(rest_copy)
        
        # Return top_k
        return ranked_restaurants[:top_k]
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse LLM response: {e}")
        # Return original restaurants if parsing fails
        for i, rest in enumerate(restaurants, 1):
            rest['llm_rank'] = i
            rest['llm_comment'] = ""
        return restaurants
    
    except Exception as e:
        print(f"❌ Error in LLM ranking: {e}")
        import traceback
        traceback.print_exc()
        # Return original restaurants if LLM call fails
        for i, rest in enumerate(restaurants, 1):
            rest['llm_rank'] = i
            rest['llm_comment'] = ""
        return restaurants
