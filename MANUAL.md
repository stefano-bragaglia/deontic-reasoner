# deontic-reasoner — User Manual

A Python library implementing a **semantic reasoner for AI agent permissions**: it answers
"is this obligatory?" and "is this permitted?" questions about agents, actions, and resources,
grounded in a real deontic-logic framework instead of ad-hoc, path-based access control rules.

This manual covers what the reasoner is, how to install it, the modeling language it exposes,
worked examples for every feature, and where to look when something doesn't behave as expected.

---

## Table of contents

1. [What is a Hohfeldian + deontic reasoner?](#1-what-is-a-hohfeldian--deontic-reasoner)
2. [Getting started](#2-getting-started) (system requirements, installation, quick start)
3. [Core public API](#3-core-public-api)
4. [The modeling language](#4-the-modeling-language)
5. [Step-by-step workflows](#5-step-by-step-workflows)
6. [Settings and configuration](#6-settings-and-configuration)
7. [Troubleshooting](#7-troubleshooting)
8. [FAQ](#8-faq)
9. [Glossary and API quick-reference](#9-glossary-and-api-quick-reference)

---

## 1. What is a Hohfeldian + deontic reasoner?

### 1.1 The problem with a flat "is this allowed" boolean

Most access-control systems answer one flat question: *is agent X allowed to do Y?* That
collapses two different things a real permission system needs to distinguish:

- **Directed obligations** — a duty is always owed *by* someone *to* someone. "FileAgent must
  write the report" is incomplete without saying *to whom* that duty is owed (its counterparty).
- **Conflicting norms** — real rule sets disagree with each other (a default policy says "send
  the file"; a compliance policy says "don't send it externally"). A flat boolean check has no
  principled way to decide which wins, short of ad-hoc priority hacks.

This reasoner addresses both by combining two ideas:

**Hohfeldian relations.** The legal theorist Wesley Hohfeld (1913) analyzed rights talk into
four correlative pairs. This project implements the four *first-party* incidents, each of
which grounds a correlative duty on the other party:

| Your incident | Your counterparty's correlative |
|---|---|
| `PRIVILEGE` — you may do X (no duty not to) | *(no correlative modeled this iteration)* |
| `RIGHT` — you are owed X | `duty` — your counterparty must provide X |
| `POWER` — you can change a normative relation (grant, revoke, waive...) | `liability` — your counterparty is subject to that change |
| `IMMUNITY` — you cannot have a relation changed against you | `disability` — your counterparty cannot change it |

**Preferential (betterness-ordering) dyadic deontic logic.** Rather than one obligation
operator `O(q)` ("q ought to be the case", full stop), the reasoner uses Hansson's *dyadic*
operator `O(q | p)` ("given p, q ought to be the case") combined with Kraus–Lehmann–Magidor
(KLM) preferential semantics: `O(q | p)` holds iff every *most-preferred* world satisfying `p`
also satisfies `q`. "Most preferred" is computed by ranking candidate worlds on how much
violated-rule weight they carry — the world violating the fewest/least-important norms wins.
Conflict resolution falls directly out of this ordering: no separate conflict-detection engine
is layered on top.

### 1.2 What this addresses

| Anomaly | Addressed? | How |
|---|---|---|
| **Chisholm's contrary-to-duty paradox** (1963) | ✅ Yes | Chisholm's puzzle breaks a *monadic*, material-conditional reading of obligation: `p → O(q)` is vacuously true whenever `p` is false, which lets you derive nonsense once anything at all is forbidden. Because every conditional obligation here is represented as a plain rule `(body → head, weight)` evaluated against a candidate world — never as a material conditional formula — the vacuous-truth failure mode cannot arise. §5.2 below walks through the actual regression scenario. |
| **Conflicting/competing norms** | ✅ Yes | Two rules that can't both be satisfied are resolved by `best_worlds`: the candidate world with the lower total violated weight (under `WEIGHTED_COUNT`, the default criterion) wins. This replaces what a combining-algorithm engine (deny-overrides, permit-overrides, priority-weighted...) would otherwise need bespoke logic for. §5.3 walks through a worked example. |
| **Deontic "explosion" from an unrelated conflict** | ✅ Yes | In classical systems, once a rule set contains *any* unresolvable conflict, some formalizations let that conflict make anything derivable. Here containment is structural: weighted-count total violated weight is additive across atom-disjoint rule groups, so a conflicting pair over one topic can never affect an unrelated query. §5.4 demonstrates this directly. |
| **Directed ("to whom") obligations** | ✅ Yes | This is exactly what the Hohfeldian layer (§1.1) adds on top of the propositional dyadic core: `ground_norm` turns a `RIGHT`/`POWER`/`IMMUNITY` norm into a rule whose head names the *counterparty's* correlative atom, not the right-holder's own. §5.5. |
| **Delegated oversight duties left unstated** | ✅ Yes | A single `delegated(delegatee, delegator, norm)` fact automatically derives the delegator's audit, revoke-on-violation, and liability duties via the ordinary rule mechanism — no hand-authored oversight rules needed. §5.6. |

### 1.3 What this does *not* address

Be precise about the reasoner's actual boundaries — these are deliberate scope decisions, not
bugs:

- **No SAT-based conflict explanation.** An earlier design used SAT solving with unsat-core
  extraction to explain *which specific norms conflict*. That machinery was dropped in favor of
  `best_worlds` — you get the *right query answer*, but not a structured "here is why these two
  rules disagree" object. `is_obligatory`/`is_permitted` return a plain `bool`.
- **No delegation-chain cycle detection.** A broken link in a delegation chain (a missing
  `valid_link` fact) correctly denies the downstream permission (§5.6), but nothing checks a
  delegation chain for *cycles* (A delegates to B delegates to... back to A). That was a
  `graphlib`-based feature in an earlier, superseded design and is out of scope here.
- **`IMMUNITY` is purely representational.** An `IMMUNITY` norm can be created, grounded, and
  forward-chained like any other Hohfeldian relation — but it has no behavioral teeth yet. It
  does not actually block a power's exercise or a revocation. Giving it real short-circuiting
  behavior is explicitly deferred to a later iteration.
- **`forward_chain` is bounded, not a general Datalog engine.** It raises `ForwardChainTimeout`
  once `max_iterations` is exhausted while output is still growing, but there is no cycle
  analysis — just a round cap.
- **No logical connectives beyond conjunction.** `Rule.body`/`Rule.head` are conjunctions of
  atoms (a `frozenset[str]`) — there is no disjunction or logical negation operator. "Not X" is
  modeled as a *separate*, independently-true atom (e.g. `not_sent` alongside `sent`), which
  means two atoms that look like negations of each other are **not** automatically mutually
  exclusive unless you add a `HardConstraint` forcing it (§5.3, §7 "Troubleshooting").
  Because of this, classical deontic paradoxes that hinge on propositional connectives — Ross's
  paradox (`O(p)` licensing `O(p ∨ q)`), the free-choice permission paradox, the Good Samaritan
  paradox — don't arise in quite their usual form here, but they also aren't *solved*: the
  reasoner simply has no disjunction/negation operator for them to be stated against. If your
  use case needs full propositional deontic logic with those connectives, this library isn't
  that.
- **No persistence, CLI, or server.** This is an embeddable library only. You get back plain
  Python objects (`bool`, `set[World]`, dataclasses); wiring it into a service, database, or
  MCP tool-authorization layer is your own application's job.
- **`Rule.weight`/`Norm.priority`-equivalent values are not access-controlled by the engine
  itself.** Nothing stops a caller from asserting an inflated `weight` to out-rank a
  restriction. The reasoner assumes whatever stores/authors rules enforces that only the
  granting authority sets weight — never the rule's own subject-agent. See §6.3.

---

## 2. Getting started

### 2.1 System requirements

- **Python**: 3.14 or later.
- **Package manager**: [`uv`](https://docs.astral.sh/uv/) (used for dependency resolution,
  the virtual environment, and running the test suite).
- **Dependencies**: none at runtime — the reasoner is standard-library only. `uv sync` pulls
  in `pytest`/`ruff`/`radon`/`pydoclint` as *development*-only dependencies; nothing extra
  ships with the library itself.
- **OS**: any platform `uv` and Python 3.14 support (macOS, Linux, Windows). No GPU, no
  minimum RAM/disk beyond what Python itself needs — the reasoner's memory use scales with the
  number of atoms in your rule set (see §6.4 on tractability), not with anything OS-specific.

### 2.2 Installation

The package is not yet published to PyPI (see the project's `Notes.md` for current publish
status). Until it is, install from source:

```bash
git clone https://github.com/stefano-bragaglia/deontic-reasoner.git
cd deontic-reasoner
uv sync
```

`uv sync` creates a local virtual environment (`.venv/`) and installs the package in editable
mode along with its dev dependencies.

**Verify the install:**

```bash
uv run python3 -c "from deontic_reasoner.queries import is_obligatory; print('ok')"
```

You should see `ok` printed with no errors. To run the full test suite (useful to confirm your
Python/`uv` versions are compatible):

```bash
uv run pytest
```

Once the package is published to PyPI, installing it into another project will be a plain:

```bash
pip install deontic-reasoner   # or: uv add deontic-reasoner
```

### 2.3 Quick start

The fastest way to see the reasoner answer a real question — a tenant obligated to pay rent,
and a hard constraint that makes eviction and rent-paying mutually exclusive:

```python
from deontic_reasoner.models import Rule, HardConstraint
from deontic_reasoner.queries import is_obligatory, is_permitted

rules = [
    Rule(head=frozenset({"pay_rent"}), weight=1.0, body=frozenset({"is_tenant"})),
    Rule(head=frozenset({"quiet_hours"}), weight=0.5),
]
constraints = [HardConstraint(forbidden=frozenset({"pay_rent", "evicted"}))]

is_obligatory(frozenset({"pay_rent"}), frozenset({"is_tenant"}), rules, constraints)  # True
is_permitted(frozenset({"evicted"}), frozenset({"is_tenant"}), rules, constraints)    # False
```

Read this as: *given* the tenant is a tenant, paying rent *is obligatory* (every best world
satisfying `is_tenant` also satisfies `pay_rent`); being evicted at the same time *is not
permitted* (no best world satisfying `is_tenant` also satisfies `evicted`, because the hard
constraint rules out any world where `pay_rent` and `evicted` hold together).

---

## 3. Core public API

Everything you interact with lives under `deontic_reasoner.*`. There is no single top-level
namespace re-export yet (`deontic_reasoner/__init__.py` is currently just the package
docstring) — import from each submodule directly:

| Module | What it provides |
|---|---|
| `deontic_reasoner.models` | The data types: `Atom`, `World`, `Rule`, `HardConstraint`, `Relation`, `Norm`. |
| `deontic_reasoner.preference` | `violates`, `excludes`, `PreferenceCriterion`, `violated_rules`, `preferred`, `best_worlds`. |
| `deontic_reasoner.queries` | `is_obligatory`, `is_permitted` — the two query entry points most callers need. |
| `deontic_reasoner.grounding` | `atom_for_norm`, `ground_norm` — turn a Hohfeldian `Norm` into rules the core understands. |
| `deontic_reasoner.scope` | `PredicateRegistry`, `UnknownPredicateError`, `evaluate_condition`, `scope_matches`. |
| `deontic_reasoner.delegation` | `atom_for_delegation`, `atom_for_violation`, `ground_delegation`, `exercise_power`, `delegate_with_narrowing`. |
| `deontic_reasoner.chaining` | `ChainResult`, `ForwardChainTimeout`, `forward_chain`. |
| `deontic_reasoner.serialization` | `to_dict`, `from_dict`, `world_to_list`, `world_from_list`. |

---

## 4. The modeling language

### 4.1 Atoms and worlds

```python
Atom = str
World = frozenset[str]
```

An **atom** is just a string naming a ground proposition (`"sent"`, `"is_tenant"`,
`"norm:n1"`). A **world** is the set of atoms true at that world — a finite truth assignment,
not a general possible-worlds Kripke frame. There is no built-in negation: if you need "not
sent" as a distinct fact, model it as its own atom (`"not_sent"`) and see §7 for the exclusivity
trap this creates.

### 4.2 Rules — the norm representation

```python
@dataclass(frozen=True, slots=True)
class Rule:
    head: frozenset[Atom]      # the conjunction that ought to hold
    weight: float              # cost, under weighted-count preference, of violating this rule
    body: frozenset[Atom] = frozenset()   # the conjunction that must hold for the rule to apply
```

A `Rule` reads as "if `body` holds, `head` ought to hold too" — a **defeasible**, weighted
conditional obligation, not a hard requirement. An empty `body` is vacuously satisfied by every
world, making the rule unconditional (a default). `violates(rule, world)` is `True` exactly
when `rule.body <= world and not rule.head <= world`.

### 4.3 Hard constraints — genuinely impossible states

```python
@dataclass(frozen=True, slots=True)
class HardConstraint:
    forbidden: frozenset[Atom]   # atoms that may never all be true together
```

Unlike a `Rule`, a `HardConstraint` doesn't just disprefer a world — it **excludes** it from
consideration entirely, regardless of how well that world otherwise satisfies every rule.
`excludes(constraint, world)` is `True` when every atom in `forbidden` is present in `world`.
Use this for states that are genuinely impossible (e.g. "sent and not-sent can never both be
true"), not merely undesirable ones — undesirable-but-possible belongs in a weighted `Rule`.

### 4.4 Preference criteria

```python
class PreferenceCriterion(Enum):
    SUBSET = auto()          # strict-subset comparison of violated-rule sets
    COUNT = auto()           # fewer violated rules wins
    WEIGHTED_COUNT = auto()  # lower total violated weight wins (default)
```

`preferred(world_a, world_b, rules, criterion)` asks "is `world_a` at least as preferred as
`world_b`?" `SUBSET` is the weakest — it leaves many world pairs incomparable (neither
dominates the other) since it's a strict-subset test, not a total order. `COUNT` is `SUBSET`'s
special case with uniform weight 1. `WEIGHTED_COUNT` is the only one of the three that reliably
*resolves* a genuine conflict between differently-important rules, and is the default
everywhere a `criterion` parameter is optional.

### 4.5 `best_worlds`, `is_obligatory`, `is_permitted`

```python
def best_worlds(
    antecedent: World, rules, hard_constraints=(), criterion=PreferenceCriterion.WEIGHTED_COUNT,
) -> set[World]: ...

def is_obligatory(b, given, rules, hard_constraints=(), criterion=...) -> bool: ...
def is_permitted(b, given, rules, hard_constraints=(), criterion=...) -> bool: ...
```

`best_worlds` computes the **maximal elements** of the preference preorder among candidate
worlds satisfying `antecedent` — a candidate stays in the result unless some *other* candidate
strictly dominates it. Enumeration is automatically scoped to the atoms actually mentioned in
`antecedent` or any rule's `body`/`head` (not every atom your program has ever used), so it
never blows up on an unrelated part of your vocabulary.

- `is_obligatory(b, given, ...)` — `True` iff `b` holds at **every** world in
  `best_worlds(given)`.
- `is_permitted(b, given, ...)` — `True` iff `b` holds at **some** world in
  `best_worlds(given)`.

**Vacuous truth on an empty result.** If `given` itself is unsatisfiable (every candidate world
gets excluded by a hard constraint), `best_worlds` returns the empty set. Universal
quantification over an empty set is vacuously `True`, so `is_obligatory` returns `True`;
existential quantification over an empty set is vacuously `False`, so `is_permitted` returns
`False`. This is standard classical-logic behavior, not a bug — see §7 if it surprises you.

### 4.6 Norms and Hohfeldian relations

```python
class Relation(StrEnum):
    PRIVILEGE = "privilege"
    RIGHT = "right"
    POWER = "power"
    IMMUNITY = "immunity"

@dataclass(frozen=True, slots=True)
class Norm:
    id: str
    relation: Relation
    subject: str
    action: str
    resource: str
    counterparty: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    condition: Atom | None = None
```

A `Norm` asserts one Hohfeldian incident. `ground_norm(norm)` (in `deontic_reasoner.grounding`)
converts it into `(atom_for_norm(norm), rule)`: an atom naming the norm itself
(`f"norm:{norm.id}"`), plus — for `RIGHT`/`POWER`/`IMMUNITY` norms with a `counterparty` — a
`Rule` whose body is the norm's own atom and whose head is the counterparty's correlative atom
(`duty:`/`liability:`/`disability:` prefixed). `PRIVILEGE` norms, and any norm with no
`counterparty`, ground to `(atom, None)` — no correlative rule.

### 4.7 Scope evaluation

```python
def scope_matches(norm: Norm, request: Mapping[str, object], registry: PredicateRegistry, now: datetime) -> bool: ...
```

Checks whether `norm` applies right now, to a concrete request. Two independent checks both
have to pass: `now` must fall within `[valid_from, valid_until]` (inclusive, either bound may
be `None` for unbounded), **and** `norm.condition` (if set) must evaluate to `True` through a
caller-supplied `registry` — a `dict` mapping condition names to
`Callable[[Norm, Mapping[str, object]], bool]`. This registry is the *only* path a condition is
ever evaluated through: there is no `eval()`/`exec()` anywhere in this reasoner, by design (see
§6.3).

### 4.8 Delegation and powers

```python
def ground_delegation(delegator, delegatee, norm_id, weight=OBLIGATION_WEIGHT) -> (Rule, Rule, Rule): ...
def exercise_power(power_norm, subject, relation, action, resource, counterparty=None, ...) -> Norm: ...
def delegate_with_narrowing(parent, subject, valid_from=None, valid_until=None, ...) -> Norm: ...
```

- `ground_delegation` turns a single `delegated(delegator, delegatee, norm_id)` fact into three
  rules — audit, dyadic revoke-on-violation, and liability — all firing off the delegation
  atom alone (revoke also requires a violation atom in its body, so it's conditional on an
  actual violation, not automatic).
- `exercise_power` constructs the new `Norm` a power's exercise brings into existence. Its
  `id` is a deterministic function of its arguments, so calling it twice with the same inputs
  is idempotent — safe to feed into `forward_chain` repeatedly.
- `delegate_with_narrowing` derives a delegatee's norm from a parent norm, automatically
  intersecting the temporal validity window so a re-delegated scope is never *wider* than the
  delegator's own.

### 4.9 Forward chaining

```python
def forward_chain(norms, delegations=(), power_exercises=(), max_iterations=1000) -> ChainResult: ...
```

Runs the "what new facts follow" loop wrapped around the query engine: each iteration grounds
every currently-known norm and delegation fact, then applies every `power_exercises` entry
against the norms known at the *start* of that iteration (so a norm created this round doesn't
get its own correlative grounded until next round — this is what makes genuine multi-round
convergence real). Stops the moment an iteration adds no genuinely new norm; raises
`ForwardChainTimeout` if `max_iterations` rounds all still grow the norm set.

### 4.10 JSON round-tripping

```python
def to_dict(obj) -> dict: ...
def from_dict(cls, data) -> T: ...
def world_to_list(world: World) -> list[str]: ...
def world_from_list(data: list[str]) -> World: ...
```

Every core dataclass (`Rule`, `HardConstraint`, `Norm`) round-trips through plain,
JSON-serializable dicts: `frozenset` fields become sorted lists, `Enum` fields become their
`.value`, `datetime` fields become ISO-8601 strings. No custom binary format.

---

## 5. Step-by-step workflows

Every example below was run against the actual library while writing this manual — the printed
output is real, not illustrative.

### 5.1 Basic obligation and permission (quick start, revisited)

See §2.3. The key habit to build: an obligation/permission query always needs `b` (what you're
asking about), `given` (the antecedent — what's already true), and the `rules`/
`hard_constraints` the world is evaluated against.

### 5.2 Chisholm's contrary-to-duty paradox

The classic 1963 puzzle: "it ought to be that a man goes to help his neighbor; it ought to be
that if he goes, he tells him he's coming; if he doesn't go, he ought not tell him." A
material-conditional reading of "ought" makes this either contradictory or lets the antecedent
itself become a derived consequence. Because every rule here is body/head, evaluated against
worlds — never a bare formula — this framework sidesteps the failure mode entirely:

```python
from deontic_reasoner.models import Rule
from deontic_reasoner.queries import is_obligatory

rules = [
    Rule(body=frozenset(), head=frozenset({"request_approval"}), weight=5.0),
    Rule(body=frozenset({"requested"}), head=frozenset({"log_request"}), weight=5.0),
    Rule(body=frozenset({"not_requested"}), head=frozenset({"flag_unauthorized"}), weight=5.0),
]
given = frozenset({"not_requested"})

is_obligatory(frozenset({"flag_unauthorized"}), given, rules)  # True
is_obligatory(frozenset({"log_request"}), given, rules)        # False
```

Given `not_requested`, flagging as unauthorized is obligatory, and logging the request is
*not* — the two contrary-to-duty branches never both fire, and neither derives the other.

### 5.3 Resolving a genuine conflict (weighted preference)

Two rules that can't both be satisfied — send by default, but don't send to an external
recipient. Because `sent`/`not_sent` are independent atoms (§4.1), a `HardConstraint` is what
makes this a genuine trade-off rather than "both rules satisfied for free":

```python
from deontic_reasoner.models import Rule, HardConstraint
from deontic_reasoner.queries import is_permitted

default_send = Rule(body=frozenset(), head=frozenset({"sent"}), weight=1.0)
external_prohibition = Rule(body=frozenset({"external_recipient"}), head=frozenset({"not_sent"}), weight=10.0)
exclusivity = HardConstraint(forbidden=frozenset({"sent", "not_sent"}))
rules = [default_send, external_prohibition]

is_permitted(frozenset({"sent"}), frozenset(), rules, hard_constraints=[exclusivity])                          # True
is_permitted(frozenset({"sent"}), frozenset({"external_recipient"}), rules, hard_constraints=[exclusivity])    # False
```

Internally (no `external_recipient`), sending is permitted by default. Once
`external_recipient` is given, the higher-weight prohibition (10.0 vs. 1.0) wins under
`WEIGHTED_COUNT`, and sending is no longer permitted. No conflict-explanation object is
returned — just the resolved `bool` (see §1.3).

### 5.4 Conflict containment (no "deontic explosion")

A conflicting rule pair over one topic must never leak into an unrelated query:

```python
from deontic_reasoner.models import Rule
from deontic_reasoner.queries import is_obligatory

conflicting_pair = [
    Rule(body=frozenset(), head=frozenset({"task1"}), weight=3.0),
    Rule(body=frozenset(), head=frozenset({"not_task1"}), weight=7.0),
]
unrelated = Rule(body=frozenset(), head=frozenset({"task2"}), weight=4.0)
rules = [*conflicting_pair, unrelated]

is_obligatory(frozenset({"task2"}), frozenset(), rules)  # True, regardless of which weight wins task1's conflict
```

This holds no matter how the `task1`/`not_task1` weights are arranged — `WEIGHTED_COUNT`'s
total is additive across atom-disjoint rule groups, so a `task1` conflict structurally cannot
touch a `task2` query.

### 5.5 Hohfeldian directed obligation

`FileAgent` holds a `RIGHT` to have `/out/report.csv` written, with `filesystem` as the
counterparty who owes the duty:

```python
from deontic_reasoner.models import Norm, Relation
from deontic_reasoner.grounding import ground_norm
from deontic_reasoner.queries import is_obligatory

norm = Norm(id="n1", relation=Relation.RIGHT, subject="FileAgent", action="write",
            resource="/out/report.csv", counterparty="filesystem")
atom, rule = ground_norm(norm)
# atom == "norm:n1"
# rule == Rule(body={"norm:n1"}, head={"duty:filesystem:write:/out/report.csv"}, weight=1000.0)

(duty_atom,) = rule.head
is_obligatory(frozenset({duty_atom}), frozenset({atom}), [rule])   # True  — norm holds, duty follows
is_obligatory(frozenset({duty_atom}), frozenset(), [rule])         # False — norm doesn't hold, no duty
```

The duty atom names `filesystem` (the counterparty), not `FileAgent` (the right-holder's own
subject) — this is what makes the obligation genuinely *directed*.

### 5.6 Scope evaluation (temporal validity)

A norm that's only valid for the next 24 hours:

```python
from datetime import datetime, timedelta
from deontic_reasoner.models import Norm, Relation
from deontic_reasoner.scope import scope_matches

t0 = datetime(2026, 1, 1)
norm = Norm(id="n2", relation=Relation.PRIVILEGE, subject="Agent", action="read",
            resource="/x", valid_until=t0 + timedelta(hours=24))

scope_matches(norm, {}, {}, now=t0 + timedelta(hours=1))    # True  — inside the window
scope_matches(norm, {}, {}, now=t0 + timedelta(hours=25))   # False — window has expired
```

Re-evaluating the *same* norm at two different `now` values gives two different answers — the
norm itself never changes, only whether it currently applies. Add a named `condition` and pass
a non-empty `registry` to layer in an arbitrary context check (e.g. `"business_hours"`,
`"request_from_trusted_ip"`) without ever calling `eval()` on request data.

### 5.7 Delegation's automatic oversight obligations

A single delegation fact derives its audit/revoke/liability trio automatically — no
hand-authored oversight rules needed:

```python
from deontic_reasoner.delegation import ground_delegation, atom_for_delegation, atom_for_violation
from deontic_reasoner.queries import is_obligatory

audit_rule, revoke_rule, liable_rule = ground_delegation("Orchestrator", "DataAgent", "n1")
delegation_atom = atom_for_delegation("Orchestrator", "DataAgent", "n1")
violation_atom = atom_for_violation("DataAgent", "n1")
(audit_atom,) = audit_rule.head
(revoke_atom,) = revoke_rule.head

is_obligatory(frozenset({audit_atom}), frozenset({delegation_atom}), [audit_rule])                       # True
is_obligatory(frozenset({revoke_atom}), frozenset({delegation_atom}), [revoke_rule])                      # False — no violation yet
is_obligatory(frozenset({revoke_atom}), frozenset({delegation_atom, violation_atom}), [revoke_rule])      # True  — dyadic: revoke *given* violation
```

Revocation is genuinely **dyadic** — it only becomes obligatory once a violation has actually
occurred, not unconditionally the moment delegation happens.

A **broken delegation chain** — one hop's `valid_link` fact simply missing — denies the
downstream permission via ordinary rule matching, no dedicated chain-walking code:

```python
from deontic_reasoner.models import Rule
from deontic_reasoner.queries import is_obligatory

chain_rule = Rule(
    body=frozenset({"delegation:Orchestrator:Supervisor:n1", "valid_link:Orchestrator:Supervisor:n1",
                     "delegation:Supervisor:DataAgent:n2", "valid_link:Supervisor:DataAgent:n2"}),
    head=frozenset({"permission:DataAgent:read:/data"}),
    weight=10.0,
)

complete = frozenset({"delegation:Orchestrator:Supervisor:n1", "valid_link:Orchestrator:Supervisor:n1",
                       "delegation:Supervisor:DataAgent:n2", "valid_link:Supervisor:DataAgent:n2"})
broken = frozenset({"delegation:Orchestrator:Supervisor:n1",
                     "delegation:Supervisor:DataAgent:n2", "valid_link:Supervisor:DataAgent:n2"})  # hop 1's valid_link missing

is_obligatory(frozenset({"permission:DataAgent:read:/data"}), complete, [chain_rule])   # True
is_obligatory(frozenset({"permission:DataAgent:read:/data"}), broken, [chain_rule])     # False
```

Note this is modeled as `is_obligatory` going `True → False`, not `is_permitted` going to
`False` — an atom nothing constrains is *permitted by default* in this framework (see §7),
so "permission fails to derive" is correctly expressed as an obligation, not a permission,
disappearing.

### 5.8 Power exercise and the forward-chaining loop

A power's exercise creates a new norm, and `forward_chain` runs the fixed-point loop that
grounds it:

```python
from deontic_reasoner.models import Norm, Relation
from deontic_reasoner.chaining import forward_chain

power_norm = Norm(id="p1", relation=Relation.POWER, subject="Orchestrator", action="grant",
                   resource="SubAgent.permissions", counterparty="SubAgent")
kwargs = {"subject": "SubAgent", "relation": Relation.PRIVILEGE, "action": "read", "resource": "/data"}

result = forward_chain(norms={"p1": power_norm}, power_exercises=[("p1", kwargs)])

result.iterations   # 2 — one round to see the exercise, one more to ground the new norm
sorted(result.norms)  # ['exercise:p1:SubAgent:privilege:read:/data:None', 'p1']
sorted(result.facts)  # ['norm:exercise:p1:SubAgent:privilege:read:/data:None', 'norm:p1']
```

The loop takes two iterations, not one: the first round sees `p1` and applies the power
exercise, producing the new `PRIVILEGE` norm; that new norm's own correlative grounding (it has
no `counterparty` here, so nothing further) only happens starting the *second* round. This is
deliberate — see §4.9.

---

## 6. Settings and configuration

### 6.1 Choosing a preference criterion

Pass `criterion=PreferenceCriterion.SUBSET` or `.COUNT` to `best_worlds`/`is_obligatory`/
`is_permitted` to override the default `WEIGHTED_COUNT`. Use `SUBSET` only if you specifically
want an unresolved-when-incomparable result (it leaves genuinely conflicting rules of equal
"importance" undecided rather than picking a winner); use `COUNT` if every rule should count
equally regardless of weight. `WEIGHTED_COUNT` is the right default for almost every real
scenario, since it's the only one of the three that reliably resolves a conflict between
differently-important rules.

### 6.2 Building a predicate registry for `scope_matches`

A registry is a plain `dict[str, Callable[[Norm, Mapping[str, object]], bool]]`:

```python
def business_hours(norm, request) -> bool:
    return 9 <= request.get("hour", 0) < 17

registry = {"business_hours": business_hours}
scope_matches(norm, {"hour": 14}, registry, now=datetime.now())
```

Register every condition name your norms might use *before* evaluating them — an unregistered
name raises `UnknownPredicateError` (§7).

### 6.3 Who is allowed to set `Rule.weight`

The reasoning engine itself does not enforce this — it is a requirement on whatever
application layer authors/stores your rules: **`weight` must be set by the rule's
granting/authoring authority, never by the rule's own subject-agent.** Nothing in
`best_worlds` stops a delegatee from asserting a rule with an inflated weight to out-rank a
restriction its own delegator imposed. If your deployment lets agents propose their own rules,
validate/clamp `weight` at the point rules are ingested, before they ever reach this library.

### 6.4 Tractability

`best_worlds` enumerates candidate worlds only over the atoms actually mentioned in the
antecedent or in some rule's `body`/`head` — not your program's entire atom vocabulary. Still,
that enumeration is `2^n` in the number of *varying* atoms for a given query, so keep the
antecedent/rule-set atom footprint for any single query reasonably small (tens of atoms, not
thousands) if you need interactive-latency answers.

### 6.5 Bounding `forward_chain`

`max_iterations` defaults to 1000. Lower it if you want a tighter bound on worst-case runtime;
raise it if a deep, legitimately multi-round delegation/power-exercise chain needs more rounds
to converge than the default allows. If a call raises `ForwardChainTimeout`, see §7 before just
raising the cap further.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `UnknownPredicateError: <name>` raised from `scope_matches`/`evaluate_condition` | A `Norm.condition` names a predicate that isn't a key in the `registry` you passed. | Register that condition name before evaluating, or check for a typo in `Norm.condition`. |
| `ForwardChainTimeout` raised from `forward_chain` | `max_iterations` rounds all still derived a genuinely new norm. Either your `power_exercises`/`delegations` describe a chain that legitimately needs more rounds, or (more likely) two power exercises are feeding each other in a way that never settles. | First try raising `max_iterations`. If it still never converges, inspect your `power_exercises` list for an exercise whose output feeds back into another exercise's input indefinitely — `forward_chain` has no cycle detection (§1.3), so a genuine cycle in your own exercise graph will never converge no matter how high you raise the cap. |
| `is_permitted(...)` returns `True` for an atom you expected to be forbidden | An unconstrained atom is **permitted by default** in this framework — if no rule or hard constraint says anything about it, it's free to be `True` in some best world. | Add an explicit rule (to disprefer it) or `HardConstraint` (to exclude it) naming that atom, rather than relying on its absence to forbid it. |
| Two rules about what look like negations of each other (`sent`/`not_sent`) both seem satisfied at once | There is no logical negation in this framework (§4.1) — `sent` and `not_sent` are independent atoms and can both be `True` in the same world unless something stops that. | Add a `HardConstraint(forbidden=frozenset({"sent", "not_sent"}))` (or whichever atom pair) to force genuine mutual exclusivity. See §5.3. |
| `is_obligatory` returns `True` and `is_permitted` returns `False` for the *same* query, and that feels contradictory | `best_worlds(given)` is empty — `given` itself is unsatisfiable under your rules/hard constraints. Universal quantification over an empty set is vacuously `True`; existential quantification over an empty set is vacuously `False`. This is correct, not a bug (§4.5). | Check whether your `given` antecedent is actually satisfiable at all — if two hard constraints (or an antecedent atom plus a hard constraint) jointly exclude every candidate world, every obligation query on that antecedent will vacuously return `True` and every permission query will vacuously return `False`, regardless of what you're asking about. |
| `best_worlds`/queries feel slow on a large rule set | `best_worlds` enumerates `2^n` candidates over the atoms relevant to your query (§6.4). | Reduce the atom footprint of a single query (split unrelated concerns into separate rule sets/queries) rather than loading your entire global rule set for every call. |
| `from_dict(cls, data)` raises a `KeyError` | `data` is missing a field `cls` expects — it must be shaped exactly like `to_dict`'s own output for that class, including every field. | Round-trip through `to_dict` first to see the exact expected shape, or diff your hand-authored dict against it field by field. |
| Contributing: `pytest`/`ruff`/`radon`/`pydoclint` gates fail on a PR | This repository enforces ≥90% test coverage (aggregate and per-file), lint, complexity, and docstring gates via pre-commit/pre-push hooks and CI — see `project/pyproject.toml`. | Run `uv run pytest`, `uv run ruff check`, `uv run radon cc -n B src tests`, and `uv run pydoclint src` locally before pushing; the pre-commit/pre-push hooks run the same checks automatically. |

---

## 8. FAQ

**Is this a full modal/propositional deontic logic engine with negation and disjunction?**
No. `Rule.body`/`Rule.head` are conjunctions of atoms only. Model "not X" as an independent
atom plus a `HardConstraint` if you need mutual exclusivity (§4.1, §7).

**Does the engine stop an agent from setting its own rule's weight arbitrarily high?**
No — that's a trust-boundary requirement on your application layer, not something
`best_worlds`/`preferred` enforce (§6.3).

**Does `IMMUNITY` actually block anything?**
Not yet. It's fully representable, groundable, and forward-chainable, but has no behavioral
short-circuiting in this iteration (§1.3).

**Can I persist rules/norms to a file or database?**
Yes, via `to_dict`/`from_dict` (§4.10) — every core dataclass round-trips through plain JSON.
There's no built-in storage layer; you own how/where the dicts get persisted.

**Is there a CLI or REST/MCP server?**
No — this iteration is a library only, meant to be embedded directly in your own application
or (in a planned, separate later iteration) an MCP server for AI agent tool/resource
authorization.

**Why does an obligation query sometimes return `True` for something I never wrote a rule
about?**
Because `best_worlds(given)` came back empty (an unsatisfiable antecedent) — see the vacuous
truth explanation in §4.5 and the matching troubleshooting entry in §7.

**Is `deontic-reasoner` published on PyPI yet?**
Check the project's `Notes.md → Publish` section for current status; if not yet published,
install from source per §2.2.

**What Python version do I need?**
3.14+, no exceptions — the codebase uses 3.14 syntax (e.g. PEP 695 generic function syntax in
`from_dict`).

---

## 9. Glossary and API quick-reference

**Atom** — a ground propositional fact, represented as a plain `str`.
**World** — `frozenset[str]`, the atoms true at that world.
**Rule** — a weighted, defeasible conditional obligation `(body → head, weight)`.
**HardConstraint** — a `forbidden` atom-set whose simultaneous truth excludes a world entirely.
**Violates** — a world "violates" a rule when the rule's body holds but its head doesn't.
**Excludes** — a hard constraint "excludes" a world when every forbidden atom is present in it.
**PreferenceCriterion** — `SUBSET` / `COUNT` / `WEIGHTED_COUNT`; how two worlds' violated-rule
sets are compared to decide which is more preferred.
**best_worlds** — the maximal (most-preferred) candidate worlds satisfying a given antecedent.
**Dyadic obligation, `O(q|p)`** — "given p, q ought to be the case" — obligation relativized to
a condition, avoiding the material-conditional vacuous-truth trap (Hansson, 1969).
**Contrary-to-duty obligation** — a secondary obligation that only applies given a primary
obligation's *violation* (Chisholm's 1963 paradox is about this family).
**Hohfeldian relation** — one of `PRIVILEGE`/`RIGHT`/`POWER`/`IMMUNITY`, the four first-party
legal incidents this reasoner implements, each with a correlative on the counterparty.
**Correlative** — the obligation a Hohfeldian incident imposes on the *other* party: `duty`
(for `RIGHT`), `liability` (for `POWER`), `disability` (for `IMMUNITY`).
**Norm** — a single Hohfeldian incident: who (`subject`), what relation, what action/resource,
optionally directed at a `counterparty`, optionally scoped by time/`condition`.
**Delegation** — `delegated(delegatee, delegator, norm_id)`; automatically derives audit,
revoke-on-violation, and liability duties on the delegator.
**Power exercise** — an ordinary domain-specific fact used as a rule's body whose head asserts
a new `Norm` — no dedicated predicate, any deployment-specific fact shape works.
**Forward chaining** — the fixed-point loop deriving every norm/fact that follows from
iterating power exercises and delegation grounding until nothing new is added.
**Scope matching** — checking whether a norm currently applies: within its temporal window,
and its named `condition` (if any) evaluates `True` through a fixed predicate registry.

### Quick-reference: the full public API

```python
# deontic_reasoner.models
Atom = str
World = frozenset[str]
class Relation(StrEnum): PRIVILEGE, RIGHT, POWER, IMMUNITY
class Rule:            head: frozenset[Atom]; weight: float; body: frozenset[Atom] = frozenset()
class HardConstraint:  forbidden: frozenset[Atom]
class Norm:             id, relation, subject, action, resource, counterparty=None,
                        valid_from=None, valid_until=None, condition=None

# deontic_reasoner.preference
violates(rule, world) -> bool
excludes(constraint, world) -> bool
class PreferenceCriterion(Enum): SUBSET, COUNT, WEIGHTED_COUNT
violated_rules(world, rules) -> frozenset[Rule]
preferred(world_a, world_b, rules, criterion=WEIGHTED_COUNT) -> bool
best_worlds(antecedent, rules, hard_constraints=(), criterion=WEIGHTED_COUNT) -> set[World]

# deontic_reasoner.queries
is_obligatory(b, given, rules, hard_constraints=(), criterion=WEIGHTED_COUNT) -> bool
is_permitted(b, given, rules, hard_constraints=(), criterion=WEIGHTED_COUNT) -> bool

# deontic_reasoner.grounding
atom_for_norm(norm) -> Atom
ground_norm(norm, weight=CORRELATIVE_WEIGHT) -> tuple[Atom, Rule | None]

# deontic_reasoner.scope
class UnknownPredicateError(Exception)
evaluate_condition(norm, request, registry) -> bool
scope_matches(norm, request, registry, now) -> bool

# deontic_reasoner.delegation
atom_for_delegation(delegator, delegatee, norm_id) -> Atom
atom_for_violation(delegatee, norm_id) -> Atom
ground_delegation(delegator, delegatee, norm_id, weight=OBLIGATION_WEIGHT) -> (Rule, Rule, Rule)
exercise_power(power_norm, subject, relation, action, resource, counterparty=None, ...) -> Norm
delegate_with_narrowing(parent, subject, valid_from=None, valid_until=None, ...) -> Norm

# deontic_reasoner.chaining
class ChainResult:      norms: dict[str, Norm]; facts: frozenset[Atom]; rules: tuple[Rule, ...]; iterations: int
class ForwardChainTimeout(Exception)
forward_chain(norms, delegations=(), power_exercises=(), max_iterations=1000) -> ChainResult

# deontic_reasoner.serialization
to_dict(obj) -> dict
from_dict(cls, data) -> T
world_to_list(world) -> list[str]
world_from_list(data) -> World
```

There are no keyboard shortcuts to document — this is an embeddable library, not an
interactive application. The table above is the complete surface you'll ever call directly.
