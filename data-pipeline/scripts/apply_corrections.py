"""
Apply manual data corrections from name_corrections.json

This script reads the corrections file and applies any pending corrections
to the database.

Usage:
    python scripts/apply_corrections.py [--dry-run]
"""

import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection


def load_corrections(file_path='../data_corrections/name_corrections.json'):
    """Load corrections from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['corrections']


def apply_correction(correction, dry_run=False):
    """Apply a single correction to the database"""
    conn = get_connection(silent=True)
    cursor = conn.cursor(dictionary=True)

    # Find the record by source_id and data_source
    query = """
        SELECT id, name, water_body_name, county
        FROM fishing_spots
        WHERE source_id = %s AND data_source = %s
    """
    cursor.execute(query, (correction['source_id'], correction['data_source']))
    result = cursor.fetchone()

    if not result:
        print(f"[WARN] Record not found: {correction['original_name']} (source_id: {correction['source_id']})")
        cursor.close()
        conn.close()
        return False

    print(f"[FOUND] {result['name']} in {result['county']} County")
    print(f"        Current: name='{result['name']}', water_body='{result['water_body_name']}'")
    print(f"        Will update to: name='{correction['corrected_name']}', water_body='{correction['corrected_water_body']}'")

    if dry_run:
        print(f"        [DRY RUN] Skipping actual update")
        cursor.close()
        conn.close()
        return True

    # Apply the correction
    update_query = """
        UPDATE fishing_spots
        SET name = %s, water_body_name = %s
        WHERE id = %s
    """
    cursor.execute(update_query, (
        correction['corrected_name'],
        correction['corrected_water_body'],
        result['id']
    ))
    conn.commit()

    print(f"        [OK] Updated successfully")

    cursor.close()
    conn.close()
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Apply manual data corrections')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    args = parser.parse_args()

    print("="*60)
    print("Data Corrections Utility")
    if args.dry_run:
        print("[DRY RUN MODE - No changes will be made]")
    print("="*60)
    print()

    # Load corrections
    corrections = load_corrections()

    # Filter to only pending corrections (not yet applied)
    pending = [c for c in corrections if not c.get('applied', False)]

    if not pending:
        print("No pending corrections found.")
        return

    print(f"Found {len(pending)} pending corrections:")
    print()

    for i, correction in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] Processing: {correction['original_name']}")
        print(f"        Reason: {correction['reason']}")
        apply_correction(correction, dry_run=args.dry_run)
        print()

    if not args.dry_run:
        print("="*60)
        print(f"Applied {len(pending)} corrections successfully")
        print("="*60)
        print()
        print("To mark these as applied, update name_corrections.json manually")
    else:
        print("="*60)
        print("[DRY RUN] Run without --dry-run to apply changes")
        print("="*60)


if __name__ == "__main__":
    main()
