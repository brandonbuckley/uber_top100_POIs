#!/usr/bin/env python3
"""
Batch reverse geocoding with progress tracking and better error handling.
"""

import json
import urllib.request
import urllib.parse
import time
import csv
import os
from typing import List, Dict, Any

def load_poi_data() -> List[Dict[str, Any]]:
    """Load POI data from GeoJSON file."""
    with open('POIs_PUDO_Hotspots_20250910/Top_100_POIs.geojson', 'r') as f:
        data = json.load(f)
    
    pois = []
    for feature in data['features'][:100]:  # Top 100
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

def reverse_geocode_batch(pois: List[Dict[str, Any]], start_index: int = 0) -> List[Dict[str, Any]]:
    """Process POIs in batches with progress saving."""
    results = []
    
    # Load existing results if available
    if os.path.exists('geocoding_progress.json') and start_index == 0:
        try:
            with open('geocoding_progress.json', 'r') as f:
                existing_results = json.load(f)
                if len(existing_results) > 0:
                    print(f"Found {len(existing_results)} existing results, resuming...")
                    results = existing_results
                    start_index = len(results)
        except:
            pass
    
    print(f"Starting geocoding from POI {start_index + 1}...")
    
    for i in range(start_index, len(pois)):
        poi = pois[i]
        print(f"Processing {i + 1}/100: {poi['name']}")
        
        # Prepare request
        params = {
            'format': 'json',
            'lat': str(poi['latitude']),
            'lon': str(poi['longitude']),
            'zoom': '18',
            'addressdetails': '1'
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"https://nominatim.openstreetmap.org/reverse?{query_string}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'POI-Parking-Identifier/1.0')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                geocode_data = json.loads(response.read().decode('utf-8'))
            
            # Extract parking information
            parking_info = analyze_location_for_parking(geocode_data, poi['name'])
            
            result = {
                'rowid': poi['rowid'],
                'poi_name': poi['name'],
                'geography': poi['geography'],
                'latitude': poi['latitude'],
                'longitude': poi['longitude'],
                'geocoded_name': geocode_data.get('name', ''),
                'display_name': geocode_data.get('display_name', ''),
                'place_type': geocode_data.get('type', ''),
                'category': geocode_data.get('category', ''),
                'parking_facility_name': parking_info['parking_name'],
                'parking_confidence': parking_info['confidence'],
                'parking_source': parking_info['source'],
                'address': format_address(geocode_data.get('address', {})),
                'osm_id': geocode_data.get('osm_id', ''),
                'error': ''
            }
            
        except Exception as e:
            print(f"  Error: {e}")
            result = {
                'rowid': poi['rowid'],
                'poi_name': poi['name'],
                'geography': poi['geography'],
                'latitude': poi['latitude'],
                'longitude': poi['longitude'],
                'geocoded_name': '',
                'display_name': '',
                'place_type': '',
                'category': '',
                'parking_facility_name': '',
                'parking_confidence': 'error',
                'parking_source': '',
                'address': '',
                'osm_id': '',
                'error': str(e)
            }
        
        results.append(result)
        
        # Save progress every 10 POIs
        if (i + 1) % 10 == 0:
            with open('geocoding_progress.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"  Progress saved: {i + 1}/100 completed")
        
        # Rate limiting
        time.sleep(1.5)
    
    return results

def analyze_location_for_parking(geocode_data: dict, poi_name: str) -> dict:
    """Analyze geocoded location data to determine parking facility information."""
    parking_keywords = ['parking', 'garage', 'lot', 'deck', 'valet', 'structure', 'motor court']
    
    result = {
        'parking_name': '',
        'confidence': 'none',
        'source': ''
    }
    
    # Check POI name first
    if any(keyword in poi_name.lower() for keyword in parking_keywords):
        result['parking_name'] = poi_name
        result['confidence'] = 'high'
        result['source'] = 'poi_name'
        return result
    
    # Check geocoded name
    geocoded_name = geocode_data.get('name', '')
    if geocoded_name and any(keyword in geocoded_name.lower() for keyword in parking_keywords):
        result['parking_name'] = geocoded_name
        result['confidence'] = 'high' 
        result['source'] = 'geocoded_name'
        return result
    
    # Check place type and category
    place_type = geocode_data.get('type', '').lower()
    category = geocode_data.get('category', '').lower()
    
    if 'parking' in place_type or 'parking' in category:
        result['parking_name'] = geocoded_name or 'Parking Facility'
        result['confidence'] = 'medium'
        result['source'] = 'osm_category'
        return result
    
    # Check display name for parking indicators
    display_name = geocode_data.get('display_name', '').lower()
    if any(keyword in display_name for keyword in parking_keywords):
        result['parking_name'] = 'Parking available'
        result['confidence'] = 'low'
        result['source'] = 'address_context'
        return result
    
    # For hotels, hospitals, venues - likely have parking
    business_types = ['hotel', 'hospital', 'venue', 'center', 'mall', 'stadium', 'arena']
    if any(btype in poi_name.lower() for btype in business_types):
        result['parking_name'] = f'{poi_name} Parking'
        result['confidence'] = 'assumed'
        result['source'] = 'business_type'
        return result
    
    return result

def format_address(address_data: dict) -> str:
    """Format address from geocoded data."""
    parts = []
    for key in ['house_number', 'road', 'neighbourhood', 'city', 'state', 'postcode']:
        if key in address_data and address_data[key]:
            parts.append(address_data[key])
    return ', '.join(parts)

def main():
    print("Loading POI data...")
    pois = load_poi_data()
    print(f"Loaded {len(pois)} POIs for processing")
    
    print("Starting reverse geocoding process...")
    results = reverse_geocode_batch(pois)
    
    # Save final results
    with open('complete_parking_analysis.csv', 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Generate summary
    print(f"\n=== GEOCODING COMPLETE ===")
    print(f"Total POIs processed: {len(results)}")
    
    # Categorize results by confidence
    high_confidence = [r for r in results if r['parking_confidence'] == 'high']
    medium_confidence = [r for r in results if r['parking_confidence'] == 'medium']  
    assumed_parking = [r for r in results if r['parking_confidence'] == 'assumed']
    low_confidence = [r for r in results if r['parking_confidence'] == 'low']
    errors = [r for r in results if r['parking_confidence'] == 'error']
    
    print(f"High confidence parking facilities: {len(high_confidence)}")
    print(f"Medium confidence parking facilities: {len(medium_confidence)}")
    print(f"Assumed parking (hotels/venues): {len(assumed_parking)}")
    print(f"Low confidence: {len(low_confidence)}")
    print(f"Errors: {len(errors)}")
    
    if high_confidence:
        print(f"\nHigh confidence parking facilities:")
        for facility in high_confidence:
            print(f"  - {facility['parking_facility_name']} ({facility['poi_name']})")
    
    print(f"\nResults saved to: complete_parking_analysis.csv")
    
    # Clean up progress file
    if os.path.exists('geocoding_progress.json'):
        os.remove('geocoding_progress.json')

if __name__ == "__main__":
    main()