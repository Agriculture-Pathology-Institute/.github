import re
import json

def parse_scad_to_config(scad_text):
    config = {
        "metadata": {
            "office_location": "UW Medicine Ballard Office - Master Integration",
            "coordinate_system": "OpenSCAD Vector Mapping Space"
        },
        "infrastructure_modbus_rs485": [],
        "machinery_isobus_j1939": []
    }
    
    translate_pattern = re.compile(r'translate\\s*\\(\\s*\\[\\s*([\\d\\.-]+)\\s*,\\s*([\\d\\.-]+)\\s*,\\s*([\\d\\.-]+)\\s*\\]\\s*\\)\\s*\\{\\s*//\\s*(.*)')
    modbus_ids = 10
    
    for line in scad_text.splitlines():
        match = translate_pattern.search(line)
        if match:
            x = float(match.group(1))
            y = float(match.group(2))
            z = float(match.group(3))
            label = match.group(4).strip().lower()
            
            if any(k in label for k in ["turbine", "greenhouse", "drainage"]):
                node_type = "ge_wind_turbine" if "turbine" in label else ("led_greenhouse" if "greenhouse" in label else "drainage_system")
                config["infrastructure_modbus_rs485"].append({
                    "node_id": modbus_ids,
                    "node_type": node_type,
                    "modbus_register_start": f"0x{modbus_ids:04X}",
                    "spatial_center_scad": [x, y, z]
                })
                modbus_ids += 1
            elif any(k in label for k in ["kodiak", "cat", "deere"]):
                brand = "Rheinmetall Kodiak" if "kodiak" in label else ("Electric CAT" if "cat" in label else "John Deere")
                config["machinery_isobus_j1939"].append({
                    "ecu_address": f"0x{80 + len(config['machinery_isobus_j1939']):02X}",
                    "equipment_brand": brand,
                    "can_pgn_mapping": 61444,
                    "clearance_radius_meters": 4.5
                })
    return config
