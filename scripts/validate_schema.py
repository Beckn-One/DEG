"""
Beckn Protocol Schema Validator

This script validates JSON payloads against Beckn protocol schemas (core and domain-specific).
It automatically discovers and loads schemas from @context URLs embedded in JSON-LD objects,
supports both core Beckn objects (beckn:Order, beckn:Offer, etc.) and domain-specific attribute
objects (ChargingOffer, ChargingSession, etc.), and handles schema references across multiple
schema files.

HOW IT WORKS:
-------------
1. Schema Discovery: The validator scans JSON payloads for objects with @context and @type fields.
   These fields indicate which schema should be used for validation.

2. On-Demand Loading: Schemas are loaded on-demand from GitHub URLs when first encountered.
   The @context URL (e.g., .../EvChargingOffer/v1/context.jsonld) is converted to the
   corresponding attributes.yaml URL for schema loading.

3. Schema Caching: Loaded schemas are cached in a Registry and attribute_schemas_map to avoid
   redundant network requests.

4. Reference Resolution: Uses the referencing library to resolve $ref JSON pointers within
   and across schema files. Core objects use $ref to the full schema document to ensure
   internal references resolve correctly.

5. Validation: Validates objects against their corresponding schemas, handling both core
   Beckn objects and domain-specific attribute objects with different validation strategies.
   
Note: Schemas are loaded from the exact branch specified in the @context URL. If a schema
is not found on that branch, validation will fail. No branch fallback is performed.

ARCHITECTURE:
-------------
- Core Objects (beckn:Order, beckn:Offer, etc.): Validated using schemas from core/v2/attributes.yaml
- Attribute Objects (ChargingOffer, ChargingSession, etc.): Validated using schemas from
  domain-specific attributes.yaml files (e.g., EvChargingOffer/v1/attributes.yaml)
- JSON-LD Support: Automatically allows @context and @type properties even when schemas
  have additionalProperties: false

USAGE EXAMPLES:
---------------
# Validate a single JSON file:
python3 scripts/validate_schema.py examples/ev-charging/v2/03_select/time-based-ev-charging-slot-select.json

# Validate multiple files:
python3 scripts/validate_schema.py examples/ev-charging/v2/**/*.json

# Validate only core Beckn objects (skip domain-specific attributes):
python3 scripts/validate_schema.py --core-only examples/ev-charging/v2/03_select/time-based-ev-charging-slot-select.json

# Validate Postman collection:
python3 scripts/validate_schema.py testnet/ev-charging-devkit/postman/ev-charging:BAP-DEG.postman_collection.json

EXAMPLE JSON STRUCTURE:
----------------------
{
  "message": {
    "order": {
      "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/context.jsonld",
      "@type": "beckn:Order",
      "beckn:id": "order-123",
      "beckn:orderItems": [
        {
          "beckn:acceptedOffer": {
            "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/context.jsonld",
            "@type": "beckn:Offer",
            "beckn:offerAttributes": {
              "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/EvChargingOffer/v1/context.jsonld",
              "@type": "ChargingOffer",
              "tariffModel": "PER_KWH"
            }
          }
        }
      ]
    }
  }
}

The validator will:
1. Detect beckn:Order and load core/v2/attributes.yaml
2. Detect beckn:Offer and use the already-loaded core schema
3. Detect ChargingOffer and load EvChargingOffer/v1/attributes.yaml
4. Validate each object against its corresponding schema

DEPENDENCIES:
-------------
- jsonschema: JSON Schema validation
- referencing: JSON Schema reference resolution
- requests: HTTP requests for schema loading
- yaml: YAML parsing for schema files
- pyld: JSON-LD processing and expansion (optional, for composed schema support)

JSON-LD SUPPORT:
---------------
When a composed context is detected (e.g., schema/composed/p2p-trading/v2/context.jsonld),
the validator can optionally expand the JSON-LD using pyld library to:
1. Expand all CURIE mappings
2. Resolve all @context references
3. Validate JSON-LD structure
4. Then validate against OpenAPI schemas

Use --jsonld flag to enable JSON-LD expansion and validation.
"""

