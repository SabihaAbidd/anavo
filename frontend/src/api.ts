export interface Appliance {name:string;power_w:number;duration_h:number;utility:number;essential:boolean;mandatory:boolean}
export interface Scenario {name:string;battery_wh:number;inverter_w:number;outage_h:number;appliances:Appliance[]}
export interface Allocation {objective_value:number;energy_used_wh:number;power_used_w:number;energy_remaining_wh:number;selected_appliances:Appliance[];deferred_appliances:Appliance[];bitstring:string}
export interface Selection {appliance_bitstring:string;count:number;probability:number;feasible:boolean;utility:number}
export interface LandscapePoint {appliance_bitstring:string;utility:number;energy_wh:number;power_w:number;feasible:boolean;probability:number}
export interface QuantumMeta {qubits:number;appliance_qubits:number;slack_qubits:number;qaoa_depth:number;shots:number;seed:number;circuit_depth:number;feasible_selection_probability:number;feasible_encoding_probability:number;optimizer_evaluations:number;objective_history:number[];parameters:number[];penalty:number;qubit_roles:string[];circuit_operations:Record<string,number>;selection_distribution:Selection[];landscape:LandscapePoint[]}
export interface Solver {status:string;feasibility:string;allocation:Allocation|null;runtime_s:number|null;message?:string;quantum_metadata?:QuantumMeta|null}
export interface Comparison {classical:Solver;quantum:Solver;comparison_status:string;relative_gap:number|null;objective_gap:number|null;optimal_selection_probability:number|null}
export interface ScheduledAppliance {name:string;power_w:number;duration_h:number;utility:number;mandatory:boolean;selected:boolean;start_slot:number|null;start:string|null;end:string|null;energy_wh:number}
export interface Slot {slot:number;start:string;end:string;load_w:number;solar_wh:number;battery_wh:number;curtailed_wh:number;inverter_headroom_w:number;running:string[]}
export interface Schedule {status:string;feasible:boolean;utility:number|null;simultaneous_utility:number|null;gain_vs_simultaneous:number|null;slot_h:number;slots:number;energy_used_wh?:number|null;solar_generated_wh?:number|null;final_battery_wh?:number|null;peak_load_w?:number|null;appliances:ScheduledAppliance[];timeline:Slot[];runtime_s:number;message?:string|null}
export interface HomeResult {name:string;weight:number;selected:string[];deferred:string[];utility:number;max_utility:number;service_ratio:number;energy_wh:number;power_w:number;mandatory_met:boolean;baseline_utility:number}
export interface Fleet {status:string;feasible:boolean;homes:number;decisions:number;utility:number|null;energy_used_wh:number|null;power_used_w:number|null;homes_fully_mandatory:number|null;fairness_index:number|null;gain_vs_equal_split:number|null;baseline:{utility:number;homes_with_mandatory_met:number;fairness_index:number;method:string};home_results:HomeResult[];runtime_s:number;message?:string|null}
export interface Job<T> {job_id:string;kind:string;status:'queued'|'running'|'succeeded'|'failed';queue_position?:number|null;result:T|null;error?:string|null;submitted_utc:string;started_utc?:string|null;finished_utc?:string|null}
export interface Source {title:string;url:string;secondary_url?:string;used_for:string}
export interface DataAppliance {name:string;power_w:number;hours:number;priority:number;basis:string;mandatory?:boolean}
export interface Archetype {id:string;label:string;weight:number;appliances:string[]}
export interface Dataset {disclaimer:string;compiled:string;sources:Record<string,Source>;outage_profiles:{id:string;label:string;daily_outage_h:number;basis:string;note:string}[];solar:{ghi_kwh_m2_day:number;basis:string;performance_ratio_assumption:number;note:string};appliances:DataAppliance[];household_archetypes:Archetype[]}
export const defaultScenario:Scenario={name:'Evening backup',battery_wh:240,inverter_w:100,outage_h:3,appliances:[{name:'Fan',power_w:40,duration_h:3,utility:9,essential:true,mandatory:false},{name:'LED lights',power_w:10,duration_h:3,utility:7,essential:true,mandatory:false},{name:'Wi-Fi router',power_w:10,duration_h:3,utility:8,essential:true,mandatory:true},{name:'Laptop',power_w:60,duration_h:2,utility:6,essential:false,mandatory:false}]};
export const quantumOptions={depth:2,shots:2048,maxiter:80,restarts:2,seed:42,max_qubits:14};
export async function request<T>(path:string,body?:unknown):Promise<T>{
 const response=await fetch(path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined});
 const data=await response.json();
 if(!response.ok){
  // Name the offending field(s) instead of only "does not satisfy the API contract".
  const details:{path?:(string|number)[];message?:string}[]=Array.isArray(data.error?.details)?data.error.details:[];
  const fields=details.slice(0,3).map(d=>{const path=(d.path||[]).filter(p=>p!=='body'&&p!=='payload').join(' › ').replaceAll('_',' ');return path?`${path}: ${d.message}`:d.message;}).filter(Boolean);
  throw new Error([data.error?.message||`API request failed (${response.status}).`,...fields].join(' — '));
 }
 return data as T;
}
/** Submit to the async job queue, then poll until the worker finishes. */
export async function runJob<T>(kind:string,payload:unknown,onUpdate?:(job:Job<T>)=>void):Promise<Job<T>>{
 let job=await request<Job<T>>('/api/jobs',{kind,payload});onUpdate?.(job);
 while(job.status==='queued'||job.status==='running'){await new Promise(r=>setTimeout(r,600));job=await request<Job<T>>(`/api/jobs/${job.job_id}`);onUpdate?.(job);}
 if(job.status==='failed')throw new Error(job.error||'Job failed.');
 return job;
}
/** Turn a dataset archetype into a home, clamping durations to the outage window. */
export function archetypeHome(name:string,archetype:Archetype,library:DataAppliance[],outage:number){
 const byName=Object.fromEntries(library.map(a=>[a.name,a]));
 return {name,weight:archetype.weight,appliances:archetype.appliances.map(n=>{const a=byName[n];return {name:n,power_w:a.power_w,duration_h:Math.min(a.hours,outage),utility:a.priority,essential:!!a.mandatory,mandatory:!!a.mandatory};})};
}
