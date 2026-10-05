# File Path: scripts/parse_acoustic_geotech.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Asynchronous Volumetric Acoustic Sub-surface Parser and Telemetry Streamer.

Converts raw sonic reflections into structural soil density, surcharge data,
and storm runoff vectors, piping JSON frames directly across server networks.
"""

import os
import sys
import json
import time
import math
import socket

class AcousticGeotechParser:
    def __init__(self, bridge_host="127.0.0.1", bridge_port=8080):
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        
        # Geotechnical Material Density Mapping (kg/m³)
        self.density_map = {"0xF": 2600.0, "0x9": 1900.0, "0x7": 1600.0, "0x3": 1100.0}

    def calculate_loading_surcharge(self, density_kg_m3, internal_friction_angle_deg=30.0):
        """
        Applies Terzaghi's bearing capacity and earth pressure equations 
        to determine the allowable load surcharge limit (kPa) before collapse.
        """
        phi_rad = math.radians(internal_friction_angle_deg)
        # Rankine Active Earth Pressure Coefficient: Ka = (1-sin(phi))/(1+sin(phi))
        ka = (1.0 - math.sin(phi_rad)) / (1.0 + math.sin(phi_rad))
        
        # Allowable surcharge load capacity calculation
        allowable_surcharge_kpa = (0.5 * density_kg_m3 * 9.80665 * ka * 2.0) / 1000.0
        return round(allowable_surcharge_kpa, 2)

    def evaluate_storm_runoff_coefficient(self, density_hex):
        """
        Determines the hydrologic runoff coefficient (C value) for stormwater planning.
        Dense bedrock blocks infiltration, while low-density silt absorbs water until saturated.
        """
        if density_hex == "0xF":
            return 0.85  # Bedrock: High runoff, extreme flash flood risk
        elif density_hex == "0x9":
            return 0.50  # Compacted gravel: Moderate runoff
        elif density_hex == "0x3":
            return 0.15  # Soft loose dirt: Absorbs initially, highest mudslide risk
        return 0.30      # Nominal farm loam

    def compose_volumetric_json(self, raw_voltage_in, coordinates_mm):
        """Transforms acoustic reflections into comprehensive 3D sub-surface data."""
        # Map raw sensor input voltage lines to 16-state hexadecimal state channels
        closest_idx = min(range(16), key=lambda i: abs((i * 0.0625) - raw_voltage_in))
        hex_state = f"0x{closest_idx:X}"
        
        density = self.density_map.get(hex_state, 1500.0)
        surcharge = self.calculate_loading_surcharge(density)
        runoff_c = self.evaluate_storm_runoff_coefficient(hex_state)
        
        timestamp_ms = int(time.time() * 1000)
        is_stable = closest_idx >= 6

        # Assemble the cross-server network payload string packet
        geotech_payload = {
            "univac_core_header": {
                "system_architecture": "AIRBORNE_ACOUSTIC_GEOTECH_NETWORK",
                "timestamp_epoch_ms": timestamp_ms
            },
            "priority_routing_overrides": {
                "tier_01_governmental_xr_oversight": {
                    "priority_index": 1,
                    "authorized_agencies": ["DOI", "OSHA", "BLM_LAND_PEOPLE", "COUNTY_ZONING"],
                    "enforce_boundary_lock": not is_stable,
                    "viewport_hud_overlay_text": "🚨 CRITICAL LANDSLIDE DANGER: UNSTABLE SOIL STRATA DETECTED." if not is_stable else "✅ GEOTECHNICAL STRUCTURAL STABILITY CONFIRMED.",
                    "viewport_hud_alert_tint": "CRITICAL_CRIMSON_REVERT" if not is_stable else "NOMINAL_GREEN_STABLE"
                },
                "tier_02_commercial_ballard_operations": {
                    "priority_index": 2,
                    "entity_name": "AGRICULTURE_PATHOLOGY_INSTITUTE_LLC",
                    "office_location": "UW_MEDICINE_BALLARD_BASE_STATION",
                    "hardware_interlock_hex_register": "0x0" if not is_stable else "0xF"
                }
            },
            "sub_surface_volumetric_matrix": {
                "3d_grid_coordinates_mm": coordinates_mm,
                "calculated_soil_density_kg_m3": density,
                "allowable_loading_surcharge_kpa": surcharge,
                "hydrologic_storm_runoff_coefficient": runoff_c,
                "structural_stability_verified": is_stable
            },
            "ue5_position_cm": [coordinates_mm[0]/10.0, coordinates_mm[1]/10.0, coordinates_mm[2]/10.0],
            "wind_speed_kts": 0.0,
            "volume_cut_m3": 0.0,
            "request_hex_state": "0x0" if not is_stable else "0xF"
        }
        return geotech_payload

    def pipe_frame_to_network_bridge(self, payload):
        """Streams the generated JSON string over a live socket connection link to port 8080."""
        payload_string = json.dumps(payload)
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.bridge_host, self.bridge_port))
            client.sendall(payload_string.encode('utf-8'))
            client.close()
            return "SUCCESS"
        except Exception as e:
            return f"CONNECTION_LINE_DROP_ERROR: {str(e)}"

# =========================================================================
# TEST INJECTION SIMULATION LOOP
# =========================================================================
if __name__ == "__main__":
    parser = AcousticGeotechParser()
    print("[*] Simulating airborne low-frequency sound wave ground-ping passes...")
    
    # Mock data capturing scans across solid bedrock layers down into an unstable mud pocket
    simulated_acoustic_pings = [
        {"v": 0.9375, "coords": [150000, 200000, -5000]}, # Solid Bedrock stratum (State 0xF)
        {"v": 0.1875, "coords": [152000, 204000, -8000]}  # Saturated Silt Pocket (State 0x3) -> Danger Fault
    ]
    
    for idx, ping in enumerate(simulated_acoustic_pings):
        frame = parser.compose_volumetric_json(ping["v"], ping["coords"])
        status = parser.pipe_frame_to_network_bridge(frame)
        print(f"[Ping {idx:02d}] Geotechnical data streamed across networks. Status response: {status}")
