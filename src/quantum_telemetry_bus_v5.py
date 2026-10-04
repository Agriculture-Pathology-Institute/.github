# File Path: src/quantum_telemetry_bus.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Closed-Loop Spatial & Atmospheric Telemetry Processing Fabric.

Ingests non-linear polyhedral keep-in bounds, models power-law crosswind 
shear forces, and pipes critical alerts straight into Univac JSON streams.
"""

import os
import sys
import json
import time
import math

class QuantumTelemetryBus:
    def __init__(self, export_directory="Data/UnivacStreams/"):
        self.export_directory = export_directory
        self.hex_states = {f"0x{i:X}": i * 0.0625 for i in range(16)}
        
        # 8-Point Arbitrary Polyhedral Boundary Vertex Matrix (Millimeters)
        # Matches the dynamic keep-in grid parameters registered at the county
        self.poly_vertices = [
            {"x": 100000, "y": 100000},
            {"x": 500000, "y": 120000},
            {"x": 480000, "y": 350000},
            {"x": 120000, "y": 320000}
        ]
        
        # Enforce isolated directory path structures for Univac log output
        if not os.path.exists(self.export_directory):
            os.makedirs(self.export_directory, exist_ok=True)

    def verify_point_in_polyhedral_bounds(self, test_x, test_y):
        """Executes a high-precision ray-casting boundary intersection validation check."""
        num_vtx = len(self.poly_vertices)
        inside = False
        p1x = self.poly_vertices[0]["x"]
        p1y = self.poly_vertices[0]["y"]
        
        for i in range(num_vtx + 1):
            p2x = self.poly_vertices[i % num_vtx]["x"]
            p2y = self.poly_vertices[i % num_vtx]["y"]
            if test_y > min(p1y, p2y):
                if test_y <= max(p1y, p2y):
                    if test_x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (test_y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or test_x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside

    def calculate_wind_shear_pressure(self, base_wind_speed_kts, tractor_cab_height_m=4.5):
        """
        Applies power-law wind scaling profiles derived from atmospheric physics models.
        Calculates dynamic pressure (Pa) acting on the machinery structure.
        """
        # Hellmann exponent for neutral crop/agricultural terrain surfaces
        terrain_roughness_exponent = 0.14
        
        # Wind velocity gradient profile calculation
        effective_wind_kts = base_wind_speed_kts * math.pow((tractor_cab_height_m / 10.0), terrain_roughness_exponent)
        effective_wind_m_s = effective_wind_kts * 0.514444
        
        # Dynamic stagnation pressure: q = 0.5 * rho * V^2 (Standard air density = 1.225 kg/m3)
        dynamic_pressure_pa = 0.5 * 1.225 * math.pow(effective_wind_m_s, 2)
        
        return effective_wind_kts, dynamic_pressure_pa

    def process_closed_loop_telemetry(self, current_hex, target_x_mm, target_y_mm, base_wind_kts, mass_cut_m3):
        """
        Blends spatial keep-in verifications with atmospheric wind shear stress values.
        Assembles the comprehensive Univac IX Core Mainframe verification tracking record.
        """
        timestamp_ms = int(time.time() * 1000)
        
        # 1. Execute Polyhedral Boundary Tracking Check
        is_spatially_safe = self.verify_point_in_polyhedral_bounds(target_x_mm, target_y_mm)
        
        # 2. Execute Wind Shear Velocity Gradient Engine
        eff_wind_kts, wind_pressure_pa = self.calculate_wind_shear_pressure(base_wind_kts)
        
        # 3. Assess Compound Multi-Bus Hazard Interlocks
        assigned_hex = current_hex
        system_interlock = "UNLOCKED_OPERATIONAL_NOMINAL"
        alert_status = "NOMINAL_SPATIAL_TRACKING_IN_BOUNDS"
        authorize_next_cut = True
        enforced_x = target_x_mm
        enforced_y = target_y_mm

        # Hazard Tier A: Aerodynamic Drift Crosswind Displacement Warning
        if wind_pressure_pa > 150.0:
            alert_status = "WARNING_WIND_DRIFT_COMPENSATION_ACTIVE"
            assigned_hex = "0xE" # Shift registers to high-torque drive correction profile
            
        # Hazard Tier B: Extreme Gale Wind Threat Deactivation
        if eff_wind_kts > 45.0:
            alert_status = "CRITICAL_GALE_VELOCITY_SUSPENSION_TRIGGERED"
            assigned_hex = "0x0" # Force bitwise emergency stop
            system_interlock = "ATMOSPHERIC_SHEAR_SHUTDOWN"
            authorize_next_cut = False
            
        # Hazard Tier C: Physical Keep-In Geometry Breach Line-Clamp Intercept
        if not is_spatially_safe:
            alert_status = "CRITICAL_PROPERTY_LINE_CLAMP_EVENT"
            assigned_hex = "0x0" # Overrides all profiles to immediate stop state
            system_interlock = "HARDWARE_LEVEL_LINE_CLAMP_ISOLATION_ACTIVE"
            authorize_next_cut = False
            # Hard clip vector redirection back to nearest safe node origin (Vertex 0 anchor)
            enforced_x = self.poly_vertices[0]["x"]
            enforced_y = self.poly_vertices[0]["y"]

        # Compile the integrated structural frame JSON schema matching Univac-IX specifications
        univac_frame = {
            "univac_core_header": {
                "system_architecture": "UNIVAC_IX_CORE_FABRIC",
                "timestamp_epoch_ms": timestamp_ms,
                "autonomic_handshake_override": "ACTIVE_REVERSE_INJECTION_TRAP" if assigned_hex == "0x0" else "STANDBY"
            },
            "boundary_isolation_matrix": {
                "polyhedral_keep_in_zone": self.poly_vertices,
                "hardware_clamp_active": not is_spatially_safe,
                "safety_alert_status": alert_status,
                "system_interlock_status": system_interlock
            },
            "unreal_spatial_tracking": {
                "requested_coordinates_mm": [target_x_mm, target_y_mm],
                "enforced_coordinates_mm": [enforced_x, enforced_y],
                "bus_voltage_target": f"{self.hex_states.get(assigned_hex, 0.0000):.4f}V",
                "assigned_hex_safety_register": assigned_hex
            },
            "atmospheric_fluid_dynamics": {
                "raw_base_wind_speed_kts": base_wind_kts,
                "effective_scaled_wind_speed_kts": round(eff_wind_kts, 2),
                "calculated_structural_wind_pressure_pa": round(wind_pressure_pa, 2)
            },
            "univac_closed_loop_checkback": {
                "actual_volume_displaced_m3": mass_cut_m3,
                "authorize_next_field_cut": authorize_next_cut
            }
        }
        return univac_frame, assigned_hex == "0x0"

    def export_frame_to_univac_json(self, univac_frame, is_critical):
        """Synchronously dumps the compiled planetary frame packet directly into an active file string."""
        prefix = "UNIVAC_CRITICAL_CLAMP_" if is_critical else "UNIVAC_NOMINAL_"
        filename = f"{prefix}{univac_frame['univac_core_header']['timestamp_epoch_ms']}.json"
        full_path = os.path.join(self.export_directory, filename)
        
        with open(full_path, "w", encoding="utf-8") as json_file:
            json.dump(univac_frame, json_file, indent=4)
        return full_path

    def run_live_stream_pipeline(self, live_sensor_batch):
        """Simulates rapid multi-channel tracking array logging over the shared fabric."""
        print(f"[*] Launching Univac-IX Live Closed-Loop JSON Pipeline Controller...")
        for idx, node in enumerate(live_sensor_batch):
            frame, is_critical = self.process_closed_loop_telemetry(
                current_hex = node["hex"],
                target_x_mm = node["x"],
                target_y_mm = node["y"],
                base_wind_kts = node["wind"],
                mass_cut_m3 = node["cut"]
            )
            saved_file = self.export_frame_to_univac_json(frame, is_critical)
            print(f"[Frame {idx:02d}] Telemetry handshake written successfully -> {saved_file}")

# =========================================================================
# SYSTEM RUNTIME VERIFICATION PASS
// Executed over the university tables to check boundary compliance triggers
# =========================================================================
if __name__ == "__main__":
    # Test dataset mapping standard run coordinates, high-speed wind gusts, and property lines
    simulated_field_stream = [
        {"hex": "0xC", "x": 200000, "y": 200000, "wind": 12.5, "cut": 4.5}, # Nominal Run In-Bounds
        {"hex": "0xC", "x": 205000, "y": 202000, "wind": 54.0, "cut": 8.1}, # Critical Weather Gale Event
        {"hex": "0xE", "x":  75000, "y": 300000, "wind": 15.1, "cut": 0.0}  # Boundary Breach Intercept
    ]
    
    bus = QuantumTelemetryBus()
    bus.run_live_stream_pipeline(simulated_field_stream)
