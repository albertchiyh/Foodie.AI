import csv
import os
import json
import ast
from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from models import Restaurant

# Neighborhood to zipcode mapping for Manhattan
NEIGHBORHOOD_TO_ZIPCODES = {
    "lower-east-side": ["10002", "10003", "10009"],
    "chinatown": ["10013", "10038"],
    "soho": ["10012", "10013"],
    "greenwich-village": ["10003", "10011", "10012", "10014"],
    "east-village": ["10003", "10009"],
    "chelsea": ["10001", "10011", "10018"],
    "midtown": ["10016", "10017", "10018", "10019", "10020", "10022", "10036"],
    "upper-west-side": ["10023", "10024", "10025"],
    "upper-east-side": ["10021", "10028", "10065", "10075"],
    "harlem": ["10026", "10027", "10029", "10030", "10031", "10032", "10035", "10037", "10039"],
    "washington-heights": ["10032", "10033", "10034", "10040"]
}

def get_zipcodes_for_neighborhood(neighborhood: Optional[str]) -> Optional[List[str]]:
    """Get list of zipcodes for a given neighborhood."""
    if not neighborhood:
        return None
    return NEIGHBORHOOD_TO_ZIPCODES.get(neighborhood)

def get_neighborhood_by_zipcode(zipcode: Optional[float]) -> Optional[str]:
    """Get neighborhood name for a given zipcode."""
    if not zipcode:
        return None
    
    zipcode_str = str(int(zipcode)) if zipcode else None
    if not zipcode_str:
        return None
    
    # Find neighborhood that contains this zipcode
    for neighborhood, zipcodes in NEIGHBORHOOD_TO_ZIPCODES.items():
        if zipcode_str in zipcodes:
            return neighborhood
    
    return None

def load_restaurants_from_csv(csv_path: str = "static/manhattan_FoodieAI_new.csv") -> List[Dict[str, Any]]:
    """Load restaurant data from CSV file."""
    restaurants = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for idx, row in enumerate(reader):
                try:
                    # Parse zipcode (handle float)
                    zipcode = row.get('Zipcode', '')
                    if zipcode:
                        try:
                            zipcode = float(zipcode)
                        except:
                            zipcode = None
                    
                    # Build address
                    buildings = str(row.get('Buildings', '')).strip()
                    street = str(row.get('Street', '')).strip()
                    address = f"{buildings} {street}".strip()
                    
                    restaurant = {
                        "index": idx,
                        "name": str(row.get('Name', '')).strip(),
                        "boro": str(row.get('BORO', '')).strip(),
                        "buildings": buildings,
                        "street": street,
                        "zipcode": zipcode,
                        "cuisine_type": str(row.get('Type', '')).strip(),
                        "address": address,
                        "rating": float(row.get('Rating', 0)) if row.get('Rating') else None,
                        "review": row.get('Review', ''),
                        "review_clean": row.get('Review_clean', '').strip(),
                        "link": str(row.get('link', '')).strip() if row.get('link') else None
                    }
                    
                    restaurants.append(restaurant)
                    
                except Exception as e:
                    print(f"Error processing row {idx}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise
    
    return restaurants

def load_faiss_index(index_path: str = "static/text_FoodieAI_index.faiss") -> Optional[faiss.Index]:
    """Load FAISS index from file."""
    try:
        if not os.path.exists(index_path):
            print(f"FAISS index file not found: {index_path}")
            return None
        
        index = faiss.read_index(index_path)
        print(f"✅ Loaded FAISS index with {index.ntotal} vectors")
        return index
        
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None

def filter_restaurants_by_zipcode(restaurants: List[Dict[str, Any]], zipcodes: Optional[List[str]]) -> List[int]:
    """Filter restaurant indices by zipcode(s). Returns list of indices."""
    if not zipcodes:
        return list(range(len(restaurants)))
    
    # Convert zipcodes to floats for comparison
    zipcode_floats = []
    for zc in zipcodes:
        try:
            zipcode_floats.append(float(zc))
        except:
            continue
    
    filtered_indices = []
    for idx, restaurant in enumerate(restaurants):
        if restaurant.get("zipcode") in zipcode_floats:
            filtered_indices.append(idx)
    
    return filtered_indices

