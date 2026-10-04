# File Path: src/hardware/rt_json_network_bridge.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Server-to-Server JSON Communication & Inter-Process Bridge.

Ingests raw JSON packets from Unreal Engine 5, validates polyhedral land bounds,
calculates microclimatic wind loads, and broadcasts real-time system states.
"""

import os
import sys
import json
import time
import math
import socket
import threading

class RtJsonNetworkBridge:
    def __init__(self, host="127.0.0.1", listen_port=8080, export_directory="Data/UnivacStreams/"):
        self.host = host
        self.listen_port = listen_port
        self.export_directory = export_directory
        self.hex_states = {f"0x{i:X}": i * 0.0625 for i in range(16)}
        
        # 4-Point Non-Linear Polyhedral Boundary Vertex Matrix (Millimeters)
        self.poly_vertices = [
            {"x": 100000, "y": 100000},
            {"x": 500000, "y": 120000},
            {"x": 480000, "y": 350000},
            {"x": 120000, "y": 320000}
        ]

        if not os.path.exists(self.export_directory):
            os.makedirs(self.export_directory, exist_ok=True)

    def verify_spatial_polygon_bounds(self, test_x, test_y):
        """Executes a cross-product intersection pass to ensure tractors stay inside the property."""
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

    def process_incoming_ue5_json(self, raw_json_string):
        """
        Parses incoming JSON telemetry strings directly from Unreal Engine servers.
        Blends 3D coordinates, wind variables, and solar angles into a Univac Core frame.
        """
        try:
            data = json.loads(raw_json_string)
            
            # Extract incoming parameters matching UE5 Virtual Coordinate mappings
            ue5_pos_cm = data.get("ue5_position_cm", [0.0, 0.0, 0.0])
            base_wind_speed_kts = data.get("wind_speed_kts", 0.0)
            mass_cut_m3 = data.get("volume_cut_m3", 0.0)
            current_hex = data.get("request_hex_state", "0xF")
            
            # Convert float centimeters straight to 32-bit millimeter scale registers
            target_x_mm = int(math.floor(ue5_pos_cm[0] * 10.0))
            target_y_mm = int(math.floor(ue5_pos_cm[1] * 10.0))
            target_z_mm = int(math.floor(ue5_pos_cm[2] * 10.0))
            
            # Calculate dynamic wind pressure gradient values
            eff_wind_kts = base_wind_speed_kts * math.pow((4.5 / 10.0), 0.14)
            wind_pressure_pa = 0.5 * 1.225 * math.pow((eff_wind_kts * 0.514444), 2)

            # Evaluate system safety overrides
            is_inside_bounds = self.verify_spatial_polygon_bounds(target_x_mm, target_y_mm)
            
            assigned_hex = current_hex
            system_interlock = "UNLOCKED_OPERATIONAL_NOMINAL"
            alert_status = "NOMINAL_SPATIAL_TRACKING_IN_BOUNDS"
            authorize_next_cut = True
            enforced_x = target_x_mm
            enforced_y = target_y_mm

            if wind_pressure_pa > 150.0:
                alert_status = "WARNING_WIND_DRIFT_COMPENSATION_ACTIVE"
                assigned_hex = "0xE" # Shift to high-torque compensation
                
            if eff_wind_kts > 45.0 or not is_inside_bounds:
                assigned_hex = "0x0" # Force bitwise emergency stop
                authorize_next_cut = False
                system_interlock = "CRITICAL_SAFETY_INTERLOCK_CLAMP_ACTIVE"
                alert_status = "CRITICAL_PROPERTY_LINE_CLAMP_EVENT" if not is_inside_bounds else "CRITICAL_GALE_FORCE_EMERGENCY"
                if not is_inside_bounds:
                    enforced_x = self.poly_vertices[0]["x"]
                    enforced_y = self.poly_vertices[0]["y"]

            univac_packet = {
                "univac_core_header": {
                    "system_architecture": "UNIVAC_IX_CORE_FABRIC",
                    "timestamp_epoch_ms": int(time.time() * 1000),
                    "autonomic_handshake_override": "ACTIVE_REVERSE_INJECTION_TRAP" if assigned_hex == "0x0" else "STANDBY"
                },
                "boundary_isolation_matrix": {
                    "polyhedral_keep_in_zone": self.poly_vertices,
                    "hardware_clamp_active": not is_inside_bounds,
                    "safety_alert_status": alert_status,
                    "system_interlock_status": system_interlock
                },
                "unreal_spatial_tracking": {
                    "requested_coordinates_mm": [target_x_mm, target_y_mm, target_z_mm],
                    "enforced_coordinates_mm": [enforced_x, enforced_y, target_z_mm],
                    "bus_voltage_target": f"{self.hex_states.get(assigned_hex, 0.0000):.4f}V",
                    "assigned_hex_safety_register": assigned_hex
                },
                "atmospheric_fluid_dynamics": {
                    "scaled_wind_speed_kts": round(eff_wind_kts, 2),
                    "calculated_wind_pressure_pa": round(wind_pressure_pa, 2)
                },
                "univac_closed_loop_checkback": {
                    "actual_volume_displaced_m3": mass_cut_m3,
                    "authorize_next_field_cut": authorize_next_cut
                }
            }
            return univac_packet, True
        except (json.JSONDecodeError, KeyError, TypeError) as err:
            error_packet = {"status": "MALFORMED_JSON_EXCEPTION", "details": str(err)}
            return error_packet, False

    def start_network_server_listener(self):
        """Launches a non-blocking TCP socket server that listens for incoming cross-server JSON frames."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.listen_port))
            server_socket.listen(5)
            print(f"[*] UNIVAC IX Core Fabric listening for cross-server JSON on: {self.host}:{self.listen_port}")
            
            while True:
                client_conn, client_addr = server_socket.accept()
                threading.Thread(target=self._handle_client_connection, args=(client_conn, client_addr), daemon=True).start()
        except Exception as e:
            print(f"[-] Server socket initialization failure: {str(e)}")
        finally:
            server_socket.close()

    def _handle_client_connection(self, connection, address):
        """Worker thread processing the received JSON stream data payload."""
        try:
            raw_data = connection.recv(4096).decode('utf-8')
            if raw_data:
                processed_frame, success = self.process_incoming_ue5_json(raw_data)
                
                # Send immediate back-channel JSON validation status message back to sender server
                response_string = json.dumps({"handshake_received": True, "syntax_valid": success, "assigned_register": processed_frame.get("unreal_spatial_tracking", {}).get("assigned_hex_safety_register", "0x0")})
                connection.sendall(response_string.encode('utf-8'))
                
                # Commit processed frame to active storage log streams
                if success:
                    prefix = "UNIVAC_CRITICAL_" if processed_frame["hardware_state_dispatch" if "hardware_state_dispatch" in processed_frame else "unreal_spatial_tracking"]["assigned_hex_safety_register"] == "0x0" else "UNIVAC_NOMINAL_"
                    filename = f"{prefix}{processed_frame['univac_core_header']['timestamp_epoch_ms']}.json"
                    with open(os.path.join(self.export_directory, filename), "w") as f:
                        json.dump(processed_frame, f, indent=4)
        except Exception as err:
            print(f"[-] Inter-server connection error processing address {address}: {str(err)}")
        finally:
            connection.close()

if __name__ == "__main__":
    # Test execution routing: Mocking a direct network payload coming out of Unreal Engine
    mock_ue5_network_packet = {
        "ue5_position_cm": [25000.0, 18000.0, 450.0], # CM input units from engine viewport space
        "wind_speed_kts": 12.4,
        "volume_cut_m3": 14.8,
        "request_hex_state": "0xC"
    }
    
    bridge = RtJsonNetworkBridge()
    print("[*] Running programmatic parsing validation check...")
    json_payload = json.dumps(mock_ue5_network_packet)
    verified_output, status_ok = bridge.process_incoming_ue5_json(json_payload)
    print(json.dumps(verified_output, indent=4))
