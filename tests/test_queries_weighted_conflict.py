from deontic_reasoner.models import HardConstraint, Rule
from deontic_reasoner.queries import is_permitted

# "sent" and "not_sent" are independent atoms in this framework (no logical negation), so
# without something forcing exclusivity, both rules below could be satisfied
# simultaneously (sent=True *and* not_sent=True), which would make is_permitted return
# True even in the "external recipient" case — silently defeating the scenario this test
# is meant to demonstrate. The hard constraint below is what makes the trade-off genuine.
_DEFAULT_SEND = Rule(body=frozenset(), head=frozenset({"sent"}), weight=1.0)
_EXTERNAL_PROHIBITION = Rule(
    body=frozenset({"external_recipient"}), head=frozenset({"not_sent"}), weight=10.0
)
_EXCLUSIVITY = HardConstraint(forbidden=frozenset({"sent", "not_sent"}))
_RULES = [_DEFAULT_SEND, _EXTERNAL_PROHIBITION]


def test_permitted_by_default_when_recipient_is_internal():
    assert is_permitted(frozenset({"sent"}), frozenset(), _RULES, hard_constraints=[_EXCLUSIVITY]) is True


def test_forbidden_when_recipient_is_external_and_prohibition_outweighs_default():
    given = frozenset({"external_recipient"})
    assert is_permitted(frozenset({"sent"}), given, _RULES, hard_constraints=[_EXCLUSIVITY]) is False


def test_result_is_a_plain_boolean_no_conflict_explanation_object():
    result = is_permitted(frozenset({"sent"}), frozenset(), _RULES, hard_constraints=[_EXCLUSIVITY])
    assert isinstance(result, bool)
