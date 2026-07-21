"""JSON round-trip helpers for the core dataclasses and :data:`World`.

Every core dataclass converts to and from plain JSON-compatible data via
:func:`to_dict`/:func:`from_dict` — ``frozenset`` fields as sorted lists, enum fields as
their ``.value``, and ``datetime`` fields via ``isoformat()`` — with no custom binary
format, per Requirements.md FR 15.
"""

import dataclasses
import typing
from datetime import datetime
from enum import Enum

from deontic_reasoner.models import World


def to_dict(obj: object) -> dict[str, object]:
    """Convert a core dataclass instance into a plain, JSON-serializable dict.

    :param obj: a dataclass instance (e.g. :class:`Rule`, :class:`HardConstraint`,
        :class:`Norm`)
    :return: a dict with every ``frozenset`` field as a sorted list, every enum field as
        its ``.value``, and every ``datetime`` field as an ISO-8601 string
    """
    result: dict[str, object] = {}
    for field in dataclasses.fields(obj):
        value = getattr(obj, field.name)
        if isinstance(value, frozenset):
            result[field.name] = sorted(value)
        elif isinstance(value, Enum):
            result[field.name] = value.value
        elif isinstance(value, datetime):
            result[field.name] = value.isoformat()
        else:
            result[field.name] = value
    return result


def _unwrap_optional(field_type: type) -> type:
    """Strip a ``| None`` union down to its single remaining type, if present.

    :param field_type: the field's declared type, possibly ``X | None``
    :return: ``X`` if ``field_type`` was ``X | None``; ``field_type`` unchanged otherwise
    """
    if typing.get_origin(field_type) is typing.Union:
        args = [arg for arg in typing.get_args(field_type) if arg is not type(None)]
        if len(args) == 1:
            return args[0]
    return field_type


def from_dict[T](cls: type[T], data: dict[str, object]) -> T:
    """Reconstruct a core dataclass instance from a dict produced by :func:`to_dict`.

    :param cls: the dataclass type to reconstruct (e.g. :class:`Rule`, :class:`Norm`)
    :param data: a dict shaped like :func:`to_dict`'s output for ``cls``
    :return: an instance of ``cls`` equal to the one ``to_dict`` was originally given
    """
    kwargs: dict[str, object] = {}
    for field in dataclasses.fields(cls):
        raw = data[field.name]
        field_type = _unwrap_optional(field.type)
        if raw is None:
            kwargs[field.name] = None
        elif typing.get_origin(field_type) is frozenset:
            kwargs[field.name] = frozenset(raw)
        elif isinstance(field_type, type) and issubclass(field_type, Enum):
            kwargs[field.name] = field_type(raw)
        elif field_type is datetime:
            kwargs[field.name] = datetime.fromisoformat(raw)
        else:
            kwargs[field.name] = raw
    return cls(**kwargs)


def world_to_list(world: World) -> list[str]:
    """Convert a :data:`World` into a sorted, JSON-serializable list of atoms.

    :param world: the world to convert
    :return: a sorted list of the atoms true at ``world``
    """
    return sorted(world)


def world_from_list(data: list[str]) -> World:
    """Reconstruct a :data:`World` from a list produced by :func:`world_to_list`.

    :param data: a list of atoms, as produced by :func:`world_to_list`
    :return: the equivalent :data:`World`
    """
    return frozenset(data)
