#!/usr/bin/env python3
"""
Generate comprehensive parking facility report from reverse geocoding results.
"""

import csv
import json
from collections import defaultdict

def analyze_parking_results():
    """Analyze the complete parking analysis results."""
    
    # Read the CSV results
    parking_facilities = {
        'high_confidence': [],
        'medium_confidence': [],
        'assumed_parking': [],
        'low_confidence': [],
        'no_parking': [],
        'errors': []
    }
    
    total_pois = 0
    
    with open('complete_parking_analysis.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_pois += 1
            
            confidence = row['parking_confidence']
            poi_info = {
                'rowid': int(row['rowid']),
                'poi_name': row['poi_name'],
                'coordinates': (float(row['longitude']), float(row['latitude'])),
                'parking_name': row['parking_facility_name'],
                'address': row['address'],
                'geocoded_name': row['geocoded_name'],
                'place_type': row['place_type'],
                'source': row['parking_source']
            }
            
            if confidence == 'high':
                parking_facilities['high_confidence'].append(poi_info)
            elif confidence == 'medium':
                parking_facilities['medium_confidence'].append(poi_info)
            elif confidence == 'assumed':
                parking_facilities['assumed_parking'].append(poi_info)
            elif confidence == 'low':
                parking_facilities['low_confidence'].append(poi_info)
            elif confidence == 'error':
                parking_facilities['errors'].append(poi_info)
            else:  # 'none'
                parking_facilities['no_parking'].append(poi_info)
    
    return parking_facilities, total_pois

def generate_report():
    """Generate comprehensive parking facility report."""
    
    print("=" * 80)
    print("COMPREHENSIVE PARKING LOT IDENTIFICATION REPORT")
    print("Top 100 POIs - Houston, Texas")
    print("=" * 80)
    
    facilities, total = analyze_parking_results()
    
    print(f"\nTOTAL POIs ANALYZED: {total}")
    print(f"PARKING FACILITIES IDENTIFIED: {len(facilities['high_confidence']) + len(facilities['medium_confidence']) + len(facilities['assumed_parking'])}")
    
    # High Confidence Parking Facilities
    print(f"\n" + "=" * 50)
    print(f"HIGH CONFIDENCE PARKING FACILITIES ({len(facilities['high_confidence'])})")
    print("=" * 50)
    print("These POIs explicitly mention parking in their names:")
    
    for i, facility in enumerate(facilities['high_confidence'], 1):
        print(f"\n{i:2d}. {facility['parking_name']}")
        print(f"    Coordinates: ({facility['coordinates'][0]:.6f}, {facility['coordinates'][1]:.6f})")
        print(f"    Address: {facility['address']}")
        print(f"    Source: {facility['source']}")
    
    # Medium Confidence Parking Facilities  
    print(f"\n" + "=" * 50)
    print(f"MEDIUM CONFIDENCE PARKING FACILITIES ({len(facilities['medium_confidence'])})")
    print("=" * 50)
    print("These locations are categorized as parking facilities by OpenStreetMap:")
    
    for i, facility in enumerate(facilities['medium_confidence'], 1):
        print(f"\n{i:2d}. {facility['poi_name']}")
        print(f"    Parking Name: {facility['parking_name']}")
        print(f"    Coordinates: ({facility['coordinates'][0]:.6f}, {facility['coordinates'][1]:.6f})")
        print(f"    Address: {facility['address']}")
        print(f"    OSM Type: {facility['place_type']}")
    
    # Assumed Parking (Hotels/Venues)
    print(f"\n" + "=" * 50)
    print(f"ASSUMED PARKING FACILITIES ({len(facilities['assumed_parking'])})")
    print("=" * 50)
    print("Hotels, hospitals, venues, and centers that likely have parking:")
    
    # Group by type for better organization
    business_types = defaultdict(list)
    for facility in facilities['assumed_parking']:
        btype = facility['place_type'] or 'unknown'
        business_types[btype].append(facility)
    
    for btype, venues in business_types.items():
        print(f"\n{btype.upper()} ({len(venues)} facilities):")
        for venue in venues:
            print(f"  • {venue['poi_name']}")
            print(f"    Parking: {venue['parking_name']}")
            print(f"    Coordinates: ({venue['coordinates'][0]:.6f}, {venue['coordinates'][1]:.6f})")
            print(f"    Address: {venue['address']}")
            print()
    
    # Summary by coordinates
    print(f"\n" + "=" * 80)
    print("SUMMARY: ALL IDENTIFIED PARKING FACILITIES WITH COORDINATES")
    print("=" * 80)
    
    all_parking = (facilities['high_confidence'] + 
                  facilities['medium_confidence'] + 
                  facilities['assumed_parking'])
    
    print(f"Total parking facilities identified: {len(all_parking)}")
    print()
    
    for i, facility in enumerate(sorted(all_parking, key=lambda x: x['rowid']), 1):
        confidence_map = {
            'poi_name': 'HIGH',
            'geocoded_name': 'HIGH', 
            'osm_category': 'MEDIUM',
            'business_type': 'ASSUMED',
            'address_context': 'LOW'
        }
        
        confidence_level = confidence_map.get(facility['source'], 'UNKNOWN')
        
        print(f"{i:3d}. {facility['parking_name']}")
        print(f"     POI Name: {facility['poi_name']}")
        print(f"     Coordinates: ({facility['coordinates'][0]:.6f}, {facility['coordinates'][1]:.6f})")
        print(f"     Address: {facility['address']}")
        print(f"     Confidence: {confidence_level}")
        print()
    
    # POIs without identified parking
    print(f"\n" + "=" * 50)
    print(f"POIs WITHOUT IDENTIFIED PARKING ({len(facilities['no_parking'])})")
    print("=" * 50)
    print("These POIs do not appear to have dedicated parking facilities:")
    
    # Group no-parking POIs by type
    no_parking_types = defaultdict(list)
    for poi in facilities['no_parking']:
        ptype = poi['place_type'] or 'unknown'
        no_parking_types[ptype].append(poi)
    
    for ptype, pois in no_parking_types.items():
        print(f"\n{ptype.upper()} ({len(pois)} locations):")
        for poi in pois:
            print(f"  • {poi['poi_name']} - ({poi['coordinates'][0]:.6f}, {poi['coordinates'][1]:.6f})")
    
    print(f"\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)

if __name__ == "__main__":
    generate_report()