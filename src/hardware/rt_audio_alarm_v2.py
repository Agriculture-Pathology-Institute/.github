# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Asynchronous Network Audio Subroutine & PIREP Weather Broadcaster.

Directly parses live JSON strings streaming from the RtJsonNetworkBridge server 
to vocalize immediate boundary and climatological wind-shear hazards.
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

    def formulate_aviation_weather_advisory(self, univac_json_frame):
        """
        Parses live structured Univac network objects and converts telemetry metrics
        into a non-abbreviated, FAA-standardized PIREP alert statement.
        """
        try:
            header = univac_json_frame.get("univac_core_header", {})
            isolation_matrix = univac_json_frame.get("boundary_isolation_matrix", {})
            spatial_tracking = univac_json_frame.get("unreal_spatial_tracking", {})
            atmosphere = univac_json_frame.get("atmospheric_fluid_dynamics", {})
            
            # Extract active system state variables
            alert_status = isolation_matrix.get("safety_alert_status", "NOMINAL")
            assigned_hex = spatial_tracking.get("assigned_hex_safety_register", "0xF")
            wind_speed = atmosphere.get("scaled_wind_speed_kts", 0.0)
            wind_pressure = atmosphere.get("calculated_wind_pressure_pa", 0.0)
            
            # Seed the standard message framing preamble
            advisory = "Attention Ballard Control Room. Live Pilot Report Update follows. "
            
            if assigned_hex == "0x0":
                if "CLAMP" in alert_status:
                    advisory += (
                        f"Critical property line constraint violation detected. The VHDL polyhedral "
                        f"keeping boundary has activated an immediate hardware line clamp intercept. "
                        f"Tractor coordinates are truncated. Systems are locked to state zero-x-zero. "
                        f"Property boundary breach has been averted."
                    )
                else:
                    advisory += (
                        f"Severe atmospheric microclimate hazard encountered. Wind velocity has breached "
                        f"safety limits, registering at {wind_speed:.1f} knots with a structural load pressure of "
                        f"{wind_pressure:.1f} pascals. Mainframe core has triggered an autonomic handshake "
                        f"velocity override. Fleet implements are restricted to state zero-x-zero."
                    )
            elif assigned_hex == "0xE":
                advisory += (
                    f"Microclimate boundary advisory. Crosswind shear force acceleration has crossed "
                    f"the one-hundred and fifty pascal threshold. Dynamic wind drift compensation is active. "
                    f"Tractor registers have transitioned to high-torque drive correction profile state zero-x-e."
                )
            else:
                advisory += (
                    f"Climatological and spatial status is nominal. Wind speed is trailing at "
                    f"{wind_speed:.1f} knots. Tracking coordinates are inside registered boundaries. "
                    f"System register is executing profile state zero-x-f."
                )
                
            return advisory
        except Exception as err:
            return f"Control room telemetry parsing error. Exception code details: {str(err)}."

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
                
            advisory_speech = self.formulate_aviation_weather_advisory(data)
            
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
    # Test packet matching a 55-knot gale warning event generated by the mainframe
    mock_univac_network_frame = {
        "univac_core_header": {
            "system_architecture": "UNIVAC_IX_CORE_FABRIC",
            "timestamp_epoch_ms": int(time.time() * 1000)
        },
        "boundary_isolation_matrix": {
            "hardware_clamp_active": False,
            "safety_alert_status": "CRITICAL_GALE_VELOCITY_SUSPENSION_TRIGGERED"
        },
        "unreal_spatial_tracking": {
            "assigned_hex_safety_register": "0x0"
        },
        "atmospheric_fluid_dynamics": {
            "scaled_wind_speed_kts": 52.4,
            "calculated_wind_pressure_pa": 241.8
        }
    }
    
    alarm_subsystem = LiveNetworkAudioAlarm()
    print("[*] Simulating live network socket arrival data packet...")
    packed_string = json.dumps(mock_univac_network_frame)
    result_code = alarm_subsystem.process_incoming_network_stream(packed_string)
    print(f"[+] Operational broadcast response status: {result_code}")
    
    # Allow background speaker process to complete before script termination
    time.sleep(12)