import json
import re
import copy
import requests
import yaml
from jsonschema import validate, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# Optional JSON-LD support
try:
    from pyld import jsonld
    JSONLD_AVAILABLE = True
except ImportError:
    JSONLD_AVAILABLE = False
    jsonld = None

# Domain-specific constraints support (YAML-based, simpler than SHACL)
# Constraints are loaded from constraints.yaml files in composed schema directories

def load_schema_from_url(url):
    """
    Load a YAML schema file from a URL.
    
    Args:
        url: URL to the attributes.yaml schema file
        
    Returns:
        dict: Parsed YAML schema as a dictionary
        
    Raises:
        requests.HTTPError: If the HTTP request fails
        yaml.YAMLError: If YAML parsing fails
    """
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
    
    Loads the schema from the branch specified in the context_url. Caches the schema
    in the registry for reuse.
    
    Args:
        context_url: The @context URL from the JSON (e.g., .../core/v2/context.jsonld)
        registry_list: List containing referencing Registry (mutated in place)
    
    Returns:
        dict: Schema data if successful, None if loading fails
    """
    registry = registry_list[0]
    attributes_url = get_attributes_url_from_context_url(context_url)
    
    # Check if already loaded in registry
    try:
        resource = registry.get(attributes_url)
        if resource is not None:
            return resource.contents
    except (KeyError, AttributeError):
        pass
    
    # Load from the branch specified in context_url
    try:
        schema_data = load_schema_from_url(attributes_url)
        registry_list[0] = registry.with_resource(attributes_url, Resource.from_contents(schema_data, DRAFT202012))
        branch = extract_branch_from_context_url(context_url)
        print(f"  Loaded core attributes schema (branch: {branch})")
        return schema_data
    except Exception as e:
        print(f"  Warning: Failed to load core attributes schema from {attributes_url}: {e}")
        return None

def load_schema_for_context_url(context_url, attribute_schemas_map, registry_list=None):
    """
    Load schema for a given @context URL from the branch specified in the URL.
    
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
    
    # Load the schema from the branch specified in context_url
    try:
        schema_data = load_schema_from_url(attributes_url)
        attribute_schemas_map[context_url] = (schema_name, schema_data, attributes_url)
        if registry_list is not None:
            registry = registry_list[0]
            registry_list[0] = registry.with_resource(attributes_url, Resource.from_contents(schema_data, DRAFT202012))
        print(f"  Loaded: {schema_name}/{version} (branch: {branch})")
        return (schema_name, schema_data, attributes_url)
    except Exception as e:
        print(f"  Warning: Failed to load {schema_name}/{version} from {attributes_url}: {e}")
        return None


def _convert_relative_refs_to_absolute(obj, base_url):
    """Recursively convert relative $ref to absolute $ref in schema definitions."""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str) and v.startswith("#"):
                result[k] = f"{base_url}{v}"
            elif k == "allOf" and isinstance(v, list):
                result[k] = [_convert_relative_refs_to_absolute(item, base_url) for item in v]
            else:
                result[k] = _convert_relative_refs_to_absolute(v, base_url)
        return result
    elif isinstance(obj, list):
        return [_convert_relative_refs_to_absolute(item, base_url) for item in obj]
    return obj

def _inject_jsonld_properties(schema):
    """Inject @context and @type properties into schema if additionalProperties is False."""
    if schema.get("additionalProperties") is False:
        if "properties" not in schema:
            schema["properties"] = {}
        schema["properties"]["@context"] = {"type": "string"}
        schema["properties"]["@type"] = {"type": "string"}
    return schema

