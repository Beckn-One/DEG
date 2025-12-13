import json
import sys
import os
import requests
import yaml
from jsonschema import validate, ValidationError, RefResolver

# Load schemas from URL
BECKN_YAML_URL = "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/api/beckn.yaml"
ATTRIBUTES_YAML_URL = "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml"

def load_schema_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return yaml.safe_load(response.text)

def get_schema_store():
    print("Loading schemas...")
    beckn_schema = load_schema_from_url(BECKN_YAML_URL)
    attributes_schema = load_schema_from_url(ATTRIBUTES_YAML_URL)
    
    schema_store = {
        BECKN_YAML_URL: beckn_schema,
        ATTRIBUTES_YAML_URL: attributes_schema
    }
    return schema_store, attributes_schema

def validate_payload(payload, schema_store, attributes_schema):
    # Determine type to validate against
    # We primarily care about Order objects for now as per user context
    
    # Helper to find Order object recursively
    errors = []
    
    def find_and_validate_order(data, path=""):
        if isinstance(data, dict):
            if data.get("@type") == "beckn:Order":
                print(f"  Validating Order at {path or 'root'}...")
                # Construct a resolver that knows about our schemas
                resolver = RefResolver(base_uri=ATTRIBUTES_YAML_URL, referrer=attributes_schema, store=schema_store)
                order_schema = attributes_schema["components"]["schemas"]["Order"]
                try:
                    validate(instance=data, schema=order_schema, resolver=resolver)
                    print(f"  Order at {path or 'root'} is VALID.")
                except ValidationError as e:
                    print(f"  Order at {path or 'root'} is INVALID: {e.message}")
                    print(f"  Path: {e.json_path}")
                    errors.append(f"{path}: {e.message}")
            
            # Recursively check children
            for key, value in data.items():
                find_and_validate_order(value, f"{path}/{key}" if path else key)
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                find_and_validate_order(item, f"{path}[{idx}]")

    find_and_validate_order(payload)
    return errors

def process_file(filepath, schema_store, attributes_schema):
    print(f"Processing {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        is_postman = "info" in data and "_postman_id" in data.get("info", {})
        
        if is_postman:
            print("  Identified as Postman collection.")
            def traverse_postman_items(items):
                for item in items:
                    if "item" in item:
                        traverse_postman_items(item["item"])
                    if "request" in item and "body" in item["request"]:
                        body = item["request"]["body"]
                        if body.get("mode") == "raw":
                            raw_content = body["raw"]
                            try:
                                json_body = json.loads(raw_content)
                                validate_payload(json_body, schema_store, attributes_schema)
                            except json.JSONDecodeError:
                                pass
            traverse_postman_items(data.get("item", []))
        else:
            validate_payload(data, schema_store, attributes_schema)
            
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")

if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print("Usage: python3 validate_schema.py <file1> <file2> ...")
        sys.exit(1)
        
    schema_store, attributes_schema = get_schema_store()
    
    for file in files:
        process_file(file, schema_store, attributes_schema)
