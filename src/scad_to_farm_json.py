# -*- coding: utf-8 -*-
"""
Agriculture Pathology Institute
OpenSCAD-to-Autonomous Farm JSON Compiler
Designed for the UW Medicine Ballard Working Session
"""

import re
import json
import sys

def parse_openscad_anchors(scad_text):
    """
    Parses OpenSCAD source files to extract standardized module deployments,
    variables, and coordinates to wire them up to low-voltage configurations.
    """
    # Look for module instantiations or coordinate definitions
    # e.g., kodiak_charger_pad = [150, 320, 0]; // VOLTAGE=480V_AC
    var_pattern = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*=\s*\[([^\]]+)\]\s*;\s*(?://\s*(.*))?$', re.MULTIMALER)
    # e.g., translate([10, 20, 5]) greenhouse_led_array();
    translate_pattern = re.compile(r'translate\s*\(\s*\[([^\]]+)\]\s*\)\s*([a-zA-Z0-9_]+)\s*\([^)]*\)\s*;')

    nodes = {}
    
    # Check variables
    for match in var_pattern.finditer(scad_text):
        name = match.group(1)
        coords = [float(x.strip()) for x in match.group(2).split(',')]
        metadata_raw = match.group(3) if match.group(3) else ""
        
        metadata = {}
        if "VOLTAGE" in metadata_raw:
            v_match = re.search(r'VOLTAGE=([A-Za-z0-9_]+)', metadata_raw)
            if v_match: metadata["voltage_rail"] = v_match.group(1)
            
        nodes[name] = {
            "coordinates_xyz": coords,
            "source_type": "variable_declaration",
            "metadata": metadata
        }

    # Check translations
    for match in translate_pattern.finditer(scad_text):
        coords = [float(x.strip()) for x in match.group(1).split(',')]
        instance_name = match.group(2)
        
        # Inject standard infrastructure mapping based on common names
        voltage = "12V_DC"
        if "charger" in instance_name.lower() or "kodiak" in instance_name.lower():
            voltage = "480V_AC"
        elif "greenhouse" in instance_name.lower() and "led" in instance_name.lower():
            voltage = "24V_DC"
        elif "turbine" in instance_name.lower():
            voltage = "690V_AC"
            
        nodes[f"{instance_name}_{len(nodes)}"] = {
            "coordinates_xyz": coords,
            "source_type": "translation_instance",
            "metadata": {
                "voltage_rail": voltage,
                "is_isolated": "DC" in voltage
            }
        }
        
    return nodes

def compile_to_farm_schema(scad_nodes):
    farm_config = {
        "$schema": "https://agriculturepathology.com/schemas/smart_farm_v2.json",
        "organization": "Agriculture Pathology Institute",
        "facility_context": "UW Medicine Ballard Engineering Session",
        "power_grid": {
            "source": "GE Wind Turbines",
            "distribution_nodes": []
        },
        "autonomous_grading_waypoints": []
    }
    
    for node_name, data in scad_nodes.items():
        v_rail = data["metadata"].get("voltage_rail", "12V_DC")
        
        node_entry = {
            "node_id": node_name,
            "spatial_coordinates": {
                "x": data["coordinates_xyz"][0],
                "y": data["coordinates_xyz"][1],
                "z": data["coordinates_xyz"][2]
            },
            "electrical_profile": {
                "operating_voltage": v_rail,
                "circuit_isolated": data["metadata"].get("is_isolated", True)
            }
        }
        
        # Route to path planning if it is grading/drainage infrastructure
        if "drainage" in node_name.lower() or "charger" in node_name.lower():
            farm_config["autonomous_grading_waypoints"].append({
                "target_node": node_name,
                "clearance_radius_meters": 5.0 if "charger" in node_name.lower() else 1.5,
                "invert_elevation_offset": -1.2 if "drainage" in node_name.lower() else 0.0
            })
            
        farm_config["power_grid"]["distribution_nodes"].append(node_entry)
        
    return farm_config

if __name__ == "__main__":
    sample_scad = """
    // Agriculture Pathology Institute - Master OpenSCAD Layout
    GE_TURBINE_COUPLING_ANCR = [0, 0, 10]; // VOLTAGE=690V_AC
    KODIAK_CHARGER_PAD_A = [150, 300, 0]; // VOLTAGE=480V_AC
    
    translate([45, 120, 0]) greenhouse_led_array_0();
    translate([60, 120, -0.5]) subsurface_drainage_valve_0();
    """
    
    print("Parsing OpenSCAD geometric context...")
    nodes = parse_openscad_anchors(sample_scad)
    config = compile_to_farm_schema(nodes)
    
    print(json.dumps(config, indent=2))