def _validate_attribute_object(data, schema_def, schema_type, schema_name, path, errors, registry_list, schema_url=None):
    """
    Validate a domain-specific attribute object against its schema.
    
    Uses $ref to full document to allow nested $ref resolution, then handles
    @context and @type properties which are required for JSON-LD.
    
    Args:
        data: Object data to validate
        schema_def: Schema definition from attributes.yaml (used as fallback)
        schema_type: Type name for logging (e.g., "ChargingOffer")
        schema_name: Schema name for logging (e.g., "EvChargingOffer")
        path: JSON path for error reporting
        errors: List to append validation errors to
        registry_list: Registry list for reference resolution
        schema_url: Full URL to the attributes.yaml file (for $ref resolution)
    """
    print(f"  Validating {schema_type} (from {schema_name}) at {path or 'root'}...")
    
    # Try using $ref to full document first (allows nested $ref resolution)
    if schema_url:
        try:
            full_doc_resource = registry_list[0].get(schema_url)
            if full_doc_resource:
                full_doc = full_doc_resource.contents
                if "components" in full_doc and "schemas" in full_doc["components"]:
                    target_schema = full_doc["components"]["schemas"].get(schema_type)
                    if target_schema:
                        resolved_schema = copy.deepcopy(target_schema)
                        resolved_schema = _convert_relative_refs_to_absolute(resolved_schema, schema_url)
                        resolved_schema = _inject_jsonld_properties(resolved_schema)
                        
                        validate(instance=data, schema=resolved_schema, registry=registry_list[0])
                        print(f"  {schema_type} at {path or 'root'} is VALID.")
                        return
        except ValidationError as e:
            print(f"  {schema_type} at {path or 'root'} is INVALID: {e.message}")
            print(f"  Path: {e.json_path}")
            errors.append(f"{path} ({schema_type}): {e.message}")
            return
        except Exception:
            pass  # Fallback to direct validation
    
    # Fallback: direct validation with schema fragment
    validation_schema = copy.deepcopy(schema_def)
    validation_schema = _inject_jsonld_properties(validation_schema)
    
    try:
        validate(instance=data, schema=validation_schema, registry=registry_list[0])
        print(f"  {schema_type} at {path or 'root'} is VALID.")
    except ValidationError as e:
        print(f"  {schema_type} at {path or 'root'} is INVALID: {e.message}")
        print(f"  Path: {e.json_path}")
        errors.append(f"{path} ({schema_type}): {e.message}")

def get_schema_store():
    """
    Initialize empty schema store for on-demand schema loading.
    
    Returns:
        tuple: (registry_list, attributes_schema, attribute_schemas_map)
            - registry_list: List containing referencing Registry (wrapped for mutability)
            - attributes_schema: Unused, kept for compatibility (None)
            - attribute_schemas_map: Dict mapping @context URLs to (schema_name, schema_data, schema_url)
    """
    registry = Registry()
    attribute_schemas_map = {}
    return [registry], None, attribute_schemas_map

def is_composed_context_url(context_url):
    """
    Check if @context URL points to a composed schema.
    
    Example:
        .../schema/composed/p2p-trading/v2/context.jsonld -> True
        .../schema/core/v2/context.jsonld -> False
    """
    return '/schema/composed/' in context_url

def get_constraints_url_from_context_url(context_url):
    """
    Get constraints file URL from composed context URL.
    
    Example:
        .../schema/composed/p2p-trading/v2/context.jsonld -> .../schema/composed/p2p-trading/v2/constraints.yaml
    """
    if is_composed_context_url(context_url):
        return context_url.replace('/context.jsonld', '/constraints.yaml')
    return None

def infer_schema_url_from_composed_context(composed_context_url, schema_type):
    """
    Infer schema URL for an attribute type from a composed context URL.
    
    Uses schemaMapping from constraints.yaml if available, otherwise constructs URL
    based on convention: schema/{SchemaName}/v{version}/context.jsonld
    
    Args:
        composed_context_url: URL to composed context (e.g., .../composed/p2p-trading/v2/context.jsonld)
        schema_type: Type name (e.g., "EnergyBuyer")
    
    Returns:
        str: Inferred schema context URL or None
    """
    if not is_composed_context_url(composed_context_url):
        return None
    
    # Extract base URL and branch from composed context
    # Pattern: .../refs/heads/{branch}/schema/composed/{domain}/{version}/context.jsonld
    match = re.search(r'(https://raw\.githubusercontent\.com/[^/]+/[^/]+/refs/heads/[^/]+)/schema/composed/([^/]+)/([^/]+)/context\.jsonld', composed_context_url)
    if not match:
        return None
    
    base_url = match.group(1)
    domain = match.group(2)
    version = match.group(3)
    
    # Try to load constraints.yaml to get schemaMapping
    constraints = load_domain_constraints(composed_context_url)
    if constraints and "schemaMapping" in constraints:
        schema_mapping = constraints.get("schemaMapping", {})
        if schema_type in schema_mapping:
            schema_path = schema_mapping[schema_type]
            # Construct full URL
            return f"{base_url}/schema/{schema_path}/context.jsonld"
    
    # Fallback: Try convention-based inference
    # Note: This is a best-effort fallback. The schemaMapping in constraints.yaml
    # should be used for accurate schema URLs. This fallback may use incorrect versions.
    # Returns None to avoid incorrect schema loading - let explicit @context handle it
    return None

