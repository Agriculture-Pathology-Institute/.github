# File Path: src/quantum_telemetry_bus.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company - Quantum Telemetry Bus Pipeline
Connects 16-State Hexadecimal FPGA Logic Registers directly with Unreal Engine.
Includes an automated live text file logging module for active industrial monitoring.
"""

import os
import sys
import json
from datetime import datetime

class QuantumTelemetryBus:
    def __init__(self, log_dir="src/hardware", log_filename="telemetry_stream.txt"):
        # Maps the 16 native voltage states to clean 4-bit hexadecimal string structures
        self.hex_states = {f"0x{i:X}": i * 0.0625 for i in range(16)}
        
        # Configure output paths for automated file compilation loops
        self.log_dir = log_dir
        self.log_path = os.path.join(self.log_dir, log_filename)
        self._initialize_log_environment()

    def _initialize_log_environment(self):
        """Ensures directories exist and creates a standardized header block for the live log file."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # Write structural reference markers if file is created freshly
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(f"=== RT ARCHITECTURE LIVE TELEMETRY BUS LOG ENGINE ===\n")
                f.write(f"Initialized: {datetime.now().isoformat()}\n")
                f.write(f"Format Block: [TIMESTAMP] [HEX_STATE] [VOLTAGE] [UNREAL_DISPATCH_EVENT] -> TARGET_BUS\n")
                f.write(f"--------------------------------------------------------------------------------\n")

    def compile_unreal_payload(self, raw_hex_signal):
        """
        Translates raw hardware hex frames into decoupled JSON payloads 
        ingestible by Unreal Engine 5's live telemetry control room scene.
        """
        clean_key = str(raw_hex_signal).strip().lower()
        if not clean_key.startswith("0x"):
            clean_key = f"0x{clean_key}"

        if clean_key not in self.hex_states:
            return {"status": "ERROR", "message": "Invalid Hexadecimal State Trigger Input"}
            
        target_voltage = self.hex_states[clean_key]
        dispatch_event, target_bus = self._get_dispatch_event_details(clean_key)
        
        payload = {
            "origin_bus": "RT_Analog_16State_Platform",
            "hex_register_nibble": clean_key,
            "measured_bus_voltage": f"{target_voltage:.4f}V",
            "unreal_dispatch_event": dispatch_event,
            "target_hardware_bus": target_bus
        }
        return payload

    def _get_dispatch_event_details(self, hex_key):
        """Internal router connecting hardware states directly to virtual environment calls and networks."""
        event_map = {
            "0x0": ("TRIGGER_EMERGENCY_STOP_ISOLATION", "HARDWARE_INTERLOCK"),
            "0x1": ("DRAINAGE_HEARTBEAT_POLL", "MODBUS_RS485_SLAVE_03"),
            "0x2": ("GREENHOUSE_LOWPOWER_MODE", "MODBUS_RS485_SLAVE_02"),
            "0x3": ("DRAINAGE_VALVE_25_PERCENT", "MODBUS_RS485_SLAVE_03"),
            "0x4": ("DRAINAGE_VALVE_50_PERCENT", "MODBUS_RS485_SLAVE_03"),
            "0x5": ("DRAINAGE_VALVE_100_PERCENT", "MODBUS_RS485_SLAVE_03"),
            "0x6": ("GREENHOUSE_LED_50_LUMENS", "MODBUS_RS485_SLAVE_02"),
            "0x7": ("GREENHOUSE_LED_100_LUMENS", "MODBUS_RS485_SLAVE_02"),
            "0x8": ("TURBINE_BRAKE_ENGAGEMENT", "MODBUS_RS485_SLAVE_01"),
            "0x9": ("TURBINE_GRID_SYNC_ON", "MODBUS_RS485_SLAVE_01"),
            "0xA": ("KODIAK_PULL_NAVIGATION_WAYPOINT", "SAE_J1939_ISOBUS"),
            "0xB": ("KODIAK_TOOL_ARM_DEPLOY", "SAE_J1939_ISOBUS"),
            "0xC": ("KODIAK_EXCAVATION_DEPTH_INC", "SAE_J1939_ISOBUS"),
            "0xD": ("ELECTRIC_CAT_ECO_PROFILE", "SAE_J1939_ISOBUS"),
            "0xE": ("JOHN_DEERE_HIGH_TORQUE_PROFILE", "SAE_J1939_ISOBUS"),
            "0xF": ("FAST_CHARGE_INTERLOCK_CLAMP", "HARDWARE_POWER_BUS")
        }
        return event_map.get(hex_key, ("UNKNOWN_HARDWARE_STATE_EXCEPTION", "DISCONNECTED"))

    def export_to_live_text_file(self, compiled_payload):
        """Appends streaming data in an optimized raw string format straight to the text file block."""
        if "status" in compiled_payload and compiled_payload["status"] == "ERROR":
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        hex_reg = compiled_payload["hex_register_nibble"]
        voltage = compiled_payload["measured_bus_voltage"]
        event = compiled_payload["unreal_dispatch_event"]
        bus = compiled_payload["target_hardware_bus"]

        log_line = f"[{timestamp}] [{hex_reg}] [{voltage}] [{event}] -> {bus}\n"
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(log_line)

    def run_live_pipeline_stream(self, hex_array):
        """Simulates raw register streaming directly out of the R-2R ladder networks into active storage."""
        print(json.dumps({"bus_init": "SUCCESS", "active_nodes": len(hex_array), "stream_path": self.log_path}, indent=2))
        for hex_node in hex_array:
            compiled_frame = self.compile_unreal_payload(hex_node)
            print(json.dumps(compiled_frame, indent=4))
            
            # Commit record into the live text destination immediately
            self.export_to_live_text_file(compiled_frame)

if __name__ == "__main__":
    # Test vector tracking across the turbine step-downs, tool arms, and drainage routes
    sim_bus_stream = ["0x0", "0x3", "0x7", "0x9", "0xA", "0xD", "0xF"]
    bus_controller = QuantumTelemetryBus()
    bus_controller.run_live_pipeline_stream(sim_bus_stream)
