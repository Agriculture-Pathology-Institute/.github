# File Path: scripts/extract_boundaries.py
#!/usr/bin/env python3
"""
Revolutionary Technology Company — UNIVAC IX Systems Group
Automated Unreal Engine 5 Mesh Boundary Extraction Pipeline.

Parses spatial landscape object files, converts centimeter data vectors 
to millimeter registers, and updates config.yaml layout mappings dynamically.
"""

import os
import sys
import yaml

class UnrealMeshExtractor:
    def __init__(self, obj_mesh_path="Assets/Mesh/farm_boundary.obj", config_path="config.yaml"):
        self.obj_mesh_path = obj_mesh_path
        self.config_path = config_path

    def extract_outer_boundary_polygon(self, max_points=4):
        """Parses geometric vertex positions and handles metric scale transformations."""
        print(f"[*] Extracting landscape boundaries from UE5 asset mesh: {self.obj_mesh_path}")
        
        if not os.path.exists(self.obj_mesh_path):
            print(f"[⚠️ Warning] Target mesh not found. Injecting nominal fallback riverbank matrix.")
            return [
                {"x": 100000, "y": 100000},
                {"x": 500000, "y": 120000},
                {"x": 480000, "y": 350000},
                {"x": 120000, "y": 320000}
            ]

        extracted_vertices = []
        with open(self.obj_mesh_path, "r", encoding="utf-8") as mesh_file:
            for line in mesh_file:
                if line.startswith("v "): # Identify vector coordinate lines
                    tokens = line.split()
                    # Unreal space tracking represents vectors in float centimeters
                    ue5_x_cm = float(tokens[1])
                    ue5_y_cm = float(tokens[2])
                    
                    # Transform floating centimeters straight to 32-bit millimeter integers
                    mm_x = int(ue5_x_cm * 10.0)
                    mm_y = int(ue5_y_cm * 10.0)
                    extracted_vertices.append({"x": mm_x, "y": mm_y})
                    
                    if len(extracted_vertices) >= max_points:
                        break
                        
        return extracted_vertices

    def flush_vectors_to_config(self):
        """Flushes newly compiled polyhedral coordinates into the system configuration configuration file."""
        poly_vertices = self.extract_outer_boundary_polygon()
        
        # Load active settings envelope to preserve background parameters
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                current_config = yaml.safe_load(f) or {}
        else:
            current_config = {}

        # Update the target boundary coordinate parameters dynamically
        if "planetary_geodetic_anchor" not in current_config:
            current_config["planetary_geodetic_anchor"] = {}
            
        current_config["planetary_geodetic_anchor"]["dynamic_polyhedral_vertices"] = poly_vertices
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(current_config, f, default_flow_style=False)
            
        print(f"[+] Successfully wrote {len(poly_vertices)} boundary mesh points straight into: {self.config_path}")

if __name__ == "__main__":
    extractor = UnrealMeshExtractor()
    extractor.flush_vectors_to_config()
