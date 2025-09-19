#!/usr/bin/env python3
"""
Simple script to identify parking lot names for POI coordinates using reverse geocoding.
Uses only built-in Python libraries with OpenStreetMap Nominatim service.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
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
    """
    params = {
        'format': 'json',
        'lat': str(lat),
        'lon': str(lon),
        'zoom': '18',
        'addressdetails': '1'
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"https://nominatim.openstreetmap.org/reverse?{query_string}"
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'POI-Parking-Identifier/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Rate limiting - be respectful to OSM
            time.sleep(1.2)
            
            return data
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for ({lat}, {lon}): {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return {'error': str(e)}

def extract_parking_info(geocode_result: Dict[str, Any], poi_name: str) -> Dict[str, str]:
    """Extract parking-related information from reverse geocoding result."""
    result = {
        'display_name': '',
        'parking_name': '',
        'address': '',
        'place_type': '',
        'is_parking_related': 'No'
    }
    
    if 'error' in geocode_result:
        result['error'] = geocode_result['error']
        return result
    
    # Basic information
    result['display_name'] = geocode_result.get('display_name', '')
    result['place_type'] = geocode_result.get('type', '')
    
    # Format address
    address = geocode_result.get('address', {})
    addr_parts = []
    for key in ['house_number', 'road', 'neighbourhood', 'city', 'state']:
        if key in address and address[key]:
            addr_parts.append(address[key])
    result['address'] = ', '.join(addr_parts)
    
    # Check for parking-related indicators
    parking_keywords = ['parking', 'garage', 'lot', 'valet', 'deck', 'structure']
    
    # Check POI name for parking indicators
    poi_lower = poi_name.lower()
    if any(keyword in poi_lower for keyword in parking_keywords):
        result['parking_name'] = poi_name
        result['is_parking_related'] = 'Yes - POI Name'
    
    # Check reverse geocoded name
    geocode_name = geocode_result.get('name', '')
    if geocode_name and any(keyword in geocode_name.lower() for keyword in parking_keywords):
        if not result['parking_name']:
            result['parking_name'] = geocode_name
        result['is_parking_related'] = 'Yes - Location Name'
    
    # Check display name
    display_name = result['display_name'].lower()
    if any(keyword in display_name for keyword in parking_keywords):
        result['is_parking_related'] = 'Yes - Address'
    
    # If no parking name identified but POI suggests parking, use POI name
    if not result['parking_name'] and result['is_parking_related'].startswith('Yes'):
        result['parking_name'] = poi_name
    
    return result

def process_pois(pois: List[Dict[str, Any]], limit: int = 100) -> List[Dict[str, Any]]:
    """Process POIs to identify parking lots."""
    results = []
    pois_to_process = pois[:limit]
    
    print(f"Processing {len(pois_to_process)} POIs...")
    
    for i, poi in enumerate(pois_to_process, 1):
        print(f"Processing {i}/{len(pois_to_process)}: {poi['name']}")
        
        # Perform reverse geocoding
        geocode_result = reverse_geocode(poi['latitude'], poi['longitude'])
        
        # Extract parking information
        parking_info = extract_parking_info(geocode_result, poi['name'])
        
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
            'place_type': parking_info.get('place_type', ''),
            'is_parking_related': parking_info.get('is_parking_related', 'No'),
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
    parking_facilities = [r for r in results if r['is_parking_related'].startswith('Yes')]
    print(f"Total POIs processed: {len(results)}")
    print(f"Identified parking-related facilities: {len(parking_facilities)}")
    
    if parking_facilities:
        print(f"\nTop parking-related POIs:")
        for i, facility in enumerate(parking_facilities[:15], 1):
            print(f"  {i:2d}. {facility['poi_name']}")
            if facility['parking_name'] != facility['poi_name']:
                print(f"      -> {facility['parking_name']}")
            print(f"      Coordinates: ({facility['longitude']}, {facility['latitude']})")
            print(f"      Address: {facility['address']}")
            print()
    
    print(f"Full results saved to: top_100_pois_parking_lots.csv")

if __name__ == "__main__":
    main()