def load_domain_constraints(context_url):
    """
    Load domain-specific constraints from YAML file if available.
    
    Args:
        context_url: The @context URL (may be composed context)
    
    Returns:
        dict: Constraints data or None if not available
    """
    constraints_url = get_constraints_url_from_context_url(context_url)
    if not constraints_url:
        return None
    
    try:
        response = requests.get(constraints_url)
        response.raise_for_status()
        constraints_data = yaml.safe_load(response.text)
        print(f"  Loaded domain constraints from {constraints_url}")
        return constraints_data
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # Constraints file doesn't exist - that's okay
            return None
        else:
            print(f"  Warning: Failed to load constraints from {constraints_url}: {e}")
            return None
    except Exception as e:
        # Other errors loading constraints - that's okay
        return None

def apply_domain_constraints(data, obj_type, constraints, path, errors):
    """
    Apply domain-specific constraints to an object.
    
    Args:
        data: Object data to validate
        obj_type: Type of the object (e.g., "beckn:Provider")
        constraints: Constraints data loaded from constraints.yaml
        path: JSON path for error reporting
        errors: List to append validation errors to
    
    Returns:
        bool: True if all constraints pass, False otherwise
    """
    if not constraints or "constraints" not in constraints:
        return True
    
    constraint_list = constraints.get("constraints", [])
    all_passed = True
    
    for constraint in constraint_list:
        target = constraint.get("target", {})
        target_type = target.get("type", "")
        
        # Check if this constraint applies to this object type
        if target_type and obj_type == target_type:
            rules = constraint.get("rules", [])
            
            for rule in rules:
                property_path = rule.get("property", "")
                message = rule.get("message", "Constraint violation")
                
                # Check required property
                if rule.get("required"):
                    if not _has_property(data, property_path):
                        print(f"  Constraint violation at {path or 'root'}: {message}")
                        errors.append(f"{path}: {message}")
                        all_passed = False
                        continue
                
                # Check property equals value
                if "equals" in rule:
                    expected_value = rule.get("equals")
                    actual_value = _get_property(data, property_path)
                    if actual_value != expected_value:
                        print(f"  Constraint violation at {path or 'root'}: {message}")
                        errors.append(f"{path}: {message}")
                        all_passed = False
    
    return all_passed

def _has_property(obj, path):
    """Check if a property exists at the given path (supports dot notation)."""
    keys = path.split(".")
    current = obj
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    return True

def _get_property(obj, path):
    """Get a property value at the given path (supports dot notation)."""
    keys = path.split(".")
    current = obj
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current

def _create_jsonld_document_loader(composed_context_url, composed_context):
    """Create a document loader for JSON-LD expansion."""
    def document_loader(url, options):
        """Custom document loader for JSON-LD expansion"""
        try:
            if url == composed_context_url:
                return {
                    'contextUrl': None,
                    'documentUrl': url,
                    'document': composed_context.get('@context', {})
                }
            resp = requests.get(url)
            resp.raise_for_status()
            doc = resp.json()
            return {
                'contextUrl': None,
                'documentUrl': url,
                'document': doc.get('@context', doc) if isinstance(doc, dict) else doc
            }
        except Exception as e:
            return {
                'contextUrl': None,
                'documentUrl': url,
                'document': None,
                'error': str(e)
            }
    return document_loader

