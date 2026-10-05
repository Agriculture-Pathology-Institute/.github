# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Asynchronous Network Audio Subroutine & PIREP Weather/Soil Broadcaster.

Parses live cross-server JSON frames to vocalize distinct structural landslide 
alarms and "Crop Zone Protection Enforced" safety advisories.
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
        Parses live structured Univac network objects and converts geotechnical and 
        operational mode variables into a non-abbreviated, FAA-standardized PIREP alert.
        """
        try:
            # Handle deep extraction across nested architectural blocks
            header = univac_json_frame.get("univac_core_header", {})
            isolation_matrix = univac_json_frame.get("boundary_isolation_matrix", {})
            spatial_tracking = univac_json_frame.get("unreal_spatial_tracking", {})
            geotech = univac_json_frame.get("sub_surface_volumetric_matrix", {})
            overrides = univac_json_frame.get("priority_routing_overrides", {})
            
            # Extract state metrics
            assigned_hex = spatial_tracking.get("assigned_hex_safety_register", "0xF")
            density = geotech.get("calculated_soil_density_kg_m3", 1500.0)
            volume_cut = univac_json_frame.get("volume_cut_m3", 0.0)
            
            # Determine active operational mode from the Edwards supervisor block
            ballard_ops = overrides.get("tier_02_commercial_ballard_operations", {})
            active_mode = ballard_ops.get("active_mode", "PLANTING_MODE")
            
            # Extract asset parameters
            meta = univac_json_frame.get("visio_data_visualizer_meta", {})
            owner = meta.get("university_owner", "UW AG Cohort")
            asset = meta.get("asset_name", "Autonomous Field Unit")

            # Seed the standard message framing preamble
            advisory = f"Attention Ballard Control Room. Live Pilot Report Update follows for {owner} assets. "
            
            if assigned_hex == "0x0":
                # Check for structural soil failure density drop boundaries
                if density < 1200.0:
                    if active_mode == "PLANTING_MODE":
                        # CROP ZONE SECURITY VIOLATION: Tools attempting to dig up soft topsoil
                        advisory += (
                            f"Pilot Report Event Profile: Crop Zone Protection Enforced. "
                            f"The {asset} toolhead array has attempted unauthorized excavation "
                            f"inside a protected soft topsoil quadrant calibrated for root growth. "
                            f"The Edwards supervisory loop has broken the circuit mechanically. "
                            f"All implement cutting mechanisms have been locked to state zero-x-zero "
                            f"to preserve the agricultural zone. Human farming beds remain uncompromised."
                        )
                    else:
                        # STRUCTURAL LANDSLIDE FAULT: Heavy vehicle sinking into mud cavity
                        advisory += (
                            f"Pilot Report Event Profile: Geotechnical collapse hazard. "
                            f"The airborne acoustic tomography sensor has tracked an extreme subgrade "
                            f"density drop registering at {density:.1f} kilograms per cubic meter. "
                            f"The system is currently operating in excavation mode. "
                            f"The loop has popped open mechanically to prevent structural vehicle overturn. "
                            f"Fleet actuators are locked to state zero-x-zero."
                        )
                else:
                    # General property line fence intercept
                    advisory += (
                        f"Pilot Report Event Profile: Critical property line boundary constraint "
                        f"violation detected on the {asset}. The VHDL polyhedral clipper has activated "
                        f"an immediate line clamp intercept. System safety register has dropped to state zero-x-zero."
                    )
            else:
                # Nominal running baseline audio loop confirmation
                advisory += (
                    f"Pristine status confirmed. The {asset} is operating inside valid geodetic coordinates. "
                    f"Subgrade soil density is stable at {density:.1f} kilograms per cubic meter. "
                    f"Current system profile is state zero-x-f."
                )
                
            return advisory
        except Exception as err:
            return f"Control room telemetry parsing exception. Code details: {str(err)}."

security_compromised = diagnostics.get("security_link_compromised", False) or (interlock_status == "SECURITY_FAULT_UNAUTHORIZED_REMOTE_PEER_BLOCKED")

if security_compromised:
    advisory += (
        f"Pilot Report Security Exception Alert. An unauthorized remote control signal source "
        f"has attempted injection variables into the active farm tracking bus. "
        f"The peer identity verification matrix has flagged an un-vetted university node. "
        f"The UNIVAC IX main operating fabric has blocked the packet token stream natively. "
        f"All field implements and vehicle power substations have been forced into hard protective "
        f"zero-x-zero shutdown locks. Remote land carving tools are fully isolated. Base grid secure."
    )

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
            assigned_hex = data.get("unreal_spatial_tracking", {}).get("assigned_hex_safety_register", "0xF")
            if assigned_hex == "0xF" and (current_time - self.last_announcement_time) < self.cooldown_seconds:
                return "SKIPPED_COOLDOWN_ACTIVE"
                
            advisory_speech = self.formulate_aviation_soil_advisory(data)
            
            # Reset countdown window register and fork background voice thread
            self.last_announcement_time = current_time
            audio_thread = threading.Thread(target=self._speak_worker_thread, args=(advisory_speech,))
            audio_thread.daemon = True
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
    # Test packet matching a crop zone excavation tool violation event
    mock_univac_network_frame = {
        "univac_core_header": {"system_architecture": "REGULATORY_COMPLIANCE_PIPELINE", "timestamp_epoch_ms": int(time.time() * 1000)},
        "boundary_isolation_matrix": {"hardware_clamp_active": True, "safety_alert_status": "CRITICAL_PROPERTY_LINE_CLAMP_EVENT"},
        "unreal_spatial_tracking": {"assigned_hex_safety_register": "0x0"},
        "sub_surface_volumetric_matrix": {"calculated_soil_density_kg_m3": 1100.0, "structural_stability_verified": True},
        "priority_routing_overrides": {
            "tier_02_commercial_ballard_operations": {
                "active_mode": "PLANTING_MODE" # System is set to look after soft topsoil
            }
        },
        "visio_data_visualizer_meta": {
            "asset_name": "Rheinmetall Kodiak Autonomous Shredder",
            "university_owner": "University of Washington AG Cohort"
        },
        "volume_cut_m3": 5.2 # Excavator is active inside the roots field!
    }
    
    alarm_subsystem = LiveNetworkAudioAlarm()
    print("[*] Testing dynamic dual-mode agricultural voice broadcaster...")
    packed_string = json.dumps(mock_univac_network_frame)
    result_code = alarm_subsystem.process_incoming_network_stream(packed_string)
    print(f"[+] Operational broadcast response status: {result_code}")
    
