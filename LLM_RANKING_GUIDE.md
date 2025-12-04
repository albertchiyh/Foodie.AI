# Foodie.AI - LLM Re-ranking Implementation Guide

## Feature Architecture

### 1. **Similarity Search (FAISS)** 
- Embed user queries using `SentenceTransformer('all-MiniLM-L6-v2')`
- Perform cosine similarity search in FAISS index
- Return Top K * 5 candidate restaurants (for filtering and ranking)

### 2. **Neighborhood Filtering**
- User selects Manhattan neighborhood
- Filter restaurants by Zipcode
- Narrow down candidate pool

### 3. **LLM Re-ranking** ✨ (New)
- Send filtered candidates to Mistral AI
- Mistral re-orders based on user query
- Generate brief comments for each restaurant (LLM insights)
- Return final ranked order

### 4. **Frontend Display**
- Show restaurants in LLM ranked order
- Display LLM comments below Review (highlighted in purple)
- Show "by AI" ranking in match badge

## New/Modified Files

### New Files
- `services/llm_ranking_service.py` - LLM ranking logic
- `.env.example` - Environment variable configuration

### Modified Files
1. **`requirements.txt`**
   - Add `mistralai>=0.0.11`

2. **`models.py`**
   - New fields in `RestaurantRecommendation`:
     - `llm_rank: Optional[int]` - LLM ranking (1 = top)
     - `llm_comment: Optional[str]` - LLM insight comment

3. **`services/restaurant_search_service.py`**
   - Import `rank_restaurants_with_llm`
   - Call LLM ranking after search
   - Add ranking and comments to results

4. **`static/foodie_ai_interface.html`**
   - Update `displayResults()` function
   - Add LLM ranking/comment display logic
   - Add `.llm-comment` CSS styling

## User Flow

```
User searches "Spicy Thai"
    ↓
FAISS similarity search → Get Top 50 candidates
    ↓
Filter by selected neighborhood → Get 20-30 restaurants in area
    ↓
Mistral AI re-ranks → "Which restaurants best match the user's needs?"
    ↓
LLM returns ranking + comments → "#1 Thai Jade: 'Perfect match, 9.2 rating'"
    ↓
Frontend displays by LLM rank → User sees most suitable options first
```

## Setup Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Mistral API Key**
   ```bash
   # Add to .env file
   MISTRAL_API_KEY=your_api_key_from_mistral
   ```

3. **Run Application**
   ```bash
   python -m uvicorn app:app --reload
   ```

## Mistral API Configuration

1. Go to https://console.mistral.ai/
2. Create API Key
3. Add to `.env` file
4. Uses `mistral-large-latest` model for ranking

## Advantages

✅ **Smarter Ranking** - Not just based on FAISS similarity  
✅ **Personalized Comments** - LLM generates context-aware insights  
✅ **Neighborhood Aware** - Prioritizes user-selected neighborhoods  
✅ **Easily Extensible** - Modify LLM prompt to change ranking strategy  

## Future Improvements

- [ ] Add user preference memory (spice level, budget, etc.)
- [ ] Implement caching to avoid repeated API calls
- [ ] Add cost monitoring (Mistral API billing)
- [ ] Support other LLMs (OpenAI, Anthropic, etc.)
