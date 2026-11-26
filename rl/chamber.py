"""CHAMBER: preliminary thrust chamber + nozzle sizing from thrust, Pc, O/F, eps and CEA c*."""
from math import pi, sqrt, tan, radians
from .core import G0, DENS, FUEL_OF, LSTAR

def size_chamber(prop, thrust_N, pc_bar, of, eps, isp_s, cstar, engines=1,
                 conv_half_deg=30.0, bell_frac=0.8, bell_half_deg=15.0):
    F = thrust_N / engines
    mdot = F / (G0 * isp_s)                      # kg/s per engine
    At = mdot * cstar / (pc_bar * 1e5)           # m2
    Dt = 2 * sqrt(At / pi)
    Ae = eps * At
    De = 2 * sqrt(Ae / pi)
    Dt_in = Dt / 0.0254
    ec = max(2.5, 8.0 * Dt_in ** -0.6 + 1.25)    # contraction ratio (Huzel & Huang)
    Ac = ec * At
    Dc = 2 * sqrt(Ac / pi)
    Vc = LSTAR[prop] * At                        # chamber volume (incl. convergent)
    L_conv = (Dc - Dt) / 2 / tan(radians(conv_half_deg))
    V_conv = pi * L_conv / 12 * (Dc**2 + Dc * Dt + Dt**2)
    L_cyl = max((Vc - V_conv) / Ac, 0.3 * Dc)
    L_noz = bell_frac * (De - Dt) / 2 / tan(radians(bell_half_deg))
    m_ox, m_fu = mdot * of / (1 + of), mdot / (1 + of)
    return dict(
        thrust_per_engine_kN=F / 1e3, mdot_kg_s=mdot, mdot_ox=m_ox, mdot_fuel=m_fu,
        Cf=F / (pc_bar * 1e5 * At),
        throat_dia_mm=Dt * 1e3, exit_dia_mm=De * 1e3, chamber_dia_mm=Dc * 1e3,
        contraction_ratio=ec, chamber_cyl_len_mm=L_cyl * 1e3,
        convergent_len_mm=L_conv * 1e3, nozzle_len_mm=L_noz * 1e3,
        total_len_mm=(L_cyl + L_conv + L_noz) * 1e3, chamber_vol_L=Vc * 1e3,
        ox_flow_L_s=m_ox / DENS["LOX"] * 1e3, fuel_flow_L_s=m_fu / DENS[FUEL_OF[prop]] * 1e3,
    )