def expand_jsonld_with_composed_context(payload, composed_context_url, registry_list):
    """
    Expand JSON-LD payload using a composed context.
    
    Args:
        payload: JSON payload (dict)
        composed_context_url: URL to composed context.jsonld
        registry_list: Registry list for schema loading (unused, kept for compatibility)
    
    Returns:
        tuple: (expanded_payload, errors) - expanded JSON-LD and any errors
    """
    if not JSONLD_AVAILABLE:
        return payload, ["JSON-LD library (pyld) not available. Install with: pip install pyld"]
    
    errors = []
    
    try:
        response = requests.get(composed_context_url)
        response.raise_for_status()
        composed_context = response.json()
        
        document_loader = _create_jsonld_document_loader(composed_context_url, composed_context)
        expanded = jsonld.expand(payload, {'base': composed_context_url, 'documentLoader': document_loader})
        return expanded, errors
    except Exception as e:
        errors.append(f"JSON-LD expansion failed: {e}")
        return payload, errors

def _find_root_context(payload):
    """Find root-level @context from payload (checks payload and message levels)."""
    if not isinstance(payload, dict):
        return None
    
    if "@context" in payload:
        return payload.get("@context")
    
    if "message" in payload and isinstance(payload["message"], dict):
        if "@context" in payload["message"]:
            return payload["message"].get("@context")
        # Check nested objects in message
        for value in payload["message"].values():
            if isinstance(value, dict) and "@context" in value:
                return value.get("@context")
    
    return None

def _infer_core_context_url_from_composed(composed_context_url):
    """Infer core context URL from composed context URL (same branch and version)."""
    match = re.search(r'(https://raw\.githubusercontent\.com/[^/]+/[^/]+/refs/heads/[^/]+)/schema/composed/[^/]+/([^/]+)/context\.jsonld', composed_context_url)
    if match:
        base_url, version = match.group(1), match.group(2)
        return f"{base_url}/schema/core/{version}/context.jsonld"
    # Fallback: pattern replacement
    return re.sub(r'/schema/composed/[^/]+/([^/]+)/', r'/schema/core/\1/', composed_context_url)

def _validate_core_object(data, obj_type, context_url, inherited_context, path, errors, registry_list, attribute_schemas_map, current_constraints):
    """Validate a core Beckn object (e.g., beckn:Order, beckn:Offer)."""
    if not (is_core_context_url(context_url) or is_composed_context_url(context_url)):
        return
    
    attributes_url = get_attributes_url_from_context_url(context_url)
    core_context_url = context_url
    
    if is_composed_context_url(context_url):
        core_context_url = _infer_core_context_url_from_composed(context_url)
        attributes_url = get_attributes_url_from_context_url(core_context_url)
    
    if attributes_url not in registry_list[0]:
        load_core_schema_for_context_url(core_context_url, registry_list)
    
    try:
        resource = registry_list[0].get(attributes_url)
        if not resource:
            return
        
        core_attributes = resource.contents
        object_name = obj_type.split(":")[-1]
        
        if "components" not in core_attributes or "schemas" not in core_attributes["components"]:
            return
        
        schemas = core_attributes["components"]["schemas"]
        if object_name not in schemas:
            return
        
        print(f"  Validating {object_name} at {path or 'root'}...")
        
        # Apply domain constraints
        if current_constraints and not apply_domain_constraints(data, obj_type, current_constraints, path, errors):
            return
        
        # Validate using $ref to full document
        try:
            schema_to_validate = {"$ref": f"{attributes_url}#/components/schemas/{object_name}"}
            validate(instance=data, schema=schema_to_validate, registry=registry_list[0])
            print(f"  {object_name} at {path or 'root'} is VALID.")
        except ValidationError as e:
            print(f"  {object_name} at {path or 'root'} is INVALID: {e.message}")
            print(f"  Path: {e.json_path}")
            errors.append(f"{path}: {e.message}")
        except Exception:
            # Fallback: direct validation
            try:
                validate(instance=data, schema=schemas[object_name], registry=registry_list[0])
                print(f"  {object_name} at {path or 'root'} is VALID.")
            except ValidationError as ve:
                print(f"  {object_name} at {path or 'root'} is INVALID: {ve.message}")
                errors.append(f"{path}: {ve.message}")
    except (KeyError, AttributeError):
        pass

