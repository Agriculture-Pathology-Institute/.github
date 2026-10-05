# File Path: scripts/predict_storm_flooding.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Asynchronous Saint-Venant & Horton Hydrologic Runoff Predictor Node.

Calculates hourly absorption decays, water flow velocities, and pooling 
diameter expansion rates, piping telemetry frames directly over server sockets.
"""

import os
import sys
import json
import time
import math
import socket

class HydrologicStormPredictor:
    def __init__(self, bridge_host="127.0.0.1", bridge_port=8080):
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port
        
        # Horton's Infiltration Model Constants for typical loam/clay agricultural terrain
        self.f0_initial_absorption_mm_hr = 50.0  # High initial dry soil capacity
        self.fc_terminal_absorption_mm_hr = 4.0   # Saturated soil baseline infiltration rate
        self.k_decay_constant_per_hr = 2.0       # Exponential absorption decay rating

    def compute_horton_absorption_rate(self, elapsed_storm_time_hr):
        """Applies Horton's Infiltration Equation to determine current absorption capacity."""
        # Formula: f(t) = fc + (f0 - fc) * e^(-kt)
        current_absorption = self.fc_terminal_absorption_mm_hr + (
            (self.f0_initial_absorption_mm_hr - self.fc_terminal_absorption_mm_hr) * 
            math.exp(-self.k_decay_constant_per_hr * elapsed_storm_time_hr)
        )
        return round(current_absorption, 2)

    def predict_pooling_expansion_rate(self, hourly_rainfall_mm_hr, absorption_rate_mm_hr, catchment_area_m2=500.0):
        """
        Calculates surface water pooling accumulation and dynamic diameter expansion rates 
        using volumetric retention principles. Assumes a shallow inverted cone basin profile.
        """
        excess_water_mm_hr = hourly_rainfall_mm_hr - absorption_rate_mm_hr
        if excess_water_mm_hr <= 0.0:
            return 0.0, 0.0  # All water absorbed; no surface pooling or runoff generated
            
        # Volumetric accumulation rate: m³ per hour
        excess_volume_m3_hr = (excess_water_mm_hr / 1000.0) * catchment_area_m2
        
        # Assume shallow basin depth profile = 0.1 * radius (Slope constant)
        # Cone Volume: V = (1/3) * pi * r² * h  -> V = (1/30) * pi * r³
        # Radius: r = ((30 * V) / pi)^(1/3)
        simulated_elapsed_hr = 1.5 # Example midpoint snapshot
        total_accumulated_volume = excess_volume_m3_hr * simulated_elapsed_hr
        
        current_radius = math.pow((30.0 * total_accumulated_volume) / math.pi, 1.0 / 3.0)
        current_diameter_meters = current_radius * 2.0
        
        # Derivative of diameter with respect to volume yields the instant expansion rate (meters/hour)
        expansion_rate_m_hr = (2.0 / math.pi) * (excess_volume_m3_hr / (3.0 * math.pow(current_radius, 2) + 0.01))
        
        return round(current_diameter_meters, 2), round(expansion_rate_m_hr, 2)

    def evaluate_flood_threat_level(self, diameter_meters, expansion_rate_m_hr):
        """Categorizes hydrologic risk parameters into actionable machine safety tiers."""
        if diameter_meters > 25.0 or expansion_rate_m_hr > 5.0:
            return "CRITICAL_FLASH_FLOOD_POOLING_ACTIVE", "0x0" # Force immediate tractor E-stop
        elif diameter_meters > 8.0:
            return "WARNING_SURFACE_WATER_ACCUMULATION", "0xE"   # Enter high-torque muddy drift mode
        return "NOMINAL_HYDROLOGIC_DRAINAGE_STABLE", "0xF"       # Safe operations

    def compose_hydrologic_json(self, target_coordinates_mm, hourly_rainfall_mm_hr, storm_duration_hr):
        """Assembles hydrologic flow metrics into a synchronized cross-server JSON frame."""
        absorption = self.compute_horton_absorption_rate(storm_duration_hr)
        pooling_dia, expand_rate = self.predict_pooling_expansion_rate(hourly_rainfall_mm_hr, absorption)
        alert_status, safety_hex = self.evaluate_flood_threat_level(pooling_dia, expand_rate)
        
        timestamp_ms = int(time.time() * 1000)
        is_safe = safety_hex != "0x0"

        # Compile unified open-source JSON payload tracking block
        hydrologic_payload = {
            "univac_core_header": {
                "system_architecture": "PLANETARY_HYDROLOGIC_FLOW_NETWORK",
                "timestamp_epoch_ms": timestamp_ms
            },
            "priority_routing_overrides": {
                "tier_01_governmental_xr_oversight": {
                    "priority_index": 1,
                    "authorized_agencies": ["DOI", "OSHA", "BLM_LAND_PEOPLE", "COUNTY_ZONING"],
                    "enforce_boundary_lock": not is_safe,
                    "viewport_hud_overlay_text": f"🚨 FLOOD HAZARD: POOLING DIA {pooling_dia}m | EXPANDING AT {expand_rate}m/HR." if not is_safe else "✅ HYDROLOGIC RUNOFF CHANNELS NOMINAL.",
                    "viewport_hud_alert_tint": "CRITICAL_CRIMSON_REVERT" if not is_safe else "NOMINAL_GREEN_STABLE"
                },
                "tier_02_commercial_ballard_operations": {
                    "priority_index": 2,
                    "entity_name": "AGRICULTURE_PATHOLOGY_INSTITUTE_LLC",
                    "office_location": "UW_MEDICINE_BALLARD_BASE_STATION",
                    "hardware_interlock_hex_register": safety_hex
                }
            },
            "hydrologic_flow_analytics": {
                "3d_grid_coordinates_mm": target_coordinates_mm,
                "current_precipitation_rate_mm_hr": hourly_rainfall_mm_hr,
                "calculated_absorption_rate_mm_hr": absorption,
                "predicted_surface_pooling_diameter_meters": pooling_dia,
                "pooling_expansion_velocity_meters_hr": expand_rate
            },
            "ue5_position_cm": [target_coordinates_mm / 10.0, target_coordinates_mm / 10.0, target_coordinates_mm / 10.0],
            "wind_speed_kts": 0.0,
            "volume_cut_m3": 0.0,
            "request_hex_state": safety_hex
        }
        return hydrologic_payload

    def pipe_frame_to_network_bridge(self, payload):
        """Streams the structured JSON string payload directly across the server gateway."""
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
# TEST SYSTEM INJECTION RUNTIME PASS
# =========================================================================
if __name__ == "__main__":
    predictor = HydrologicStormPredictor()
    print("[*] Simulating high-intensity cloudburst storm events over agricultural plots...")
    
    # Mock data tracking a continuous 100-year cloudburst over a 3-hour duration timeline
    simulated_storm_timeline = [
        {"rainfall": 15.0, "duration": 0.25, "coords": [200000, 250000, 0]}, # Early storm: soil absorbs water safely
        {"rainfall": 85.0, "duration": 2.50, "coords":}  # Saturated core: high rainfall causes flash flooding
    ]
    
    for idx, snap in enumerate(simulated_storm_timeline):
        frame = predictor.compose_hydrologic_json(snap["coords"], snap["rainfall"], snap["duration"])
        status = predictor.pipe_frame_to_network_bridge(frame)
        print(f"[Storm Snap {idx:02d}] Hydrologic curves dispatched. Server response code: {status}")
