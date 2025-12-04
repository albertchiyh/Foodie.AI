import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from models import RestaurantSearchRequest, RestaurantSearchResponse
from services.restaurant_search_service import search_restaurants, initialize_restaurant_data
from services.restaurant_service import get_zipcodes_for_neighborhood

app = FastAPI(title="Foodie.AI", description="AI-powered restaurant recommendation system for Manhattan")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load environment variables
load_dotenv()

# Initialize restaurant data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application with restaurant data."""
    print("🚀 Starting Foodie.AI...")
    try:
        initialize_restaurant_data()
        print("🎉 Foodie.AI is ready!")
    except Exception as e:
        print(f"❌ Failed to initialize Foodie.AI: {e}")

@app.post("/search-restaurants", response_model=RestaurantSearchResponse)
async def search_restaurants_endpoint(request: RestaurantSearchRequest):
    """Search for restaurants based on user query and optional neighborhood filter."""
    start_time = time.time()
    
    try:
        recommendations = search_restaurants(
            query=request.query,
            neighborhood=request.neighborhood,
            top_k=request.top_k
        )
        
        return RestaurantSearchResponse(
            restaurants=recommendations,
            query=request.query,
            total_matches=len(recommendations),
            processing_time=time.time() - start_time
        )
        
    except Exception as e:
        print(f"Error in restaurant search: {e}")
        raise HTTPException(status_code=500, detail=f"Restaurant search failed: {str(e)}")

@app.get("/api/neighborhood-by-zipcode/{zipcode}")
async def get_neighborhood_by_zipcode(zipcode: str):
    """Get neighborhood for a given zipcode."""
    try:
        # Get all neighborhoods and their zipcodes
        from services.restaurant_service import NEIGHBORHOOD_TO_ZIPCODES
        
        # Convert zipcode to string for comparison
        zipcode_str = str(zipcode).strip()
        
        # Find neighborhood that contains this zipcode
        for neighborhood, zipcodes in NEIGHBORHOOD_TO_ZIPCODES.items():
            if zipcode_str in zipcodes:
                return {
                    "neighborhood": neighborhood,
                    "zipcode": zipcode_str,
                    "found": True
                }
        
        return {
            "neighborhood": None,
            "zipcode": zipcode_str,
            "found": False
        }
    except Exception as e:
        print(f"Error getting neighborhood for zipcode {zipcode}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get neighborhood: {str(e)}")

# UI endpoint - will be created from the HTML file
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the Foodie.AI interface."""
    html_file_path = "static/foodie_ai_interface.html"
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body>
                <h1>Foodie.AI</h1>
                <p>Frontend HTML file not found. Please create static/index.html</p>
            </body>
        </html>
        """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
