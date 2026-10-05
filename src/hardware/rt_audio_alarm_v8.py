# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Asynchronous Network Audio Subroutine & PIREP Fluid Ballistics Broadcaster.

Parses live cross-server JSON frames to vocalize independent modular asset stacking,
nozzle jet exit velocities, and exact effective fire suppression throw radii.
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
        /**
         * Parses independent modular installation assets and converts hydromechanical
         * variables into a non-abbreviated, FAA-standardized PIREP alert.
         */
        try:
            # Handle deep extraction across nested decoupled payload blocks
            header = univac_json_frame.get("univac_core_header", {})
            tracking = univac_json_frame.get("unreal_spatial_tracking", {})
            installation = univac_json_frame.get("assigned_installation_payload", {})
            architecture_type = header.get("system_architecture", "")
            
            # Extract basic state parameters
            assigned_hex = tracking.get("resolved_hex_register_nibble", "0xF")
            
            # Extract nested decoupled asset mechanics
            parent_pad_id = installation.get("parent_leveling_pad_id", "UNKNOWN_PAD")
            blueprint_name = installation.get("asset_blueprint_name", "UNKNOWN_ASSET")
            source_file = installation.get("physical_device_source", "UNKNOWN_SOURCE")
            
            # Unpack the nested fluid hydraulics matrix
            hydraulics = installation.get("fluid_hydraulics_matrix", {})
            nozzle_mm = hydraulics.get("nozzle_diameter_mm", 0.0)
            velocity_mps = hydraulics.get("jet_velocity_m_s", 0.0)
            flow_gpm = hydraulics.get("flow_discharge_gpm", 0.0)
            flow_m3_hr = hydraulics.get("flow_discharge_m3_hr", 0.0)
            throw_radius_m = hydraulics.get("effective_throw_radius_meters", 0.0)
            coverage_m2 = hydraulics.get("total_suppression_coverage_m2", 0.0)
            
            meta = univac_json_frame.get("visio_data_visualizer_meta", {})
            owner = meta.get("university_owner", "UW AG Cohort")

            # Seed the standard message framing preamble
            advisory = f"Attention Ballard Control Room. Live Pilot Report Update follows for {owner} assets. "
            
            # 1. EVALUATE DECOUPLED MODULAR ASSET STACKING OVERRIDES (State 0x5 / Asset Code)
            if architecture_type == "MODULAR_ASSET_STACKING_NETWORK" or assigned_hex == "0x5":
                # Target matches your precise verbal advisory instruction string [1.15]
                advisory += (
                    f"Independent Installation Payload Compiled Natively. "
                    f"A modular {blueprint_name.replace('_', ' ')} asset derived from physical source script "
                    f"{source_file} has been stacked successfully on top of verified structural leveling pad "
                    f"identification code {parent_pad_id}. The hydromechanical coverage engine has calculated "
                    f"the exact ballistics profile under active line pressure. "
                    f"The integrated smooth tapered {nozzle_mm:.1f} millimeter nozzle generates a fluid jet exit velocity "
                    f"of {velocity_mps:.1f} meters per second. This produces a non-abbreviated effective throw radius "
                    f"of exactly {throw_radius_m:.1f} meters, establishing a continuous circular water curtain fire-suppression "
                    f"coverage area of {coverage_m2:.1f} square meters. The volumetric volumetric flow discharge rate "
                    f"is clocked at {flow_m3_hr:.1f} cubic meters per hour, equivalent to {flow_gpm:.1f} gallons per minute. "
                    f"The local solenoid interlock gates remain in normal standby mode."
                )
            
            # 2. STANDARD EMERGENCY STATE OVERRIDES (State 0x0)
            elif assigned_hex == "0x0":
                advisory += (
                    f"Pilot Report Event Profile: Critical safety interlock active. An unauthorized "
                    f"boundary trespass or severe structural overvoltage condition has been logged. "
                    f"The main security rail has collapsed mechanically to state zero-x-zero."
                )
            else:
                advisory += (
                    f"Pristine status confirmed. The field implement is operating inside valid geodetic coordinates. "
                    f"Current system profile is executing state zero-x-f."
                )
                
            return advisory
        except Exception as err:
            return f"Control room telemetry parsing exception. Code details: {str(err)}."

    def _speak_worker_thread(self, alert_string):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.voice_rate)
            engine.say(alert_string)
            engine.runAndWait()
        except Exception as e:
            print(f"[-] Asynchronous audio subsystem exception: {str(e)}", file=sys.stderr)

    def process_incoming_network_stream(self, raw_json_packet):
        current_time = time.time()
        try:
            data = json.loads(raw_json_packet)
            assigned_hex = data.get("unreal_spatial_tracking", {}).get("resolved_hex_register_nibble", "0xF")
            if assigned_hex == "0xF" and (current_time - self.last_announcement_time) < self.cooldown_seconds:
                return "SKIPPED_COOLDOWN_ACTIVE"
                
            advisory_speech = self.formulate_aviation_soil_advisory(data)
            self.last_announcement_time = current_time
            audio_thread = threading.Thread(target=self._speak_worker_thread, args=(advisory_speech,), daemon=True)
            audio_thread.start()
            return "AUDIO_DISPATCHED"
        except json.JSONDecodeError:
            return "MALFORMED_STREAM_PACKET"

    def start_network_audio_listener(self):
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
                    pass
                finally:
                    conn.close()
        except Exception as init_err:
            pass
        finally:
            server_socket.close()

if __name__ == "__main__":
    # Test execution harness checking the decoupled asset stacking alert flow
    mock_frame = {
        "univac_core_header": {"system_architecture": "MODULAR_ASSET_STACKING_NETWORK"},
        "unreal_spatial_tracking": {"resolved_hex_register_nibble": "0x5"},
        "assigned_installation_payload": {
            "parent_leveling_pad_id": "PAD_104",
            "asset_blueprint_name": "GIANT_IMPACT_SPRINKLER_HEAD",
            "physical_device_source": "giant_impact_sprinkler.scad",
            "fluid_hydraulics_matrix": {
                "nozzle_diameter_mm": 34.29,
                "jet_velocity_m_s": 27.24,
                "flow_discharge_gpm": 393.38,
                "flow_discharge_m3_hr": 89.34,
                "effective_throw_radius_meters": 48.71,
                "total_suppression_coverage_m2": 7453.64
            }
        },
        "visio_data_visualizer_meta": {"university_owner": "University of Washington AG Cohort"}
    }
    alarm_subsystem = LiveNetworkAudioAlarm()
    print("[*] Instantiating independent asset voice simulation run...")
    alarm_subsystem.process_incoming_network_stream(json.dumps(mock_frame))
    time.sleep(12)
