"""
Apply all corrections from corrections_manifest.json

This script should be run after importing raw data to ensure
the database matches the manually-curated state.

Usage:
    python apply_all_corrections.py [--dry-run]
"""

import mysql.connector
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('..')
from config import DB_CONFIG

def load_manifest():
    """Load corrections manifest"""
    manifest_path = Path(__file__).parent / 'corrections_manifest.json'
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_name_fixes(cur, fixes, dry_run=False):
    """Apply name corrections"""
    print("\n" + "="*70)
    print("APPLYING NAME FIXES")
    print("="*70 + "\n")

    fixed_count = 0
    for fix in fixes:
        # Find the spot
        cur.execute("""
            SELECT id, name, water_body_name, description
            FROM fishing_spots
            WHERE name = %s AND county = %s AND data_source = %s
        """, (fix['old_name'], fix['county'], fix['source']))

        spot = cur.fetchone()
        if not spot:
            print(f"⚠️  NOT FOUND: {fix['old_name']} ({fix['county']}) - may already be fixed")
            continue

        print(f"✓ Found: {spot['name']} (ID {spot['id']})")
        print(f"  → Updating to: {fix['new_name']}")
        print(f"  Reason: {fix['reason']}")

        if not dry_run:
            updates = {
                'name': fix['new_name'],
                'slug': fix['new_name'].lower().replace(' ', '-') + f"-{fix['county'].lower()}"
            }

            if 'new_water_body' in fix:
                updates['water_body_name'] = fix['new_water_body']

            if 'new_description' in fix:
                updates['description'] = fix['new_description']

            set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [spot['id']]

            cur.execute(f"UPDATE fishing_spots SET {set_clause} WHERE id = %s", values)
            fixed_count += 1
        print()

    return fixed_count

def apply_duplicate_deletions(cur, deletions, dry_run=False):
    """Delete known duplicates"""
    print("\n" + "="*70)
    print("DELETING DUPLICATES")
    print("="*70 + "\n")

    deleted_count = 0
    for dup in deletions:
        # Find the duplicate
        query = "SELECT id, name, spot_type, county FROM fishing_spots WHERE name = %s AND county = %s"
        params = [dup['name'], dup['county']]

        if 'source' in dup:
            query += " AND data_source = %s"
            params.append(dup['source'])

        cur.execute(query, params)
        spots = cur.fetchall()

        if not spots:
            print(f"⚠️  NOT FOUND: {dup['name']} ({dup['county']}) - may already be deleted")
            continue

        for spot in spots:
            print(f"🗑️  Deleting: {spot['name']} (ID {spot['id']}, {spot['spot_type']})")
            print(f"  Reason: {dup['reason']}")
            if 'keep_instead' in dup:
                print(f"  Keeping: {dup['keep_instead']['name']}")

            if not dry_run:
                cur.execute("DELETE FROM fishing_spots WHERE id = %s", (spot['id'],))
                deleted_count += 1
            print()

    return deleted_count

def apply_numbered_pond_consolidations(cur, groups, dry_run=False):
    """Consolidate numbered ponds into parent entries"""
    print("\n" + "="*70)
    print("CONSOLIDATING NUMBERED PONDS")
    print("="*70 + "\n")

    parents_created = 0
    children_linked = 0

    for group in groups:
        print(f"📍 {group['base_name']} ({group['county']})")

        # Check if parent already exists
        cur.execute("""
            SELECT id, name FROM fishing_spots
            WHERE name = %s AND county = %s AND is_parent = TRUE
        """, (group['base_name'], group['county']))

        parent = cur.fetchone()

        if parent:
            print(f"  ✓ Parent already exists (ID {parent['id']})")
            parent_id = parent['id']
        else:
            # Find first child to get coordinates
            cur.execute("""
                SELECT id, latitude, longitude, state, spot_type
                FROM fishing_spots
                WHERE name = %s AND county = %s
                LIMIT 1
            """, (group['numbered_entries'][0], group['county']))

            first_child = cur.fetchone()

            if not first_child:
                print(f"  ⚠️  No children found - may already be consolidated")
                print()
                continue

            if not dry_run:
                # Create parent
                slug = f"{group['base_name'].lower().replace(' ', '-')}-{group['county'].lower()}"
                water_body = group.get('water_body', group['base_name'])
                description = group.get('description', f"Public water access with {len(group['numbered_entries'])} fishing areas.")

                cur.execute("""
                    INSERT INTO fishing_spots
                    (name, slug, spot_type, county, state, latitude, longitude,
                     water_body_name, description, data_source, is_parent, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Manual_Consolidation', TRUE, NOW(), NOW())
                """, (group['base_name'], slug, first_child['spot_type'], group['county'],
                      first_child['state'], first_child['latitude'], first_child['longitude'],
                      water_body, description))

                parent_id = cur.lastrowid
                parents_created += 1
                print(f"  ✓ Created parent (ID {parent_id})")
            else:
                print(f"  [DRY-RUN] Would create parent")
                parent_id = None

        # Link children
        for child_name in group['numbered_entries']:
            cur.execute("""
                SELECT id, name FROM fishing_spots
                WHERE name = %s AND county = %s AND (parent_spot_id IS NULL OR parent_spot_id != %s)
            """, (child_name, group['county'], parent_id if parent_id else 0))

            children = cur.fetchall()

            for child in children:
                if not dry_run and parent_id:
                    cur.execute("""
                        UPDATE fishing_spots
                        SET parent_spot_id = %s, is_parent = FALSE
                        WHERE id = %s
                    """, (parent_id, child['id']))
                    children_linked += 1
                    print(f"  ✓ Linked: {child['name']} (ID {child['id']})")
                else:
                    print(f"  [DRY-RUN] Would link: {child['name']}")

        print()

    return parents_created, children_linked

