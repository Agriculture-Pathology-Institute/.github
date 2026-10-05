# UE5 Leveling Square Wireframe & Voxel Shader Specification
## 32-Bit Coordinate Alignment & Volumetric Rendering Rules

---

### 1. Color-Coded Dimension Profiles

When incoming JSON strings stream over your private network bridge, the engine unboxes the `structural_leveling_square` parameters and automatically overlays bounding meshes formatted to reflect footprint utility:

*   **Small High-Altitude Footprint (`TOWER_FOOTPRINT` / Size <= 5m):** Renders a glowing **Electric Cyan Wireframe (Hex #00FFFF)** outline. Used to pinpoint rigid anchors for communication masts, weather arrays, or small high-torque crane bases.
*   **Medium Equipment Footprint (`MACHINERY_PAD` / Size 5m–10m):** Renders a solid **Cobalt Blue Translucent Mesh (Hex #0044FF)** base layer. Optimized for mounting agricultural processors, sorting shakers, or auxiliary water storage tanks.
*   **Large Heavy Industrial Footprint (`HEAVY_MACHINERY_PAD` / Size >= 10m):** Renders a **Brilliant Gold Geometric Plate (Hex #FFD700)** grid line matrix. Used to map structural concrete pours for turbine sub-stations or heavy processing barns.

---

### 2. Safety Interlock Strobe Overrides
If the structural base logic reports a safety failure (`geotechnical_foundation_safety_lock = false`), the voxel material state undergoes an immediate override condition:

*   **Visual Hazard Behavior:** The entire leveling square wireframe snaps from its standard color to a **Blinking Hazard Crimson Red (Hex #FF0000)** strobe pulsing at a frequency of **5.0 Hz**.
*   **Tractor Interlock:** The control core blocks your **Rheinmetall Kodiak AEV** blade deployment or **Electric CAT** digging actuators from starting a cut pass inside the failed pad zone, completely preventing foundation settlement cracks down line [0.1.20, 1.20].
