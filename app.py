import streamlit as st
import pandas as pd
from rl.mission import Mission
from rl.veh import trade
from rl.thermo import best_of, HAS_CEA
from rl.core import PROPELLANTS

st.title("RL - RocketLab")
payload = st.number_input("Payload mass (kg)", 1.0, 1e6, 100.0)
alt = st.number_input("Orbit altitude (km)", 100.0, 40000.0, 400.0)
with st.expander("MISSION assumptions"):
    lat = st.number_input("Launch latitude (deg)", 0.0, 90.0, 28.5)
    gl = st.number_input("Gravity loss (m/s)", 0.0, 3000.0, 1200.0)
    dl = st.number_input("Drag loss (m/s)", 0.0, 1000.0, 150.0)
    sl = st.number_input("Steering loss (m/s)", 0.0, 1000.0, 100.0)

dv = Mission(payload, alt, lat, gl, dl, sl).delta_v()
st.subheader("MISSION")
st.json({k: round(v, 1) for k, v in dv.items()})

st.subheader("VEH / TRADE (2-stage, sorted by liftoff mass)")
rows = [dict(stage1=v.prop1, stage2=v.prop2, split_s1=round(v.split, 2),
             liftoff_kg=round(v.liftoff_kg), s1_prop_kg=round(v.s1["prop"]),
             s2_prop_kg=round(v.s2["prop"]), thrust1_kN=round(v.thrust1_kN, 1),
             thrust2_kN=round(v.thrust2_kN, 1)) for v in trade(payload, dv["total"])]
st.dataframe(pd.DataFrame(rows))

st.subheader("THERMO")
pc = st.number_input("Chamber pressure (bar)", 5.0, 300.0, 70.0)
eps = st.number_input("Nozzle expansion ratio", 2.0, 300.0, 40.0)
if not HAS_CEA:
    st.warning("RocketCEA not available: showing placeholder values.")
rows = []
for p in PROPELLANTS:
    of, r = best_of(p, pc, eps)
    rows.append(dict(propellant=p, best_OF=round(of, 2), isp_vac_s=round(r["isp_vac"]),
                     isp_sl_s=round(r["isp_sl"]), cstar_ms=r["cstar"] and round(r["cstar"]),
                     chamber_T_K=r["tc"] and round(r["tc"]), source=r["source"]))
st.dataframe(pd.DataFrame(rows))
