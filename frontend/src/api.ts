export interface Appliance {name:string;power_w:number;duration_h:number;utility:number;essential:boolean;mandatory:boolean}
export interface Scenario {name:string;battery_wh:number;inverter_w:number;outage_h:number;appliances:Appliance[]}
export interface Allocation {objective_value:number;energy_used_wh:number;power_used_w:number;energy_remaining_wh:number;selected_appliances:Appliance[];deferred_appliances:Appliance[];bitstring:string}
export interface Solver {status:string;feasibility:string;allocation:Allocation|null;runtime_s:number|null;message?:string;quantum_metadata?:{qubits:number;shots:number;seed:number;circuit_depth:number;feasible_selection_probability:number}|null}
export interface Comparison {classical:Solver;quantum:Solver;comparison_status:string;relative_gap:number|null;objective_gap:number|null}
export const defaultScenario:Scenario={name:'Evening backup',battery_wh:240,inverter_w:100,outage_h:3,appliances:[{name:'Fan',power_w:40,duration_h:3,utility:9,essential:true,mandatory:false},{name:'LED lights',power_w:10,duration_h:3,utility:7,essential:true,mandatory:false},{name:'Wi-Fi router',power_w:10,duration_h:3,utility:8,essential:true,mandatory:true},{name:'Laptop',power_w:60,duration_h:2,utility:6,essential:false,mandatory:false}]};
export async function request<T>(path:string,body?:unknown):Promise<T>{
 const response=await fetch(path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined});
 const data=await response.json();
 if(!response.ok)throw new Error(data.error?.message||`API request failed (${response.status}).`);
 return data as T;
}
