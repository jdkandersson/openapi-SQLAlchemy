"""Types for model generation."""

import dataclasses
import functools
import textwrap
import typing


@dataclasses.dataclass
class ColumnSchemaArtifacts:
    """Artifacts from the OpenAPI schema."""

    # The type of the column
    type: str
    # The format of the column
    format: typing.Optional[str] = None
    # Whether the column is nullable
    nullable: typing.Optional[bool] = None
    # Whether the column is required
    required: typing.Optional[bool] = None
    # The model being reference for an object/array type
    de_ref: typing.Optional[str] = None
    # Whether the value of the column is generated (eg. through auto increment)
    generated: typing.Optional[bool] = None
    # The description of the column
    description: typing.Optional[str] = None


@dataclasses.dataclass
class ColumnArtifacts:
    """Artifacts for the column portion of a model template."""

    # The name of the column
    name: str
    # The type of the column
    type: str
    # The description of the column
    description: typing.Optional[str] = None


@dataclasses.dataclass
class ColumnArgArtifacts:
    """Artifacts for the __init__ and from_dict signatures of a model template."""

    # The name of the argument
    name: str
    # The type of the argument for __init__
    init_type: str
    # The type of the argument for from_dict
    from_dict_type: str


@dataclasses.dataclass
class ArgArtifacts:
    """Artifacts for the __init__ and from_dict args for a model."""

    # The artifacts for the arguments that are required
    required: typing.List[ColumnArgArtifacts]
    # The artifacts for the arguments that are not required
    not_required: typing.List[ColumnArgArtifacts]


@dataclasses.dataclass
class SQLAlchemyModelArtifacts:
    """Artifacts for the SQLAlchemy model."""

    # The name of the model
    name: str
    # Whether the columns are empty
    empty: bool
    # The columns for the model
    columns: typing.List[ColumnArtifacts]
    # The artifacts for the arguments for __init__ and from_dict
    arg: ArgArtifacts
    # The parent class
    parent_cls: str
    # The description of the model
    description: typing.Optional[str] = None

    # Calculated properties
    @property
    def docstring(self):
        """Calculate docstring for model."""
        return model_docstring(self)


@dataclasses.dataclass
class TypedDictClassArtifacts:
    """Artifacts for a TypedDict class."""

    # The properties for the TypedDict
    props: typing.List[ColumnArtifacts]
    # Whether the properties list is empty
    empty: bool
    # The name of the TypedDict
    name: typing.Optional[str]
    # The name of the parent class
    parent_class: typing.Optional[str]


@dataclasses.dataclass
class TypedDictArtifacts:
    """Artifacts for the TypedDicts for a model."""

    # The artifacts for the required TypedDict
    required: TypedDictClassArtifacts
    # The artifacts for the required TypedDict
    not_required: TypedDictClassArtifacts


@dataclasses.dataclass
class ModelArtifacts:
    """Artifacts for a model template."""

    # The artifacts for the SQLAlchemy model
    sqlalchemy: SQLAlchemyModelArtifacts
    # The artifacts for the TypedDicts
    typed_dict: TypedDictArtifacts


_DocstringWrapper = textwrap.TextWrapper(width=75)  # pylint: disable=invalid-name
_DEFAULT_DOCSTRING = "SQLAlchemy model protocol."


def model_docstring(artifacts: SQLAlchemyModelArtifacts) -> str:
    """
    Create docstring from description.

    Args:
        description: The description of the model.

    Returns:
        The docstring for the model.

    """
    if artifacts.description is None and artifacts.empty:
        return _DEFAULT_DOCSTRING

    # Calculate description
    description: str
    if artifacts.description is None:
        description = f"""
    {_DEFAULT_DOCSTRING}"""
    else:
        wrapped_description = _DocstringWrapper.wrap(artifacts.description)
        joined_description = "\n    ".join(wrapped_description)
        description = f"""
    {_DEFAULT_DOCSTRING}

    {joined_description}"""

    # Calculate docs for the attributes
    attr_docs = ""
    if not artifacts.empty:
        model_attr_docs_model_name_set = functools.partial(
            model_attr_docs, model_name=artifacts.name
        )
        mapped_attrs = map(model_attr_docs_model_name_set, artifacts.columns)
        joined_attrs = "\n        ".join(mapped_attrs)
        attr_docs = f"""

    Attrs:
        {joined_attrs}"""

    return f"""{description}{attr_docs}

    """


_AttrFirstWrapper = textwrap.TextWrapper(width=71)  # pylint: disable=invalid-name
_AttrRemainingWrapper = textwrap.TextWrapper(width=67)  # pylint: disable=invalid-name


def model_attr_docs(artifacts: ColumnArtifacts, model_name: str) -> str:
    """
    Calculate attribute documentation.

    Args:
        artifacts: The artifacts for the column to produce attribute documentation for.
        model_name: The name of the model that contains the attribute.

    Returns:
        The documentation for the attribute.

    """
    # Calculating docs for the attribute
    doc = _calculate_column_doc(artifacts=artifacts, model_name=model_name)

    # Wrapping and joining
    return _wrap_column_doc(
        doc=doc,
        first_wrapper=_AttrFirstWrapper,
        remaining_wrapper=_AttrRemainingWrapper,
        line_separator="\n            ",
    )


def _calculate_column_doc(artifacts: ColumnArtifacts, model_name: str) -> str:
    """
    Calculate the documentation for the column.

    Args:
        artifacts: The artifacts for the column.
        model_name: The name of the model to which the column belongs.

    Returns:
        The documentation for the column.

    """
    description: str
    if artifacts.description is not None:
        description = artifacts.description
    else:
        description = f"The {artifacts.name} of the {model_name}."
    return f"{artifacts.name}: {description}"


def _wrap_column_doc(
    *,
    doc: str,
    first_wrapper: textwrap.TextWrapper,
    remaining_wrapper: textwrap.TextWrapper,
    line_separator: str,
) -> str:
    """
    Calculate the documentation for a column.

    Args:
        doc: The documentation string for the column.
        first_wrapper: The text wrapper to use for the first line.
        remaining_wrapper: The wrapper to use for all remaining lines.
        line_separator: The string to use between lines.

    Returns:
        The documentation for the column.

    """
    # Wrapping and joining
    wrapped_doc = first_wrapper.wrap(doc)
    if len(wrapped_doc) > 1:
        remaining_doc = " ".join(wrapped_doc[1:])
        remaining_doc_wrapped = remaining_wrapper.wrap(remaining_doc)
        wrapped_doc = [wrapped_doc[0]] + remaining_doc_wrapped
    return line_separator.join(wrapped_doc)
