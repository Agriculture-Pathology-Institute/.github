# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Asynchronous Network Audio Subroutine & PIREP Network Security Broadcaster.

Parses live cross-server JSON frames to vocalize unauthorized access blocks,
un-whitelisted peer attempts, and immediate network perimeter intrusion alerts.
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
        Parses incoming network security metrics and converts intrusion exceptions 
        into a non-abbreviated, FAA-standardized PIREP alert.
        """
        try:
            # Handle deep extraction across nested architectural blocks
            header = univac_json_frame.get("univac_core_header", {})
            tracking = univac_json_frame.get("unreal_spatial_tracking", {})
            diagnostics = univac_json_frame.get("hardware_fault_diagnostics", {})
            meta = univac_json_frame.get("visio_data_visualizer_meta", {})
            
            # Extract basic state and interlock parameters
            assigned_hex = univac_json_frame.get("request_hex_state", "0xF")
            interlock_status = diagnostics.get("resolved_interlock_state", "UNLOCKED_OPERATIONAL_NOMINAL")
            security_compromised = meta.get("security_link_compromised", False)
            
            # Extract asset parameters
            owner = meta.get("university_owner", "Unknown Actor")
            asset = meta.get("asset_name", "Autonomous Field Unit")

            # Seed the standard message framing preamble
            advisory = f"Attention Ballard Control Room. Live Pilot Report Update follows. "
            
            # 1. CHECK FOR NATIVE NETWORK INTRUSION SECURITY OVERRIDES (State 0x0 / Security Fault)
            if assigned_hex == "0x0" and (security_compromised or interlock_status == "SECURITY_FAULT_UNAUTHORIZED_REMOTE_PEER_BLOCKED"):
                # Target matches your precise verbal advisory instruction string
                advisory += (
                    f"Network Intrusion Detected. An un-whitelisted external device or remote control emulator "
                    f"has attempted unauthorized socket packet injection over the active data bus lines. "
                    f"The zero-trust planetary environment controller has identified a security perimeter mismatch "
                    f"and completely dropped the packet frame. The hardware interlock has engaged, collapsing "
                    f"the main security rail to state zero-x-zero. All tractor steering systems, hydraulic toolheads, "
                    f"and physical power booster lines are pinned to a safe lockdown state. Network perimeter remains secure."
                )
            
            # 2. STANDARD SPATIAL BOUNDARY OVERRIDES (State 0x0)
            elif assigned_hex == "0x0":
                advisory += (
                    f"Pilot Report Event Profile: Critical safety interlock active. An unauthorized "
                    f"boundary trespass or severe structural overvoltage condition has been logged. "
                    f"The main security rail has collapsed mechanically to state zero-x-zero."
                )
            else:
                # Nominal running baseline audio loop confirmation
                advisory += (
                    f"Pristine status confirmed. The system is operating inside valid geodetic coordinates. "
                    f"Network peer authentication is secure. Current system profile is executing state zero-x-f."
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
            assigned_hex = data.get("request_hex_state", "0xF")
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
    # Test execution harness checking the network intrusion security alert flow
    mock_intrusion_frame = {
        "univac_core_header": {"system_architecture": "REGULATORY_COMPLIANCE_PIPELINE"},
        "request_hex_state": "0x0",
        "hardware_fault_diagnostics": {
            "peer_identity_authenticated": False,
            "resolved_interlock_state": "SECURITY_FAULT_UNAUTHORIZED_REMOTE_PEER_BLOCKED"
        },
        "visio_data_visualizer_meta": {
            "security_link_compromised": True,
            "university_owner": "REJECTED_UNKNOWN_ACTOR"
        }
    }
    
    alarm_subsystem = LiveNetworkAudioAlarm()
    print("[*] Instantiating security perimeter intrusion voice simulation run...")
    alarm_subsystem.process_incoming_network_stream(json.dumps(mock_intrusion_frame))
    time.sleep(12)
