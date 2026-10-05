# UE5 Independent Asset Stacking & Volumetric Coverage Shader Specification
## 32-Bit Nested JSON Architecture & Blueprint Linking Rules

---

### 1. Decoupled Volumetric Rendering Pass

When the `assigned_installation_payload` matrix streams across your private network bridge, your custom Unreal Engine 5 viewports dynamically instance and link the asset blueprint without modifying the underlying terrain mesh transformations:

*   **Asset Anchor Position (`installation_anchor_coordinates_mm`):** Spawns a floating **High-Vis Neon Magenta Ring (Hex #FF00FF)** marker directly centered on top of the parent leveling square surface. This defines the exact mechanical centerpoint for the swivel flange.
*   **Water Jet Coverage Dome (`fluid_hydraulics_matrix`):** Renders a sweeping, translucent **Aero Blue Volumetric Dome (Hex #00FFFF, Opacity 0.20)** extending outward from the ring. The dome radius reads the `effective_throw_radius_meters` variable to visually show the complete water curtain path.

---

### 2. Live Telemetry Data Feed
The viewport HUD component parses the independent payload layer to render fluid parameter data arrays on-screen right next to the physical installation coordinates:
*   `Hourly Discharge Rate:` Pulled dynamically from `flow_discharge_m3_hr` (Cubic meters per hour) or `flow_discharge_gpm` (Gallons per minute).
*   `Active Loop Interlock:` If a fire detection pipe loops or a **normally closed contact** breaks, the shader triggers a **5.0 Hz stroboscopic hazard flash**, and the **`rt_irrigation_gatekeeper.vhd`** chip instantly snaps local solenoid valves open to flood the zone [1.15, 1.20].
