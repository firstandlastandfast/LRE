"""MISSION: payload + orbit altitude -> required delta-v."""
from dataclasses import dataclass
from math import sqrt, cos, radians
from .core import MU, R_E, OMEGA_E

@dataclass
class Mission:
    payload_kg: float
    altitude_km: float
    launch_lat_deg: float = 28.5
    gravity_loss: float = 1200.0   # m/s, adjustable estimate
    drag_loss: float = 150.0       # m/s
    steering_loss: float = 100.0   # m/s

    def delta_v(self) -> dict:
        r = R_E + self.altitude_km * 1e3
        v_circ = sqrt(MU / r)
        d_phi = MU * (1 / R_E - 1 / r)
        ideal = sqrt(v_circ**2 + 2 * d_phi)  # kinetic + potential energy gain
        rot = OMEGA_E * R_E * cos(radians(self.launch_lat_deg))  # eastward launch
        losses = self.gravity_loss + self.drag_loss + self.steering_loss
        return dict(v_circ=v_circ, ideal=ideal, rotation_bonus=rot,
                    losses=losses, total=ideal + losses - rot)
