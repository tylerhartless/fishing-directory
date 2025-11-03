import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enrich_raca_amenities import reverse_geocode

result = reverse_geocode(29.847926904693182, -97.85898829370356)
print(f"Result: {result}")
