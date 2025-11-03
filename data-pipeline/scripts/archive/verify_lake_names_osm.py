"""
Verify Lake Names using OpenStreetMap Overpass API

This tool queries OSM to find water bodies near our fishing spots and
compares names to help identify data quality issues.

Usage:
    python scripts/verify_lake_names_osm.py [--county COUNTY] [--limit N]
"""

import requests
import time
import sys
import os
import json
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection


class OSMWaterBodyVerifier:
    """Query OSM for water bodies and verify our lake names"""

    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FishingDirectoryBot/1.0 (Educational fishing access directory)'
        })

    def query_water_bodies_near_point(self, lat: float, lon: float, radius_meters: int = 1000) -> List[Dict]:
        """
        Query OSM for water bodies near a point

        Args:
            lat: Latitude
            lon: Longitude
            radius_meters: Search radius in meters (default 1km)

        Returns:
            List of water body features with names
        """
        # Overpass QL query for water bodies
        query = f"""
        [out:json][timeout:25];
        (
          way["natural"="water"]["name"](around:{radius_meters},{lat},{lon});
          way["water"="lake"]["name"](around:{radius_meters},{lat},{lon});
          way["water"="pond"]["name"](around:{radius_meters},{lat},{lon});
          way["water"="reservoir"]["name"](around:{radius_meters},{lat},{lon});
          relation["natural"="water"]["name"](around:{radius_meters},{lat},{lon});
          relation["water"="lake"]["name"](around:{radius_meters},{lat},{lon});
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

            # Extract water bodies with names
            water_bodies = []
            for element in data.get('elements', []):
                if 'tags' in element and 'name' in element['tags']:
                    # Get center coordinates
                    if 'center' in element:
                        center_lat = element['center']['lat']
                        center_lon = element['center']['lon']
                    elif 'lat' in element:
                        center_lat = element['lat']
                        center_lon = element['lon']
                    else:
                        continue

                    water_bodies.append({
                        'osm_id': element['id'],
                        'osm_type': element['type'],
                        'name': element['tags']['name'],
                        'water_type': element['tags'].get('water', element['tags'].get('natural')),
                        'lat': center_lat,
                        'lon': center_lon,
                        'tags': element['tags']
                    })

            return water_bodies

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] OSM query failed: {e}")
            return []

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters (Haversine)"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371000  # Earth radius in meters

        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)

        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def verify_spot(self, spot: Dict) -> Dict:
        """
        Verify a single fishing spot against OSM

        Returns dict with verification results
        """
        result = {
            'spot_id': spot['id'],
            'spot_name': spot['name'],
            'spot_water_body': spot['water_body_name'],
            'county': spot['county'],
            'lat': spot['latitude'],
            'lon': spot['longitude'],
            'osm_matches': [],
            'status': 'unknown',
            'suggestion': None
        }

        # Query OSM for nearby water bodies
        water_bodies = self.query_water_bodies_near_point(
            spot['latitude'],
            spot['longitude'],
            radius_meters=2000  # 2km radius
        )

        if not water_bodies:
            result['status'] = 'no_osm_data'
            return result

        # Find closest water body
        for wb in water_bodies:
            distance = self.calculate_distance(
                spot['latitude'], spot['longitude'],
                wb['lat'], wb['lon']
            )
            wb['distance_meters'] = distance

        # Sort by distance
        water_bodies.sort(key=lambda x: x['distance_meters'])
        result['osm_matches'] = water_bodies[:3]  # Top 3 closest

        # Check for name matches
        closest = water_bodies[0]
        our_name = spot['water_body_name'].lower()
        osm_name = closest['name'].lower()

        # Simple name matching
        if our_name in osm_name or osm_name in our_name:
            result['status'] = 'name_match'
        elif closest['distance_meters'] < 500:  # Within 500m
            result['status'] = 'name_mismatch'
            result['suggestion'] = f"Consider: '{closest['name']}' (OSM, {int(closest['distance_meters'])}m away)"
        else:
            result['status'] = 'uncertain'

        return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Verify lake names using OpenStreetMap')
    parser.add_argument('--county', help='Only check spots in specific county')
    parser.add_argument('--limit', type=int, default=10, help='Number of spots to check (default 10)')
    parser.add_argument('--spot-type', default='public_water', help='Spot type to check (default: public_water)')
    parser.add_argument('--output', help='Save results to JSON file')
    args = parser.parse_args()

    print("="*60)
    print("OSM Lake Name Verification Tool")
    print("="*60)
    print()

    # Connect to database
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Build query
    query = "SELECT id, name, water_body_name, county, latitude, longitude, spot_type FROM fishing_spots WHERE spot_type = %s"
    params = [args.spot_type]

    if args.county:
        query += " AND county = %s"
        params.append(args.county)

    query += " ORDER BY RAND() LIMIT %s"  # Random sample
    params.append(args.limit)

    cursor.execute(query, params)
    spots = cursor.fetchall()

    print(f"Checking {len(spots)} spots...")
    print()

    verifier = OSMWaterBodyVerifier()
    results = []

    for i, spot in enumerate(spots, 1):
        print(f"[{i}/{len(spots)}] {spot['name']} ({spot['county']} County)")
        print(f"         Our data: '{spot['water_body_name']}'")

        result = verifier.verify_spot(spot)
        results.append(result)

        if result['status'] == 'no_osm_data':
            print(f"         [NO OSM DATA] No water bodies found nearby")
        elif result['status'] == 'name_match':
            print(f"         [OK] Name matches OSM: '{result['osm_matches'][0]['name']}'")
        elif result['status'] == 'name_mismatch':
            print(f"         [MISMATCH] {result['suggestion']}")
            if len(result['osm_matches']) > 1:
                other_names = ', '.join([f"{m['name']} ({int(m['distance_meters'])}m)" for m in result['osm_matches'][1:]])
                print(f"         Other nearby: {other_names}")
        else:
            print(f"         [UNCERTAIN] Closest OSM: '{result['osm_matches'][0]['name']}' ({int(result['osm_matches'][0]['distance_meters'])}m away)")

        print()

        # Rate limiting - OSM requests max 2 per second
        time.sleep(0.6)

    # Summary
    print("="*60)
    print("Summary")
    print("="*60)

    status_counts = {}
    for r in results:
        status_counts[r['status']] = status_counts.get(r['status'], 0) + 1

    for status, count in status_counts.items():
        print(f"{status}: {count}")

    print()
    print("Name Mismatches to Review:")
    print("-" * 60)
    mismatches = [r for r in results if r['status'] == 'name_mismatch']
    for m in mismatches:
        print(f"• {m['spot_name']} ({m['county']})")
        print(f"  Our name: '{m['spot_water_body']}'")
        print(f"  {m['suggestion']}")
        print()

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
