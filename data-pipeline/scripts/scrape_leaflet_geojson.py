"""
Generic GeoJSON Scraper for Leaflet/ESRI Maps

This script can extract GeoJSON data from web maps that use Leaflet.js,
regardless of how the data is loaded (JavaScript variable, external file, API endpoint).

Supports multiple data loading patterns:
1. Inline JavaScript variable (var data = {...})
2. External .js file with variable
3. External .json or .geojson file
4. API endpoints returning GeoJSON

Usage:
    python scrape_leaflet_geojson.py <url> [--output filename.json]
"""

import requests
import re
import json
import sys
import argparse
from urllib.parse import urljoin, urlparse


class LeafletGeoJSONScraper:
    """Generic scraper for Leaflet-based maps with GeoJSON data"""

    def __init__(self, url: str):
        self.url = url
        self.base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FishingDirectoryBot/1.0 (Educational fishing access directory; +https://github.com/yourusername/fishing-directory)'
        })

    def fetch_page(self) -> str:
        """Fetch the main page HTML"""
        response = self.session.get(self.url)
        response.raise_for_status()
        return response.text

    def find_geojson_sources(self, html: str) -> list:
        """
        Analyze page HTML to find potential GeoJSON data sources

        Returns list of potential sources in priority order
        """
        sources = []

        # Pattern 1: External .js files (like cfl.js)
        js_files = re.findall(r'<script[^>]+src=["\'](.*?\.js)["\']', html)
        for js_file in js_files:
            full_url = urljoin(self.url, js_file)
            # Skip common libraries
            if not any(lib in js_file.lower() for lib in ['jquery', 'leaflet', 'esri', 'bootstrap', 'foundation', 'analytics', 'google']):
                sources.append(('js_file', full_url))

        # Pattern 2: Inline <script> blocks with variable declarations
        inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for script in inline_scripts:
            # Look for variable assignments with GeoJSON-like structure
            if re.search(r'var\s+\w+\s*=\s*{["\']type["\']\s*:\s*["\']FeatureCollection["\']', script):
                sources.append(('inline_script', script))

        # Pattern 3: .json or .geojson files
        json_files = re.findall(r'["\'](.*?\.(?:json|geojson))["\']', html)
        for json_file in json_files:
            full_url = urljoin(self.url, json_file)
            sources.append(('json_file', full_url))

        # Pattern 4: API endpoints (common patterns)
        api_patterns = [
            r'["\'](.*?/api/.*?)["\']',
            r'["\'](.*?\.php\?.*?)["\']',
            r'["\'](.*?/arcgis/rest/services/.*?)["\']'
        ]
        for pattern in api_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                full_url = urljoin(self.url, match)
                sources.append(('api', full_url))

        return sources

    def extract_geojson_from_js(self, js_content: str) -> dict:
        """
        Extract GeoJSON from JavaScript content

        Handles patterns like:
        - var data = {...}
        - const data = {...}
        - window.data = {...}
        """
        # Find where FeatureCollection starts
        fc_match = re.search(r'(?:var|const|let)\s+(\w+)\s*=\s*({["\']type["\']\s*:\s*["\']FeatureCollection["\'])', js_content, re.DOTALL)

        if not fc_match:
            return None

        var_name = fc_match.group(1)
        start_pos = fc_match.start(2)

        # Find the matching closing brace using a simple bracket counter
        json_str = self.extract_balanced_braces(js_content[start_pos:])

        if json_str:
            # Clean up JavaScript-specific syntax
            json_str = self.clean_js_to_json(json_str)

            try:
                data = json.loads(json_str)
                if self.is_valid_geojson(data):
                    print(f"[OK] Found GeoJSON in variable '{var_name}'")
                    return data
            except json.JSONDecodeError as e:
                print(f"[WARN] Found potential GeoJSON but failed to parse: {e}")

        return None

    def extract_balanced_braces(self, text: str) -> str:
        """Extract text from opening { to matching closing }"""
        depth = 0
        start = -1

        for i, char in enumerate(text):
            if char == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start != -1:
                    return text[start:i+1]

        return None

    def clean_js_to_json(self, js_str: str) -> str:
        """Convert JavaScript object notation to valid JSON"""
        import html

        # Decode HTML entities (like &amp;#39; -> ')
        js_str = html.unescape(js_str)

        # Remove trailing commas
        js_str = re.sub(r',\s*}', '}', js_str)
        js_str = re.sub(r',\s*]', ']', js_str)

        # Remove comments
        js_str = re.sub(r'//.*?\n', '\n', js_str)
        js_str = re.sub(r'/\*.*?\*/', '', js_str, flags=re.DOTALL)

        # Handle single-quoted strings (convert to double quotes)
        # This is tricky - simple approach for basic cases
        # js_str = js_str.replace("'", '"')  # Too aggressive, can break

        return js_str

    def is_valid_geojson(self, data: dict) -> bool:
        """Check if data looks like valid GeoJSON"""
        if not isinstance(data, dict):
            return False

        # Must have type
        if data.get('type') not in ['FeatureCollection', 'Feature', 'GeometryCollection']:
            return False

        # FeatureCollection must have features array
        if data.get('type') == 'FeatureCollection':
            if not isinstance(data.get('features'), list):
                return False

        return True

    def try_fetch_geojson(self, source_type: str, source: str) -> dict:
        """Attempt to fetch and parse GeoJSON from a source"""
        try:
            if source_type == 'inline_script':
                # Source is the script content itself
                return self.extract_geojson_from_js(source)

            elif source_type in ['js_file', 'json_file', 'api']:
                # Source is a URL
                print(f"Trying {source_type}: {source}")
                response = self.session.get(source, timeout=10)
                response.raise_for_status()

                content = response.text

                if source_type == 'js_file':
                    return self.extract_geojson_from_js(content)
                else:
                    # Try direct JSON parsing
                    data = json.loads(content)
                    if self.is_valid_geojson(data):
                        print(f"[OK] Found valid GeoJSON")
                        return data

        except Exception as e:
            print(f"[FAIL] {e}")

        return None

    def scrape(self) -> dict:
        """
        Main scraping method - tries all strategies to find GeoJSON

        Returns GeoJSON dict or None
        """
        print(f"\n{'='*60}")
        print(f"Scraping GeoJSON from: {self.url}")
        print(f"{'='*60}\n")

        # Step 1: Fetch the page
        print("[1/3] Fetching page...")
        html = self.fetch_page()
        print("[OK] Page fetched\n")

        # Step 2: Find potential GeoJSON sources
        print("[2/3] Analyzing page for GeoJSON sources...")
        sources = self.find_geojson_sources(html)
        print(f"[OK] Found {len(sources)} potential sources\n")

        # Step 3: Try each source until we find valid GeoJSON
        print("[3/3] Attempting to extract GeoJSON...")
        for source_type, source in sources:
            geojson = self.try_fetch_geojson(source_type, source)
            if geojson:
                return geojson

        print("\n[FAIL] No valid GeoJSON found")
        return None

    def save_geojson(self, data: dict, output_path: str):
        """Save GeoJSON to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"\n[OK] Saved GeoJSON to: {output_path}")

        # Print summary
        if data.get('type') == 'FeatureCollection':
            print(f"  Features: {len(data.get('features', []))}")

            # Show sample feature properties
            if data.get('features'):
                first_feature = data['features'][0]
                print(f"  Sample properties: {list(first_feature.get('properties', {}).keys())}")


def main():
    parser = argparse.ArgumentParser(
        description='Scrape GeoJSON data from Leaflet/ESRI maps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape and save to auto-generated filename
  python scrape_leaflet_geojson.py https://example.com/map.html

  # Scrape and save to specific file
  python scrape_leaflet_geojson.py https://example.com/map.html --output lakes.json

  # Texas Community Fishing Lakes
  python scrape_leaflet_geojson.py https://tpwd.texas.gov/fishboat/fish/recreational/lakes/cfl.phtml --output community_lakes.json
        """
    )

    parser.add_argument('url', help='URL of the map page')
    parser.add_argument('--output', '-o', help='Output JSON file path')

    args = parser.parse_args()

    # Create scraper
    scraper = LeafletGeoJSONScraper(args.url)

    # Scrape
    geojson = scraper.scrape()

    if geojson:
        # Determine output filename
        if args.output:
            output_path = args.output
        else:
            # Auto-generate from URL
            url_path = urlparse(args.url).path
            filename = url_path.split('/')[-1].replace('.phtml', '').replace('.html', '')
            if not filename:
                filename = 'data'
            output_path = f"../../raw-data/{filename}_geojson.json"

        scraper.save_geojson(geojson, output_path)
        return 0
    else:
        print("\n[ERROR] Failed to extract GeoJSON from page")
        print("\nTroubleshooting:")
        print("1. Check if the map loads data dynamically via AJAX")
        print("2. Try inspecting network requests in browser DevTools")
        print("3. Look for API endpoints or data files in Network tab")
        return 1


if __name__ == "__main__":
    sys.exit(main())
