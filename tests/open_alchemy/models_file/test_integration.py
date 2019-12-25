"""Tests for models file."""

import pytest

from open_alchemy import models_file

DOCSTRING = '"""Autogenerated SQLAlchemy models based on OpenAlchemy models."""'
LONG_NAME = "extremely_long_name_that_will_cause_wrapping_aaaaaaaaaaaaaaaaaa"


@pytest.mark.parametrize(
    "schemas, expected_source",
    [
        (
            [({"properties": {"id": {"type": "integer"}}}, "Model")],
            f'''{DOCSTRING}
# pylint: disable=no-member,useless-super-delegation

import typing

from open_alchemy import models


class ModelDict(typing.TypedDict, total=False):
    """TypedDict for properties that are not required."""

    id: typing.Optional[int]


class Model(models.Model):
    """SQLAlchemy model."""

    id: typing.Optional[int]

    @classmethod
    def from_dict(cls, **kwargs: typing.Any) -> "Model":
        """Construct from a dictionary (eg. a POST payload)."""
        return super().from_dict(**kwargs)

    def to_dict(self) -> ModelDict:
        """Convert to a dictionary (eg. to send back for a GET request)."""
        return super().to_dict()
''',
        ),
        (
            [
                ({"properties": {"id": {"type": "integer"}}}, "Model1"),
                ({"properties": {"id": {"type": "string"}}}, "Model2"),
            ],
            f'''{DOCSTRING}
# pylint: disable=no-member,useless-super-delegation

import typing

from open_alchemy import models


class Model1Dict(typing.TypedDict, total=False):
    """TypedDict for properties that are not required."""

    id: typing.Optional[int]


class Model1(models.Model1):
    """SQLAlchemy model."""

    id: typing.Optional[int]

    @classmethod
    def from_dict(cls, **kwargs: typing.Any) -> "Model1":
        """Construct from a dictionary (eg. a POST payload)."""
        return super().from_dict(**kwargs)

    def to_dict(self) -> Model1Dict:
        """Convert to a dictionary (eg. to send back for a GET request)."""
        return super().to_dict()


class Model2Dict(typing.TypedDict, total=False):
    """TypedDict for properties that are not required."""

    id: typing.Optional[str]


class Model2(models.Model2):
    """SQLAlchemy model."""

    id: typing.Optional[str]

    @classmethod
    def from_dict(cls, **kwargs: typing.Any) -> "Model2":
        """Construct from a dictionary (eg. a POST payload)."""
        return super().from_dict(**kwargs)

    def to_dict(self) -> Model2Dict:
        """Convert to a dictionary (eg. to send back for a GET request)."""
        return super().to_dict()
''',
        ),
        (
            [({"properties": {LONG_NAME: {"type": "integer"}}}, "Model")],
            f'''{DOCSTRING}
# pylint: disable=no-member,useless-super-delegation

import typing

from open_alchemy import models


class ModelDict(typing.TypedDict, total=False):
    """TypedDict for properties that are not required."""

    extremely_long_name_that_will_cause_wrapping_aaaaaaaaaaaaaaaaaa: typing.Optional[
        int
    ]


class Model(models.Model):
    """SQLAlchemy model."""

    extremely_long_name_that_will_cause_wrapping_aaaaaaaaaaaaaaaaaa: typing.Optional[
        int
    ]

    @classmethod
    def from_dict(cls, **kwargs: typing.Any) -> "Model":
        """Construct from a dictionary (eg. a POST payload)."""
        return super().from_dict(**kwargs)

    def to_dict(self) -> ModelDict:
        """Convert to a dictionary (eg. to send back for a GET request)."""
        return super().to_dict()
''',
        ),
    ],
    ids=["single", "multiple", "black formatting"],
)
@pytest.mark.models_file
def test_integration(schemas, expected_source):
    """
    GIVEN schema and name
    WHEN schema is added to the models file and the models file is generated
    THEN the models source code is returned.
    """
    models = models_file.ModelsFile()
    for schema, name in schemas:
        models.add_model(schema=schema, name=name)
    source = models.generate_models()

    assert source == expected_source
