# POI Parking Lot Analysis

Comprehensive parking facility identification for top 100 POIs across multiple geographies using reverse geocoding.

## Overview

This project analyzes Point of Interest (POI) data to identify parking facilities using coordinates and reverse geocoding. The analysis covers both Houston, Texas and South Bay Area, California, with comprehensive parking facility identification and categorization.

## Features

- **Multi-Geography Support**: Houston and South Bay Area analysis
- **Reverse Geocoding**: Uses OpenStreetMap Nominatim API for location identification
- **Confidence Levels**: High, Medium, and Assumed confidence parking identification
- **Comprehensive Reporting**: Detailed CSV outputs and formatted reports
- **Rate Limiting**: Respectful API usage with proper delays

## Results Summary

### Houston, Texas (100 POIs)
- **Total parking facilities identified**: 38
- **High confidence**: 2 (explicit parking names)
- **Medium confidence**: 9 (OSM categorized as parking)
- **Assumed parking**: 27 (hotels, hospitals, venues)

### South Bay Area, California (100 POIs)
- **Total parking facilities identified**: 57
- **High confidence**: 1 (explicit parking names)
- **Medium confidence**: 8 (OSM categorized as parking)
- **Assumed parking**: 48 (hotels, tech companies, venues)

## Key Files

### Data Files
- `POIs_PUDO_Hotspots_20250910/Top_100_POIs.geojson` - Original POI data
- `complete_parking_analysis.csv` - Houston analysis results
- `south_bay_parking_analysis.csv` - South Bay Area analysis results

### Analysis Scripts
- `batch_geocoder.py` - Houston reverse geocoding analysis
- `south_bay_geocoder.py` - South Bay Area reverse geocoding analysis
- `parking_analysis_report.py` - Houston report generator
- `south_bay_report_generator.py` - South Bay Area report generator

### Quick Analysis
- `quick_parking_analysis.py` - Fast name-based parking identification
- `simple_parking_identifier.py` - Lightweight geocoding script

## Methodology

1. **Data Loading**: Extract POI coordinates from GeoJSON format
2. **Reverse Geocoding**: Query OpenStreetMap Nominatim API for location details
3. **Parking Identification**: Multi-level confidence scoring:
   - **High**: POI name explicitly mentions parking
   - **Medium**: OSM categorizes location as parking facility
   - **Assumed**: Business type likely has parking (hotels, hospitals, venues)
4. **Report Generation**: Comprehensive analysis with coordinates and addresses

## Confidence Levels

### High Confidence
- POI name contains keywords: "parking", "garage", "valet", "lot"
- Examples: "Hilton Americas Valet and Self Parking"

### Medium Confidence
- OpenStreetMap categorizes location as parking facility
- OSM place_type = "parking"

### Assumed Parking
- Business types that typically have parking:
  - Hotels and accommodations
  - Hospitals and medical centers
  - Shopping centers and venues
  - Corporate campuses and tech companies

## Geographic Coverage

### Houston, Texas
- Focus on downtown area and medical center
- Major venues: Toyota Center, George R. Brown Convention Center
- Medical facilities: MD Anderson, Ben Taub Hospital

### South Bay Area, California
- Silicon Valley tech corridor
- Cities: Palo Alto, Mountain View, Sunnyvale, Cupertino
- Major companies: Apple, Google, Microsoft
- Transportation hubs: Caltrain stations

## Usage

```bash
# Run Houston analysis
python3 batch_geocoder.py

# Run South Bay Area analysis
python3 south_bay_geocoder.py

# Generate reports
python3 parking_analysis_report.py
python3 south_bay_report_generator.py
```

## Rate Limiting

The scripts implement proper rate limiting (1.5 second delays) to respect OpenStreetMap's Nominatim usage policy. Progress is saved every 10 POIs to handle interruptions gracefully.

## Technology Stack

- **Python 3**: Core analysis and scripting
- **OpenStreetMap Nominatim**: Reverse geocoding API
- **GeoJSON**: Input data format
- **CSV**: Output data format

## Data Sources

- Original POI data from Uber mobility analysis
- OpenStreetMap for reverse geocoding
- Geographic boundaries for Houston and South Bay Area

---

Generated with Claude Code for comprehensive POI parking analysis.