def _validate_attribute_object_from_type(data, obj_type, context_url, inherited_context, path, errors, registry_list, attribute_schemas_map, core_only):
    """Validate a domain-specific attribute object (e.g., EnergyBuyer, ChargingOffer)."""
    if core_only:
        return
    
    schema_type = obj_type.split(":")[-1] if ":" in obj_type else obj_type
    
    # Infer schema URL from composed context if needed
    if not context_url or is_composed_context_url(context_url):
        composed_context = inherited_context or context_url
        if composed_context and is_composed_context_url(composed_context):
            inferred_url = infer_schema_url_from_composed_context(composed_context, schema_type)
            if inferred_url:
                context_url = inferred_url
    
    if not context_url or context_url not in attribute_schemas_map:
        if context_url:
            load_schema_for_context_url(context_url, attribute_schemas_map, registry_list)
    
    if context_url and context_url in attribute_schemas_map:
        schema_name, schema_data, schema_url = attribute_schemas_map[context_url]
        if "components" in schema_data and "schemas" in schema_data["components"]:
            schemas = schema_data["components"]["schemas"]
            
            # Try exact match, then case-insensitive
            if schema_type in schemas:
                _validate_attribute_object(data, schemas[schema_type], schema_type, schema_name, path, errors, registry_list, schema_url)
            else:
                for schema_key, schema_def in schemas.items():
                    if schema_key.lower() == schema_type.lower():
                        _validate_attribute_object(data, schema_def, schema_key, schema_name, path, errors, registry_list, schema_url)
                        break

def validate_payload(payload, registry_list, attributes_schema, attribute_schemas_map=None, core_only=False, jsonld_mode=False):
    """
    Validate JSON payload against Beckn protocol schemas.
    
    Recursively traverses the payload, identifies objects with @context and @type,
    loads schemas on-demand, and validates each object against its corresponding schema.
    Supports both core Beckn objects (beckn:Order, etc.) and domain-specific attribute
    objects (ChargingOffer, etc.).
    
    Args:
        payload: JSON payload to validate (dict or list)
        registry_list: List containing referencing Registry with all loaded schemas
        attributes_schema: Unused, kept for compatibility (None)
        attribute_schemas_map: Dict mapping @context URLs to (schema_name, schema_data, schema_url)
        core_only: If True, only validate core Beckn objects, skip domain-specific attributes
        jsonld_mode: If True, expand JSON-LD using composed contexts before validation
    
    Returns:
        list: List of validation error messages (empty if validation passes)
    """
    errors = []
    
    # Find root context and load domain constraints
    root_context = _find_root_context(payload)
    domain_constraints = None
    if root_context and is_composed_context_url(root_context):
        domain_constraints = load_domain_constraints(root_context)
    
    # JSON-LD expansion if enabled
    if jsonld_mode and root_context and is_composed_context_url(root_context):
        print(f"  Detected composed context: {root_context}")
        expanded, jsonld_errors = expand_jsonld_with_composed_context(payload, root_context, registry_list)
        errors.extend(jsonld_errors)
        if not jsonld_errors:
            print(f"  JSON-LD expansion successful")
            payload = expanded
        else:
            print(f"  JSON-LD expansion failed, continuing with original payload")
    
    def find_and_validate_objects(data, path="", inherited_context=None):
        """Recursively find and validate objects with @type in the payload."""
        if isinstance(data, dict):
            context_url = data.get("@context") or inherited_context
            obj_type = data.get("@type")
            
            if "@context" in data:
                inherited_context = data.get("@context")
            
            # Load domain constraints if needed
            current_constraints = domain_constraints
            if not current_constraints:
                check_context = context_url or inherited_context
                if check_context and is_composed_context_url(check_context):
                    current_constraints = load_domain_constraints(check_context)
            
            # Validate objects with @type
            if obj_type and attribute_schemas_map is not None:
                if obj_type.startswith("beckn:"):
                    _validate_core_object(data, obj_type, context_url, inherited_context, path, errors, registry_list, attribute_schemas_map, current_constraints)
                else:
                    _validate_attribute_object_from_type(data, obj_type, context_url, inherited_context, path, errors, registry_list, attribute_schemas_map, core_only)
            
            # Recursively process children
            for key, value in data.items():
                find_and_validate_objects(value, f"{path}/{key}" if path else key, inherited_context)
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                find_and_validate_objects(item, f"{path}[{idx}]", inherited_context)

    find_and_validate_objects(payload)
    return errors

