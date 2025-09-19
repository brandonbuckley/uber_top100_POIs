#!/usr/bin/env python3
"""
Quick analysis of POI names to identify parking facilities and extract coordinates.
"""

import json
import csv

def load_and_analyze_pois():
    """Load POI data and identify parking facilities based on name analysis."""
    
    # Load the GeoJSON data
    with open('POIs_PUDO_Hotspots_20250910/Top_100_POIs.geojson', 'r') as f:
        data = json.load(f)
    
    # Keywords that indicate parking facilities
    parking_keywords = [
        'parking', 'garage', 'valet', 'lot', 'deck', 'structure', 
        'park', 'auto park', 'self park', 'motor court'
    ]
    
    results = []
    parking_facilities = []
    
    # Process first 100 POIs
    features = data['features'][:100]
    
    for feature in features:
        coords = feature['geometry']['coordinates']
        props = feature['properties']
        
        poi_data = {
            'rowid': props['rowid'],
            'poi_name': props['name'],
            'geography': props.get('geog', 'Unknown'),
            'longitude': coords[0],
            'latitude': coords[1],
            'is_parking_facility': False,
            'parking_indicator': ''
        }
        
        # Check if POI name suggests it's a parking facility
        name_lower = props['name'].lower()
        for keyword in parking_keywords:
            if keyword in name_lower:
                poi_data['is_parking_facility'] = True
                poi_data['parking_indicator'] = keyword
                parking_facilities.append(poi_data)
                break
        
        results.append(poi_data)
    
    return results, parking_facilities

def save_results(all_results, parking_results):
    """Save results to CSV files."""
    
    # Save all POIs with parking analysis
    with open('top_100_pois_analysis.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['rowid', 'poi_name', 'geography', 'longitude', 'latitude', 
                     'is_parking_facility', 'parking_indicator']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    # Save only parking facilities
    if parking_results:
        with open('parking_facilities_top_100.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['rowid', 'poi_name', 'geography', 'longitude', 'latitude', 'parking_indicator']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for facility in parking_results:
                writer.writerow({
                    'rowid': facility['rowid'],
                    'poi_name': facility['poi_name'],
                    'geography': facility['geography'],
                    'longitude': facility['longitude'],
                    'latitude': facility['latitude'],
                    'parking_indicator': facility['parking_indicator']
                })

def main():
    print("Analyzing top 100 POIs for parking facilities...")
    
    all_results, parking_facilities = load_and_analyze_pois()
    
    print(f"\n=== RESULTS ===")
    print(f"Total POIs analyzed: {len(all_results)}")
    print(f"Parking facilities identified: {len(parking_facilities)}")
    
    if parking_facilities:
        print(f"\nParking facilities found by name analysis:")
        print("-" * 80)
        for i, facility in enumerate(parking_facilities, 1):
            print(f"{i:2d}. {facility['poi_name']}")
            print(f"    Coordinates: ({facility['longitude']:.6f}, {facility['latitude']:.6f})")
            print(f"    Geography: {facility['geography']}")
            print(f"    Parking indicator: '{facility['parking_indicator']}'")
            print()
    
    # Save results
    save_results(all_results, parking_facilities)
    
    print(f"Results saved to:")
    print(f"  - top_100_pois_analysis.csv (all POIs)")
    print(f"  - parking_facilities_top_100.csv (parking facilities only)")

if __name__ == "__main__":
    main()