"""Autogenerated SQLAlchemy models based on OpenAlchemy models."""
# pylint: disable=no-member,super-init-not-called,unused-argument

import typing

import sqlalchemy
from sqlalchemy import orm

from open_alchemy import models


class RefEmployeeDict(typing.TypedDict, total=False):
    """TypedDict for properties that are not required."""

    id: typing.Optional[int]
    name: typing.Optional[str]
    division: typing.Optional[str]


class TRefEmployee(typing.Protocol):
    """
    SQLAlchemy model protocol.

    Person that works for a company.

    Attrs:
        id: Unique identifier for the employee.
        name: The name of the employee.
        division: The part of the company the employee works in.

    """

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    id: typing.Optional[int]
    name: typing.Optional[str]
    division: typing.Optional[str]

    def __init__(
        self,
        id: typing.Optional[int] = None,
        name: typing.Optional[str] = None,
        division: typing.Optional[str] = None,
    ) -> None:
        """
        Construct.

        Args:
            id: Unique identifier for the employee.
            name: The name of the employee.
            division: The part of the company the employee works in.

        """
        ...

    @classmethod
    def from_dict(
        cls,
        id: typing.Optional[int] = None,
        name: typing.Optional[str] = None,
        division: typing.Optional[str] = None,
    ) -> "TRefEmployee":
        """
        Construct from a dictionary (eg. a POST payload).

        Args:
            id: Unique identifier for the employee.
            name: The name of the employee.
            division: The part of the company the employee works in.

        Returns:
            Model instance based on the dictionary.

        """
        ...

    @classmethod
    def from_str(cls, value: str) -> "TRefEmployee":
        """
        Construct from a JSON string (eg. a POST payload).

        Returns:
            Model instance based on the JSON string.

        """
        ...

    def to_dict(self) -> RefEmployeeDict:
        """
        Convert to a dictionary (eg. to send back for a GET request).

        Returns:
            Dictionary based on the model instance.

        """
        ...

    def to_str(self) -> str:
        """
        Convert to a JSON string (eg. to send back for a GET request).

        Returns:
            JSON string based on the model instance.

        """
        ...


RefEmployee: TRefEmployee = models.RefEmployee  # type: ignore
