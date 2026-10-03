import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import axios from "axios";

import api, { apiError, ParkingRequest, ParkingSession, Recommendation, Slot } from "./api";
import { useAuth } from "./App";

type PageProps = { title: string; description: string };

function PlaceholderPage({ title, description }: PageProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl shadow-black/20">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-300">SmartPark AI</p>
      <h1 className="mt-3 text-3xl font-bold">{title}</h1>
      <p className="mt-3 max-w-2xl text-slate-300">{description}</p>
      <div className="mt-8 rounded-xl border border-dashed border-slate-700 bg-slate-950/50 p-6 text-slate-400">
        This module is ready for the next implementation phase.
      </div>
    </section>
  );
}

export function HomePage() {
  const [health, setHealth] = useState("Checking backend health…");

  useEffect(() => {
    axios
      .get<{ status: string }>("http://localhost:8000/health")
      .then(({ data }) => setHealth(`Backend status: ${data.status}`))
      .catch(() => setHealth("Backend unavailable — start the FastAPI server to connect."));
  }, []);

  return (
    <section className="rounded-2xl border border-teal-400/30 bg-gradient-to-br from-slate-900 to-teal-950 p-8 shadow-xl shadow-teal-950/20">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-300">Intelligent parking allocation</p>
      <h1 className="mt-3 text-4xl font-bold">Find the right parking slot, not just the nearest one.</h1>
      <p className="mt-4 max-w-2xl text-slate-300">SmartPark AI will use explainable fuzzy logic to rank available parking slots.</p>
      <p className="mt-8 inline-flex rounded-full bg-slate-950/70 px-4 py-2 text-sm text-slate-200">{health}</p>
    </section>
  );
}

export const ParkingPage = () => <PlaceholderPage title="Parking" description="Submit parking requirements and explore available slots." />;

const vehicleTypes = ["Bike", "Car", "SUV", "Van", "Electric Car"];
const blankRequest: ParkingRequest = { vehicle_type: "Car", requires_ev: false, requires_accessible: false, priority: 50 };

