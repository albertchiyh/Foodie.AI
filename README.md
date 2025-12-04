# Foodie.AI - Manhattan Restaurant Recommendation System

A smart restaurant recommendation system for Manhattan that helps users find restaurants based on their food cravings. The system uses semantic embeddings with FAISS for fast similarity search to match user queries with restaurant reviews.

## Features

- **AI-Powered Search**: Natural language search understands exactly what you're craving
- **Location-Based Filtering**: Filter restaurants by Manhattan neighborhood
- **FAISS Similarity Search**: Fast and efficient semantic search using FAISS index
- **Review-Based Matching**: Matches user queries with restaurant reviews using SentenceTransformer embeddings
- **Restaurant Recommendations**: Get restaurants with match scores, ratings, and reviews

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure you have the required data files in the `static/` directory:
   - `manhattan_FoodieAI.csv`: CSV file with restaurant data
   - `text_FoodieAI_index.faiss`: FAISS index file with pre-computed embeddings

3. Run the application:

```bash
python app.py
```

The application will start at `http://localhost:8000`

## Usage

1. **Search for Restaurants**:
   - Go to the web interface at `http://localhost:8000`
   - Describe your food craving in natural language (e.g., "spicy Thai crab curry", "authentic Italian pasta")
   - Optionally select a Manhattan neighborhood to filter results
   - Click "Find My Perfect Restaurant" to get recommendations

2. **View Results**:
   - See restaurants ranked by match score (cosine similarity)
   - View restaurant details: name, cuisine type, address, rating
   - Read review snippets that match your query

## API Endpoints

### Search Restaurants

```
POST /search-restaurants
Content-Type: application/json

{
  "query": "spicy Thai crab curry",
  "neighborhood": "chinatown",  // optional
  "top_k": 10
}
```

Response:
```json
{
  "restaurants": [
    {
      "name": "Restaurant Name",
      "address": "123 Main St",
      "cuisine_type": "Thai",
      "rating": 4.5,
      "match_score": 0.85,
      "zipcode": 10013,
      "review_clean": "Great Thai food..."
    }
  ],
  "query": "spicy Thai crab curry",
  "total_matches": 10,
  "processing_time": 0.123
}
```

## How It Works

1. **Data Loading**: Restaurant data is loaded from CSV file with reviews
2. **FAISS Index**: Pre-computed embeddings stored in FAISS index for fast search
3. **Query Embedding**: User query is embedded using SentenceTransformer ('all-MiniLM-L6-v2')
4. **Similarity Search**: FAISS performs fast cosine similarity search
5. **Neighborhood Filtering**: Results are filtered by zipcode based on selected neighborhood
6. **Ranking**: Results are ranked by match score (cosine similarity)

## File Structure

```
├── app.py                              # Main FastAPI application
├── models.py                           # Pydantic data models
├── utils.py                            # Embedding utilities (SentenceTransformer)
├── services/
│   ├── restaurant_service.py          # CSV loading and FAISS index management
│   └── restaurant_search_service.py   # Restaurant search logic with FAISS
├── static/
│   ├── index.html                     # Frontend HTML interface
│   ├── manhattan_FoodieAI.csv         # Restaurant data CSV
│   └── text_FoodieAI_index.faiss     # FAISS index file
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## Neighborhood Mapping

The system supports filtering by Manhattan neighborhoods:

- Lower East Side
- Chinatown
- SoHo
- Greenwich Village
- East Village
- Chelsea
- Midtown
- Upper West Side
- Upper East Side
- Harlem
- Washington Heights

Each neighborhood is mapped to specific zipcodes for accurate filtering.

## Technologies Used

- **FastAPI**: Web framework for building APIs
- **FAISS**: Facebook AI Similarity Search for efficient vector search
- **SentenceTransformer**: For generating semantic embeddings
- **Pandas**: For CSV data processing
- **NumPy**: For numerical operations

## Customization

- Modify `services/restaurant_service.py` to change CSV parsing logic or neighborhood mappings
- Adjust `services/restaurant_search_service.py` for different search algorithms
- Update the UI in `static/index.html` for different interface designs
- Modify embedding models in `utils.py` (currently uses 'all-MiniLM-L6-v2')

## Troubleshooting

- Ensure CSV file and FAISS index are in the `static/` directory
- Check that the FAISS index matches the CSV data (same number of rows)
- Verify embeddings were created with the same model ('all-MiniLM-L6-v2')
- Check console logs for error messages during startup or search
