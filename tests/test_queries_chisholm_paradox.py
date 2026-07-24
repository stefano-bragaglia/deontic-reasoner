from deontic_reasoner.models import Rule
from deontic_reasoner.queries import is_obligatory

# The historical regression test for the exact failure mode dyadic obligation exists to
# prevent: a material-conditional treatment of "if not requested, ought to flag" would
# either derive a contradiction or make the antecedent itself a consequence of the rule
# set. The dyadic representation (the condition as a plain rule body, per this
# framework's design) must avoid both.
_RULES = [
    Rule(body=frozenset(), head=frozenset({"request_approval"}), weight=5.0),
    Rule(body=frozenset({"requested"}), head=frozenset({"log_request"}), weight=5.0),
    Rule(body=frozenset({"not_requested"}), head=frozenset({"flag_unauthorized"}), weight=5.0),
]
_GIVEN = frozenset({"not_requested"})


def test_flag_unauthorized_is_obligatory_when_not_requested():
    assert is_obligatory(frozenset({"flag_unauthorized"}), _GIVEN, _RULES) is True


def test_log_request_is_not_obligatory_when_not_requested():
    assert is_obligatory(frozenset({"log_request"}), _GIVEN, _RULES) is False


def test_no_contradiction_both_obligations_are_never_asserted_together():
    flag_obligatory = is_obligatory(frozenset({"flag_unauthorized"}), _GIVEN, _RULES)
    log_obligatory = is_obligatory(frozenset({"log_request"}), _GIVEN, _RULES)
    assert not (flag_obligatory and log_obligatory)
