# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Asynchronous Network Audio Subroutine & PIREP Leveling Pad Broadcaster.

Parses live cross-server JSON frames to vocalize dynamic multi-altitude leveling square
placements, ultimate bearing capacity indices, and structural foundation safety faults.
"""

import os
import sys
import json
import time
import socket
import threading
import pyttsx3

class LiveNetworkAudioAlarm:
    def __init__(self, listen_host="127.0.0.1", listen_port=8081, voice_rate=165):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.voice_rate = voice_rate
        
        # Guard rail configuration tracking the last vocalized frame to prevent audio buffering stacks
        self.last_announcement_time = 0
        self.cooldown_seconds = 4.0 

    def formulate_aviation_soil_advisory(self, univac_json_frame):
        """
        Parses live structured Univac network objects and converts geotechnical engineering
        and multi-altitude pad variables into a non-abbreviated, FAA-standardized PIREP alert.
        """
        try:
            # Handle deep extraction across nested architectural blocks
            header = univac_json_frame.get("univac_core_header", {})
            tracking = univac_json_frame.get("unreal_spatial_tracking", {})
            pad_matrix = univac_json_frame.get("structural_leveling_square", {})
            architecture_type = header.get("system_architecture", "")
            
            # Extract state metrics
            assigned_hex = tracking.get("assigned_hex_safety_register", "0xF")
            
            # Extract sub-surface pad analytics
            coords_mm = pad_matrix.get("center_point_coordinates_mm", [0, 0, 0])
            footprint_type = pad_matrix.get("footprint_classification", "UNKNOWN")
            pad_width_m = pad_matrix.get("square_dimension_width_meters", 0.0)
            bearing_capacity_kpa = pad_matrix.get("allowable_bearing_pressure_kpa", 0.0)
            is_bearing_safe = pad_matrix.get("geotechnical_foundation_safety_lock", True)
            
            # Convert target altitude millimeters back to clear meters for the vocal report
            target_altitude_m = float(coords_mm[2]) / 1000.0
            
            # Extract asset parameters
            meta = univac_json_frame.get("visio_data_visualizer_meta", {})
            owner = meta.get("university_owner", "UW AG Cohort")
            asset = meta.get("asset_name", "Autonomous Field Unit")

            # Seed the standard message framing preamble
            advisory = f"Attention Ballard Control Room. Live Pilot Report Update follows for {owner} assets. "
            
            # 1. CHECK FOR NATIVE VOLUMETRIC LEVELING PROFILE FAULTS (State 0x0 / Failure Flag)
            if assigned_hex == "0x0" or architecture_type == "VOLUMETRIC_LEVELING_PAD_NETWORK":
                if not is_bearing_safe:
                    # Target matches your precise verbal advisory instruction string
                    advisory += (
                        f"Pilot Report Engineering Exception Warning. A heavy structural leveling pad placement "
                        f"has failed compliance rules at targeted altitude level {target_altitude_m:.1f} meters. "
                        f"The requested {footprint_type.replace('_', ' ')} footprint width of {pad_width_m:.1f} meters "
                        f"exceeds the maximum allowable bearing capacity of {bearing_capacity_kpa:.1f} kilopascals "
                        f"calculated for this local subgrade stratum. The autonomic safety interlock has engaged, "
                        f"dropping the hardware register to state zero-x-zero. Excavation blade deployment and "
                        f"structural concrete pouring is locked out to prevent severe foundation settlement shear cracks."
                    )
                else:
                    # Nominal layout placement announcement
                    advisory += (
                        f"Pilot Report structural layout confirmation. A new structural leveling square has been "
                        f"staged at altitude {target_altitude_m:.1f} meters. The {footprint_type.replace('_', ' ')} "
                        f"footprint maintains a verified allowable bearing pressure of {bearing_capacity_kpa:.1f} kilopascals. "
                        f"Geotechnical foundation safety lock is secure. System profile is executing state zero-x-f."
                    )
            
            # 2. EMERGENCY LINE REVERT SIGNALS
            elif assigned_hex == "0x0":
                advisory += (
                    f"Pilot Report Event Profile: Critical safety interlock active. An unauthorized "
                    f"boundary trespass or severe structural overvoltage condition has been logged. "
                    f"The main security rail has collapsed mechanically to state zero-x-zero. All heavy machinery "
                    f"is pinned to an immediate emergency brake lock."
                )
            else:
                # Nominal running baseline audio loop confirmation
                advisory += (
                    f"Pristine status confirmed. The {asset} is operating inside valid geodetic coordinates. "
                    f"Current system profile is executing state zero-x-f."
                )
                
            return advisory
        except Exception as err:
            return f"Control room telemetry parsing exception. Code details: {str(err)}."

    def _speak_worker_thread(self, alert_string):
        """Low-level background audio engine execution loop."""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.voice_rate)
            engine.say(alert_string)
            engine.runAndWait()
        except Exception as e:
            print(f"[-] Asynchronous audio subsystem exception: {str(e)}", file=sys.stderr)

    def process_incoming_network_stream(self, raw_json_packet):
        """Validates incoming network JSON data and dispatches detached speech workers."""
        current_time = time.time()
        
        try:
            data = json.loads(raw_json_packet)
            
            # Rate-limit nominal read confirmations to protect vocal pathways from spamming
            assigned_hex = data.get("unreal_spatial_tracking", {}).get("resolved_hex_register_nibble", "0xF")
            if assigned_hex == "0xF" and (current_time - self.last_announcement_time) < self.cooldown_seconds:
                return "SKIPPED_COOLDOWN_ACTIVE"
                
            advisory_speech = self.formulate_aviation_soil_advisory(data)
            
            # Reset countdown window register and fork background voice thread
            self.last_announcement_time = current_time
            audio_thread = threading.Thread(target=self._speak_worker_thread, args=(advisory_speech,), daemon=True)
            audio_thread.start()
            
            return "AUDIO_DISPATCHED"
        except json.JSONDecodeError:
            return "MALFORMED_STREAM_PACKET"

    def start_network_audio_listener(self):
        """Spawns an active TCP socket interface to ingest synchronized telemetry messages from the network bridge."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.listen_host, self.listen_port))
            server_socket.listen(5)
            print(f"[*] Asynchronous Audio Alarm Module listening on: {self.listen_host}:{self.listen_port}")
            
            while True:
                conn, _ = server_socket.accept()
                try:
                    raw_payload = conn.recv(8192).decode('utf-8')
                    if raw_payload:
                        self.process_incoming_network_stream(raw_payload)
                        conn.sendall(json.dumps({"audio_stream_latch": True}).encode('utf-8'))
                except Exception as stream_err:
                    print(f"[-] Error routing socket data to speaker: {str(stream_err)}", file=sys.stderr)
                finally:
                    conn.close()
        except Exception as init_err:
            print(f"[-] Could not bind audio network listener port: {str(init_err)}", file=sys.stderr)
        finally:
            server_socket.close()

