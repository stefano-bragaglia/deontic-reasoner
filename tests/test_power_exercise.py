from deontic_reasoner.delegation import exercise_power
from deontic_reasoner.grounding import ground_norm
from deontic_reasoner.models import Norm, Relation

_POWER_NORM = Norm(
    id="p1",
    relation=Relation.POWER,
    subject="Orchestrator",
    action="grant",
    resource="SubAgent.permissions",
    counterparty="SubAgent",
)


def test_exercise_power_returns_a_norm_with_the_given_fields():
    new_norm = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="read", resource="R2"
    )
    assert new_norm.subject == "SubAgent"
    assert new_norm.relation == Relation.PRIVILEGE
    assert new_norm.action == "read"
    assert new_norm.resource == "R2"
    assert new_norm.counterparty is None


def test_exercise_power_id_is_deterministic():
    first = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="read", resource="R2"
    )
    second = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="read", resource="R2"
    )
    assert first.id == second.id


def test_exercise_power_called_twice_with_identical_arguments_returns_equal_norms():
    first = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="read", resource="R2"
    )
    second = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="read", resource="R2"
    )
    assert first == second


def test_exercise_power_id_differs_for_different_arguments():
    a = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="read", resource="R2"
    )
    b = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="write", resource="R2"
    )
    assert a.id != b.id


def test_exercised_norm_is_valid_input_to_ground_norm():
    new_norm = exercise_power(
        _POWER_NORM, subject="SubAgent", relation=Relation.PRIVILEGE, action="read", resource="R2"
    )
    atom, rule = ground_norm(new_norm)
    assert atom
    assert rule is None


def test_immunity_norm_from_ground_norm_produces_atom_and_disability_rule():
    immunity_norm = exercise_power(
        _POWER_NORM,
        subject="AuditAgent",
        relation=Relation.IMMUNITY,
        action="write",
        resource="audit-log",
        counterparty="Orchestrator",
    )
    atom, rule = ground_norm(immunity_norm)
    assert atom
    assert rule is not None
    (head_atom,) = rule.head
    assert "disability" in head_atom


def test_exercise_power_succeeds_unconditionally_despite_an_existing_immunity_norm():
    immunity_norm = exercise_power(
        _POWER_NORM,
        subject="AuditAgent",
        relation=Relation.IMMUNITY,
        action="write",
        resource="audit-log",
        counterparty="Orchestrator",
    )
    assert immunity_norm is not None

    revoking_norm = exercise_power(
        _POWER_NORM,
        subject="Orchestrator",
        relation=Relation.POWER,
        action="revoke",
        resource="audit-log",
        counterparty="AuditAgent",
    )
    assert revoking_norm is not None
