"""
Enrich Community Fishing Lake data with OpenStreetMap information

This tool queries OSM to find:
1. Actual water body names (lakes, ponds, reservoirs)
2. Park/facility names and details
3. Available amenities (parking, restrooms, boat ramps, etc.)

Usage:
    python scripts/enrich_from_osm.py [--county COUNTY] [--limit N] [--dry-run]
"""

import requests
import time
import sys
import os
import json
from typing import List, Dict, Optional
from math import radians, sin, cos, sqrt, atan2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection


class OSMEnricher:
    """Query OSM for water bodies, facilities, and amenities"""

    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FishingDirectoryBot/1.0 (Educational fishing access directory)'
        })

    def query_features_near_point(self, lat: float, lon: float, radius_meters: int = 500) -> Dict:
        """
        Query OSM for water bodies, parks, and amenities near a point

        Returns dict with:
        - water_bodies: list of nearby water features
        - facilities: list of parks, preserves, recreation areas
        - amenities: dict of available amenities
        """
        # Overpass QL query for comprehensive feature search
        query = f"""
        [out:json][timeout:25];
        (
          // Water bodies
          way["natural"="water"]["name"](around:{radius_meters},{lat},{lon});
          relation["natural"="water"]["name"](around:{radius_meters},{lat},{lon});
          way["water"="lake"]["name"](around:{radius_meters},{lat},{lon});
          way["water"="pond"]["name"](around:{radius_meters},{lat},{lon});
          way["water"="reservoir"]["name"](around:{radius_meters},{lat},{lon});

          // Parks and facilities
          way["leisure"="park"]["name"](around:{radius_meters},{lat},{lon});
          relation["leisure"="park"]["name"](around:{radius_meters},{lat},{lon});
          way["leisure"="nature_reserve"]["name"](around:{radius_meters},{lat},{lon});

          // Amenities
          node["amenity"="parking"](around:{radius_meters},{lat},{lon});
          node["amenity"="toilets"](around:{radius_meters},{lat},{lon});
          way["amenity"="parking"](around:{radius_meters},{lat},{lon});
          way["amenity"="toilets"](around:{radius_meters},{lat},{lon});
          node["leisure"="fishing"](around:{radius_meters},{lat},{lon});
          node["leisure"="slipway"](around:{radius_meters},{lat},{lon});
          node["leisure"="marina"](around:{radius_meters},{lat},{lon});
          way["leisure"="slipway"](around:{radius_meters},{lat},{lon});
          node["amenity"="picnic_site"](around:{radius_meters},{lat},{lon});
          way["leisure"="picnic_table"](around:{radius_meters},{lat},{lon});
        );
        out center tags;
        """

        try:
            response = self.session.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Parse results into categories
            water_bodies = []
            facilities = []
            amenities_found = set()

            for element in data.get('elements', []):
                tags = element.get('tags', {})

                # Get center coordinates
                if 'center' in element:
                    elem_lat = element['center']['lat']
                    elem_lon = element['center']['lon']
                elif 'lat' in element:
                    elem_lat = element['lat']
                    elem_lon = element['lon']
                else:
                    continue

                distance = self.calculate_distance(lat, lon, elem_lat, elem_lon)

                # Categorize water bodies
                if tags.get('natural') == 'water' or tags.get('water') in ['lake', 'pond', 'reservoir']:
                    if 'name' in tags:
                        # Filter out islands - we want the water body, not islands in it
                        name = tags['name']
                        if 'Island' not in name and 'island' not in name:
                            water_bodies.append({
                                'name': name,
                                'type': tags.get('water', tags.get('natural')),
                                'distance_meters': distance,
                                'osm_id': element['id']
                            })

                # Categorize facilities (parks, preserves)
                if tags.get('leisure') == 'park' or tags.get('leisure') == 'nature_reserve':
                    if 'name' in tags:
                        facilities.append({
                            'name': tags['name'],
                            'type': tags.get('leisure'),
                            'distance_meters': distance,
                            'osm_id': element['id'],
                            'phone': tags.get('phone'),
                            'website': tags.get('website')
                        })

                # Track amenities
                amenity_type = tags.get('amenity')
                leisure_type = tags.get('leisure')

                if amenity_type == 'parking':
                    amenities_found.add('parking')
                elif amenity_type == 'toilets':
                    amenities_found.add('restrooms')
                elif amenity_type == 'picnic_site' or leisure_type == 'picnic_table':
                    amenities_found.add('picnic_area')
                elif leisure_type in ['slipway', 'marina']:
                    amenities_found.add('boat_ramp')
                elif leisure_type == 'fishing':
                    amenities_found.add('fishing_pier')

            # Sort by distance
            water_bodies.sort(key=lambda x: x['distance_meters'])
            facilities.sort(key=lambda x: x['distance_meters'])

            return {
                'water_bodies': water_bodies,
                'facilities': facilities,
                'amenities': amenities_found,
                'success': True
            }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'timeout'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters (Haversine)"""
        # Convert to float to handle Decimal types from database
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

        R = 6371000  # Earth radius in meters

        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)

        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def enrich_spot(self, spot: Dict) -> Dict:
        """
        Enrich a single fishing spot with OSM data

        Returns dict with:
        - suggested_name: Better name for the spot
        - suggested_water_body: Actual water body name
        - suggested_amenities: Dict of amenities found
        - facility_info: Park/facility details
        """
        result = {
            'spot_id': spot['id'],
            'current_name': spot['name'],
            'current_water_body': spot['water_body_name'],
            'county': spot['county'],
        }

        # Query OSM
        osm_data = self.query_features_near_point(
            spot['latitude'],
            spot['longitude'],
            radius_meters=500  # 500m radius
        )

        if not osm_data['success']:
            result['status'] = 'osm_error'
            result['error'] = osm_data.get('error')
            return result

        # Extract suggestions
        water_bodies = osm_data['water_bodies']
        facilities = osm_data['facilities']
        amenities = osm_data['amenities']

        # Suggest water body name
        if water_bodies and water_bodies[0]['distance_meters'] < 200:
            result['suggested_water_body'] = water_bodies[0]['name']
            result['water_body_distance'] = water_bodies[0]['distance_meters']
        else:
            result['suggested_water_body'] = None

        # Suggest facility name
        if facilities and facilities[0]['distance_meters'] < 300:
            result['facility_name'] = facilities[0]['name']
            result['facility_distance'] = facilities[0]['distance_meters']
            result['facility_phone'] = facilities[0].get('phone')
            result['facility_website'] = facilities[0].get('website')
        else:
            result['facility_name'] = None

        # Amenities
        result['amenities'] = {
            'parking': 'parking' in amenities,
            'restrooms': 'restrooms' in amenities,
            'picnic_area': 'picnic_area' in amenities,
            'boat_ramp': 'boat_ramp' in amenities,
            'fishing_pier': 'fishing_pier' in amenities,
        }

        result['status'] = 'success'
        return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Enrich fishing spot data with OSM information')
    parser.add_argument('--county', help='Only enrich spots in specific county')
    parser.add_argument('--limit', type=int, default=10, help='Number of spots to enrich (default 10)')
    parser.add_argument('--spot-type', default='public_water', help='Spot type to enrich (default: public_water)')
    parser.add_argument('--dry-run', action='store_true', help='Show suggestions without updating database')
    parser.add_argument('--output', help='Save results to JSON file')
    args = parser.parse_args()

    print("="*60)
    print("OSM Enrichment Tool")
    print("="*60)
    print()

    # Connect to database
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Build query
    query = "SELECT id, name, water_body_name, county, latitude, longitude FROM fishing_spots WHERE spot_type = %s"
    params = [args.spot_type]

    if args.county:
        query += " AND county = %s"
        params.append(args.county)

    query += " ORDER BY RAND() LIMIT %s"
    params.append(args.limit)

    cursor.execute(query, params)
    spots = cursor.fetchall()

    print(f"Enriching {len(spots)} spots...")
    print()

    enricher = OSMEnricher()
    results = []

    for i, spot in enumerate(spots, 1):
        print(f"[{i}/{len(spots)}] {spot['name']} ({spot['county']} County)")
        print(f"         Current: '{spot['water_body_name']}'")

        result = enricher.enrich_spot(spot)
        results.append(result)

        if result['status'] == 'osm_error':
            print(f"         [ERROR] {result.get('error')}")
        elif result['status'] == 'success':
            # Show water body suggestion
            if result['suggested_water_body']:
                if result['suggested_water_body'].lower() != spot['water_body_name'].lower():
                    print(f"         [WATER BODY] Suggest: '{result['suggested_water_body']}' ({int(result['water_body_distance'])}m away)")
                else:
                    print(f"         [OK] Water body name matches OSM")

            # Show facility info
            if result['facility_name']:
                print(f"         [FACILITY] {result['facility_name']} ({int(result['facility_distance'])}m away)")
                if result['facility_website']:
                    print(f"                    Website: {result['facility_website']}")

            # Show amenities
            found_amenities = [k for k, v in result['amenities'].items() if v]
            if found_amenities:
                print(f"         [AMENITIES] {', '.join(found_amenities)}")
            else:
                print(f"         [AMENITIES] None found in OSM")

        print()

        # Rate limiting - OSM requests max 2 per second
        time.sleep(0.6)

    # Summary
    print("="*60)
    print("Summary")
    print("="*60)

    success_count = len([r for r in results if r['status'] == 'success'])
    water_body_suggestions = len([r for r in results if r.get('suggested_water_body')])
    facility_found = len([r for r in results if r.get('facility_name')])

    print(f"Successfully queried: {success_count}/{len(results)}")
    print(f"Water body names found: {water_body_suggestions}")
    print(f"Facilities found: {facility_found}")

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
