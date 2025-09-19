#!/usr/bin/env python3
"""
Generate comprehensive South Bay Area parking facility report from reverse geocoding results.
"""

import csv
import json
from collections import defaultdict

def analyze_south_bay_parking_results():
    """Analyze the South Bay parking analysis results."""
    
    parking_facilities = {
        'high_confidence': [],
        'medium_confidence': [],
        'assumed_parking': [],
        'low_confidence': [],
        'no_parking': [],
        'errors': []
    }
    
    total_pois = 0
    
    with open('south_bay_parking_analysis.csv', 'r', encoding='utf-8') as f:
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
                'source': row['parking_source'],
                'city': extract_city_from_address(row['address'])
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

def extract_city_from_address(address: str) -> str:
    """Extract city name from address."""
    parts = address.split(', ')
    if len(parts) >= 2:
        # Usually city is the second to last part before state
        for part in parts:
            if part in ['Palo Alto', 'Mountain View', 'Sunnyvale', 'Cupertino', 
                       'Menlo Park', 'Santa Clara', 'Stanford']:
                return part
    return 'Unknown'

def generate_south_bay_report():
    """Generate comprehensive South Bay parking facility report."""
    
    print("=" * 80)
    print("COMPREHENSIVE PARKING LOT IDENTIFICATION REPORT")
    print("Top 100 POIs - South Bay Area, California")
    print("=" * 80)
    
    facilities, total = analyze_south_bay_parking_results()
    
    print(f"\nTOTAL POIs ANALYZED: {total}")
    total_parking = (len(facilities['high_confidence']) + 
                    len(facilities['medium_confidence']) + 
                    len(facilities['assumed_parking']))
    print(f"PARKING FACILITIES IDENTIFIED: {total_parking}")
    
    # High Confidence Parking Facilities
    print(f"\n" + "=" * 50)
    print(f"HIGH CONFIDENCE PARKING FACILITIES ({len(facilities['high_confidence'])})")
    print("=" * 50)
    print("These POIs explicitly mention parking in their names:")
    
    for i, facility in enumerate(facilities['high_confidence'], 1):
        print(f"\n{i:2d}. {facility['parking_name']}")
        print(f"    POI: {facility['poi_name']}")
        print(f"    Coordinates: ({facility['coordinates'][0]:.6f}, {facility['coordinates'][1]:.6f})")
        print(f"    Address: {facility['address']}")
        print(f"    City: {facility['city']}")
    
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
        print(f"    City: {facility['city']}")
        print(f"    OSM Type: {facility['place_type']}")
    
    # Assumed Parking by City
    print(f"\n" + "=" * 50)
    print(f"ASSUMED PARKING FACILITIES BY CITY ({len(facilities['assumed_parking'])})")
    print("=" * 50)
    print("Hotels, offices, tech companies, and venues that likely have parking:")
    
    # Group by city for better organization
    by_city = defaultdict(list)
    for facility in facilities['assumed_parking']:
        by_city[facility['city']].append(facility)
    
    for city, city_facilities in sorted(by_city.items()):
        print(f"\n{city.upper()} ({len(city_facilities)} facilities):")
        
        # Group by business type within city
        business_types = defaultdict(list)
        for facility in city_facilities:
            btype = facility['place_type'] or 'unknown'
            business_types[btype].append(facility)
        
        for btype, venues in business_types.items():
            if len(venues) > 3:  # Only show categories with multiple entries
                print(f"\n  {btype.upper()} ({len(venues)} locations):")
                for venue in venues[:5]:  # Show first 5
                    print(f"    • {venue['poi_name']}")
                    print(f"      {venue['parking_name']}")
                    print(f"      ({venue['coordinates'][0]:.6f}, {venue['coordinates'][1]:.6f})")
                if len(venues) > 5:
                    print(f"    ... and {len(venues) - 5} more")
                print()
            else:
                for venue in venues:
                    print(f"  • {venue['poi_name']} ({btype})")
                    print(f"    {venue['parking_name']}")
                    print(f"    ({venue['coordinates'][0]:.6f}, {venue['coordinates'][1]:.6f})")
                    print()
    
    # Summary by coordinates
    print(f"\n" + "=" * 80)
    print("SUMMARY: ALL SOUTH BAY PARKING FACILITIES WITH COORDINATES")
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
        print(f"     City: {facility['city']}")
        print(f"     Confidence: {confidence_level}")
        print()
    
    # Tech Companies and Corporate Campuses
    tech_companies = [f for f in facilities['assumed_parking'] + facilities['no_parking'] 
                     if any(keyword in f['poi_name'].lower() for keyword in 
                           ['google', 'apple', 'microsoft', 'intuit', 'uber', 'databricks']) or
                        f['place_type'] in ['company', 'it', 'computer']]
    
    if tech_companies:
        print(f"\n" + "=" * 50)
        print(f"TECH COMPANY CAMPUSES ({len(tech_companies)})")
        print("=" * 50)
        print("Major technology companies in South Bay Area:")
        
        for company in tech_companies:
            parking_status = "HAS PARKING" if company['parking_name'] else "NO PARKING IDENTIFIED"
            print(f"  • {company['poi_name']} - {parking_status}")
            print(f"    ({company['coordinates'][0]:.6f}, {company['coordinates'][1]:.6f})")
            print(f"    {company['address']}")
            print()
    
    print(f"\n" + "=" * 80)
    print("END OF SOUTH BAY AREA REPORT")
    print("=" * 80)

if __name__ == "__main__":
    generate_south_bay_report()