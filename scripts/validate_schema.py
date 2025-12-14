import json
import re
import copy
import requests
import yaml
from jsonschema import validate, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# Note: All schemas (core and non-core) are loaded on-demand from @context URLs in the JSON
# No preloading needed - schemas are inferred from @context and cached for reuse

def load_schema_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return yaml.safe_load(response.text)

def extract_schema_info_from_url(url):
    """
    Extract schema name and version from attributes.yaml URL.
    
    Example: 
        https://.../EvChargingOffer/v1/attributes.yaml -> (EvChargingOffer, v1)
    """
    match = re.search(r'/schema/([^/]+)/([^/]+)/attributes\.yaml', url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def extract_branch_from_context_url(context_url):
    """
    Extract branch name from @context URL.
    
    Example:
        .../refs/heads/draft/schema/... -> draft
        .../refs/heads/p2p_trading/schema/... -> p2p_trading
        .../refs/heads/main/schema/... -> main
    """
    match = re.search(r'/refs/heads/([^/]+)/schema/', context_url)
    if match:
        return match.group(1)
    return None

def get_attributes_url_from_context_url(context_url):
    """
    Convert context.jsonld URL to corresponding attributes.yaml URL.
    Infers branch from the context URL.
    
    Example:
        .../draft/schema/EvChargingOffer/v1/context.jsonld -> .../draft/schema/EvChargingOffer/v1/attributes.yaml
        .../p2p_trading/schema/EnergyResource/v0.2/context.jsonld -> .../p2p_trading/schema/EnergyResource/v0.2/attributes.yaml
        .../draft/schema/core/v2/context.jsonld -> .../draft/schema/core/v2/attributes.yaml
    """
    return context_url.replace('/context.jsonld', '/attributes.yaml')

def is_core_context_url(context_url):
    """
    Check if @context URL points to core schema.
    
    Example:
        .../schema/core/v2/context.jsonld -> True
        .../schema/EvChargingOffer/v1/context.jsonld -> False
    """
    return '/schema/core/' in context_url

def load_core_schema_for_context_url(context_url, registry_list):
    """
    Load core attributes schema for a given @context URL.
    
    Args:
        context_url: The @context URL from the JSON (e.g., .../core/v2/context.jsonld)
        registry_list: List containing referencing Registry (mutated in place)
    
    Returns:
        schema_data or None if failed
    """
    registry = registry_list[0]
    # Convert context URL to attributes URL
    attributes_url = get_attributes_url_from_context_url(context_url)
    
    # Check if already loaded in registry
    try:
        resource = registry.get(attributes_url)
        if resource is not None:
            return resource.contents
    except (KeyError, AttributeError):
        pass
    
    # Try to load the schema from the inferred branch
    try:
        schema_data = load_schema_from_url(attributes_url)
        registry_list[0] = registry.with_resource(attributes_url, Resource.from_contents(schema_data, DRAFT202012))
        print(f"  Loaded core attributes schema (branch: {extract_branch_from_context_url(context_url)})")
        return schema_data
    except Exception:
        # Try alternative branches (main, draft, p2p_trading)
        branch = extract_branch_from_context_url(context_url)
        alternative_branches = ["main", "draft", "p2p_trading"]
        for alt_branch in alternative_branches:
            if alt_branch == branch:
                continue
            try:
                alt_url = attributes_url.replace(f"/refs/heads/{branch}/", f"/refs/heads/{alt_branch}/")
                schema_data = load_schema_from_url(alt_url)
                registry = registry_list[0]
                registry_list[0] = registry.with_resource(alt_url, Resource.from_contents(schema_data, DRAFT202012))
                # Also map the original context URL's attributes URL to this schema
                registry = registry_list[0]
                registry_list[0] = registry.with_resource(attributes_url, Resource.from_contents(schema_data, DRAFT202012))
                print(f"  Loaded core attributes schema (branch: {alt_branch}, mapped from {branch})")
                return schema_data
            except:
                continue
        
        print(f"  Warning: Failed to load core attributes schema from any branch")
        return None

def load_schema_for_context_url(context_url, attribute_schemas_map, registry_list=None):
    """
    Dynamically load schema for a given @context URL by inferring branch from the URL.
    
    Args:
        context_url: The @context URL from the JSON
        attribute_schemas_map: Existing map to add to (may be modified)
        registry_list: List containing referencing Registry (mutated in place, optional)
    
    Returns:
        tuple: (schema_name, schema_data, schema_url) or None if failed
    """
    # Check if we already have this context URL mapped
    if context_url in attribute_schemas_map:
        return attribute_schemas_map[context_url]
    
    # Extract branch from context URL
    branch = extract_branch_from_context_url(context_url)
    if not branch:
        return None
    
    # Convert context URL to attributes URL
    attributes_url = get_attributes_url_from_context_url(context_url)
    
    # Extract schema name and version
    schema_name, version = extract_schema_info_from_url(attributes_url)
    if not schema_name:
        return None
    
    # Try to load the schema from the inferred branch
    try:
        schema_data = load_schema_from_url(attributes_url)
        attribute_schemas_map[context_url] = (schema_name, schema_data, attributes_url)
        if registry_list is not None:
            registry = registry_list[0]
            registry_list[0] = registry.with_resource(attributes_url, Resource.from_contents(schema_data, DRAFT202012))
        print(f"  Loaded: {schema_name}/{version} (branch: {branch})")
        return (schema_name, schema_data, attributes_url)
    except Exception:
        # Try alternative branches (main, draft, p2p_trading)
        alternative_branches = ["main", "draft", "p2p_trading"]
        for alt_branch in alternative_branches:
            if alt_branch == branch:
                continue
            try:
                alt_url = attributes_url.replace(f"/refs/heads/{branch}/", f"/refs/heads/{alt_branch}/")
                schema_data = load_schema_from_url(alt_url)
                # Map the original context URL to the schema loaded from alternative branch
                attribute_schemas_map[context_url] = (schema_name, schema_data, alt_url)
                if registry_list is not None:
                    registry = registry_list[0]
                    registry_list[0] = registry.with_resource(alt_url, Resource.from_contents(schema_data, DRAFT202012))
                print(f"  Loaded: {schema_name}/{version} (branch: {alt_branch}, mapped from {branch})")
                return (schema_name, schema_data, alt_url)
            except:
                continue
        
        print(f"  Warning: Failed to load {schema_name}/{version} from any branch")
        return None


def get_schema_store():
    """
    Get schema store. All schemas (core and non-core) are loaded on-demand from @context URLs and cached.
    """
    # Initialize empty caches - all schemas loaded on-demand
    # Use a list to hold registry so it can be mutated
    registry = Registry()
    attribute_schemas_map = {}
    
    return [registry], None, attribute_schemas_map

def validate_payload(payload, registry_list, attributes_schema, attribute_schemas_map=None):
    """
    Validate payload against core and non-core attribute schemas.
    All schemas are loaded on-demand from @context URLs and cached.
    
    Args:
        payload: JSON payload to validate
        registry_list: List containing referencing Registry with all schemas (core and non-core)
        attributes_schema: Unused (kept for compatibility, now None)
        attribute_schemas_map: Mapping from @context URLs to (schema_name, schema_data, schema_url)
    """
    errors = []
    registry = registry_list[0]
    
    def find_and_validate_objects(data, path=""):
        if isinstance(data, dict):
            # Check for objects with @context and @type
            if "@context" in data and "@type" in data and attribute_schemas_map is not None:
                context_url = data.get("@context")
                obj_type = data.get("@type")
                
                # Handle core Beckn objects (e.g., beckn:Order, beckn:Offer)
                if obj_type and obj_type.startswith("beckn:"):
                    # Load core attributes schema on-demand if needed
                    if is_core_context_url(context_url):
                        attributes_url = get_attributes_url_from_context_url(context_url)
                        # Check if already loaded
                        if attributes_url not in registry_list[0]:
                            load_core_schema_for_context_url(context_url, registry_list)
                            
                            # Validate core object
                            try:
                                resource = registry_list[0].get(attributes_url)
                                if resource is not None:
                                    core_attributes = resource.contents
                                    # Extract object name (e.g., "beckn:Order" -> "Order")
                                    object_name = obj_type.split(":")[-1]
                                    
                                    if "components" in core_attributes and "schemas" in core_attributes["components"]:
                                        schemas = core_attributes["components"]["schemas"]
                                        if object_name in schemas:
                                            print(f"  Validating {object_name} at {path or 'root'}...")
                                            try:
                                                # Use a $ref that points to the schema within the full document
                                                # This allows $ref JSON pointers in the schema (like #/components/schemas/Provider/properties/beckn:id)
                                                # to resolve correctly because they're relative to the full document root
                                                schema_to_validate = {
                                                    "$ref": f"{attributes_url}#/components/schemas/{object_name}"
                                                }
                                                validate(instance=data, schema=schema_to_validate, registry=registry_list[0])
                                                print(f"  {object_name} at {path or 'root'} is VALID.")
                                            except ValidationError as e:
                                                print(f"  {object_name} at {path or 'root'} is INVALID: {e.message}")
                                                print(f"  Path: {e.json_path}")
                                                errors.append(f"{path}: {e.message}")
                                            except Exception as e:
                                                # If $ref resolution fails, fall back to direct fragment validation
                                                # This might fail for schemas with internal $ref, but worth trying
                                                print(f"  Warning: $ref resolution failed, trying direct validation: {e}")
                                                try:
                                                    validate(instance=data, schema=schemas[object_name], registry=registry_list[0])
                                                    print(f"  {object_name} at {path or 'root'} is VALID.")
                                                except ValidationError as ve:
                                                    print(f"  {object_name} at {path or 'root'} is INVALID: {ve.message}")
                                                    print(f"  Path: {ve.json_path}")
                                                    errors.append(f"{path}: {ve.message}")
                            except (KeyError, AttributeError):
                                pass
                
                # Handle non-core slotted attribute objects
                else:
                    # Check if this context URL matches a known non-core attribute schema
                    # If not found, try to load it dynamically
                    if context_url not in attribute_schemas_map:
                        result = load_schema_for_context_url(context_url, attribute_schemas_map, registry_list)
                        if result is None:
                            # Schema not found, continue recursion but don't validate this object
                            pass
                    
                    # Validate if we have a schema (loaded on-demand and cached)
                    if context_url in attribute_schemas_map:
                        schema_name, schema_data, schema_url = attribute_schemas_map[context_url]
                        
                        # Find the schema component that matches @type
                        # @type might be just the name (e.g., "ChargingOffer") or full IRI
                        schema_type = obj_type
                        if ":" in obj_type:
                            # Extract local name from IRI (e.g., "ev:ChargingOffer" -> "ChargingOffer")
                            schema_type = obj_type.split(":")[-1]
                        
                        # Look for schema in components/schemas
                        if "components" in schema_data and "schemas" in schema_data["components"]:
                            schemas = schema_data["components"]["schemas"]
                            
                            if schema_type in schemas:
                                print(f"  Validating {schema_type} (from {schema_name}) at {path or 'root'}...")
                                
                                # Create a modified schema that allows @context and @type
                                validation_schema = copy.deepcopy(schemas[schema_type])
                                if "additionalProperties" in validation_schema and validation_schema["additionalProperties"] is False:
                                    # Allow @context and @type by adding them to properties
                                    if "properties" not in validation_schema:
                                        validation_schema["properties"] = {}
                                    validation_schema["properties"]["@context"] = {"type": "string"}
                                    validation_schema["properties"]["@type"] = {"type": "string"}
                                
                                try:
                                    validate(instance=data, schema=validation_schema, registry=registry_list[0])
                                    print(f"  {schema_type} at {path or 'root'} is VALID.")
                                except ValidationError as e:
                                    print(f"  {schema_type} at {path or 'root'} is INVALID: {e.message}")
                                    print(f"  Path: {e.json_path}")
                                    errors.append(f"{path} ({schema_type}): {e.message}")
                            else:
                                # Try to find by matching schema name
                                for schema_key, schema_def in schemas.items():
                                    if schema_key.lower() == schema_type.lower():
                                        print(f"  Validating {schema_key} (from {schema_name}) at {path or 'root'}...")
                                        
                                        # Create a modified schema that allows @context and @type
                                        validation_schema = copy.deepcopy(schema_def)
                                        if "additionalProperties" in validation_schema and validation_schema["additionalProperties"] is False:
                                            # Allow @context and @type by adding them to properties
                                            if "properties" not in validation_schema:
                                                validation_schema["properties"] = {}
                                            validation_schema["properties"]["@context"] = {"type": "string"}
                                            validation_schema["properties"]["@type"] = {"type": "string"}
                                        
                                        try:
                                            validate(instance=data, schema=validation_schema, registry=registry_list[0])
                                            print(f"  {schema_key} at {path or 'root'} is VALID.")
                                        except ValidationError as e:
                                            print(f"  {schema_key} at {path or 'root'} is INVALID: {e.message}")
                                            print(f"  Path: {e.json_path}")
                                            errors.append(f"{path} ({schema_key}): {e.message}")
                                        break
            
            # Recursively check children
            for key, value in data.items():
                find_and_validate_objects(value, f"{path}/{key}" if path else key)
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                find_and_validate_objects(item, f"{path}[{idx}]")

    find_and_validate_objects(payload)
    return errors

def process_file(filepath, registry_list, attributes_schema, attribute_schemas_map=None):
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
                                validate_payload(json_body, registry_list, attributes_schema, attribute_schemas_map)
                            except json.JSONDecodeError:
                                pass
            traverse_postman_items(data.get("item", []))
        else:
            validate_payload(data, registry_list, attributes_schema, attribute_schemas_map)
            
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate JSON files against Beckn protocol schemas")
    parser.add_argument("files", nargs="+", help="JSON files or Postman collections to validate")
    
    args = parser.parse_args()
    
    registry, attributes_schema, attribute_schemas_map = get_schema_store()
    
    for file in args.files:
        process_file(file, registry, attributes_schema, attribute_schemas_map)
