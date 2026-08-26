import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.model_config import extract_and_parse_json
from schemas.pddl_blueprint import DomainBlueprint

sample_raw_llm_output = """
User Safety: safe

Here is the extracted PDDL blueprint JSON:
```json
{
  "domain_name": "test_logistics",
  "requirements": [":strips", ":typing"],
  "types": {"truck": "vehicle"},
  "predicates": ["(at ?t - truck ?l - location)"],
  "actions": []
}
```
"""

res = extract_and_parse_json(DomainBlueprint, sample_raw_llm_output)
print("Extracted Domain Name:", res.domain_name)
print("Extracted Types:", res.types)
print("SUCCESSFULLY PARSED NON-JSON PREAMBLE RESPONSE!")
