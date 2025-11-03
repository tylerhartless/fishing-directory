# Manual CSV Import Workflow

## Overview
This workflow is for importing manually extracted fishing spot data from PDFs into the database with proper deduplication and species tracking.

## Import Script: `import_austin_csv.py`

### Features
1. **Fuzzy Name Matching** (85% threshold)
   - Matches facility names against existing database entries
   - Normalizes names (removes suffixes like "Park", "Lake", etc.)
   - Checks both spot name and water body name

2. **Location Verification** (NEW!)
   - Geocodes CSV addresses using Nominatim API
   - Calculates distance between CSV location and database entry
   - Rejects matches if locations are >5km apart
   - **Prevents false matches** like "Barkley Meadows" vs "Jersey Meadows"

3. **Address Enrichment**
   - Updates database entries that lack addresses
   - Preserves existing addresses

4. **Species Tracking**
   - Maps common fish names to database enum values
   - Adds species to `spot_votes` table
   - Increments vote count for duplicate entries

### Species Mapping
The script automatically maps fish names to database categories:
- Largemouth Bass, Guadalupe Bass, Smallmouth Bass → `largemouth_bass`
- Striped Bass, Hybrid Striped Bass → `striped_bass`
- White Bass → `white_bass`
- Channel Catfish, Blue Catfish → `catfish`
- Bluegill, Redbreast Sunfish → `sunfish`
- White Crappie → `crappie`
- Common Carp, Buffalo → `carp`
- etc.

### Usage

1. **Prepare CSV** with columns:
   - `Facility Name` (required)
   - `Species Available` (comma-separated list)
   - `Facility Address` (optional, but recommended for verification)

2. **Place CSV** in `raw-data/` folder

3. **Update script** to point to your CSV:
   ```python
   csv_path = '../../raw-data/YourCity PDF - Sheet1.csv'
   ```

4. **Run script**:
   ```bash
   cd data-pipeline/scripts
   python import_austin_csv.py
   ```

5. **Review output** for:
   - Matched entries (verified by location)
   - Updated addresses
   - Species added
   - Entries not matched (need manual addition)

### Important Notes

- **Rate Limiting**: Script sleeps 1 second between geocoding requests (Nominatim requirement)
- **False Match Prevention**: Location verification ensures matches are actually the same place
- **Manual Review**: Unmatched entries need to be added as new spots (see output list)

### Example Output
```
Processing: Lake Georgetown
  Geocoding CSV address: 500 Lake Overlook Drive, Georgetown...
    Got coords: 30.6521, -97.7032
  Species: largemouth_bass, sunfish
  [MATCH] Found: Lake Georgetown - Williamson County Access (score: 1.00)
    [OK] Distance verification: 0.52km apart
    DB ID: 2137
    [OK] Updated address: 500 Lake Overlook Drive, Georgetown
    [OK] Added 2 species
```

## Fixing Errors

If false matches occur:

1. **Check the match** - review similarity score and distance
2. **Use fix scripts** to remove incorrect data:
   ```python
   # Example: remove incorrect species votes
   DELETE FROM spot_votes WHERE fishing_spot_id = XXX AND vote_count = 1
   ```
3. **Adjust thresholds** if needed:
   - Increase similarity threshold (currently 0.85)
   - Decrease distance threshold (currently 5km)

## Next Steps

After import:
1. Review unmatched entries
2. Add new spots for entries that don't exist in database
3. Manually verify any questionable matches
4. Run database summary to see updated counts
