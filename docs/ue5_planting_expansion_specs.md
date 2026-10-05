# UE5 Planting Expansion Wireframe & Drainage Overlay Specification
## Volumetric Bounding Box Rendering & Core Scale Rules

---

### 1. Color-Coded Shape Overlay Profiles

When the `PlantingZoneOptimizer` script streams telemetry tokens over your private network bridge, your custom Unreal viewport actors intercept the data fields and project floating geometric meshes into the scene workspace:

*   **Natural Soft Bed Boundary (Oval/Meander):** Renders a soft, glowing **Saturated Violet Silhouette (Hex #8A2BE2)** tracing the exact outer edge of the ancient water channel. This highlights the baseline root matrix.
*   **Optimized Crop Plot Boundary (Square/Rectangle):** Projects a crisp, bright **Emerald Green Grid Frame (Hex #00FF00)** box fitted inside or framing the oval. This shows the maximum cultivable field space.
*   **Hydrologic Drainage Vectors (Ditches):** Overlays flashing **Neon Orange Arrows (Hex #FF4500)** directly on top of your existing drainage line actors. The text labels dynamically render the required expansion metrics (e.g., `+124.5mm WIDEN` or `+82.1mm DEEPEN`) right in the operator's field of view.

---

### 2. Toolhead Interlock Protective Limits
To safeguard the organic integrity of the newly mapped crop block, the hardware layer enforces a strict execution rule:

*   **Cutting Lockout Rule:** While operating within the verified **State 0x5 (Protected Soft Planting Sector)**, your physical **`rt_irrigation_gatekeeper.vhd`** FPGA chip cuts all power to primary excavation toolheads. 
*   **Downstream Release:** Heavy grading tools like the **Rheinmetall Kodiak AEV** are completely locked out until the tractor drives clear of the emerald box boundaries, protecting your natural water paths from destructive digital grading overshoot.
