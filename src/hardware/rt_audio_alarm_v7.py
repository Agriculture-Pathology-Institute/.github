# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Production Asynchronous Network Audio Subroutine & PIREP Drainage Broadcaster.

Parses live cross-server JSON frames to vocalize rectangular crop expansions,
volumetric storm-water runoff increases, and precise ditch dimension scaling.
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
        self.last_announcement_time = 0
        self.cooldown_seconds = 4.0 

    def formulate_aviation_soil_advisory(self, univac_json_frame):
        """
        Parses live structured Univac network objects and converts plot expansion 
        and hydrologic scaling parameters into an FAA-standardized PIREP alert.
        """
        try:
            header = univac_json_frame.get("univac_core_header", {})
            tracking = univac_json_frame.get("unreal_spatial_tracking", {})
            optimization = univac_json_frame.get("agricultural_plot_optimization", {})
            
            assigned_hex = tracking.get("resolved_hex_register_nibble", "0xF")
            architecture_type = header.get("system_architecture", "")
            
            # Extract volumetric geometric parameters
            natural_area = optimization.get("natural_oval_bounding_area_m2", 0.0)
            rect_area = optimization.get("calculated_rectangular_area_m2", 0.0)
            dimensions = optimization.get("optimized_plot_dimensions_m", [0.0, 0.0])
            
            # Extract nested hydrologic drainage expansion requirements
            drainage = optimization.get("dynamic_drainage_scaling", {})
            added_runoff = drainage.get("added_stormwater_runoff_m3_hr", 0.0)
            widen_mm = drainage.get("recommended_ditch_widening_mm", 0.0)
            deepen_mm = drainage.get("recommended_ditch_deepening_mm", 0.0)
            
            meta = univac_json_frame.get("visio_data_visualizer_meta", {})
            owner = meta.get("university_owner", "UW AG Cohort")

            advisory = f"Attention Ballard Control Room. Live Pilot Report Update follows for {owner} assets. "
            
            # 1. EVALUATE ACTIVE PLOT OPTIMIZATION SHAPE EXPANSION CODES
            if architecture_type == "PLANETARY_PLOT_GEOMETRIC_OPTIMIZER" or assigned_hex == "0x5":
                advisory += (
                    f"Natural Waterway Optimization Event Processed. "
                    f"A natural oval field footprint measuring {natural_area:.1f} square meters has been "
                    f"successfully expanded into a regular agricultural crop block measuring {dimensions[0]:.1f} meters "
                    f"width, by {dimensions[1]:.1f} meters length, establishing a total cultivated area of {rect_area:.1f} "
                    f"square meters. To counteract the increased runoff footprint and protect crop root integrity under "
                    f"Manning open-channel velocity rules, the local drainage routes require scaling. "
                    f"The commercial fleet implements must widen the existing drainage ditches by exactly {widen_mm:.1f} millimeters, "
                    f"or deepen the channels by exactly {deepen_mm:.1f} millimeters. This channel buffer accommodates "
                    f"an additional stormwater surge capacity of {added_runoff:.1f} cubic meters per hour. "
                    f"Crop zone protection remains enforced."
                )
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
    # Test execution harness checking the optimized plot expansion advisory flow
    mock_frame = {
        "univac_core_header": {"system_architecture": "PLANETARY_PLOT_GEOMETRIC_OPTIMIZER"},
        "unreal_spatial_tracking": {"resolved_hex_register_nibble": "0x5"},
        "agricultural_plot_optimization": {
            "natural_oval_bounding_area_m2": 2199.11,
            "calculated_rectangular_area_m2": 1400.00,
            "optimized_plot_dimensions_m": [49.49, 28.28],
            "dynamic_drainage_scaling": {
                "added_stormwater_runoff_m3_hr": 253.12,
                "recommended_ditch_widening_mm": 142.5,
                "recommended_ditch_deepening_mm": 95.1
            }
        },
        "visio_data_visualizer_meta": {"university_owner": "University of Washington AG Cohort"}
    }
    alarm_subsystem = LiveNetworkAudioAlarm()
    print("[*] Instantiating hydrologic ditch scaling voice simulation run...")
    alarm_subsystem.process_incoming_network_stream(json.dumps(mock_frame))
    time.sleep(12)
