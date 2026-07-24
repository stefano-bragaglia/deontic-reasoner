from deontic_reasoner.delegation import atom_for_delegation
from deontic_reasoner.models import Rule
from deontic_reasoner.queries import is_obligatory

# §14.5 adaptation: a broken delegation chain reads as `is_obligatory` for the downstream
# permission going True -> False, not `is_permitted` going to False (an atom nothing
# constrains is permitted by default in this framework) — this is the correct way to model
# "the permission fails to derive" here, per the story's own edge-case note.
_HOP1_DELEGATION = atom_for_delegation("Orchestrator", "Supervisor", "n1")
_HOP2_DELEGATION = atom_for_delegation("Supervisor", "DataAgent", "n2")
_HOP1_VALID_LINK = "valid_link:Orchestrator:Supervisor:n1"
_HOP2_VALID_LINK = "valid_link:Supervisor:DataAgent:n2"
_PERMISSION_ATOM = "permission:DataAgent:read:/data"

_CHAIN_RULE = Rule(
    body=frozenset({_HOP1_DELEGATION, _HOP1_VALID_LINK, _HOP2_DELEGATION, _HOP2_VALID_LINK}),
    head=frozenset({_PERMISSION_ATOM}),
    weight=10.0,
)


def test_permission_is_obligatory_when_every_hops_valid_link_is_present():
    given = frozenset({_HOP1_DELEGATION, _HOP1_VALID_LINK, _HOP2_DELEGATION, _HOP2_VALID_LINK})
    assert is_obligatory(frozenset({_PERMISSION_ATOM}), given, [_CHAIN_RULE]) is True


def test_permission_is_not_obligatory_when_one_hops_valid_link_is_missing():
    given = frozenset({_HOP1_DELEGATION, _HOP2_DELEGATION, _HOP2_VALID_LINK})
    assert is_obligatory(frozenset({_PERMISSION_ATOM}), given, [_CHAIN_RULE]) is False
