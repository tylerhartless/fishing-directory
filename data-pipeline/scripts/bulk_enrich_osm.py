"""
Bulk OSM Enrichment for Existing Database Records

This script enriches ALL existing fishing spots with OpenStreetMap data.
Useful for backfilling amenities and improving data quality.

Usage:
    python scripts/bulk_enrich_osm.py [--spot-type TYPE] [--county COUNTY] [--limit N] [--resume]
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_utils import get_connection
from scripts.enrich_from_osm import OSMEnricher


class BulkEnricher:
    """Bulk enrichment of database spots with OSM data"""

    def __init__(self, resume_file='osm_enrichment_progress.json'):
        self.enricher = OSMEnricher()
        self.resume_file = resume_file
        self.processed_ids = set()
        self.stats = {
            'total': 0,
            'enriched': 0,
            'water_bodies_found': 0,
            'facilities_found': 0,
            'amenities_added': 0,
            'errors': 0,
            'skipped': 0
        }

        # Load resume data if exists
        if os.path.exists(resume_file):
            with open(resume_file, 'r') as f:
                resume_data = json.load(f)
                self.processed_ids = set(resume_data.get('processed_ids', []))
                self.stats = resume_data.get('stats', self.stats)
                print(f"[RESUME] Loaded progress: {len(self.processed_ids)} spots already processed")

    def save_progress(self):
        """Save progress to file for resume capability"""
        with open(self.resume_file, 'w') as f:
            json.dump({
                'processed_ids': list(self.processed_ids),
                'stats': self.stats,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)

    def enrich_spot(self, spot: Dict, conn) -> bool:
        """
        Enrich a single spot and update database

        Returns True if updated, False if skipped/error
        """
        # Skip if already processed (resume)
        if spot['id'] in self.processed_ids:
            self.stats['skipped'] += 1
            return False

        try:
            # Query OSM
            osm_result = self.enricher.enrich_spot(spot)

            if osm_result['status'] != 'success':
                self.stats['errors'] += 1
                self.processed_ids.add(spot['id'])
                return False

            # Prepare update
            update_needed = False
            update_data = {}

            # Update water body name if OSM has a better one
            if osm_result.get('suggested_water_body'):
                current_wb = spot['water_body_name']
                suggested_wb = osm_result['suggested_water_body']

                # Only update if significantly different
                if suggested_wb.lower() != current_wb.lower():
                    update_data['water_body_name'] = suggested_wb
                    update_needed = True
                    self.stats['water_bodies_found'] += 1

            # Update amenities
            osm_amenities = osm_result.get('amenities', {})
            current_amenities = json.loads(spot['amenities']) if spot['amenities'] else {}

            # Merge amenities (OSM adds new ones, doesn't remove existing)
            merged_amenities = {**current_amenities}
            amenities_changed = False

            for amenity, has_it in osm_amenities.items():
                if has_it and not merged_amenities.get(amenity):
                    merged_amenities[amenity] = True
                    amenities_changed = True
                    self.stats['amenities_added'] += 1

            if amenities_changed:
                update_data['amenities'] = json.dumps(merged_amenities)
                update_needed = True

            # Update description with facility info
            if osm_result.get('facility_name'):
                facility_name = osm_result['facility_name']
                current_desc = spot['description']

                # Only add if facility name not already in description
                if facility_name.lower() not in current_desc.lower():
                    facility_info = f"Located at {facility_name}. "
                    if osm_result.get('facility_website'):
                        facility_info += f"Visit {osm_result['facility_website']} for more details. "

                    update_data['description'] = facility_info + current_desc
                    update_needed = True
                    self.stats['facilities_found'] += 1

            # Execute update if needed
            if update_needed:
                cursor = conn.cursor()
                set_clause = ', '.join([f"{k} = %s" for k in update_data.keys()])
                values = list(update_data.values())
                values.append(spot['id'])

                query = f"UPDATE fishing_spots SET {set_clause} WHERE id = %s"
                cursor.execute(query, values)
                conn.commit()
                cursor.close()

                self.stats['enriched'] += 1

            self.processed_ids.add(spot['id'])
            return update_needed

        except Exception as e:
            print(f"      [ERROR] Spot {spot['id']}: {e}")
            self.stats['errors'] += 1
            self.processed_ids.add(spot['id'])
            return False

    def run(self, spot_type=None, county=None, limit=None):
        """
        Run bulk enrichment

        Args:
            spot_type: Filter by spot type (optional)
            county: Filter by county (optional)
            limit: Max spots to process (optional, for testing)
        """
        print("="*60)
        print("Bulk OSM Enrichment")
        print("="*60)
        print()

        # Build query
        conn = get_connection(silent=True)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, name, water_body_name, county, latitude, longitude, amenities, description FROM fishing_spots WHERE 1=1"
        params = []

        if spot_type:
            query += " AND spot_type = %s"
            params.append(spot_type)

        if county:
            query += " AND county = %s"
            params.append(county)

        query += " ORDER BY id"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cursor.execute(query, params)
        spots = cursor.fetchall()
        cursor.close()

        self.stats['total'] = len(spots)

        print(f"Found {len(spots)} spots to enrich")
        if len(self.processed_ids) > 0:
            print(f"Resuming: {len(self.processed_ids)} already processed")
        print()

        # Process spots
        start_time = time.time()
        last_save = time.time()

        for i, spot in enumerate(spots, 1):
            # Progress indicator
            if i % 10 == 0 or i == len(spots):
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                remaining = (len(spots) - i) / rate if rate > 0 else 0

                print(f"[{i}/{len(spots)}] {spot['name'][:40]:40} | "
                      f"Enriched: {self.stats['enriched']} | "
                      f"ETA: {remaining/60:.1f}min")

            # Enrich spot
            self.enrich_spot(spot, conn)

            # Rate limiting
            time.sleep(0.6)

            # Save progress every 50 spots
            if time.time() - last_save > 30:  # Every 30 seconds
                self.save_progress()
                last_save = time.time()

        conn.close()

        # Final save
        self.save_progress()

        # Summary
        elapsed = time.time() - start_time
        print()
        print("="*60)
        print("Enrichment Complete")
        print("="*60)
        print(f"Total spots processed: {self.stats['total']}")
        print(f"Successfully enriched: {self.stats['enriched']}")
        print(f"Water bodies updated: {self.stats['water_bodies_found']}")
        print(f"Facilities found: {self.stats['facilities_found']}")
        print(f"Amenities added: {self.stats['amenities_added']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Skipped (already processed): {self.stats['skipped']}")
        print(f"Time elapsed: {elapsed/60:.1f} minutes")
        print("="*60)

        # Clean up resume file if complete
        if len(self.processed_ids) == len(spots) and os.path.exists(self.resume_file):
            os.remove(self.resume_file)
            print("[OK] Resume file deleted (enrichment complete)")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Bulk enrich fishing spots with OSM data')
    parser.add_argument('--spot-type', help='Only enrich specific spot type')
    parser.add_argument('--county', help='Only enrich specific county')
    parser.add_argument('--limit', type=int, help='Limit number of spots (for testing)')
    parser.add_argument('--resume', action='store_true', help='Resume from previous run')
    args = parser.parse_args()

    enricher = BulkEnricher()
    enricher.run(
        spot_type=args.spot_type,
        county=args.county,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
