import json
from pathlib import Path

from jsonschema import Draft202012Validator, validators
from jsonschema.exceptions import ValidationError

CONFIG_VERSION = 2

CONDA_FORGE_YAML_DEFAULTS_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / f"conda-forge.v{CONFIG_VERSION}.yml"
)

CONDA_FORGE_YAML_SCHEMA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / f"conda-forge.v{CONFIG_VERSION}.json"
)


class DeprecatedFieldWarning(ValidationError):
    pass


def deprecated_validator(validator, value, instance, schema):
    if value and instance is not None:
        yield DeprecatedFieldWarning(
            f"'{schema['title']}' is deprecated.\n" + schema["description"]
        )


def get_validator_class():
    all_validators = dict(Draft202012Validator.VALIDATORS)
    all_validators["deprecated"] = deprecated_validator

    return validators.create(
        meta_schema=Draft202012Validator.META_SCHEMA, validators=all_validators
    )


_VALIDATOR_CLASS = get_validator_class()


def validate_json_schema(config, schema_file: str = None):
    # Validate the merged configuration against a JSON schema
    if not schema_file:
        schema_file = CONDA_FORGE_YAML_SCHEMA_FILE

    with open(schema_file, "r") as fh:
        _json_schema = json.loads(fh.read())

    validator = _VALIDATOR_CLASS(_json_schema)
    lints = []
    hints = []
    for error in validator.iter_errors(config):
        if isinstance(error, DeprecatedFieldWarning):
            hints.append(error)
        else:
            lints.append(error)
    return lints, hints

