#!/usr/bin/env python3
"""
Script to identify parking lot names for POI coordinates using reverse geocoding.
Uses OpenStreetMap Nominatim service for reverse geocoding.
"""

import json
import requests
import time
import csv
from typing import List, Dict, Any

def load_poi_data(geojson_file: str) -> List[Dict[str, Any]]:
    """Load POI data from GeoJSON file."""
    with open(geojson_file, 'r') as f:
        data = json.load(f)
    
    pois = []
    for feature in data['features']:
        coords = feature['geometry']['coordinates']
        props = feature['properties']
        pois.append({
            'rowid': props['rowid'],
            'name': props['name'],
            'geography': props.get('geog', 'Unknown'),
            'longitude': coords[0],
            'latitude': coords[1]
        })
    
    return pois

def reverse_geocode(lat: float, lon: float, retries: int = 3) -> Dict[str, Any]:
    """
    Perform reverse geocoding using OpenStreetMap Nominatim service.
    Returns detailed address information including parking-related details.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'format': 'json',
        'lat': lat,
        'lon': lon,
        'zoom': 18,  # High zoom for detailed results
        'addressdetails': 1,
        'extratags': 1,  # Include extra tags that might contain parking info
        'namedetails': 1
    }
    
    headers = {
        'User-Agent': 'POI-Parking-Identifier/1.0 (research@example.com)'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Rate limiting - be respectful to OSM
            time.sleep(1.2)  # 1.2 second delay between requests
            
            return data
            
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed for ({lat}, {lon}): {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retry
            else:
                return {'error': str(e)}

def extract_parking_info(geocode_result: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract parking-related information from reverse geocoding result.
    """
    result = {
        'display_name': '',
        'parking_name': '',
        'amenity': '',
        'building': '',
        'address': '',
        'osm_type': '',
        'category': ''
    }
    
    if 'error' in geocode_result:
        result['error'] = geocode_result['error']
        return result
    
    # Basic information
    result['display_name'] = geocode_result.get('display_name', '')
    result['osm_type'] = geocode_result.get('osm_type', '')
    result['category'] = geocode_result.get('category', '')
    
    # Check if this is explicitly a parking facility
    tags = geocode_result.get('extratags', {})
    address = geocode_result.get('address', {})
    
    # Look for parking-specific tags
    if 'amenity' in tags and tags['amenity'] == 'parking':
        result['parking_name'] = geocode_result.get('name', 'Unnamed Parking')
        result['amenity'] = 'parking'
    
    # Check if it's a building with parking
    if 'building' in tags:
        result['building'] = tags['building']
    
    # Look for parking in the name
    name = geocode_result.get('name', '')
    if any(keyword in name.lower() for keyword in ['parking', 'garage', 'lot', 'valet']):
        result['parking_name'] = name
    
    # Format address
    addr_parts = []
    for key in ['house_number', 'road', 'neighbourhood', 'city', 'state']:
        if key in address and address[key]:
            addr_parts.append(address[key])
    result['address'] = ', '.join(addr_parts)
    
    return result

def process_pois(pois: List[Dict[str, Any]], limit: int = 100) -> List[Dict[str, Any]]:
    """
    Process POIs to identify parking lots.
    """
    results = []
    
    # Take only the top N POIs as requested
    pois_to_process = pois[:limit]
    
    print(f"Processing {len(pois_to_process)} POIs...")
    
    for i, poi in enumerate(pois_to_process, 1):
        print(f"Processing {i}/{len(pois_to_process)}: {poi['name']}")
        
        # Perform reverse geocoding
        geocode_result = reverse_geocode(poi['latitude'], poi['longitude'])
        
        # Extract parking information
        parking_info = extract_parking_info(geocode_result)
        
        # Combine POI data with parking info
        result = {
            'rowid': poi['rowid'],
            'poi_name': poi['name'],
            'geography': poi['geography'],
            'latitude': poi['latitude'],
            'longitude': poi['longitude'],
            'parking_name': parking_info.get('parking_name', ''),
            'display_name': parking_info.get('display_name', ''),
            'address': parking_info.get('address', ''),
            'amenity': parking_info.get('amenity', ''),
            'building': parking_info.get('building', ''),
            'osm_type': parking_info.get('osm_type', ''),
            'category': parking_info.get('category', ''),
            'error': parking_info.get('error', '')
        }
        
        results.append(result)
        
        # Progress indicator
        if i % 10 == 0:
            print(f"Completed {i} POIs...")
    
    return results

def save_results(results: List[Dict[str, Any]], output_file: str):
    """Save results to CSV file."""
    if not results:
        print("No results to save.")
        return
    
    fieldnames = results[0].keys()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results saved to {output_file}")

def main():
    # Load POI data
    print("Loading POI data...")
    pois = load_poi_data('POIs_PUDO_Hotspots_20250910/Top_100_POIs.geojson')
    print(f"Loaded {len(pois)} POIs from GeoJSON file")
    
    # Process top 100 POIs
    results = process_pois(pois, limit=100)
    
    # Save results
    save_results(results, 'top_100_pois_parking_lots.csv')
    
    # Print summary
    print("\n=== SUMMARY ===")
    parking_facilities = [r for r in results if r['parking_name'] or r['amenity'] == 'parking']
    print(f"Total POIs processed: {len(results)}")
    print(f"Identified parking facilities: {len(parking_facilities)}")
    
    if parking_facilities:
        print("\nParking facilities found:")
        for facility in parking_facilities[:10]:  # Show first 10
            print(f"  - {facility['poi_name']}: {facility['parking_name'] or 'Parking facility'}")
    
    print(f"\nFull results saved to: top_100_pois_parking_lots.csv")

if __name__ == "__main__":
    main()