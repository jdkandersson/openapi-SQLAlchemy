"""Autogenerated SQLAlchemy models based on OpenAlchemy models."""
# pylint: disable=no-member,super-init-not-called,unused-argument

import typing

import sqlalchemy
from sqlalchemy import orm

from open_alchemy import models


class _EmployeeDictBase(typing.TypedDict, total=True):
    """TypedDict for properties that are required."""

    name: str
    division: str


class EmployeeDict(_EmployeeDictBase, total=False):
    """TypedDict for properties that are not required."""

    id: int
    salary: typing.Optional[float]


class TEmployee(typing.Protocol):
    """
    SQLAlchemy model protocol.

    Person that works for a company.

    Attrs:
        id: Unique identifier for the employee.
        name: The name of the employee.
        division: The part of the company the employee works in.
        salary: The amount of money the employee is paid.

    """

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    id: "sqlalchemy.Column[int]"
    name: "sqlalchemy.Column[str]"
    division: "sqlalchemy.Column[str]"
    salary: "sqlalchemy.Column[typing.Optional[float]]"

    def __init__(
        self,
        name: str,
        division: str,
        id: typing.Optional[int] = None,
        salary: typing.Optional[float] = None,
    ) -> None:
        """
        Construct.

        Args:
            id: Unique identifier for the employee.
            name: The name of the employee.
            division: The part of the company the employee works in.
            salary: The amount of money the employee is paid.

        """
        ...

    @classmethod
    def from_dict(
        cls,
        name: str,
        division: str,
        id: typing.Optional[int] = None,
        salary: typing.Optional[float] = None,
    ) -> "TEmployee":
        """
        Construct from a dictionary (eg. a POST payload).

        Args:
            id: Unique identifier for the employee.
            name: The name of the employee.
            division: The part of the company the employee works in.
            salary: The amount of money the employee is paid.

        Returns:
            Model instance based on the dictionary.

        """
        ...

    @classmethod
    def from_str(cls, value: str) -> "TEmployee":
        """
        Construct from a JSON string (eg. a POST payload).

        Returns:
            Model instance based on the JSON string.

        """
        ...

    def to_dict(self) -> EmployeeDict:
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


Employee: typing.Type[TEmployee] = models.Employee  # type: ignore
