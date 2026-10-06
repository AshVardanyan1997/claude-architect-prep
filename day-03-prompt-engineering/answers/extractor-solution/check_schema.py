"""Free check: is the tool's input_schema valid JSON Schema (draft 2020-12)?

The API returns "400 ... JSON schema is invalid" without saying where. This
script prints the exact spot. Run it after every schema.py edit:

    python check_schema.py
"""

import jsonschema

from schema import EXTRACT_TOOL

validator = jsonschema.Draft202012Validator(jsonschema.Draft202012Validator.META_SCHEMA)
errors = sorted(validator.iter_errors(EXTRACT_TOOL["input_schema"]), key=lambda e: list(map(str, e.absolute_path)))
seen = set()
for e in errors:
    where = "input_schema" + "".join(f"[{p!r}]" for p in e.absolute_path)
    if where in seen:
        continue
    seen.add(where)
    hint = ("  <- a Python set: you wrote a comma where JSON needs a colon, e.g. {\"type\", \"null\"} "
            "instead of {\"type\": \"null\"}") if isinstance(e.instance, set) else ""
    print(f"INVALID  {where}{hint}\n         {e.message}")
print("schema is valid draft 2020-12" if not errors else
      "\nCommon causes: Python None where JSON needs the string \"null\" (write {\"type\": \"null\"}), "
      "or \"required\": True on a property (required is a list on the parent object).")
