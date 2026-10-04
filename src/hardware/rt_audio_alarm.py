# File Path: src/hardware/rt_audio_alarm.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Aviation-Aligned Asynchronous Text-to-Speech (TTS) Control Room Alarm.

Ingests real-time hardware status metrics and generates non-abbreviated,
FAA-standardized style PIREP auditory advisories to prevent property breach events.
"""

import os
import sys
import json
import threading
import pyttsx3

class ControlRoomAudioAlarm:
    def __init__(self, voice_rate=165):
        # Initialize the cross-platform Text-to-Speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', voice_rate)
        
        # Select a crisp, clean voice profile (prefers an articulate, clear speech pattern)
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 0:
            # Default to an authoritative voice variant if present
            self.tts_engine.setProperty('voice', voices[0].id)

    def formulate_aviation_style_advisory(self, node_metadata):
        """
        Translates raw hardware register exceptions into a structured, 
        non-abbreviated FAA-style advisory string.
        """
        asset_name = node_metadata.get("asset_name", "UNKNOWN ASSET")
        owner = node_metadata.get("university_owner", "CONSORTIUM FORCE")
        
        # Pull hazard flags out of the metadata dictionary
        clamp_active = node_metadata.get("boundary_clamp_tripped", False)
        torque_fault = node_metadata.get("torque_overload_fault", False)
        wind_hazard = node_metadata.get("wind_gale_hazard", False)
        
        # Seed the standard message framing preamble
        advisory_text = f"Attention Ballard Control Room. Advisory message follows for {owner} field assets. "

        if clamp_active:
            # Build string mapping exact property perimeter lock states
            advisory_text += (
                f"Pilot Report Event Profile: Critical property line constraint violation detected on "
                f"the {asset_name} platform. The VHDL polyhedral keeping boundary has activated an "
                f"instantaneous hardware line clamp intercept. Tractor coordinates are truncated. "
                f"All auxiliary cutting tools are locked to state zero-x-zero. Property boundary breach has been averted."
            )
        elif torque_fault:
            # Build string mapping mechanical load anomalies
            measured_torque = node_metadata.get("measured_torque_nm", 0.0)
            advisory_text += (
                f"Pilot Report Event Profile: Mechanical exception warning. The {asset_name} implement arm "
                f"is experiencing an extreme joint torque overload fault. Measured force metrics indicate "
                f"{measured_torque:.1f} Newton meters. The Teletank mechanical safety drum has interlocked "
                f"the Westinghouse service brakes to prevent local structural stress fracture."
            )
        elif wind_hazard:
            # Build string mapping microclimatic atmospheric hazards
            wind_speed = node_metadata.get("wind_speed_kts", 0.0)
            advisory_text += (
                f"Pilot Report Event Profile: Localized climatological weather warning. The {asset_name} "
                f"enclosure has detected severe atmospheric wind shear. Measured velocity exceeds "
                f"{wind_speed:.1f} knots. Extreme crosswind drift compensation is active. Core mainframe "
                f"L-N-O-I optic rings are entering protective data shelter routing loops."
            )
        else:
            # Nominal telemetry confirmation message
            hex_state = node_metadata.get("active_hex_state", "0xF")
            advisory_text += (
                f"Pristine status confirmed. The {asset_name} tracking parameters are completely inside "
                f"registered county layout bounds. System register state is nominal hexadecimal {hex_state}."
            )

        return advisory_text

    def _speak_worker(self, complete_message_string):
        """Internal low-level worker running natively inside the background thread."""
        try:
            # Enforce an isolated execution loop for the speech engine instance
            engine_instance = pyttsx3.init()
            engine_instance.setProperty('rate', 165)
            engine_instance.say(complete_message_string)
            engine_instance.runAndWait()
        except Exception as err:
            print(f"[-] Asynchronous audio subsystem exception caught: {str(err)}", file=sys.stderr)

    def dispatch_alert_announcement_async(self, node_metadata):
        """
        Forks a non-blocking background thread to vocalize the aviation advisory 
        without freezing your real-time 3D Unreal Engine spatial update pipelines.
        """
        message = self.formulate_aviation_style_advisory(node_metadata)
        
        # Instantiate a detached thread loop to prevent frame rate drops in the control room
        audio_thread = threading.Thread(target=self._speak_worker, args=(message,))
        audio_thread.daemon = True
        audio_thread.start()
        
        return message

# =========================================================================
# RUNTIME INTEGRITY EVALUATION PASS
# =========================================================================
if __name__ == "__main__":
    # Test cases matching the incoming VHDL property-line breach exceptions
    mock_vhdl_exception = {
        "asset_name": "Rheinmetall Kodiak Autonomous Vehicle",
        "university_owner": "University of Washington AG Cohort",
        "boundary_clamp_tripped": True,
        "torque_overload_fault": False,
        "wind_gale_hazard": False,
        "active_hex_state": "0x0"
    }

    alarm_system = ControlRoomAudioAlarm()
    print("[*] Processing VHDL boundary exception array through aviation speech matrix...")
    broadcast_text = alarm_system.dispatch_alert_announcement_async(mock_vhdl_exception)
    
    print("\n[📢 Live Broadcast String Output]:")
    print(broadcast_text)
    
    # Keep main thread alive momentarily in local testing mode to allow background speaker to flush
    time.sleep(12)
    print("\n[+] Audio dispatch pass complete.")
