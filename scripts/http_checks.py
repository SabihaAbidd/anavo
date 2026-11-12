"""Real HTTP requests and assertions, independent of TestClient and mocks."""
from copy import deepcopy
import json
import urllib.error
import urllib.request
from dataclasses import asdict
from src.scenarios import presets


def request_json(base,method,path,payload=None,headers=None):
    headers=dict(headers or {})
    data=None
    if payload is not None:
        data=json.dumps(payload,allow_nan=False).encode()
        headers["Content-Type"]="application/json"
    req=urllib.request.Request(base+path,data=data,headers=headers,method=method)
    try:
        response=urllib.request.urlopen(req,timeout=90)
    except urllib.error.HTTPError as exc:
        response=exc
    with response:
        body=response.read().decode()
        try: body=json.loads(body)
        except ValueError: pass
        return response.status,body,{key.lower():value for key,value in response.headers.items()}


def measured_quantum(result):
    q=result.get("quantum_metadata") or {}
    counts=q.get("counts",{})
    allocation=result.get("allocation")
    return (result.get("status")=="sampled" and allocation is not None
            and allocation.get("feasible") is True and q.get("shots")==256
            and bool(counts) and all(type(v) is int and v>0 for v in counts.values())
            and sum(counts.values())==256)


def run_http_checks(base):
    checks=[]

    def check(name,method,path,payload,predicate,headers=None):
        try:
            status,body,response_headers=request_json(base,method,path,payload,headers)
            passed=bool(predicate(status,body,response_headers))
            checks.append(dict(name=name,method=method,path=path,status_code=status,
                               passed=passed,response=body))
        except (OSError,ValueError,TypeError,KeyError) as exc:
            checks.append(dict(name=name,method=method,path=path,passed=False,error=str(exc)))

    evening=asdict(presets()["Evening backup"])
    small=dict(name="HTTP circuit probe",battery_wh=1,inverter_w=1,outage_h=1,
        appliances=[dict(name="Light",power_w=1,duration_h=1,utility=3,essential=True,mandatory=True),
                    dict(name="Optional",power_w=1,duration_h=1,utility=2)])
    quantum_options=dict(depth=1,shots=256,maxiter=20,restarts=1,seed=42)
    check("health","GET","/health",None,lambda s,b,h:s==200 and b["service"]=="ANAVO API" and b["status"]=="ok")
    check("scenarios","GET","/api/scenarios",None,lambda s,b,h:s==200 and len(b["scenarios"])==4)
    check("algorithm_info","GET","/api/algorithm-info",None,lambda s,b,h:s==200 and b["quantum"]["algorithm"]=="QAOA" and b["quantum"]["speedup_claim"] is False)
    check("classical_optimize","POST","/api/optimize",dict(scenario=evening),
        lambda s,b,h:s==200 and b["result"]["allocation"]["objective_value"]==24
            and b["result"]["allocation"]["energy_used_wh"]==180 and b["result"]["allocation"]["power_used_w"]==60)
    check("quantum_optimize","POST","/api/optimize",dict(scenario=small,algorithm="quantum",quantum_options=quantum_options),
        lambda s,b,h:s==200 and measured_quantum(b["result"]))
    check("compare","POST","/api/compare",dict(scenario=small,quantum_options=quantum_options),
        lambda s,b,h:s==200 and b["comparison_status"]=="complete" and measured_quantum(b["quantum"])
            and b["classical"]["allocation"]["objective_value"]==3 and b["objective_gap"]==0)
    check("mandatory_infeasible","POST","/api/optimize",dict(scenario=asdict(presets()["Mandatory infeasible"])),
        lambda s,b,h:s==200 and b["result"]["status"]=="infeasible" and b["result"]["allocation"] is None)
    invalid=deepcopy(evening);invalid["battery_wh"]=-1
    check("invalid_request","POST","/api/optimize",dict(scenario=invalid),
        lambda s,b,h:s==422 and b["error"]["code"]=="validation_error")
    check("quantum_limit","POST","/api/optimize",dict(scenario=evening,algorithm="quantum",quantum_options=dict(max_qubits=1)),
        lambda s,b,h:s==413 and b["error"]["code"]=="quantum_resource_limit")
    zero=deepcopy(evening);zero["battery_wh"]=0;zero["inverter_w"]=0
    for a in zero["appliances"]: a["mandatory"]=False
    check("zero_budget","POST","/api/optimize",dict(scenario=zero),
        lambda s,b,h:s==200 and b["result"]["allocation"]["selection"]==[0,0,0,0])
    check("cors_allowed","OPTIONS","/api/optimize",None,
        lambda s,b,h:s==200 and h.get("access-control-allow-origin")=="http://localhost:5173",
        {"Origin":"http://localhost:5173","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"Content-Type"})
    check("cors_rejected","OPTIONS","/api/optimize",None,
        lambda s,b,h:s==400 and "access-control-allow-origin" not in h,
        {"Origin":"https://untrusted.example","Access-Control-Request-Method":"POST"})
    return checks
