"""Used to resolve schema references."""

import functools
import json
import os
import re
import typing

from open_alchemy import exceptions
from open_alchemy import types

_REF_PATTER = re.compile(r"^#\/components\/schemas\/(\w+)$")


NameSchema = typing.Tuple[str, types.Schema]


def resolve(*, name: str, schema: types.Schema, schemas: types.Schemas) -> NameSchema:
    """
    Resolve reference to another schema.

    Recursively resolves $ref until $ref key is no longer found. On each step, the name
    of the schema is recorded.

    Raises SchemaNotFound is a $ref resolution fails.

    Args:
        name: The name of the schema from the last step.
        schema: The specification of the schema from the last step.
        schemas: Dictionary with all defined schemas used to resolve $ref.

    Returns:
        The first schema that no longer has the $ref key and the name of that schema.

    """
    # Checking whether schema is a reference schema
    ref = schema.get("$ref")
    if ref is None:
        return name, schema

    ref_name, ref_schema = get_ref(ref=ref, schemas=schemas)

    return resolve(name=ref_name, schema=ref_schema, schemas=schemas)


def get_ref(*, ref: str, schemas: types.Schemas) -> NameSchema:
    """
    Get the schema referenced by ref.

    Raises SchemaNotFound is a $ref resolution fails.

    Args:
        ref: The reference to the schema.
        schemas: The schemas to use to resolve the ref.

    Returns:
        The schema referenced by ref.

    """
    # Check for remote ref
    if not ref.startswith("#"):
        return get_remote_ref(ref=ref)

    # Checking value of $ref
    match = _REF_PATTER.match(ref)
    if not match:
        raise exceptions.SchemaNotFoundError(
            f"{ref} format incorrect, expected #/components/schemas/<SchemaName>"
        )

    # Retrieving new schema
    ref_name = match.group(1)
    ref_schema = schemas.get(ref_name)
    if ref_schema is None:
        raise exceptions.SchemaNotFoundError(f"{ref_name} was not found in schemas.")

    return ref_name, ref_schema


def _norm_context(*, context: str) -> str:
    """
    Normalize the path and case of a context.

    Args:
        context: The context to normalize.

    Returns:
        The normalized context.

    """
    norm_context = os.path.normpath(context)
    return os.path.normcase(norm_context)


def _separate_context_path(*, ref: str) -> typing.Tuple[str, str]:
    """
    Separate the context and path of a reference.

    Raise MalformedSchemaError if the reference does not contain #.

    Args:
        ref: The reference to separate.

    Returns:
        The context and path to the schema as a tuple.

    """
    try:
        ref_context, ref_schema = ref.split("#")
    except ValueError:
        raise exceptions.MalformedSchemaError(
            f"A reference must contain exactly one #. Actual reference: {ref}"
        )
    return ref_context, ref_schema


def _add_remote_context(*, context: str, ref: str) -> str:
    """
    Add remote context to any $ref within a schema retrieved from a remote reference.

    There are 3 cases:
    1. The $ref value starts with # in which case the context is prepended.
    2. The $ref starts with a filename in which case only the file portion of the
        context is prepended.
    3. The $ref starts with a relative path and ends with a file in which case the file
        portion of the context is prepended and merged so that the shortest possible
        relative path is used.

    After the paths are merged the following operations are done:
    1. a normalized relative path is calculated (eg. turning ./dir1/../dir2 to ./dir2)
        and
    2. the case is normalized.

    Args:
        context: The context of the document from which the schema was retrieved which
            is the relative path to the file on the system from the base OpenAPI
            specification.
        ref: The value of a $ref within the schema.

    Returns:
        The $ref value with the context of the document included.

    """
    ref_context, ref_schema = _separate_context_path(ref=ref)
    context_head, _ = os.path.split(context)

    # Handle reference within document
    if not ref_context:
        return f"{context}{ref}"

    # Handle reference outside document
    new_ref_context = os.path.join(context_head, ref_context)
    norm_new_ref_context = _norm_context(context=new_ref_context)
    return f"{norm_new_ref_context}#{ref_schema}"


def _handle_match(match: typing.Match, *, context: str) -> str:
    """
    Map a match to the updated value.

    Args:
        match: The match to the regular expression for the reference.
        context: The context to use to update the reference.

    Returns:
        The updated reference.

    """
    ref = match.group(1)
    mapped_ref = _add_remote_context(context=context, ref=ref)
    return match.group(0).replace(ref, mapped_ref)


_REF_VALUE_PATTERN = r'"\$ref": "(.*?)"'


