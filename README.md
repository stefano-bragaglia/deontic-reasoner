# deontic-reasoner

Hohfeldian + deontic-logic semantic reasoner for AI agent permission governance.

[![CI](https://github.com/stefano-bragaglia/deontic-reasoner/actions/workflows/ci.yml/badge.svg)](https://github.com/stefano-bragaglia/deontic-reasoner/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Visuals

<!-- Add a logo/diagram here (e.g. project/docs/logo.png) once one exists. -->

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
uv sync
```

## Features

A minimal **Preferential (Betterness-Ordering) Dyadic Deontic Logic** reasoner — Hansson's dyadic
`O(q|p)` combined with KLM preferential semantics — plus a Hohfeldian layer on top:

- **Propositional core** — `Atom`/`World`/`Rule`/`HardConstraint`, with JSON round-tripping.
- **Preference ordering and best worlds** — `violates`/`excludes`/`preferred`/`best_worlds` under a
  choice of `SUBSET`, `COUNT`, or `WEIGHTED_COUNT` preference criteria; conflict resolution falls
  directly out of which worlds are most preferred, no separate conflict-detection machinery needed.
- **Obligation and permissibility queries** — `is_obligatory`/`is_permitted`, universal/existential
  quantification over the best worlds satisfying a given antecedent.
- **Hohfeldian grounding** — `ground_norm` turns a `Norm` (privilege/right/power/immunity) into the
  correlative duty/liability/disability rule its counterparty bears.
- **Scope evaluation** — `scope_matches`/`evaluate_condition` against a `PredicateRegistry`, covering
  temporal validity windows and named applicability conditions.
- **Forward chaining and delegation** — `forward_chain` runs a bounded fixed-point loop over power
  exercises (`exercise_power`) and delegation (`ground_delegation`/`delegate_with_narrowing`), so
  oversight obligations and newly-granted powers are derived automatically rather than hand-authored.

## Usage

This project is a library, not yet published. A minimal example:

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

See the vault's `documentation/` for the full design and worked scenarios.

## Contributing

Solo project for now — see the vault root's `Notes.md` for current phase and status. Every change
to `src/` requires tests (coverage ≥ 90%, aggregate and per-file) and passes `ruff`/`radon` gates,
enforced by pre-commit hook and CI.

## License

[MIT](LICENSE)
