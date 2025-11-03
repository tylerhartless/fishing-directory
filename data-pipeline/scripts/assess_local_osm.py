"""
Quick assessment of what's in the local OSM data file
Count amenities, water bodies, etc. to see if it's worth importing
"""

import osmium
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class DataCounter(osmium.SimpleHandler):
    """Count different feature types in OSM data"""
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.node_count = 0
        self.way_count = 0
        self.amenity_count = 0
        self.water_count = 0
        self.leisure_count = 0
        self.park_count = 0
        self.processed = 0

        self.amenity_types = {}
        self.leisure_types = {}

    def node(self, n):
        self.node_count += 1
        self.processed += 1

        if self.processed % 10000000 == 0:
            print(f"  Processed {self.processed:,} nodes...")

        tags = {t.k: t.v for t in n.tags}

        if 'amenity' in tags:
            self.amenity_count += 1
            amenity_type = tags['amenity']
            self.amenity_types[amenity_type] = self.amenity_types.get(amenity_type, 0) + 1

        if tags.get('natural') == 'water' or 'water' in tags:
            self.water_count += 1

        if 'leisure' in tags:
            self.leisure_count += 1
            leisure_type = tags['leisure']
            self.leisure_types[leisure_type] = self.leisure_types.get(leisure_type, 0) + 1

        if tags.get('leisure') == 'park':
            self.park_count += 1

    def way(self, w):
        self.way_count += 1

print("="*70)
print("LOCAL OSM DATA ASSESSMENT")
print("="*70)
print()
print("Scanning: data-pipeline/osm/us-south-251101.osm.pbf")
print("File size: 3.7GB")
print()
print("This will take a few minutes to scan the entire file...")
print()

handler = DataCounter()

try:
    handler.apply_file('../osm/us-south-251101.osm.pbf', locations=True)

    print()
    print("="*70)
    print("SCAN COMPLETE")
    print("="*70)
    print()
    print(f"Total nodes: {handler.node_count:,}")
    print(f"Total ways: {handler.way_count:,}")
    print()
    print(f"🎯 Amenities found: {handler.amenity_count:,}")
    print(f"💧 Water bodies found: {handler.water_count:,}")
    print(f"🏞️  Leisure facilities found: {handler.leisure_count:,}")
    print(f"🌳 Parks found: {handler.park_count:,}")
    print()

    print("Top 10 amenity types:")
    for amenity, count in sorted(handler.amenity_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {amenity}: {count:,}")

    print()
    print("Top 10 leisure types:")
    for leisure, count in sorted(handler.leisure_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {leisure}: {count:,}")

    print()
    print("="*70)
    print("RECOMMENDATION")
    print("="*70)
    print()

    if handler.amenity_count > 100000:
        print("✅ This OSM file contains rich amenity data!")
        print("   Worth importing to PostGIS for fast spatial queries")
        print()
        print("   However, for the current Texas data:")
        print("   - Overpass API enrichment is already complete")
        print("   - 99% success rate with good coverage")
        print("   - Recommend using those results for now")
        print()
        print("   Save PostGIS import for when expanding to more states")
    else:
        print("⚠️  Limited amenity data in this region")
        print("   Overpass API may be better for current needs")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("This might take too long or use too much memory.")
    print("For production use, recommend importing to PostGIS database.")
