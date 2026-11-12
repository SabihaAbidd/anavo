"""Strict, versioned JSON contracts shared by API handlers and service tests."""
from typing import Annotated, Literal
from dataclasses import asdict
from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator
from src.models import Appliance, Scenario


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False,
                              str_strip_whitespace=True)


Name = Annotated[str, Field(min_length=1, max_length=120)]
Nonnegative = Annotated[float, Field(ge=0)]


class ApplianceInput(Contract):
    name: Name
    power_w: Annotated[float, Field(ge=0, le=1_000_000)]
    duration_h: Annotated[float, Field(ge=0, le=168)]
    utility: Annotated[float, Field(ge=0, le=1_000_000)]
    essential: bool = False
    mandatory: bool = False


class ScenarioInput(Contract):
    name: Name = "Custom outage"
    appliances: Annotated[list[ApplianceInput], Field(min_length=1, max_length=16)]
    battery_wh: Annotated[float, Field(ge=0, le=1_000_000_000)]
    inverter_w: Annotated[float, Field(ge=0, le=10_000_000)]
    outage_h: Annotated[float, Field(gt=0, le=168)]

    @classmethod
    def from_domain(cls, scenario):
        data = asdict(scenario)
        data["appliances"] = list(data["appliances"])
        return cls(**data)

    def to_domain(self) -> Scenario:
        return Scenario(self.name, tuple(Appliance(**a.model_dump()) for a in self.appliances),
                        self.battery_wh, self.inverter_w, self.outage_h)

    @model_validator(mode="after")
    def check_physical_scenario(self):
        self.to_domain()  # Reuse cross-field/name checks from the existing engine.
        return self


class QuantumOptions(Contract):
    depth: Annotated[int, Field(ge=1, le=4)] = 2
    shots: Annotated[int, Field(ge=1, le=8192)] = 2048
    maxiter: Annotated[int, Field(ge=10, le=200)] = 80
    restarts: Annotated[int, Field(ge=1, le=3)] = 2
    seed: Annotated[int, Field(ge=0, le=2**31-1)] = 42
    max_qubits: Annotated[int, Field(ge=1, le=14)] = 14


class OptimizeRequest(Contract):
    scenario: ScenarioInput
    algorithm: Literal["classical", "quantum"] = "classical"
    quantum_options: QuantumOptions = Field(default_factory=QuantumOptions)


class CompareRequest(Contract):
    scenario: ScenarioInput
    quantum_options: QuantumOptions = Field(default_factory=QuantumOptions)


class ApplianceDecision(ApplianceInput):
    selected: bool
    energy_wh: Nonnegative


class Allocation(Contract):
    feasible: bool
    objective_value: Nonnegative
    bitstring: str
    selection: list[int]
    selected_appliances: list[ApplianceDecision]
    deferred_appliances: list[ApplianceDecision]
    energy_used_wh: Nonnegative
    energy_remaining_wh: float
    power_used_w: Nonnegative
    inverter_remaining_w: float
    energy_utilization: Nonnegative
    essential_served: int
    essential_total: int
    violations: list[str]


class OptimizerRun(Contract):
    nfev: int
    success: bool
    message: str
    objective: float


class Measurement(Contract):
    measured_bitstring: str
    appliance_bitstring: str
    count: int
    feasible: bool
    encoding_feasible: bool
    utility: Nonnegative
    qubo_energy: float


class QuantumMetadata(Contract):
    qubits: int
    appliance_qubits: int
    slack_qubits: int
    qaoa_depth: int
    circuit_depth: int
    shots: int
    seed: int
    optimizer: str
    max_evaluations_per_restart: int
    restarts: int
    optimizer_evaluations: int
    optimizer_runs: list[OptimizerRun]
    optimizer_iterations: int | None
    iteration_note: str
    parameters: list[float]
    penalty: float
    hamiltonian_scale: float
    expected_qubo_energy: float
    objective_history: list[float]
    feasible_selection_probability: Annotated[float, Field(ge=0, le=1)]
    feasible_encoding_probability: Annotated[float, Field(ge=0, le=1)]
    counts: dict[str, int]
    distribution: list[Measurement]


class SolverResult(Contract):
    algorithm: Literal["classical", "quantum"]
    method: str
    status: Literal["optimal", "infeasible", "sampled", "no_feasible_sample", "unavailable", "oversized", "failed"]
    feasibility: Literal["feasible", "infeasible", "unknown"] = "unknown"
    allocation: Allocation | None = None
    runtime_s: Nonnegative | None = None
    enumerated: int | None = None
    feasible_selections: int | None = None
    quantum_metadata: QuantumMetadata | None = None
    error_code: str | None = None
    message: str | None = None


class OptimizeResponse(Contract):
    schema_version: Literal["1.0"] = "1.0"
    scenario: ScenarioInput
    result: SolverResult
    fallback_used: Literal[False] = False
    environment: dict[str, str | None]


class CompareResponse(Contract):
    schema_version: Literal["1.0"] = "1.0"
    scenario: ScenarioInput
    classical: SolverResult
    quantum: SolverResult
    comparison_status: Literal["complete", "quantum_unavailable", "quantum_oversized", "quantum_failed", "no_feasible_pair"]
    objective_gap: float | None
    relative_gap: float | None
    environment: dict[str, str | None]
    bit_order: str
    interpretation: str


class ScenariosResponse(Contract):
    scenarios: list[ScenarioInput]


class HealthResponse(Contract):
    status: Literal["ok"] = "ok"
    service: Literal["ANAVO API"] = "ANAVO API"
    version: str
    classical_available: bool = True
    quantum_dependencies_available: bool
    quantum_note: str = "Dependency presence does not establish actual circuit validation."


class AlgorithmInfo(Contract):
    schema_version: Literal["1.0"] = "1.0"
    objective: str
    units: dict[str, str]
    classical: str
    quantum: dict[str, JsonValue]
    limits: dict[str, JsonValue]
    assumptions: list[str]
    frontend_status: str


class ErrorDetail(Contract):
    code: str
    message: str
    details: JsonValue = None


class ErrorResponse(Contract):
    error: ErrorDetail
