"""THERMO: combustion performance via NASA CEA (pip package `cea`).
Falls back to CORE placeholders if CEA is missing or errors (error is shown in `source`)."""
from functools import lru_cache
from .core import PROPELLANTS, G0

# fuel name, fuel temp [K]; oxidizer is always liquid O2 at 90.17 K
FUELS = {"kerolox": ("RP-1", 298.15), "methalox": ("CH4(L)", 111.64), "hydrolox": ("H2(L)", 20.27)}
OX = ("O2(L)", 90.17)
OF_RANGE = {"kerolox": (1.8, 3.2), "methalox": (2.4, 4.2), "hydrolox": (3.5, 8.0)}
P_AMB_BAR = 1.01325

try:
    import numpy as np
    import cea
    HAS_CEA = True
except Exception:
    HAS_CEA = False

@lru_cache(maxsize=None)
def _setup(prop):
    fuel, tf = FUELS[prop]
    names = [fuel, OX[0]]
    try:
        reac = cea.Mixture(names)
    except Exception:
        names = [n.encode() for n in names]   # older API wants bytes
        reac = cea.Mixture(names)
    prod = cea.Mixture(names, products_from_reactants=True)
    return reac, prod, np.array([tf, OX[1]])

def perf(prop, pc_bar, of, eps):
    """Isp (sea level & vacuum) [s], c* [m/s], chamber temp [K] for given Pc [bar], O/F, expansion ratio."""
    fallback = PROPELLANTS[prop]
    if not HAS_CEA:
        return dict(isp_sl=fallback["isp_sl"], isp_vac=fallback["isp_vac"], cstar=None, tc=None, source="placeholder")
    try:
        reac, prod, temps = _setup(prop)
        solver = cea.RocketSolver(prod, reactants=reac)
        sol = cea.RocketSolution(solver)
        w = reac.of_ratio_to_weights(np.array([0.0, 1.0]), np.array([1.0, 0.0]), of)
        hc = reac.calc_property(cea.ENTHALPY, w, temps) / cea.R
        solver.solve(sol, w, pc_bar, [10.0], supar=[eps], hc=hc, iac=True)
        if not sol.converged:
            raise RuntimeError("CEA did not converge")
        isp_vac = float(sol.Isp_vacuum[-1])      # m/s at the supar station
        cstar = float(sol.c_star[-1])
        isp_sl = isp_vac - P_AMB_BAR * eps * cstar / pc_bar   # subtract ambient-pressure loss
        return dict(isp_sl=isp_sl / G0, isp_vac=isp_vac / G0, cstar=cstar, tc=float(sol.T[0]), source="CEA")
    except Exception as e:
        return dict(isp_sl=fallback["isp_sl"], isp_vac=fallback["isp_vac"], cstar=None, tc=None,
                    source=f"placeholder (CEA error: {e})")

def best_of(prop, pc_bar, eps, n=15):
    """Sweep O/F for max vacuum Isp."""
    lo, hi = OF_RANGE[prop]
    best = None
    for i in range(n):
        of = lo + (hi - lo) * i / (n - 1)
        r = perf(prop, pc_bar, of, eps)
        if best is None or r["isp_vac"] > best[1]["isp_vac"]:
            best = (of, r)
        if r["source"] != "CEA":
            break
    return best
