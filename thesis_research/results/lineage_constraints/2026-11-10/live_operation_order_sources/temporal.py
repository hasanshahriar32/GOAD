"""Exact continuous-time difference constraints with explicit evidence IDs.

Established simple-temporal-network reasoning, used as a research component.
No ordering edge is inferred from cross-host record numbers or timestamp order.
Fractions and strict inequalities avoid an arbitrary floating-point epsilon.
"""

from dataclasses import dataclass
from fractions import Fraction


def rational(value):
    return Fraction(str(value))


@dataclass(frozen=True)
class Limit:
    value: Fraction
    strict: bool = False

    def __add__(self, other):
        return Limit(self.value + other.value, self.strict or other.strict)

    def tighter_than(self, other):
        return (self.value, not self.strict) < (other.value, not other.strict)


@dataclass(frozen=True)
class Constraint:
    """left - right <= upper, or < upper if strict."""
    left: str
    right: str
    upper: Fraction
    evidence_id: str
    strict: bool = False

    def __post_init__(self):
        if not self.evidence_id:
            raise ValueError("Every constraint needs an evidence/assumption ID")
        object.__setattr__(self, "upper", rational(self.upper))


class TemporalNetwork:
    ORIGIN = "__origin__"

    def __init__(self, bounds, constraints=()):
        """bounds maps each variable to (lower, upper), or None if unbounded."""
        if self.ORIGIN in bounds:
            raise ValueError("Reserved origin variable")
        self.bounds = dict(bounds)
        self.constraints = list(constraints)
        for name, interval in self.bounds.items():
            if interval is None:
                continue
            lower, upper = map(rational, interval)
            if lower > upper:
                raise ValueError("Reversed temporal bounds")
            self.constraints += [Constraint(name, self.ORIGIN, upper, f"bound:{name}:upper"),
                                 Constraint(self.ORIGIN, name, -lower, f"bound:{name}:lower")]
        self.names = [self.ORIGIN] + sorted(self.bounds)
        self.index = {name: i for i, name in enumerate(self.names)}
        self.distances = self._closure(self.constraints)

    def _closure(self, constraints):
        n = len(self.names)
        d = [[None for _ in range(n)] for _ in range(n)]
        for i in range(n):
            d[i][i] = Limit(Fraction(0))
        for c in constraints:
            if c.left not in self.index or c.right not in self.index:
                raise ValueError("Constraint refers to an undeclared variable")
            i, j = self.index[c.right], self.index[c.left]
            v = Limit(c.upper, c.strict)
            if d[i][j] is None or v.tighter_than(d[i][j]):
                d[i][j] = v
        for k in range(n):
            for i in range(n):
                if d[i][k] is None:
                    continue
                for j in range(n):
                    if d[k][j] is None:
                        continue
                    candidate = d[i][k] + d[k][j]
                    if d[i][j] is None or candidate.tighter_than(d[i][j]):
                        d[i][j] = candidate
        return d

    @staticmethod
    def _consistent(distances):
        zero = Limit(Fraction(0))
        return not any(row[i].tighter_than(zero) for i, row in enumerate(distances))

    @property
    def consistent(self):
        return self._consistent(self.distances)

    def entails_before(self, earlier, later):
        if not self.consistent:
            return False  # Do not turn inconsistency into vacuous certainty.
        bound = self.distances[self.index[later]][self.index[earlier]]
        return bound is not None and bound.value <= 0

    def overlap(self, opened, issuance, closed):
        if not self.consistent:
            return "inconsistent_evidence"
        query = [Constraint(opened, issuance, 0, "query:open-before-issue"),
                 Constraint(issuance, closed, 0, "query:issue-before-close")]
        if not self._consistent(self._closure(self.constraints + query)):
            return "impossible_overlap"
        if self.entails_before(opened, issuance) and self.entails_before(issuance, closed):
            return "definite_overlap"
        return "possible_overlap"

    def inconsistent_core(self):
        """One deletion-minimal contradictory set, not a minimum-cardinality set."""
        if self.consistent:
            return ()
        core = list(self.constraints)
        for c in tuple(core):
            trial = list(core)
            trial.remove(c)
            if not self._consistent(self._closure(trial)):
                core = trial
        return tuple(c.evidence_id for c in core)
