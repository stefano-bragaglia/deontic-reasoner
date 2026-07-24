from deontic_reasoner.chaining import forward_chain
from deontic_reasoner.delegation import exercise_power
from deontic_reasoner.grounding import atom_for_norm
from deontic_reasoner.models import Norm, Relation

# §14.6 / multi-round convergence, end-to-end: a POWER norm's exercise derives a new RIGHT
# norm; that new norm's own correlative duty rule can only be grounded on a *later*
# iteration, since grounding runs on the norms known at the start of each iteration, before
# that same iteration's power exercises add anything new.
_POWER_NORM = Norm(
    id="p1",
    relation=Relation.POWER,
    subject="Orchestrator",
    action="grant",
    resource="SubAgent.permissions",
    counterparty="SubAgent",
)
_EXERCISE_KWARGS = {
    "subject": "SubAgent",
    "relation": Relation.RIGHT,
    "action": "read",
    "resource": "R2",
    "counterparty": "ResourceOwner",
}


def test_power_exercise_norm_is_grounded_on_a_later_iteration():
    power_exercises = (("p1", _EXERCISE_KWARGS),)
    result = forward_chain(norms={"p1": _POWER_NORM}, power_exercises=power_exercises)

    new_norm_id = exercise_power(_POWER_NORM, **_EXERCISE_KWARGS).id
    assert new_norm_id in result.norms
    assert result.iterations >= 2

    new_norm = result.norms[new_norm_id]
    atom = atom_for_norm(new_norm)
    matching = [rule for rule in result.rules if rule.body == frozenset({atom})]
    assert len(matching) == 1
    (duty_atom,) = matching[0].head
    assert "duty" in duty_atom
