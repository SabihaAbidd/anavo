"""Physical inputs and shared feasibility evaluation; units are W, h, Wh."""
from dataclasses import dataclass, asdict
from math import isfinite
from numbers import Real


def nonnegative(name, value):
    if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")


@dataclass(frozen=True)
class Appliance:
    name: str
    power_w: float
    duration_h: float
    utility: float
    essential: bool = False
    mandatory: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Appliance name must be nonempty")
        for field in ("power_w", "duration_h", "utility"):
            nonnegative(field, getattr(self, field))
        if type(self.essential) is not bool or type(self.mandatory) is not bool:
            raise ValueError("essential and mandatory must be boolean")

    @property
    def energy_wh(self):
        return self.power_w * self.duration_h


@dataclass(frozen=True)
class Scenario:
    name: str
    appliances: tuple[Appliance, ...]
    battery_wh: float
    inverter_w: float
    outage_h: float

    def __post_init__(self):
        object.__setattr__(self, "appliances", tuple(self.appliances))
        if not self.appliances or len(self.appliances) > 20:
            raise ValueError("Use between 1 and 20 appliances for exact enumeration")
        if not all(isinstance(a, Appliance) for a in self.appliances):
            raise ValueError("Every load must be an Appliance")
        for field in ("battery_wh", "inverter_w", "outage_h"):
            nonnegative(field, getattr(self, field))
        if self.outage_h <= 0:
            raise ValueError("Outage duration must be positive")
        if len({a.name.strip().casefold() for a in self.appliances}) != len(self.appliances):
            raise ValueError("Appliance names must be unique")
        if any(a.duration_h > self.outage_h for a in self.appliances):
            raise ValueError("Appliance duration cannot exceed outage duration")
        if not all(isfinite(a.energy_wh) for a in self.appliances):
            raise ValueError("Appliance energy must be finite")
        if not isfinite(sum(a.utility for a in self.appliances)):
            raise ValueError("Total utility must be finite")


def evaluate(scenario, selection):
    if len(selection) != len(scenario.appliances) or any(x not in (0, 1) for x in selection):
        raise ValueError("Selection must contain one binary value per appliance")
    chosen = [a for a, x in zip(scenario.appliances, selection) if x]
    energy = sum(a.energy_wh for a in chosen)
    power = sum(a.power_w for a in chosen)
    # Exact decimal arithmetic aligns feasibility with QUBO normalization.
    from fractions import Fraction
    energy_exact = sum(Fraction(str(a.power_w)) * Fraction(str(a.duration_h)) for a in chosen)
    power_exact = sum(Fraction(str(a.power_w)) for a in chosen)
    violations = []
    if energy_exact > Fraction(str(scenario.battery_wh)):
        violations.append("battery energy exceeded")
    if power_exact > Fraction(str(scenario.inverter_w)):
        violations.append("inverter power exceeded")
    if any(a.mandatory and not x for a, x in zip(scenario.appliances, selection)):
        violations.append("mandatory load omitted")
    return dict(selection=list(selection), bitstring="".join(map(str, selection)),
                selected=[a.name for a in chosen],
                unselected=[a.name for a, x in zip(scenario.appliances, selection) if not x],
                utility=sum(a.utility for a in chosen), energy_wh=energy, power_w=power,
                remaining_wh=scenario.battery_wh-energy,
                essential_served=sum(a.essential for a in chosen),
                essential_total=sum(a.essential for a in scenario.appliances),
                feasible=not violations, violations=violations)


def scenario_dict(scenario):
    return asdict(scenario)
