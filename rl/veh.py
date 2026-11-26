"""VEH: two-stage sizing from delta-v, propellant choice per stage."""
from dataclasses import dataclass
from math import exp
from .core import G0, PROPELLANTS

def _stage(m_pl, dv, isp, eps):
    R = exp(dv / (G0 * isp))
    if R * eps >= 1:
        return None
    k = m_pl * (R - 1) / (1 - R * eps)   # propellant + structure
    return dict(m0=m_pl + k, prop=(1 - eps) * k, struct=eps * k, mass_ratio=R, dv=dv, isp=isp)

@dataclass
class Vehicle:
    prop1: str
    prop2: str
    s1: dict
    s2: dict
    liftoff_kg: float
    thrust1_kN: float
    thrust2_kN: float
    split: float

def size(payload_kg, dv_total, prop1, prop2, isp1=None, isp2=None, tw_liftoff=1.3, tw_stage2=0.8):
    p1, p2 = PROPELLANTS[prop1], PROPELLANTS[prop2]
    isp1 = isp1 or 0.35 * p1["isp_sl"] + 0.65 * p1["isp_vac"]   # stage 1 effective
    isp2 = isp2 or p2["isp_vac"]
    best = None
    for i in range(1, 1000):
        f = i / 1000
        s2 = _stage(payload_kg, dv_total * (1 - f), isp2, p2["eps"])
        if not s2:
            continue
        s1 = _stage(s2["m0"], dv_total * f, isp1, p1["eps"])
        if not s1:
            continue
        if best is None or s1["m0"] < best[0]["m0"]:
            best = (s1, s2, f)
    if best is None:
        return None
    s1, s2, f = best
    return Vehicle(prop1, prop2, s1, s2, s1["m0"],
                   tw_liftoff * s1["m0"] * G0 / 1e3, tw_stage2 * s2["m0"] * G0 / 1e3, f)

def trade(payload_kg, dv_total, isp1=None, isp2=None):
    """Compare all propellant pairs. isp1/isp2: optional {prop: Isp [s]} from THERMO."""
    isp1, isp2 = isp1 or {}, isp2 or {}
    out = [size(payload_kg, dv_total, a, b, isp1.get(a), isp2.get(b)) for a in PROPELLANTS for b in PROPELLANTS]
    return sorted([v for v in out if v], key=lambda v: v.liftoff_kg)
