from deontic_reasoner.chaining import forward_chain
from deontic_reasoner.delegation import atom_for_delegation
from deontic_reasoner.queries import is_obligatory

# §14.3, end-to-end: a bare delegation fact, with no norms and no power exercises, must be
# enough for forward_chain to derive audit and liability as genuinely obligatory duties.
_DELEGATOR = "Orchestrator"
_DELEGATEE = "DataAgent"
_NORM_ID = "n1"


def test_audit_and_liability_are_obligatory_given_only_a_delegation_fact():
    delegations = frozenset({(_DELEGATOR, _DELEGATEE, _NORM_ID)})
    result = forward_chain(norms={}, delegations=delegations)

    delegation_atom = atom_for_delegation(_DELEGATOR, _DELEGATEE, _NORM_ID)
    assert delegation_atom in result.facts

    given = frozenset({delegation_atom})
    matching_heads = [
        head
        for rule in result.rules
        if rule.body == frozenset({delegation_atom})
        for head in rule.head
    ]
    assert len(matching_heads) == 2  # audit and liability
    for head_atom in matching_heads:
        assert is_obligatory(frozenset({head_atom}), given, result.rules) is True
