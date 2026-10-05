# File Path: src/hardware/rt_edwards_supervisory_node.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Edwards FireWorks High-Priority Watchdog & Soil Safeguard Core.

Pops the normally closed hardware loops open if structural soil density drops
below 1200 kg/m³, while protecting soft topsoil zones during planting mode.
"""

import os
import sys
import json
import time
import socket
import threading

class EdwardsSupervisoryHeartbeatNode:
    def __init__(self, host="127.0.0.1", port=8083, watch_timeout_ms=2000):
        self.host = host
        self.port = port
        self.timeout_seconds = watch_timeout_ms / 1000.0
        
        # Core Mechanical Safety Constants
        self.MIN_STRUCTURAL_DENSITY_KG_M3 = 1200.0
        
        # Operational Watchdog States
        self.last_heartbeat_received = time.time()
        self.hardware_loop_active = True
        self.relay_pin_energized = True # Active-High baseline pattern logic
        
        # Dynamic Operational Mode Flag (Loaded from config.yaml layout templates)
        # "PLANTING_MODE"  -> Soft topsoil is authorized, digging toolheads are locked out.
        # "EXCAVATION_MODE" -> Soft soil triggers an immediate landslide structural fault stop.
        self.operational_mode = "PLANTING_MODE" 

    def process_incoming_heartbeat(self, raw_json_frame):
        """Ingests live cross-server JSON frames and evaluates soil density constraints."""
        try:
            data = json.loads(raw_json_frame)
            header = data.get("univac_core_header", {})
            geotech = data.get("sub_surface_volumetric_matrix", {})
            
            # Extract volumetric variables from the airborne acoustic string stream
            density = geotech.get("calculated_soil_density_kg_m3", 1500.0)
            is_stable = geotech.get("structural_stability_verified", True)
            
            # Verify if the packet originates from an active native computing fabric
            if "ACOUSTIC" in header.get("system_architecture", "") or "UNIVAC" in header.get("system_architecture", ""):
                
                # 1. EVALUATE DYNAMIC SOIL DENSITY STRATUM CLEAR ZONE CONSTANTS
                if density < self.MIN_STRUCTURAL_DENSITY_KG_M3:
                    if self.operational_mode == "EXCAVATION_MODE":
                        print(f"[🚨 GEOTECHNICAL COLLAPSE FAULT] Density dropped to {density} kg/m³. Tripping Edwards loop!")
                        self.relay_pin_energized = False
                        return "CRITICAL_LANDSLIDE_DROP"
                        
                    elif self.operational_mode == "PLANTING_MODE":
                        # Soft topsoil is expected for root growth. 
                        # Interlock blocks digging/heavy cutting to protect agricultural zones.
                        volume_cut = data.get("volume_cut_m3", 0.0)
                        if volume_cut > 0.0:
                            print(f"[🚨 CROP ROOT ZONE SECURITY PROTECTION] Excavation toolhead detected inside soft planting terrain! Locking tool arrays.")
                            self.relay_pin_energized = False
                            return "CROP_ZONE_EXCAVATION_VIOLATION_DROP"
                
                # 2. Standard watch-timer refresh on clean, valid signal frames
                if is_stable and self.relay_pin_energized:
                    self.last_heartbeat_received = time.time()
                    self.relay_pin_energized = True
                    return "TIMER_REFRESHED"
                    
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[-] Malformed telemetry data packet passed to heartbeat loop: {str(e)}", file=sys.stderr)
        return "PARSE_EXCEPTION"

    def execute_watchdog_sentinel_thread(self):
        """Continuous background thread evaluating elapsed milliseconds since the last successful frame pass."""
        print(f"[*] Initializing Active-High Watchdog Sentinel. Mode = {self.operational_mode}")
        while self.hardware_loop_active:
            current_duration = time.time() - self.last_heartbeat_received
            
            if current_duration > self.timeout_seconds:
                if self.relay_pin_energized:
                    print("\n[🚨 CATASTROPHIC WATCHDOG TIMEOUT] System execution loop has stalled!")
                    print(f"[!] DROPPING GPIO CONTROL PIN LOW -> NORMALLY CLOSED RELAY CIRCUIT POPS OPEN.")
                    print("[!] EDWARDS FIREWORKS PANEL TRIGGERING PRIORITY 1 INCIDENT REPORT EVACUATION MODE.")
                    self.relay_pin_energized = False
            time.sleep(0.1) # 100ms check interval rate matches your industrial divider

    def launch_supervisory_socket_listener(self):
        """Launches a non-blocking TCP server to intercept synchronous health signals from the network bridge."""
        sentinel_thread = threading.Thread(target=self.execute_watchdog_sentinel_thread, daemon=True)
        sentinel_thread.start()
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"[*] Edwards Supervisory Sentinel Core listening on network address: {self.host}:{self.port}")
            
            while self.hardware_loop_active:
                conn, _ = server_socket.accept()
                try:
                    payload = conn.recv(4096).decode('utf-8')
                    if payload:
                        self.process_incoming_heartbeat(payload)
                        conn.sendall(json.dumps({"relay_pin_energized": self.relay_pin_energized, "active_mode": self.operational_mode}).encode('utf-8'))
                except Exception as err:
                    pass
                finally:
                    conn.close()
        except Exception as e:
            print(f"[-] Sentinel server socket initialization failure: {str(e)}", file=sys.stderr)
        finally:
            server_socket.close()

if __name__ == "__main__":
    # Test pass: Mocking a heavy vehicle entering a designated soft-dirt planting sector
    monitor = EdwardsSupervisoryHeartbeatNode()
    monitor.operational_mode = "PLANTING_MODE"
    
    server_thread = threading.Thread(target=monitor.launch_supervisory_socket_listener, daemon=True)
    server_thread.start()
    time.sleep(0.2)
    
    # Inbound test node from acoustic scanner: Soft soil (1100 kg/m³) with active tool displacement
    mock_violation_frame = {
        "univac_core_header": {"system_architecture": "AIRBORNE_ACOUSTIC_GEOTECH_NETWORK"},
        "sub_surface_volumetric_matrix": {
            "calculated_soil_density_kg_m3": 1100.0, # Below 1200 safety limit
            "structural_stability_verified": true
        },
        "volume_cut_m3": 4.5 # Heavy excavator tool head is active inside soft dirt!
    }
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 8083))
    s.sendall(json.dumps(mock_violation_frame).encode('utf-8'))
    
    response = json.loads(s.recv(1024).decode('utf-8'))
    s.close()
    
    print(f"\n[📊 Injection Check Complete] Panel Pin Energized = {response['relay_pin_energized']} | System Mode = {response['active_mode']}")
