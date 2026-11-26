import streamlit as st
import pandas as pd
from rl.mission import Mission
from rl.veh import trade
from rl.thermo import best_of
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

st.subheader("THERMO (CEA)")
c1, c2 = st.columns(2)
pc1 = c1.number_input("Stage 1 chamber pressure (bar)", 5.0, 300.0, 70.0)
e1 = c1.number_input("Stage 1 nozzle expansion ratio", 2.0, 300.0, 20.0)
pc2 = c2.number_input("Stage 2 chamber pressure (bar)", 5.0, 300.0, 60.0)
e2 = c2.number_input("Stage 2 nozzle expansion ratio", 2.0, 300.0, 80.0)

rows, isp1, isp2 = [], {}, {}
for p in PROPELLANTS:
    of1, r1 = best_of(p, pc1, e1)
    of2, r2 = best_of(p, pc2, e2)
    isp1[p] = 0.35 * r1["isp_sl"] + 0.65 * r1["isp_vac"]
    isp2[p] = r2["isp_vac"]
    rows.append(dict(propellant=p, s1_best_OF=round(of1, 2), s1_isp_sl=round(r1["isp_sl"]),
                     s1_isp_vac=round(r1["isp_vac"]), s2_best_OF=round(of2, 2),
                     s2_isp_vac=round(r2["isp_vac"]),
                     s1_chamber_T_K=r1["tc"] and round(r1["tc"]), source=r1["source"]))
st.dataframe(pd.DataFrame(rows))

st.subheader("VEH / TRADE (2-stage, uses THERMO Isp, sorted by liftoff mass)")
rows = [dict(stage1=v.prop1, stage2=v.prop2, split_s1=round(v.split, 2),
             liftoff_kg=round(v.liftoff_kg), s1_prop_kg=round(v.s1["prop"]),
             s2_prop_kg=round(v.s2["prop"]), thrust1_kN=round(v.thrust1_kN, 1),
             thrust2_kN=round(v.thrust2_kN, 1)) for v in trade(payload, dv["total"], isp1, isp2)]
st.dataframe(pd.DataFrame(rows))
