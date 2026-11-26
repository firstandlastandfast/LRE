"""CORE: constants and propellant data (preliminary estimates; THERMO will replace Isp later)."""
G0 = 9.80665          # m/s^2
MU = 3.986004418e14   # m^3/s^2, Earth
R_E = 6.371e6         # m, mean radius
OMEGA_E = 7.2921159e-5  # rad/s

# isp_sl, isp_vac [s], bulk_density [kg/m3], eps = structural fraction (inert/(inert+prop))
PROPELLANTS = {
    "kerolox":  dict(isp_sl=311, isp_vac=353, rho=1030, eps=0.06),
    "methalox": dict(isp_sl=327, isp_vac=363, rho=830,  eps=0.07),
    "hydrolox": dict(isp_sl=390, isp_vac=450, rho=360,  eps=0.12),
}

# Liquid densities [kg/m3] and typical characteristic chamber length L* [m] (preliminary)
DENS = {"LOX": 1141.0, "RP-1": 810.0, "LCH4": 422.0, "LH2": 71.0}
FUEL_OF = {"kerolox": "RP-1", "methalox": "LCH4", "hydrolox": "LH2"}
LSTAR = {"kerolox": 1.1, "methalox": 1.0, "hydrolox": 0.8}
