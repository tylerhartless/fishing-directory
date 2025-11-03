"""
Analyze OSM coverage for US South states to help decide next state to implement

Requires: PostGIS database with US South OSM data imported
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# States in US South extract
SOUTH_STATES = [
    'Texas', 'Louisiana', 'Arkansas', 'Oklahoma',
    'Mississippi', 'Alabama', 'Tennessee', 'Kentucky',
    'Florida', 'Georgia', 'South Carolina', 'North Carolina',
    'Virginia', 'West Virginia'
]

def analyze_coverage():
    """Analyze OSM water body coverage by state"""

    print("Connecting to OSM database...")
    conn = psycopg2.connect(
        dbname='fishing_osm',
        user='postgres',
        host='localhost'
    )

    print("Analyzing OSM coverage by state...\n")
    print("=" * 80)

    results = {}

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Analyze water bodies
        print("\n1. Named Water Bodies by State\n")
        print(f"{'State':<20} {'Lakes':<10} {'Ponds':<10} {'Reservoirs':<10} {'Total':<10}")
        print("-" * 80)

        query = """
            SELECT
                b.tags->'name' as state,
                COUNT(*) FILTER (WHERE w.water = 'lake') as lakes,
                COUNT(*) FILTER (WHERE w.water = 'pond') as ponds,
                COUNT(*) FILTER (WHERE w.water = 'reservoir') as reservoirs,
                COUNT(*) FILTER (WHERE w.waterway = 'river') as rivers,
                COUNT(*) as total
            FROM planet_osm_polygon w
            JOIN planet_osm_polygon b ON
                ST_Contains(b.way, ST_Centroid(w.way))
            WHERE (w.natural = 'water' OR w.waterway IS NOT NULL)
              AND w.name IS NOT NULL
              AND b.boundary = 'administrative'
              AND b.admin_level = '4'
            GROUP BY b.tags->'name'
            ORDER BY total DESC;
        """

        cur.execute(query)
        rows = cur.fetchall()

        for row in rows:
            state = row['state']
            if state in SOUTH_STATES:
                results[state] = {
                    'water_bodies': {
                        'lakes': row['lakes'],
                        'ponds': row['ponds'],
                        'reservoirs': row['reservoirs'],
                        'rivers': row['rivers'],
                        'total': row['total']
                    }
                }
                print(f"{state:<20} {row['lakes']:<10} {row['ponds']:<10} "
                      f"{row['reservoirs']:<10} {row['total']:<10}")

        # Analyze parks
        print("\n2. Named Parks by State\n")
        print(f"{'State':<20} {'Parks':<10} {'Nature Reserves':<15} {'Total':<10}")
        print("-" * 80)

        query = """
            SELECT
                b.tags->'name' as state,
                COUNT(*) FILTER (WHERE p.leisure = 'park') as parks,
                COUNT(*) FILTER (WHERE p.leisure = 'nature_reserve') as nature_reserves,
                COUNT(*) as total
            FROM planet_osm_polygon p
            JOIN planet_osm_polygon b ON
                ST_Contains(b.way, ST_Centroid(p.way))
            WHERE p.leisure IN ('park', 'nature_reserve')
              AND p.name IS NOT NULL
              AND b.boundary = 'administrative'
              AND b.admin_level = '4'
            GROUP BY b.tags->'name'
            ORDER BY total DESC;
        """

        cur.execute(query)
        rows = cur.fetchall()

        for row in rows:
            state = row['state']
            if state in SOUTH_STATES and state in results:
                results[state]['parks'] = {
                    'parks': row['parks'],
                    'nature_reserves': row['nature_reserves'],
                    'total': row['total']
                }
                print(f"{state:<20} {row['parks']:<10} {row['nature_reserves']:<15} {row['total']:<10}")

        # Analyze amenities
        print("\n3. Fishing-Related Amenities by State\n")
        print(f"{'State':<20} {'Boat Ramps':<12} {'Fishing Piers':<15} {'Marinas':<10}")
        print("-" * 80)

        query = """
            SELECT
                b.tags->'name' as state,
                COUNT(*) FILTER (WHERE a.leisure = 'slipway') as boat_ramps,
                COUNT(*) FILTER (WHERE a.leisure = 'fishing') as fishing_piers,
                COUNT(*) FILTER (WHERE a.leisure = 'marina') as marinas
            FROM planet_osm_point a
            JOIN planet_osm_polygon b ON
                ST_Contains(b.way, a.way)
            WHERE a.leisure IN ('slipway', 'fishing', 'marina')
              AND b.boundary = 'administrative'
              AND b.admin_level = '4'
            GROUP BY b.tags->'name'
            ORDER BY boat_ramps + fishing_piers + marinas DESC;
        """

        cur.execute(query)
        rows = cur.fetchall()

        for row in rows:
            state = row['state']
            if state in SOUTH_STATES and state in results:
                results[state]['amenities'] = {
                    'boat_ramps': row['boat_ramps'],
                    'fishing_piers': row['fishing_piers'],
                    'marinas': row['marinas']
                }
                print(f"{state:<20} {row['boat_ramps']:<12} {row['fishing_piers']:<15} {row['marinas']:<10}")

    conn.close()

    # Calculate quality scores
    print("\n4. OSM Quality Score Ranking\n")
    print(f"{'Rank':<6} {'State':<20} {'Score':<10} {'Quality':<15}")
    print("-" * 80)

    scored_states = []
    for state, data in results.items():
        # Calculate score based on data completeness
        score = 0

        # Water bodies (40 points max)
        wb = data.get('water_bodies', {})
        score += min(wb.get('total', 0) / 100, 40)

        # Parks (30 points max)
        parks = data.get('parks', {})
        score += min(parks.get('total', 0) / 50, 30)

        # Amenities (30 points max)
        amenities = data.get('amenities', {})
        amenity_count = (amenities.get('boat_ramps', 0) +
                        amenities.get('fishing_piers', 0) +
                        amenities.get('marinas', 0))
        score += min(amenity_count / 20, 30)

        # Quality rating
        if score >= 80:
            quality = "Excellent"
        elif score >= 60:
            quality = "Good"
        elif score >= 40:
            quality = "Fair"
        else:
            quality = "Poor"

        scored_states.append({
            'state': state,
            'score': round(score, 1),
            'quality': quality,
            'data': data
        })

    # Sort by score
    scored_states.sort(key=lambda x: x['score'], reverse=True)

    for rank, item in enumerate(scored_states, 1):
        print(f"{rank:<6} {item['state']:<20} {item['score']:<10} {item['quality']:<15}")

    # Save detailed results
    output = {
        'analyzed_at': datetime.now().isoformat(),
        'database': 'US South OSM Extract',
        'states_analyzed': len(results),
        'rankings': scored_states
    }

    with open('staged/reports/osm_coverage_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 80)
    print(f"\nDetailed results saved to: staged/reports/osm_coverage_analysis.json")
    print("\nRecommendation:")
    print(f"  Best OSM coverage: {scored_states[0]['state']} (score: {scored_states[0]['score']})")
    print(f"  2nd best: {scored_states[1]['state']} (score: {scored_states[1]['score']})")
    print(f"  3rd best: {scored_states[2]['state']} (score: {scored_states[2]['score']})")

    print("\nConsider these factors when choosing next state:")
    print("  1. OSM coverage quality (above)")
    print("  2. Availability of state fishing authority data")
    print("  3. Population/user demand")
    print("  4. Geographic diversity (coastal vs inland)")

if __name__ == "__main__":
    try:
        analyze_coverage()
    except psycopg2.OperationalError as e:
        print(f"\n[ERROR] Cannot connect to fishing_osm database")
        print(f"Make sure PostgreSQL is running and OSM data is imported")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
