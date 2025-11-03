"""Check and fix American Legion Park Pond duplicate"""
import sys
sys.path.insert(0, '..')
import mysql.connector
from config import DB_CONFIG

db_config = {k: v for k, v in DB_CONFIG.items() if k != 'cursorclass'}
conn = mysql.connector.connect(**db_config)
cur = conn.cursor(dictionary=True)

print("Checking for American Legion Park Pond duplicates...\n")

# Find all American Legion entries in Fort Bend County
cur.execute("""
    SELECT id, name, slug, county, latitude, longitude, address,
           description, amenities, data_source, spot_type, water_body_name
    FROM fishing_spots
    WHERE name LIKE '%American Legion%'
    AND county = 'Fort Bend'
    ORDER BY id
""")

duplicates = cur.fetchall()

print(f"Found {len(duplicates)} entries:\n")

for i, spot in enumerate(duplicates, 1):
    print(f"Entry {i}:")
    print(f"  ID: {spot['id']}")
    print(f"  Name: {spot['name']}")
    print(f"  Slug: {spot['slug']}")
    print(f"  County: {spot['county']}")
    print(f"  Coords: {spot['latitude']}, {spot['longitude']}")
    print(f"  Address: {spot['address']}")
    print(f"  Description: {spot['description']}")
    print(f"  Amenities: {spot['amenities']}")
    print(f"  Data Source: {spot['data_source']}")
    print(f"  Spot Type: {spot['spot_type']}")
    print(f"  Water Body: {spot['water_body_name']}")
    print()

if len(duplicates) > 1:
    print("\nDuplicates detected! Analyzing...")

    # Determine which one to keep (more complete data)
    best_entry = None
    best_score = -1

    for spot in duplicates:
        score = 0
        if spot['address']: score += 3
        if spot['description'] and spot['description'] not in ['null', '']: score += 2
        if spot['amenities']: score += 2
        if spot['latitude'] and spot['longitude']: score += 1

        print(f"Entry {spot['id']} completeness score: {score}")

        if score > best_score:
            best_score = score
            best_entry = spot

    print(f"\nBest entry: ID {best_entry['id']} (score: {best_score})")

    # Merge data if needed
    merged_data = {
        'id': best_entry['id'],
        'address': best_entry['address'],
        'description': best_entry['description'],
        'amenities': best_entry['amenities'],
        'latitude': best_entry['latitude'],
        'longitude': best_entry['longitude']
    }

    # Check if any other entry has data the best one doesn't
    for spot in duplicates:
        if spot['id'] != best_entry['id']:
            if not merged_data['address'] and spot['address']:
                merged_data['address'] = spot['address']
                print(f"  Taking address from ID {spot['id']}")
            if not merged_data['amenities'] and spot['amenities']:
                merged_data['amenities'] = spot['amenities']
                print(f"  Taking amenities from ID {spot['id']}")
            if not merged_data['latitude'] and spot['latitude']:
                merged_data['latitude'] = spot['latitude']
                merged_data['longitude'] = spot['longitude']
                print(f"  Taking coordinates from ID {spot['id']}")

    print("\nMerged data:")
    print(f"  ID to keep: {merged_data['id']}")
    print(f"  Address: {merged_data['address']}")
    print(f"  Description: {merged_data['description']}")
    print(f"  Amenities: {merged_data['amenities']}")
    print(f"  Coords: {merged_data['latitude']}, {merged_data['longitude']}")

    # Update the best entry with merged data
    print(f"\nUpdating entry {merged_data['id']} with merged data...")
    cur.execute("""
        UPDATE fishing_spots
        SET address = %s,
            description = %s,
            amenities = %s,
            latitude = %s,
            longitude = %s
        WHERE id = %s
    """, (
        merged_data['address'],
        merged_data['description'],
        merged_data['amenities'],
        merged_data['latitude'],
        merged_data['longitude'],
        merged_data['id']
    ))

    # Delete the duplicates
    for spot in duplicates:
        if spot['id'] != best_entry['id']:
            print(f"Deleting duplicate entry {spot['id']}...")
            cur.execute("DELETE FROM fishing_spots WHERE id = %s", (spot['id'],))

    conn.commit()
    print("\n[OK] Duplicates merged and removed!")
else:
    print("No duplicates found.")

cur.close()
conn.close()