def apply_sheldon_consolidation(cur, sheldon_config, dry_run=False):
    """Apply Sheldon Lake complex consolidation"""
    print("\n" + "="*70)
    print("SHELDON LAKE CONSOLIDATION")
    print("="*70 + "\n")

    parent_config = sheldon_config['parent']

    # Find parent
    cur.execute("""
        SELECT id, name, spot_type FROM fishing_spots
        WHERE name = %s AND county = %s
    """, (parent_config['name'], parent_config['county']))

    parent = cur.fetchone()

    if not parent:
        print("⚠️  Parent not found - may need to be imported first")
        return 0, 0

    print(f"✓ Found parent: {parent['name']} (ID {parent['id']})")

    # Ensure it's marked as parent and correct type
    if not dry_run:
        cur.execute("""
            UPDATE fishing_spots
            SET is_parent = TRUE, spot_type = %s
            WHERE id = %s
        """, (parent_config['spot_type'], parent['id']))
        print(f"  ✓ Set as parent with type '{parent_config['spot_type']}'")

    # Link children
    children_linked = 0
    for child_name in sheldon_config['children']:
        cur.execute("""
            SELECT id, name FROM fishing_spots
            WHERE name LIKE %s AND county = %s
        """, (f"%{child_name}%", parent_config['county']))

        children = cur.fetchall()
        for child in children:
            if not dry_run:
                cur.execute("""
                    UPDATE fishing_spots
                    SET parent_spot_id = %s, is_parent = FALSE
                    WHERE id = %s
                """, (parent['id'], child['id']))
                children_linked += 1
            print(f"  ✓ Linked: {child['name']} (ID {child['id']})")

    # Delete duplicates
    deleted = 0
    for dup in sheldon_config['delete']:
        cur.execute("""
            SELECT id, name FROM fishing_spots
            WHERE name = %s AND county = %s
        """, (dup['name'], parent_config['county']))

        dups = cur.fetchall()
        for d in dups:
            if not dry_run:
                cur.execute("DELETE FROM fishing_spots WHERE id = %s", (d['id'],))
                deleted += 1
            print(f"  🗑️  Deleted: {d['name']} (ID {d['id']}) - {dup['reason']}")

    print()
    return children_linked, deleted

def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("\n🔍 DRY-RUN MODE - No changes will be made\n")

    manifest = load_manifest()
    corrections = manifest['corrections']

    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)

    try:
        # Apply corrections
        name_fixes = apply_name_fixes(cur, corrections['name_fixes']['entries'], dry_run)
        deletions = apply_duplicate_deletions(cur, corrections['duplicate_deletions']['entries'], dry_run)
        parents, children = apply_numbered_pond_consolidations(cur, corrections['numbered_pond_groups']['entries'], dry_run)
        sheldon_children, sheldon_deleted = apply_sheldon_consolidation(cur, corrections['sheldon_lake_consolidation'], dry_run)

        if not dry_run:
            conn.commit()

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Name fixes applied: {name_fixes}")
        print(f"Duplicates deleted: {deletions}")
        print(f"Parent entries created: {parents}")
        print(f"Children linked: {children + sheldon_children}")
        print(f"Sheldon duplicates deleted: {sheldon_deleted}")
        print()

        if dry_run:
            print("✅ Dry-run complete - run without --dry-run to apply changes")
        else:
            print("✅ All corrections applied successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not dry_run:
            conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()
