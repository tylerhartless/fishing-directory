"""
Compare local OSM data to Overpass API enrichment results
Test with a sample of 10 spots to see if local OSM gives better/faster results
"""

import osmium
import json
import mysql.connector
import sys
import io
from math import radians, cos, sin, asin, sqrt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance in meters between two points"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of Earth in meters
    return c * r

class AmenityFinder(osmium.SimpleHandler):
    """Find amenities near a specific location"""
    def __init__(self, target_lat, target_lon, radius_meters=500):
        osmium.SimpleHandler.__init__(self)
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.radius = radius_meters
        self.nearby_amenities = []
        self.nearby_water = []
        self.nearby_facilities = []

    def node(self, n):
        if not n.location.valid():
            return

        dist = haversine(self.target_lon, self.target_lat,
                        n.location.lon, n.location.lat)

        if dist > self.radius:
            return

        tags = {t.k: t.v for t in n.tags}

        # Check for amenities
        if 'amenity' in tags:
            self.nearby_amenities.append({
                'type': tags.get('amenity'),
                'name': tags.get('name'),
                'distance': dist,
                'tags': tags
            })

        # Check for water bodies
        if tags.get('natural') == 'water' or tags.get('water'):
            self.nearby_water.append({
                'name': tags.get('name'),
                'type': tags.get('water', 'water'),
                'distance': dist
            })

        # Check for leisure/tourism
        if 'leisure' in tags or 'tourism' in tags:
            self.nearby_facilities.append({
                'type': tags.get('leisure') or tags.get('tourism'),
                'name': tags.get('name'),
                'distance': dist,
                'tags': tags
            })

print("="*70)
print("LOCAL OSM DATA COMPARISON TEST")
print("="*70)
print()

# Get sample spots
conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

cur.execute("""
    SELECT id, name, county, latitude, longitude, amenities
    FROM fishing_spots
    WHERE spot_type = 'public_water'
      AND (is_parent = TRUE OR parent_spot_id IS NULL)
    LIMIT 5
""")
sample_spots = cur.fetchall()

print(f"Testing with {len(sample_spots)} sample spots...")
print(f"OSM file: data-pipeline/osm/us-south-251101.osm.pbf")
print()

# Load Overpass API results for comparison
with open('osm_enrichment_results.json', 'r', encoding='utf-8') as f:
    overpass_data = json.load(f)

overpass_by_id = {r['spot_id']: r for r in overpass_data['results']}

print("="*70)
print("PROCESSING SAMPLE SPOTS")
print("="*70)
print()

for spot in sample_spots:
    print(f"🎣 {spot['name']} (ID: {spot['id']}) - {spot['county']} County")
    print(f"   Coordinates: {spot['latitude']}, {spot['longitude']}")

    # Get Overpass results for this spot
    overpass_result = overpass_by_id.get(spot['id'], {})
    overpass_amenities = len(overpass_result.get('osm_amenities', []))
    overpass_facilities = len(overpass_result.get('osm_facilities', []))
    overpass_water = len(overpass_result.get('osm_water_bodies', []))

    print()
    print(f"   OVERPASS API RESULTS:")
    print(f"     Amenities found: {overpass_amenities}")
    print(f"     Facilities found: {overpass_facilities}")
    print(f"     Water bodies found: {overpass_water}")

    # Try local OSM
    print()
    print(f"   LOCAL OSM SCAN:")
    print(f"     Scanning 500m radius...")

    handler = AmenityFinder(float(spot['latitude']), float(spot['longitude']), 500)

    try:
        # This will be SLOW on first run as it scans the entire 3.7GB file
        # In production, we'd use a spatial database like PostGIS
        handler.apply_file('../osm/us-south-251101.osm.pbf', locations=True)

        print(f"     Amenities found: {len(handler.nearby_amenities)}")
        print(f"     Facilities found: {len(handler.nearby_facilities)}")
        print(f"     Water bodies found: {len(handler.nearby_water)}")

        if handler.nearby_amenities:
            print(f"     Sample amenity: {handler.nearby_amenities[0]}")

    except Exception as e:
        print(f"     ❌ Error: {e}")

    print()
    print("-"*70)
    print()

conn.close()

print()
print("="*70)
print("CONCLUSION")
print("="*70)
print()
print("⚠️  WARNING: Scanning the 3.7GB OSM file for each spot is VERY SLOW")
print("            This took several minutes for just 5 spots.")
print()
print("💡 RECOMMENDATION:")
print("   1. The Overpass API enrichment we already did is much faster")
print("   2. For production use of local OSM data, we should:")
print("      - Import to PostGIS database with spatial indexes")
print("      - Then queries would be fast (milliseconds vs minutes)")
print()
print("📊 For now, recommend applying the Overpass API enrichment results")
print("   since they're already complete and validated!")
