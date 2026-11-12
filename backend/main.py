"""Run: python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000."""
import importlib.util
import logging
from threading import BoundedSemaphore
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.scenarios import presets
from . import __version__
from . import service
from .settings import cors_origins
from .schemas import (AlgorithmInfo, CompareRequest, CompareResponse, ErrorResponse,
    HealthResponse, OptimizeRequest, OptimizeResponse, ScenarioInput, ScenariosResponse)

logger = logging.getLogger(__name__)


def error_response(status, code, message, details=None, headers=None):
    body = ErrorResponse(error=dict(code=code, message=message, details=details))
    return JSONResponse(status_code=status, content=body.model_dump(mode="json"), headers=headers)


def create_app():
    app = FastAPI(title="ANAVO Energy Optimization API", version=__version__,
        description="Household backup-energy decision support. Exact optimization and honest Qiskit simulator comparison. No electrical control or quantum speedup claim.")
    app.add_middleware(CORSMiddleware, allow_origins=cors_origins(), allow_credentials=False,
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    # Per-process admission control bounds CPU/memory usage; handlers run in the threadpool.
    jobs = BoundedSemaphore(1)
    app.state.optimization_slots = jobs

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        details = [dict(path=list(e["loc"]), message=e["msg"], type=e["type"]) for e in exc.errors()]
        return error_response(422, "validation_error", "Request does not satisfy the API contract.", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        if isinstance(exc.detail, dict):
            return error_response(exc.status_code, exc.detail["code"], exc.detail["message"],
                                  exc.detail.get("details"), exc.headers)
        return error_response(exc.status_code, "http_error", str(exc.detail), headers=exc.headers)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logger.exception("Unhandled API error", exc_info=exc)
        return error_response(500, "internal_error", "An internal error occurred; consult backend logs.")

    def execute(function, payload):
        if not jobs.acquire(blocking=False):
            raise HTTPException(429, detail=dict(code="optimizer_busy", message="Another optimization is running; retry shortly."),
                                headers={"Retry-After":"1"})
        try:
            return function(payload)
        finally:
            jobs.release()

    errors = {status: {"model": ErrorResponse} for status in (413, 422, 429, 500, 503)}

    @app.get("/health", response_model=HealthResponse, tags=["System"])
    def health():
        present = bool(importlib.util.find_spec("qiskit") and importlib.util.find_spec("qiskit_aer"))
        return HealthResponse(version=__version__, quantum_dependencies_available=present)

    @app.get("/api/scenarios", response_model=ScenariosResponse, tags=["Configuration"])
    def scenarios():
        return ScenariosResponse(scenarios=[ScenarioInput.from_domain(s) for s in presets().values()])

    @app.post("/api/optimize", response_model=OptimizeResponse, responses=errors, tags=["Optimization"])
    def optimize(payload: OptimizeRequest):
        result = execute(service.optimize, payload)
        status = {"unavailable":503, "oversized":413, "failed":503}.get(result.result.status)
        if status:
            raise HTTPException(status, detail=dict(code=result.result.error_code,
                message=result.result.message, details=result.model_dump(mode="json")))
        return result

    @app.post("/api/compare", response_model=CompareResponse, responses=errors, tags=["Optimization"])
    def compare(payload: CompareRequest):
        # Partial comparison returns 200 with explicit quantum status and no fabricated gap.
        return execute(service.compare, payload)

    @app.get("/api/algorithm-info", response_model=AlgorithmInfo, tags=["Configuration"])
    def algorithm_info():
        return AlgorithmInfo(objective="Maximize sum of selected appliance utilities under hard energy, power and mandatory constraints.",
            units=dict(power="W", energy="Wh", duration="h", utility="user-stated score"),
            classical="Independent exhaustive enumeration with lexicographic tie handling.",
            quantum=dict(algorithm="QAOA", backend="Qiskit Aer ideal statevector simulator",
                optimizer="SciPy COBYLA", encoding="Bounded slack QUBO -> Ising x=(1-Z)/2",
                penalty="1 + total utility", training="Exact simulator expectations; final circuit shot measurement",
                hardware=False, speedup_claim=False),
            limits=dict(appliances=16, qubits=14, depth=4, shots=8192, evaluations_per_restart=200,
                        restarts=3, concurrent_jobs_per_process=1),
            assumptions=["Usable AC-side battery energy; fixed requested durations within outage.",
                "Conservative simultaneous inverter power; no time-slot scheduling or surge model.",
                "Essential is a label; utility is a preference; mandatory is a hard constraint.",
                "Deferred means unselected for this request, not a future scheduled time.",
                "No quantum measurements are reported unless an actual circuit executes."],
            frontend_status="React/TypeScript/Vite frontend deferred pending design; Streamlit is optional legacy code outside the backend release.")

    return app


app = create_app()