function Header({ eyebrow, title, action }: { eyebrow: string; title: string; action?: React.ReactNode }) {
  return <div className="mb-7 flex flex-wrap items-end justify-between gap-4"><div><p className="eyebrow">{eyebrow}</p><h1 className="page-title">{title}</h1></div>{action}</div>;
}
function Problem({ text }: { text: string }) { return <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">{text}</div>; }
function useLiveSlots() {
  const [slots, setSlots] = useState<Slot[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const load = async () => { setLoading(true); try { setSlots((await api.get<Slot[]>("/api/parking/slots")).data); setError(""); } catch (e) { setError(apiError(e)); } finally { setLoading(false); } };
  useEffect(() => { void load(); }, []); return { slots, loading, error, load };
}

function OccupancyChart({ slots }: { slots: Slot[] }) {
  const occupied = slots.filter((slot) => slot.is_occupied).length;
  const data = [{ name: "Available", value: slots.length - occupied, color: "#14b8a6" }, { name: "Occupied", value: occupied, color: "#64748b" }];
  return <div className="card mt-6 h-56"><p className="mb-2 text-sm font-semibold text-slate-700">Live occupancy</p><ResponsiveContainer width="100%" height="90%"><PieChart><Pie data={data} dataKey="value" nameKey="name" innerRadius={45} outerRadius={72} paddingAngle={3}>{data.map((item) => <Cell key={item.name} fill={item.color}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer></div>;
}

export function LandingPage() {
  return <div className="min-h-screen bg-slate-950 text-white"><header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5"><b>SMARTPARK <span className="text-teal-400">AI</span></b><div className="flex gap-4"><Link to="/login" className="text-sm text-slate-300">Sign in</Link><Link to="/register" className="btn-primary">Create account</Link></div></header><main className="mx-auto grid max-w-7xl gap-12 px-6 py-20 lg:grid-cols-2"><section><p className="eyebrow text-teal-300">Explainable intelligent parking</p><h1 className="mt-4 text-5xl font-bold leading-tight">Intelligent Parking<br/>Slot Allocation</h1><p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">A fuzzy-logic parking engine that weighs distance, congestion, compatibility, walking distance, and priority.</p><div className="mt-8 flex gap-3"><Link className="btn-primary" to="/find-parking">Find Parking</Link><Link className="btn-dark-outline" to="/how-ai-works">Explore AI</Link></div></section><section className="rounded-3xl border border-slate-700 bg-slate-900 p-6"><p className="text-sm font-semibold text-teal-300">DECISION SIGNALS</p><div className="mt-6 grid grid-cols-2 gap-3">{["Distance", "Congestion", "Compatibility", "Priority"].map((x) => <div className="rounded-xl bg-slate-800 p-4" key={x}><b>{x}</b><p className="mt-1 text-xs text-slate-400">Used in each real score</p></div>)}</div><p className="mt-5 rounded-xl bg-teal-400/10 p-4 text-sm text-teal-100">Scores and explanations come directly from the SmartPark AI backend.</p></section></main></div>;
}

function AuthForm({ register }: { register?: boolean }) {
  const navigate = useNavigate(); const { refresh } = useAuth(); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const f = new FormData(event.currentTarget); setBusy(true); setError(""); try { if (register) await api.post("/api/auth/register", { username: f.get("username"), email: f.get("email"), password: f.get("password"), role: "USER" }); const token = await api.post<{ access_token: string }>("/api/auth/login", { username: f.get("username"), password: f.get("password") }); localStorage.setItem("smartpark_token", token.data.access_token); await refresh(); navigate("/dashboard"); } catch (e) { setError(apiError(e)); } finally { setBusy(false); } };
  return <div className="auth-shell"><form className="card w-full max-w-md p-7" onSubmit={submit}><Link to="/" className="font-bold">SMARTPARK <span className="text-teal-600">AI</span></Link><h1 className="mt-7 text-2xl font-bold">{register ? "Create account" : "Welcome back"}</h1>{error && <p className="mt-4"><Problem text={error} /></p>}<label className="field">Username<input name="username" required minLength={3}/></label>{register && <label className="field">Email<input name="email" type="email" required/></label>}<label className="field">Password<input name="password" type="password" required minLength={8}/></label><button className="btn-primary mt-6 w-full" disabled={busy}>{busy ? "Please wait…" : register ? "Create account" : "Sign in"}</button><p className="mt-5 text-center text-sm text-slate-500">{register ? "Already registered?" : "New here?"} <Link className="text-teal-700" to={register ? "/login" : "/register"}>{register ? "Sign in" : "Register"}</Link></p></form></div>;
}
export const LoginPage = () => <AuthForm />;
export const RegisterPage = () => <AuthForm register />;

export function DashboardPage() {
  const { slots, loading, error, load } = useLiveSlots(); const values = useMemo(() => { const available = slots.filter((x) => !x.is_occupied).length; const occupied = slots.length - available; return [["Total Slots", slots.length], ["Available", available], ["Occupied", occupied], ["EV", slots.filter((x) => x.is_ev).length], ["Accessible", slots.filter((x) => x.is_accessible).length], ["Occupancy %", slots.length ? `${Math.round(100 * occupied / slots.length)}%` : "—"]]; }, [slots]);
  return <><Header eyebrow="Live overview" title="Parking dashboard" action={<Link className="btn-primary" to="/find-parking">Find parking</Link>}/>{loading ? <p>Loading live slot data…</p> : error ? <Problem text={error} /> : <><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{values.map(([name, value]) => <div className="card" key={String(name)}><p className="text-sm text-slate-500">{name}</p><p className="mt-2 text-3xl font-bold">{value}</p></div>)}</div><OccupancyChart slots={slots}/><button className="btn-secondary mt-6" onClick={() => void load()}>Refresh live data</button></>}</>;
}

export function FindParkingPage() {
  const navigate = useNavigate(); const [request, setRequest] = useState<ParkingRequest>(blankRequest); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  const submit = async (event: FormEvent) => { event.preventDefault(); setBusy(true); setError(""); try { const result = await api.post<{ recommendations: Recommendation[] }>("/api/parking/recommend", request); sessionStorage.setItem("smartpark_recommendations", JSON.stringify({ request, recommendations: result.data.recommendations })); navigate("/recommendations"); } catch (e) { setError(apiError(e)); } finally { setBusy(false); } };
  return <><Header eyebrow="Parking request" title="Find the right slot"/><form className="card grid gap-5 md:grid-cols-2" onSubmit={submit}>{error && <div className="md:col-span-2"><Problem text={error}/></div>}<label className="field">Vehicle number<input placeholder="MH 12 AB 1234" /></label><label className="field">Vehicle type<select value={request.vehicle_type} onChange={(e) => setRequest({...request, vehicle_type: e.target.value})}>{vehicleTypes.map((x) => <option key={x}>{x}</option>)}</select></label><label className="field">Vehicle size<select><option>Standard</option><option>Large</option></select></label><label className="field">Parking duration<select><option>Up to 1 hour</option><option>1–3 hours</option><option>3+ hours</option></select></label><label className="field">Priority: {request.priority}<input type="range" min="0" max="100" value={request.priority} onChange={(e) => setRequest({...request, priority: +e.target.value})}/></label><div className="flex items-end gap-5"><label className="check"><input type="checkbox" checked={request.requires_ev} onChange={(e) => setRequest({...request, requires_ev: e.target.checked})}/> EV required</label><label className="check"><input type="checkbox" checked={request.requires_accessible} onChange={(e) => setRequest({...request, requires_accessible: e.target.checked})}/> Accessibility</label></div><p className="text-xs text-slate-500 md:col-span-2">Current backend matching uses vehicle type, EV/accessibility needs, and priority. Details are retained for the request flow.</p><button className="btn-primary w-fit md:col-span-2" disabled={busy}>{busy ? "Calculating…" : "Get AI recommendations"}</button></form></>;
}

export function RecommendationsPage() {
  const navigate = useNavigate(); const stored = sessionStorage.getItem("smartpark_recommendations"); const data = stored ? JSON.parse(stored) as { request: ParkingRequest; recommendations: Recommendation[] } : null; const [busy, setBusy] = useState<number | null>(null); const [notice, setNotice] = useState(""); const [error, setError] = useState("");
  const allocate = async (item: Recommendation) => { if (!data) return; setBusy(item.slot_id); try { const r = await api.post("/api/parking/allocate", { selected_slot_id: item.slot_id, ...data.request }); setNotice(`Slot ${r.data.slot} is allocated and your parking session has started.`); } catch (e) { setError(apiError(e)); } finally { setBusy(null); } };
  if (!data) return <><Header eyebrow="AI results" title="No current recommendation"/><div className="card"><p className="text-slate-600">Submit a parking request to get live recommendations.</p><Link className="btn-primary mt-5" to="/find-parking">Find parking</Link></div></>;
  return <><Header eyebrow="Fuzzy logic results" title="Your top recommendations" action={<Link className="btn-secondary" to="/map">View map</Link>}/>{notice && <p className="mb-4 rounded-xl bg-emerald-50 p-4 text-emerald-800">{notice}</p>}{error && <div className="mb-4"><Problem text={error}/></div>}<div className="grid gap-4 xl:grid-cols-3">{data.recommendations.map((item, i) => { const f = item.factors as Record<string, number>; return <article className="card" key={item.slot_id}><div className="flex justify-between"><div><p className="eyebrow">#{i + 1} recommendation</p><h2 className="mt-1 text-2xl font-bold">{item.slot}</h2></div><b className="score-badge">{item.score}</b></div><p className="mt-3 font-semibold text-teal-700">{item.category}</p><div className="mt-5 grid grid-cols-2 gap-3 text-sm">{[["Distance", `${f.distance ?? "—"}m`], ["Congestion", `${f.congestion ?? "—"}%`], ["Compatibility", `${f.compatibility ?? "—"}%`], ["Walking", `${f.walking_distance ?? "—"}m`]].map(([a,b]) => <p key={a}><span className="text-slate-500">{a}</span><br/><b>{b}</b></p>)}</div><p className="mt-5 border-t pt-4 text-sm leading-6 text-slate-600">{item.reason}</p><button className="btn-primary mt-5 w-full" disabled={busy !== null || Boolean(notice)} onClick={() => void allocate(item)}>{busy === item.slot_id ? "Allocating…" : notice ? "Allocated" : "Select"}</button></article>; })}</div></>;
}

function LegacyParkingMapPage() {
  const { slots, loading, error, load } = useLiveSlots(); const stored = sessionStorage.getItem("smartpark_recommendations"); const recommended = new Set((stored ? JSON.parse(stored).recommendations : []).map((x: Recommendation) => x.slot_id));
  return <><Header eyebrow="Live slot layout" title="Parking map" action={<button className="btn-secondary" onClick={() => void load()}>Refresh</button>}/><div className="mb-5 flex flex-wrap gap-4 text-xs text-slate-600"><span>■ Available</span><span>■ Occupied</span><span className="text-teal-700">■ Recommended</span><span className="text-violet-700">■ EV</span><span className="text-amber-700">■ Accessible</span></div>{loading ? <p>Loading map…</p> : error ? <Problem text={error}/> : slots.length ? <div className="grid grid-cols-3 gap-3 sm:grid-cols-5 lg:grid-cols-8">{slots.map((slot) => { const state = recommended.has(slot.id) ? "slot-recommended" : slot.is_occupied ? "slot-occupied" : slot.is_accessible ? "slot-accessible" : slot.is_ev ? "slot-ev" : "slot-available"; return <div className={`slot ${state}`} title={`${slot.slot_number}: ${slot.is_occupied ? "occupied" : "available"}`} key={slot.id}><b>{slot.slot_number}</b><span>{slot.is_occupied ? "Occupied" : "Available"}</span></div>; })}</div> : <div className="card text-slate-600">No slots are in the database yet. An admin can add them from the Admin dashboard.</div>}</>;
}

export function HistoryPage() {
  const [sessions, setSessions] = useState<ParkingSession[]>([]); const [error, setError] = useState(""); const [loading, setLoading] = useState(true);
  const load = async () => { setLoading(true); try { setSessions((await api.get<ParkingSession[]>("/api/parking/history")).data); setError(""); } catch (e) { setError(apiError(e)); } finally { setLoading(false); } }; useEffect(() => { void load(); }, []);
  const release = async (slotId: number) => { try { await api.post("/api/parking/release", { slot_id: slotId }); await load(); } catch (e) { setError(apiError(e)); } };
  return <><Header eyebrow="Your activity" title="Parking history"/>{loading ? <p>Loading history…</p> : error ? <Problem text={error}/> : <div className="card overflow-x-auto"><table><thead><tr><th>Slot ID</th><th>Vehicle</th><th>Priority</th><th>Started</th><th>Status</th><th></th></tr></thead><tbody>{sessions.map((s) => <tr key={s.id}><td>{s.slot_id}</td><td>{s.vehicle_type}</td><td>{s.priority}</td><td>{new Date(s.started_at).toLocaleString()}</td><td>{s.ended_at ? "Released" : "Active"}</td><td>{!s.ended_at && <button className="btn-secondary" onClick={() => void release(s.slot_id)}>Release</button>}</td></tr>)}</tbody></table>{!sessions.length && <p className="text-slate-500">No parking sessions yet.</p>}</div>}</>;
}

function LegacyAiSimulatorPage() {
  const [values, setValues] = useState({ distance: 40, congestion: 20, compatibility: 90, walking_distance: 40, priority: 70 }); const [result, setResult] = useState<{ score: number; category: string; explanation: string } | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const calculate = async () => { setBusy(true); try { setResult((await api.post("/api/ai/calculate-score", values)).data); setError(""); } catch (e) { setError(apiError(e)); } finally { setBusy(false); } };
  return <><Header eyebrow="Interactive fuzzy logic" title="AI simulator"/><div className="grid gap-6 lg:grid-cols-[1fr_.8fr]"><section className="card"><p className="text-sm text-slate-600">Adjust a real fuzzy-engine input set, then calculate a deterministic suitability score.</p><div className="mt-6 grid gap-4">{Object.entries(values).map(([key, value]) => <label className="field capitalize" key={key}>{key.replace("_", " ")}: {value}<input type="range" min="0" max={key.includes("distance") ? "200" : "100"} value={value} onChange={(e) => setValues({...values, [key]: +e.target.value})}/></label>)}</div><button className="btn-primary mt-5" onClick={() => void calculate()} disabled={busy}>{busy ? "Calculating…" : "Calculate score"}</button></section><section className="card">{error && <Problem text={error}/>} {result ? <><p className="eyebrow">Engine result</p><p className="mt-3 text-5xl font-bold text-teal-700">{result.score}</p><p className="mt-2 font-semibold">{result.category}</p><p className="mt-5 text-sm leading-6 text-slate-600">{result.explanation}</p></> : <p className="text-slate-500">Run a calculation to see the live fuzzy-engine result.</p>}</section></div></>;
}

export function HowAiWorksPage() {
  const [rules, setRules] = useState<{ id: string; description: string; consequent: string }[]>([]); const [error, setError] = useState(""); useEffect(() => { api.get<{ rules: { id: string; description: string; consequent: string }[] }>("/api/ai/rules").then((r) => setRules(r.data.rules)).catch((e) => setError(apiError(e))); }, []);
  return <><Header eyebrow="Explainability" title="How SmartPark AI works"/><div className="grid gap-5 lg:grid-cols-2"><section className="card"><ol className="space-y-4">{["Fuzzify distance, congestion, compatibility, walking distance, and priority.", "Evaluate the documented fuzzy rules with Mamdani inference.", "Aggregate the activated rules and use centroid defuzzification.", "Rank only compatible, available slots and explain the result."].map((x, i) => <li className="flex gap-4" key={x}><span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-teal-100 font-bold text-teal-800">{i+1}</span><p className="text-sm leading-6 text-slate-700">{x}</p></li>)}</ol></section><section className="card"><p className="eyebrow">Live rule set</p>{error ? <Problem text={error}/> : <div className="mt-4 space-y-3">{rules.map((r) => <div className="border-b pb-3 text-sm" key={r.id}><b>{r.id} · {r.consequent}</b><p className="mt-1 text-slate-600">{r.description}</p></div>)}</div>}</section></div></>;
}

export function AdminPage() {
  const { slots, loading, error, load } = useLiveSlots(); const [stats, setStats] = useState<{total_slots:number;available_slots:number;occupied_slots:number;fuzzy_rules:number} | null>(null); const [newSlot, setNewSlot] = useState({ slot_number:"", vehicle_type:"Car", distance_from_entrance:50, walking_distance:50, congestion_level:10 }); const [message, setMessage] = useState("");
  const loadStats = async () => { try { setStats((await api.get("/api/ai/statistics")).data); } catch (e) { setMessage(apiError(e)); } }; useEffect(() => { void loadStats(); }, []);
  const create = async (e: FormEvent) => { e.preventDefault(); try { await api.post("/api/parking/slots", newSlot); setMessage("Parking slot created."); setNewSlot({...newSlot, slot_number:""}); await load(); await loadStats(); } catch (x) { setMessage(apiError(x)); } };
  const toggle = async (slot: Slot) => { try { await api.patch(`/api/parking/slots/${slot.id}/status`, { is_occupied: !slot.is_occupied }); await load(); await loadStats(); } catch (e) { setMessage(apiError(e)); } };
  return <><Header eyebrow="Administrator" title="Admin dashboard"/>{stats && <div className="grid gap-4 sm:grid-cols-4">{Object.entries(stats).map(([k,v]) => <div className="card" key={k}><p className="text-xs text-slate-500">{k.replaceAll("_", " ")}</p><p className="mt-1 text-2xl font-bold">{v}</p></div>)}</div>}<div className="mt-6 grid gap-6 lg:grid-cols-[.8fr_1.2fr]"><form className="card grid gap-3" onSubmit={create}><h2 className="font-semibold">Add parking slot</h2><label className="field">Slot number<input required value={newSlot.slot_number} onChange={e => setNewSlot({...newSlot, slot_number:e.target.value})}/></label><label className="field">Vehicle type<select value={newSlot.vehicle_type} onChange={e => setNewSlot({...newSlot, vehicle_type:e.target.value})}>{vehicleTypes.map(x => <option key={x}>{x}</option>)}</select></label><label className="field">Distance<input type="number" value={newSlot.distance_from_entrance} onChange={e => setNewSlot({...newSlot, distance_from_entrance:+e.target.value})}/></label><label className="field">Walking distance<input type="number" value={newSlot.walking_distance} onChange={e => setNewSlot({...newSlot, walking_distance:+e.target.value})}/></label><label className="field">Congestion<input type="number" value={newSlot.congestion_level} onChange={e => setNewSlot({...newSlot, congestion_level:+e.target.value})}/></label><button className="btn-primary">Create slot</button>{message && <p className="text-sm text-slate-600">{message}</p>}</form><section className="card overflow-x-auto"><h2 className="mb-3 font-semibold">Slot status</h2>{loading ? "Loading…" : error ? <Problem text={error}/> : <table><thead><tr><th>Slot</th><th>Vehicle</th><th>State</th><th></th></tr></thead><tbody>{slots.map(s => <tr key={s.id}><td>{s.slot_number}</td><td>{s.vehicle_type}</td><td>{s.is_occupied ? "Occupied" : "Available"}</td><td><button className="btn-secondary" onClick={() => void toggle(s)}>Mark {s.is_occupied ? "free" : "occupied"}</button></td></tr>)}</tbody></table>}</section></div></>;
}

type FuzzyResult = {
  score: number; category: string; explanation: string;
  membership_values: Record<string, Record<string, number>>;
  activated_rules: { id: string; strength: number; consequent: string; description: string }[];
};

export function AiSimulatorPage() {
  const [values, setValues] = useState({ distance: 35, congestion: 20, compatibility: 90, walking_distance: 40, priority: 70 });
  const [result, setResult] = useState<FuzzyResult | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(true);
  useEffect(() => {
    const timeout = window.setTimeout(async () => { setBusy(true); try { const response = await api.post<FuzzyResult>("/api/ai/calculate-score", values); setResult(response.data); setError(""); } catch (e) { setError(apiError(e)); } finally { setBusy(false); } }, 250);
    return () => window.clearTimeout(timeout);
  }, [values]);
  const update = (key: keyof typeof values, value: number) => setValues({ ...values, [key]: value });
  const distanceChart = result ? Object.entries(result.membership_values.distance).map(([term, value]) => ({ term, value: Math.round(value * 100) })) : [];
  return <><Header eyebrow="Interactive fuzzy inference" title="Fuzzy Logic Parking Simulator"/><p className="mb-6 max-w-3xl text-sm leading-6 text-slate-600">Every slider adjustment calls the actual Python fuzzy engine. Values below are returned by FastAPI; no suitability values are calculated in React.</p><div className="grid gap-6 lg:grid-cols-[.85fr_1.15fr]"><section className="card"><p className="eyebrow">Input values</p><div className="mt-5 grid gap-5">{([['distance','Distance',200,'m'],['congestion','Congestion',100,''],['compatibility','Compatibility',100,''],['walking_distance','Walking distance',200,'m'],['priority','Priority',100,'']] as const).map(([key,label,max,unit]) => <label className="field" key={key}>{label}: {values[key]}{unit}<input type="range" min="0" max={max} value={values[key]} onChange={(e) => update(key, Number(e.target.value))}/></label>)}</div><p className="mt-5 text-xs text-slate-500">{busy ? "Calling fuzzy engine…" : "Live result received from the backend."}</p></section><section>{error && <Problem text={error}/>} {result && <div className="space-y-5"><div className="card"><p className="eyebrow">Defuzzification</p><div className="mt-3 flex items-end justify-between"><div><p className="text-5xl font-bold text-teal-700">{result.score}</p><p className="mt-1 font-semibold">Decision: {result.category}</p></div><span className="score-badge">0–100</span></div><p className="mt-4 text-sm leading-6 text-slate-600">{result.explanation}</p></div><div className="card"><p className="eyebrow">Fuzzification</p><div className="mt-4 grid gap-4 md:grid-cols-2">{Object.entries(result.membership_values).map(([name, terms]) => <div className="rounded-xl bg-slate-50 p-3" key={name}><b className="capitalize">{name.replace("_", " ")}</b>{Object.entries(terms).map(([term,value]) => <p className="mt-1 flex justify-between text-sm" key={term}><span>{term}</span><span className="font-semibold">{value.toFixed(4)}</span></p>)}</div>)}</div></div><div className="card h-64"><p className="eyebrow">Distance membership</p><ResponsiveContainer width="100%" height="88%"><BarChart data={distanceChart}><XAxis dataKey="term"/><YAxis domain={[0,100]}/><Tooltip/><Bar dataKey="value" name="Membership %" fill="#0f766e" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div><div className="card"><p className="eyebrow">Rule activation</p><div className="mt-4 space-y-3">{result.activated_rules.map((rule) => <div className="border-b border-slate-100 pb-3 text-sm" key={rule.id}><div className="flex justify-between"><b>{rule.id} → {rule.consequent}</b><b className="text-teal-700">{rule.strength.toFixed(4)}</b></div><p className="mt-1 text-slate-600">{rule.description}</p></div>)}</div></div></div>}</section></div></>;
}

function ModuleSixParkingMapPage() {
  const { slots, loading, error, load } = useLiveSlots(); const [selected, setSelected] = useState<Slot | null>(null);
  const stored = sessionStorage.getItem("smartpark_recommendations"); const recommended = new Set((stored ? JSON.parse(stored).recommendations : []).map((item: Recommendation) => item.slot_id));
  const slotByNumber = new Map(slots.map((slot) => [slot.slot_number, slot])); const layout = ["A", "B", "C", "D"].map((row) => Array.from({ length: 5 }, (_, index) => `${row}${String(index + 1).padStart(2, "0")}`));
  return <><Header eyebrow="Interactive parking lot" title="Parking map" action={<button className="btn-secondary" onClick={() => void load()}>Refresh live status</button>}/><div className="mb-5 flex flex-wrap gap-4 text-xs text-slate-600"><span className="text-emerald-700">■ Available</span><span className="text-slate-600">■ Occupied</span><span className="text-teal-700">■ Recommended</span><span className="text-violet-700">■ EV</span><span className="text-amber-700">■ Accessible</span></div>{loading ? <p>Loading live parking layout…</p> : error ? <Problem text={error}/> : <div className="grid gap-6 lg:grid-cols-[1fr_260px]"><section className="card"><div className="mb-6 rounded-xl border-2 border-dashed border-teal-300 bg-teal-50 py-3 text-center text-sm font-bold tracking-[0.25em] text-teal-800">ENTRANCE</div><div className="space-y-4">{layout.map((row) => <div className="grid grid-cols-5 gap-3" key={row[0]}>{row.map((number) => { const slot = slotByNumber.get(number); if (!slot) return <div className="slot border-dashed text-slate-400" key={number}>{number}<span>Unconfigured</span></div>; const state = recommended.has(slot.id) ? "slot-recommended" : slot.is_occupied ? "slot-occupied" : slot.is_accessible ? "slot-accessible" : slot.is_ev ? "slot-ev" : "slot-available"; return <button className={`slot ${state}`} aria-pressed={selected?.id === slot.id} onClick={() => setSelected(slot)} key={slot.id}><b>{slot.slot_number}</b><span>{slot.is_occupied ? "OCCUPIED" : "AVAILABLE"}</span><span>{slot.slot_type}{slot.is_ev ? " · EV" : ""}{slot.is_accessible ? " · Accessible" : ""}</span></button>; })}</div>)}</div></section><aside className="card h-fit"><p className="eyebrow">Slot details</p>{selected ? <div className="mt-4 space-y-2 text-sm"><h2 className="text-2xl font-bold">{selected.slot_number}</h2><p><b>Availability:</b> {selected.is_occupied ? "Occupied" : "Available"}</p><p><b>Type:</b> {selected.slot_type}</p><p><b>Vehicle:</b> {selected.vehicle_type}</p><p><b>EV:</b> {selected.is_ev ? "Yes" : "No"}</p><p><b>Accessible:</b> {selected.is_accessible ? "Yes" : "No"}</p><p><b>Distance:</b> {selected.distance_from_entrance}m</p><p><b>Congestion:</b> {selected.congestion_level}%</p></div> : <p className="mt-4 text-sm text-slate-500">Select a slot to inspect its real API data.</p>}</aside></div>}</>;
}

export function ParkingMapPage() {
  const { slots, loading, error, load } = useLiveSlots();
  const [selected, setSelected] = useState<Slot | null>(null);
  const stored = sessionStorage.getItem("smartpark_recommendations");
  const recommended = new Set((stored ? JSON.parse(stored).recommendations : []).map((item: Recommendation) => item.slot_id));
  const byNumber = new Map(slots.map((slot) => [slot.slot_number, slot]));
  const rows = ["A", "B", "C", "D"].map((letter) => Array.from({ length: 5 }, (_, i) => `${letter}${String(i + 1).padStart(2, "0")}`));
  const visualState = (slot: Slot) => recommended.has(slot.id) ? "slot-recommended" : slot.is_reserved ? "slot-reserved" : slot.is_occupied ? "slot-occupied" : slot.is_accessible ? "slot-accessible" : slot.is_ev ? "slot-ev" : "slot-available";
  const availability = (slot: Slot) => slot.is_reserved ? "RESERVED" : slot.is_occupied ? "OCCUPIED" : "AVAILABLE";
  return <><Header eyebrow="Interactive parking lot" title="Parking map" action={<button className="btn-secondary" onClick={() => void load()}>Refresh live status</button>}/>
    <div className="mb-5 flex flex-wrap gap-4 text-xs"><span className="text-emerald-700">■ Available</span><span className="text-slate-600">■ Occupied</span><span className="text-rose-700">■ Reserved</span><span className="text-teal-700">■ Recommended</span><span className="text-violet-700">■ EV</span><span className="text-amber-700">■ Accessible</span></div>
    {loading ? <p>Loading live parking layout…</p> : error ? <Problem text={error}/> : <div className="grid gap-6 lg:grid-cols-[1fr_260px]"><section className="card"><div className="mb-6 rounded-xl border-2 border-dashed border-teal-300 bg-teal-50 py-3 text-center text-sm font-bold tracking-[0.25em] text-teal-800">ENTRANCE</div><div className="space-y-4">{rows.map((row) => <div className="grid grid-cols-5 gap-3" key={row[0]}>{row.map((number) => { const slot = byNumber.get(number); return slot ? <button className={`slot ${visualState(slot)}`} aria-pressed={selected?.id === slot.id} onClick={() => setSelected(slot)} key={slot.id}><b>{slot.slot_number}</b><span>{availability(slot)}</span><span>{slot.slot_type}{slot.is_ev ? " · EV" : ""}{slot.is_accessible ? " · Accessible" : ""}</span></button> : <div className="slot border-dashed text-slate-400" key={number}><b>{number}</b><span>Unconfigured</span></div>; })}</div>)}</div></section><aside className="card h-fit"><p className="eyebrow">Slot details</p>{selected ? <div className="mt-4 space-y-2 text-sm"><h2 className="text-2xl font-bold">{selected.slot_number}</h2><p><b>Availability:</b> {availability(selected)}</p><p><b>Type:</b> {selected.slot_type}</p><p><b>Vehicle:</b> {selected.vehicle_type}</p><p><b>EV:</b> {selected.is_ev ? "Yes" : "No"}</p><p><b>Accessible:</b> {selected.is_accessible ? "Yes" : "No"}</p><p><b>Distance:</b> {selected.distance_from_entrance}m</p><p><b>Congestion:</b> {selected.congestion_level}%</p></div> : <p className="mt-4 text-sm text-slate-500">Select a slot to inspect its real API data.</p>}</aside></div>}</>;
}
