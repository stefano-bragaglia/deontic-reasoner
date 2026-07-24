from dataclasses import replace

from deontic_reasoner.grounding import ground_norm
from deontic_reasoner.models import Norm, Relation
from deontic_reasoner.queries import is_obligatory

# §14.2 adaptation: proves grounding a RIGHT norm produces a genuinely *directed* obligation
# — the counterparty's duty, not a reflexive duty on the right-holder's own subject.
_NORM = Norm(
    id="n1",
    relation=Relation.RIGHT,
    subject="FileAgent",
    action="write",
    resource="/out/report.csv",
    counterparty="filesystem",
)


def test_duty_is_obligatory_when_the_norms_own_atom_holds():
    atom, rule = ground_norm(_NORM)
    (duty_atom,) = rule.head
    assert is_obligatory(frozenset({duty_atom}), frozenset({atom}), [rule]) is True


def test_duty_is_not_obligatory_without_the_norms_own_atom():
    _, rule = ground_norm(_NORM)
    (duty_atom,) = rule.head
    assert is_obligatory(frozenset({duty_atom}), frozenset(), [rule]) is False


def test_duty_atom_is_built_from_counterparty_not_subject():
    _, rule = ground_norm(_NORM)
    (duty_atom,) = rule.head

    wrong_norm = replace(_NORM, counterparty=_NORM.subject)
    _, wrong_rule = ground_norm(wrong_norm)
    (wrong_duty_atom,) = wrong_rule.head

    assert duty_atom != wrong_duty_atom