def process_file(filepath, registry_list, attributes_schema, attribute_schemas_map=None, core_only=False, jsonld_mode=False):
    """
    Process and validate a JSON file or Postman collection.
    
    Supports two file types:
    1. Regular JSON files: Validated directly
    2. Postman collections: Extracts JSON bodies from request items and validates them
    
    Args:
        filepath: Path to JSON file or Postman collection
        registry_list: List containing referencing Registry
        attributes_schema: Unused, kept for compatibility (None)
        attribute_schemas_map: Dict mapping @context URLs to schema info
        core_only: If True, only validate core Beckn objects, skip domain-specific attributes
        jsonld_mode: If True, expand JSON-LD using composed contexts before validation
    """
    print(f"Processing {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        is_postman = "info" in data and "_postman_id" in data.get("info", {})
        
        if is_postman:
            print("  Identified as Postman collection.")
            _traverse_postman_items(data.get("item", []), registry_list, attributes_schema, attribute_schemas_map, core_only, jsonld_mode)
        else:
            validate_payload(data, registry_list, attributes_schema, attribute_schemas_map, core_only, jsonld_mode)
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")

def _traverse_postman_items(items, registry_list, attributes_schema, attribute_schemas_map, core_only=False, jsonld_mode=False):
    """
    Recursively traverse Postman collection items and validate JSON request bodies.
    
    Args:
        items: List of Postman collection items (may contain nested items)
        registry_list: List containing referencing Registry
        attributes_schema: Unused, kept for compatibility (None)
        attribute_schemas_map: Dict mapping @context URLs to schema info
        core_only: If True, only validate core Beckn objects, skip domain-specific attributes
        jsonld_mode: If True, expand JSON-LD using composed contexts before validation
    """
    for item in items:
        if "item" in item:
            _traverse_postman_items(item["item"], registry_list, attributes_schema, attribute_schemas_map, core_only, jsonld_mode)
        if "request" in item and "body" in item["request"]:
            body = item["request"]["body"]
            if body.get("mode") == "raw":
                try:
                    json_body = json.loads(body["raw"])
                    validate_payload(json_body, registry_list, attributes_schema, attribute_schemas_map, core_only, jsonld_mode)
                except json.JSONDecodeError:
                    pass

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate JSON files against Beckn protocol schemas",
        epilog="Example: python3 scripts/validate_schema.py examples/ev-charging/v2/**/*.json"
    )
    parser.add_argument("files", nargs="+", help="JSON files or Postman collections to validate")
    parser.add_argument(
        "--core-only",
        action="store_true",
        default=False,
        help="Only validate core Beckn objects (beckn:Order, beckn:Offer, etc.), skip domain-specific attribute objects"
    )
    parser.add_argument(
        "--jsonld",
        action="store_true",
        default=False,
        help="Enable JSON-LD expansion and validation for composed contexts (requires pyld library)"
    )
    
    args = parser.parse_args()
    
    if args.jsonld and not JSONLD_AVAILABLE:
        print("Warning: --jsonld flag specified but pyld library not available.")
        print("Install with: pip install pyld")
        print("Continuing without JSON-LD expansion...")
        args.jsonld = False
    
    registry, attributes_schema, attribute_schemas_map = get_schema_store()
    
    for file in args.files:
        process_file(file, registry, attributes_schema, attribute_schemas_map, core_only=args.core_only, jsonld_mode=args.jsonld)
