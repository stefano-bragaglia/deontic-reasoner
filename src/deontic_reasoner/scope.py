"""Predicate registry and condition evaluation — the only path a :class:`Norm`'s condition is evaluated through.

Resolving ``Norm.condition`` through a fixed, engine-owned registry (never ``eval()``,
``exec()``, or ``ast.literal_eval`` on data that traces back to an external agent request)
is what makes it structurally impossible to execute arbitrary code via a condition name.
"""

from collections.abc import Callable, Mapping
from datetime import datetime

from deontic_reasoner.models import Norm

PredicateRegistry = Mapping[str, Callable[[Norm, Mapping[str, object]], bool]]


class UnknownPredicateError(Exception):
    """Raised when a norm's condition name is absent from the predicate registry."""


def evaluate_condition(norm: Norm, request: Mapping[str, object], registry: PredicateRegistry) -> bool:
    """Resolve ``norm.condition`` through ``registry`` and evaluate it against ``request``.

    :param norm: the norm whose condition is being evaluated
    :param request: the context the registered predicate evaluates the condition against
    :param registry: the fixed, engine-owned mapping from condition name to callable
    :return: ``True`` if ``norm.condition`` is ``None``; otherwise the result of
        ``registry[norm.condition](norm, request)``
    :raises UnknownPredicateError: if ``norm.condition`` is set but absent from ``registry``
    """
    if norm.condition is None:
        return True
    predicate = registry.get(norm.condition)
    if predicate is None:
        raise UnknownPredicateError(norm.condition)
    return predicate(norm, request)


def scope_matches(
    norm: Norm,
    request: Mapping[str, object],
    registry: PredicateRegistry,
    now: datetime,
) -> bool:
    """Check whether ``norm`` applies at ``now`` to ``request``, re-evaluated fresh each call.

    :param norm: the norm whose scope is being checked
    :param request: the context passed through to :func:`evaluate_condition`
    :param registry: the fixed, engine-owned predicate registry
    :param now: the time to check ``norm``'s temporal bounds against
    :return: ``True`` iff ``now`` falls within ``norm``'s ``valid_from``/``valid_until`` bounds
        (inclusive on both ends) and :func:`evaluate_condition` also holds (which may itself
        raise :class:`UnknownPredicateError`)
    """
    if norm.valid_from is not None and now < norm.valid_from:
        return False
    if norm.valid_until is not None and now > norm.valid_until:
        return False
    return evaluate_condition(norm, request, registry)
