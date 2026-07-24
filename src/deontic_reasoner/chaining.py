"""Forward-chaining fixed-point loop — the integration point wrapping the query engine.

Each iteration grounds every norm and delegation fact currently known, then applies every
power exercise against the norms known at the *start* of that iteration, before any norm
added by this same iteration's own power exercises exists. This defers a newly-exercised
norm's own correlative grounding to the next iteration, making genuine multi-round
convergence an observable property of the loop rather than a single-pass shortcut.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from deontic_reasoner.delegation import atom_for_delegation, exercise_power, ground_delegation
from deontic_reasoner.grounding import ground_norm
from deontic_reasoner.models import Atom, Norm, Rule

PowerExercise = tuple[str, Mapping[str, object]]
Delegation = tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class ChainResult:
    """The outcome of a `forward_chain` run.

    :param norms: every norm known once the loop converged, keyed by ``Norm.id``
    :param facts: every atom known to hold: each norm's own atom plus each delegation's atom
    :param rules: every correlative/obligation rule derived from the known norms and
        delegation facts
    :param iterations: how many iterations the loop actually ran before converging
    """

    norms: dict[str, Norm]
    facts: frozenset[Atom]
    rules: tuple[Rule, ...]
    iterations: int


class ForwardChainTimeout(Exception):
    """Raised when the loop still has genuinely new output after ``max_iterations`` rounds."""


def _rule_sort_key(rule: Rule) -> tuple[tuple[Atom, ...], tuple[Atom, ...], float]:
    return tuple(sorted(rule.body)), tuple(sorted(rule.head)), rule.weight


def forward_chain(
    norms: Mapping[str, Norm],
    delegations: Iterable[Delegation] = frozenset(),
    power_exercises: Iterable[PowerExercise] = (),
    max_iterations: int = 1000,
) -> ChainResult:
    """Forward-chain norms, delegation facts, and power exercises to a fixed point.

    :param norms: the initially-known norms, keyed by ``Norm.id``
    :param delegations: ``(delegator, delegatee, norm_id)`` facts to ground every iteration
    :param power_exercises: ``(power_norm_id, kwargs)`` pairs; ``kwargs`` is passed to
        :func:`~deontic_reasoner.delegation.exercise_power` as its keyword arguments beyond
        ``power_norm``. A ``power_norm_id`` absent from the currently-known norms derives
        nothing for that entry, rather than raising
    :param max_iterations: the round cap; exceeding it while output is still growing raises
        :class:`ForwardChainTimeout`
    :return: a :class:`ChainResult` once an iteration adds no genuinely new norm
    :raises ForwardChainTimeout: if ``max_iterations`` rounds all still derive a new norm
    """
    delegations = list(delegations)
    power_exercises = list(power_exercises)
    current_norms: dict[str, Norm] = dict(norms)

    for iteration in range(1, max_iterations + 1):
        facts: set[Atom] = set()
        rules: list[Rule] = []

        for norm in current_norms.values():
            atom, rule = ground_norm(norm)
            facts.add(atom)
            if rule is not None:
                rules.append(rule)

        for delegator, delegatee, norm_id in delegations:
            facts.add(atom_for_delegation(delegator, delegatee, norm_id))
            rules.extend(ground_delegation(delegator, delegatee, norm_id))

        new_norms: dict[str, Norm] = {}
        for power_norm_id, kwargs in power_exercises:
            power_norm = current_norms.get(power_norm_id)
            if power_norm is None:
                continue
            new_norm = exercise_power(power_norm, **kwargs)
            if new_norm.id not in current_norms:
                new_norms[new_norm.id] = new_norm

        if not new_norms:
            sorted_rules = tuple(sorted(rules, key=_rule_sort_key))
            return ChainResult(
                norms=current_norms, facts=frozenset(facts), rules=sorted_rules, iterations=iteration
            )

        if iteration == max_iterations:
            raise ForwardChainTimeout(f"forward_chain did not converge within {max_iterations} iterations")

        current_norms = {**current_norms, **new_norms}

    raise ForwardChainTimeout(f"forward_chain did not converge within {max_iterations} iterations")
