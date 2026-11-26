"""THERMO: combustion performance via RocketCEA (falls back to CORE placeholders if unavailable)."""
from .core import PROPELLANTS

NAMES = {"kerolox": ("LOX", "RP-1"), "methalox": ("LOX", "CH4"), "hydrolox": ("LOX", "H2")}
OF_RANGE = {"kerolox": (1.8, 3.2), "methalox": (2.4, 4.2), "hydrolox": (3.5, 8.0)}
BAR_TO_PSIA = 14.5038
FTS_TO_MS = 0.3048
R_TO_K = 1 / 1.8

try:
    from rocketcea.cea_obj import CEA_Obj
    HAS_CEA = True
except Exception:
    HAS_CEA = False

def perf(prop, pc_bar, of, eps):
    """Isp (sea level & vacuum), c*, chamber temp at given Pc [bar], O/F, expansion ratio."""
    if not HAS_CEA:
        p = PROPELLANTS[prop]
        return dict(isp_sl=p["isp_sl"], isp_vac=p["isp_vac"], cstar=None, tc=None, source="placeholder")
    ox, fu = NAMES[prop]
    c = CEA_Obj(oxName=ox, fuelName=fu)
    pc = pc_bar * BAR_TO_PSIA
    isp_vac, cstar, tc = c.get_IvacCstrTc(Pc=pc, MR=of, eps=eps)
    isp_sl = c.estimate_Ambient_Isp(Pc=pc, MR=of, eps=eps, Pamb=14.696)[0]
    return dict(isp_sl=isp_sl, isp_vac=isp_vac, cstar=cstar * FTS_TO_MS, tc=tc * R_TO_K, source="CEA")

def best_of(prop, pc_bar, eps, n=25):
    """Sweep O/F for max vacuum Isp."""
    lo, hi = OF_RANGE[prop]
    best = None
    for i in range(n):
        of = lo + (hi - lo) * i / (n - 1)
        r = perf(prop, pc_bar, of, eps)
        if best is None or r["isp_vac"] > best[1]["isp_vac"]:
            best = (of, r)
        if not HAS_CEA:
            break
    return best