# =========================================================================
# RUNTIME INTEGRITY EVALUATION PASS
# =========================================================================
if __name__ == "__main__":
    # Test packet matching a failed heavy machinery pad placement due to soft subgrade
    mock_failed_pad_frame = {
        "univac_core_header": {
            "system_architecture": "VOLUMETRIC_LEVELING_PAD_NETWORK",
            "timestamp_epoch_ms": int(time.time() * 1000)
        },
        "structural_leveling_square": {
            "center_point_coordinates_mm":, # Altitude = 12.5 meters
            "footprint_classification": "HEAVY_MACHINERY_PAD",
            "square_dimension_width_meters": 15.0,
            "allowable_bearing_pressure_kpa": 47.35,
            "geotechnical_foundation_safety_lock": False # Fails structural validation
        },
        "unreal_spatial_tracking": {
            "assigned_hex_safety_register": "0x0" # Force state 0x0 hardware lock out
        },
        "visio_data_visualizer_meta": {
            "asset_name": "Rheinmetall Kodiak Grading Blade",
            "university_owner": "University of Washington AG Cohort"
        }
    }
    
    alarm_subsystem = LiveNetworkAudioAlarm()
    print("[*] Testing dynamic multi-altitude leveling square voice announcer...")
packed_string = json.dumps(mock_failed_pad_frame)\
result_code = alarm_subsystem.process_incoming_network_stream(packed_string)\
print(f"[+] Operational broadcast response status: {result_code}")

# Allow background speaker process to complete before script termination\
time.sleep(12)