def _map_remote_schema_ref(*, schema: types.Schema, context: str) -> types.Schema:
    """
    Update and $ref within the schema with the remote context.

    Serialize the schema, look for $ref and update value to include context.

    Args:
        schema: The schema to update.
        context: The con text of the schema.

    Returns:
        The schema with any $ref mapped to include the context.

    """
    # Define context for mapping
    handle_match_context = functools.partial(_handle_match, context=context)

    str_schema = json.dumps(schema)
    mapped_str_schema = re.sub(_REF_VALUE_PATTERN, handle_match_context, str_schema)
    mapped_schema = json.loads(mapped_str_schema)
    return mapped_schema


class _RemoteSchemaStore:
    """Store remote schemas in memory to speed up use."""

    _schemas: typing.Dict[str, types.Schemas]
    spec_context: typing.Optional[str]

    def __init__(self) -> None:
        """Construct."""
        self._schemas = {}
        self.spec_context = None

    def reset(self):
        """Reset the state of the schema store."""
        self._schemas = {}
        self.spec_context = None

    def get_schemas(self, *, context: str) -> types.Schema:
        """
        Retrieve the schemas for a context.

        Raise MissingArgumentError if the context for the original OpenAPI specification
            has not been set.
        Raise SchemaNotFoundError if the context doesn't exist or is not a json or yaml
            file.

        Args:
            context: The path, relative to the original OpenAPI specification, with the
                file containing the schemas.

        Returns:
            The schemas.

        """
        # Check whether the context is already loaded
        if context in self._schemas:
            return self._schemas[context]

        if self.spec_context is None:
            raise exceptions.MissingArgumentError(
                "Cannot find the file containing the remote reference, either "
                "initialize OpenAlchemy with init_json or init_yaml or pass the path "
                "to the OpenAPI specification to OpenAlchemy."
            )

        # Check for json, yaml or yml file extension
        _, extension = os.path.splitext(context)
        extension = extension.lower()
        if extension is None or extension not in {".json", ".yaml", ".yml"}:
            raise exceptions.SchemaNotFoundError(
                "The remote context is not a JSON nor YAML file. The path is: "
                f"{context}"
            )

        # Calculate location of schemas
        spec_dir = os.path.dirname(self.spec_context)
        remote_spec_filename = os.path.join(spec_dir, context)
        try:
            with open(remote_spec_filename) as in_file:
                if extension == ".json":
                    try:
                        schemas = json.load(in_file)
                    except json.JSONDecodeError:
                        raise exceptions.SchemaNotFoundError(
                            "The remote reference file is not valid JSON. The path "
                            f"is: {context}"
                        )
                else:
                    # Import as needed to make yaml optional
                    import yaml  # pylint: disable=import-outside-toplevel

                    try:
                        schemas = yaml.safe_load(in_file)
                    except yaml.scanner.ScannerError:
                        raise exceptions.SchemaNotFoundError(
                            "The remote reference file is not valid YAML. The path "
                            f"is: {context}"
                        )
        except FileNotFoundError:
            raise exceptions.SchemaNotFoundError(
                "The file with the remote reference was not found. The path is: "
                f"{context}"
            )

        # Store for faster future retrieval
        self._schemas[context] = schemas
        return schemas


_remote_schema_store = _RemoteSchemaStore()  # pylint: disable=invalid-name


def set_context(*, path: str) -> None:
    """
    Set the context for the initial OpenAPI specification.

    Args:
        path: The path to the OpenAPI specification

    """
    _remote_schema_store.spec_context = path


def _retrieve_schema(*, schemas: types.Schemas, path: str) -> NameSchema:
    """
    Retrieve schema from a dictionary.

    Raise SchemaNotFoundError if the schema is not found at the path.

    Args:
        schemas: All the schemas.
        path: The location to retrieve the schema from.

    Returns:
        The schema at the path from the schemas.

    """
    # Strip leading /
    if path.startswith("/"):
        path = path[1:]

    path_components = path.split("/", 1)

    try:
        # Base case, no tail
        if len(path_components) == 1:
            return path_components[0], schemas[path_components[0]]
        # Recursive case, call again with path tail
        return _retrieve_schema(
            schemas=schemas[path_components[0]], path=path_components[1]
        )
    except KeyError:
        raise exceptions.SchemaNotFoundError(
            f"The schema was not found in the remote schemas. Path subsection: {path}"
        )


def get_remote_ref(*, ref: str) -> NameSchema:
    """
    Retrieve remote schema based on reference.

    Args:
        ref: The reference to the remote schema.

    Returns:
        The remote schema.

    """
    context, path = _separate_context_path(ref=ref)
    context = _norm_context(context=context)
    schemas = _remote_schema_store.get_schemas(context=context)
    name, schema = _retrieve_schema(schemas=schemas, path=path)
    schema = _map_remote_schema_ref(schema=schema, context=context)
    return name, schema
