# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Asynchronous Network Audio Subroutine & PIREP Natural Waterway Broadcaster.

Parses live cross-server JSON frames to vocalize distinct ancient paleo-channel 
detections, root preservation locks, and automatic irrigation valve diversions.
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
        Parses live structured Univac network objects and converts geotech, hydrologic,
        and natural irrigation variables into a non-abbreviated, FAA-standardized PIREP alert.
        """
        try:
            # Handle deep extraction across nested architectural blocks
            header = univac_json_frame.get("univac_core_header", {})
            tracking = univac_json_frame.get("unreal_spatial_tracking", {})
            geotech = univac_json_frame.get("natural_waterway_analytics", {})
            overrides = univac_json_frame.get("priority_routing_overrides", {})
            
            # Extract state metrics
            assigned_hex = tracking.get("resolved_hex_register_nibble", "0xF")
            architecture_type = header.get("system_architecture", "")
            
            # Extract subgrade feature analytics
            density = geotech.get("measured_soil_density_kg_m3", 1500.0)
            feature_type = geotech.get("detected_subgrade_feature", "COMPACTED_MATRIX")
            dig_style = geotech.get("recommended_digging_style", "STANDARD_GRADING")
            trench_shape = geotech.get("optimal_trench_profile_shape", "NONE")
            absorption_rating = geotech.get("soil_absorption_efficiency_rating", 0.0)
            
            # Extract asset parameters
            meta = univac_json_frame.get("visio_data_visualizer_meta", {})
            owner = meta.get("university_owner", "UW AG Cohort")
            asset = meta.get("asset_name", "Autonomous Field Unit")

            # Seed the standard message framing preamble
            advisory = f"Attention Ballard Control Room. Live Pilot Report Update follows for {owner} assets. "
            
            # 1. CHECK FOR NATIVE NATURAL IRRIGATION GEOMETRY OVERRIDES (State 0x5)
            if assigned_hex == "0x5" or architecture_type == "NATURAL_HYDRO_IRRIGATION_NETWORK":
                if "ROOT" in feature_type:
                    advisory += (
                        f"Pilot Report Event Profile: Tree Root Matrix Preservation Lock Active. "
                        f"The airborne acoustic tomography sensor has isolated an advanced organic root network "
                        f"at current coordinates. The toolhead gatekeeper has successfully engaged an active-high "
                        f"hydraulic lock. Implements are restricted to state zero-x-five. Cutting operations "
                        f"are suspended to prevent subgrade root fracture and protect local canopy stability."
                    )
                else:
                    # Target matches your precise verbal advisory instruction string
                    advisory += (
                        f"Natural Waterway Detected — Diverting Irrigation Gate. "
                        f"Airborne infrasound tomographic scanning has traced an historic paleo-channel water path "
                        f"with a localized soil absorption efficiency rating of {absorption_rating * 100.0:.0f} percent. "
                        f"The core operating fabric has initiated an autonomic configuration shift. "
                        f"Excavation tools are locked to prevent topsoil destruction, and local sub-station "
                        f"gates are opening to guide natural stormwater runoff channels along a contour aligned "
                        f"{dig_style.replace('_', ' ')} path using a {trench_shape.replace('_', ' ')} geometry."
                    )
            
            # 2. STANDARD STATE SAFETY INTERLOCK OVERRIDES (State 0x0)
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
                    f"Sub-surface soil strata evaluation is complete and nominal. "
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
    # Test packet matching an ancient water channel interception pass
    mock_natural_waterway_frame = {
        "univac_core_header": {
            "system_architecture": "NATURAL_HYDRO_IRRIGATION_NETWORK",
            "timestamp_epoch_ms": int(time.time() * 1000)
        },
        "natural_waterway_analytics": {
            "measured_soil_density_kg_m3": 1220.0,
            "detected_subgrade_feature": "ANCIENT_PALEO_CHANNEL_WATER_PATH",
            "recommended_digging_style": "SINUOUS_MEANDER_DITCH",
            "optimal_trench_profile_shape": "TRAPEZOIDAL_SHELF",
            "soil_absorption_efficiency_rating": 0.92
        },
        "unreal_spatial_tracking": {
            "resolved_hex_register_nibble": "0x5" # State 0x5 triggers natural loop diversion
        },
        "visio_data_visualizer_meta": {
            "asset_name": "Electric CAT Hydro Shifter",
            "university_owner": "University of Washington AG Cohort"
        }
    }
    
    alarm_subsystem = LiveNetworkAudioAlarm()
    print("[*] Testing dynamic out-of-grid paleo-channel audio announcer...")
    packed_string = json.dumps(mock_natural_waterway_frame)
