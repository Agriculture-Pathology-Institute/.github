Agriculture Pathology Institute
----------------------------------

Multi-Core Accelerated, Closed-Loop Planetary Mainframe OS & Real-Time 3D Land Carving Ecosystem
------------------------------------------------------------------------------------------------

Welcome to the master control repository of the Agriculture Pathology Institute (API). This centralized organizational workspace orchestrates the server-to-server networks, autonomic planetary environmental controllers, and automated life-safety interlocks required to sustain independent, high-performance smart farming operations across any country, territory, or off-grid community globally.

Our architecture bridges centuries of computing engineering by unifying Unreal Engine 5 real-time 3D spatial simulation platforms with native 16-state hexadecimal analog computing silicon (0.0V--1.0V), eliminating legacy binary bottlenecks and unmanaged processing latency.

* * * * *

Core Architecture Components & Repositories
----------------------------------------------

The entire multi-university engineering consortium handles code development by isolating tasks into three discrete, clean repositories to guarantee absolute architectural conformity and zero dynamic memory fragmentation:

1\. API / .github (This Workspace)
-------------------------------------

The master software abstraction, microclimatological tracking core, and server-to-server routing network.

-   `validate-config.js`: The central Planetary Environment Controller. Parses live 3D coordinates, topocentric solar radiation vectors, and microclimatic wind shear matrices over a live network TCP socket loop.
-   `config.yaml`: The central platform infrastructure template, locking down real-world geodetic origins (WGS84) and enforcing strict 2-inch (50.8 mm) hardware safety setbacks relative to property boundaries.
-   `src/hardware/rt_json_network_bridge.py`: The server-side Python network gateway. Runs on configuration port `8080` to dynamically parse incoming cross-server JSON frames and map data to internal memory registers.
-   `src/hardware/rt_audio_alarm.py`: The network-aware voice alert subsystem. Parses live telemetry exceptions and vocalizes non-abbreviated, FAA-standardized PIREP weather advisories over control room speakers.
-   `scripts/extract_boundaries.py`: Automated pipeline that extracts landscape boundary vertices directly from Unreal Engine 5 `.obj` meshes and flushes them into the platform configurations.

2\. API / GE-Heavy-Industrial-Weatherproof-Signal-Power-Amplifier
-------------------------------------------------------------------

The physical manufacturing blueprints, 8-layer PCB files, and hardware-in-the-loop (HIL) simulation testbenches.

-   `ge_univac_amplifier.vhd`: Unrolled systolic core current booster. Intercepts native 16-state intervals and leverages wind turbine/hydro power rails to amplify signals across macro antenna arrays.
-   `ge_amplifier_chassis.scad`: Parametric OpenSCAD cast aluminum enclosure featuring 8.0 mm creepage slots, a solid internal Faraday shield wall, and sloped fluid drainage scuppers to handle field moisture.
-   `build_amplifier_netlist.py`: Programmatic KiCad routing script that auto-draws the massive 26.03 mm high-current copper tracks (3oz copper) dictated by IPC-2152 thermodynamic formulas.
-   `verify_pcb_clearance.py`: Design Rule Check (DRC) gatekeeper that automatically ensures a >12.0 mm insulation air gap between high-voltage traces and physical GM-specification mounting fasteners.

3. API / Zephyr-RTOS-Board-Support-Package-BSP
-------------------------------------------------

The out-of-tree hardware configuration layer mapping physical silicon pins directly into the operating system.

-   `rt_hex_board.dts`: Custom hardware Device Tree Source mapping parallel input bit lines (`Q0--Q3` from the Micrel serial converter) and latch lines directly to the TI CD4514B line decoder.
-   `rt_hex_board_defconfig`: Core kernel configurations syncing system frequencies to our 10.0 MHz Stage 2 Industrial Divider clock.

* * * * *

The Priority-Driven Data Pipeline
------------------------------------

To protect adjoining land assets and respect regulatory constraints, data frames parse across our private, encrypted network bridge (`univac_secure_fabric`) using an automated Multi-Tier Priority Routing Override Layer:

```
                  [ USER COMMITS DESIGN OR HARDWARE ADJUSTMENT ]
                                        │
                                        ▼
    ┌───────────────────────────────────────────────────────────────────────┐
    │              .github/workflows/univac_ci.yml VM RUNNER                │
    ├───────────────────────────────────────────────────────────────────────┤
    │  Executes validate-config.js environment matrix checks.               │
    │  Audits verify_pcb_clearance.py to lock out overlapping copper traces.│
    │  Simulates VHDL window comparators under 55-Knot noise surges.       │
    └───────────────────────────────────┬───────────────────────────────────┘
                                        │
         ┌──────────────────────────────┴──────────────────────────────┐
         │                                                             │
         ▼ [ Priority 1: Government XR Viewport ]                      ▼ [ Priority 2: Ballard Commercial Base ]
  [ DOI / OSHA / County Ingestion ]                              [ Downstream Real-World Fleet Actuation ]
  - Locks foveated HUD rendering paths.                          - Energizes 1.0V hex logic amplifiers.
  - Verifies legal clear-zone boundaries.                        - Refreshes Microsoft Visio process maps.
  - Grants multi-party compliance release.                       - Opens hydraulic steering valves to tractors.

```

* * * * *

Production Deployment & Core Execution
-----------------------------------------

The platform is orchestrated entirely within an isolated, zero-trust Docker container framework on an Ubuntu host. Live streaming files are processed strictly inside an ephemeral RAM-disk volume (`tmpfs`) to achieve near-instantaneous execution speeds.

1. Docker Multi-Container Architecture (`docker-compose.yml`)
----------------------------------------------------------------

```
version: '3.8'
services:
  validate-config:
    image: node:20-alpine
    container_name: univac_ix_planetary_controller
    restart: always
    user: "node"
    networks: [- univac_secure_fabric]
    volumes: [".:/usr/src/app:ro", "univac_stream_data:/usr/src/app/Data/UnivacStreams"]
    command: ["node", "validate-config.js"]

  edwards-firewatch-bridge:
    image: python:3.11-slim-bookworm
    container_name: edwards_firewatch_bridge
    restart: always
    runtime: nvidia # Maps straight to host NVIDIA GPU hardware for pixel processing
    networks: [- univac_secure_fabric]
    volumes: [".:/app:ro", "univac_stream_data:/app/Data/UnivacStreams"]
    command: ["python3", "src/hardware/rt_edwards_alarm_driver.py"]

  zephyr-embedded-bridge:
    build: { context: ../GE-Heavy-Industrial-Weatherproof-Signal-Power-Amplifier, dockerfile: Dockerfile.zephyr }
    container_name: zephyr_embedded_bridge
    restart: always
    networks: [- univac_secure_fabric]

```

2. Deployment Commands
-------------------------

To compile the out-of-tree hardware layers, build the zero-trust application containers, and launch the real-time monitoring fabric headlessly from a terminal, execute the following parameters:

```
# Initialize the multi-container prioritized lifecycle loop
docker-compose up -d --build

# Follow the live closed-loop checkback and VHDL line-clamp status entries
docker-compose logs -f --tail=30

# Safely shut down the infrastructure and clear the volatile RAM data buffers
docker-compose down -v

```

* * * * *

The Edwards FireWorks Fail-Safe Integration
----------------------------------------------

Our system integrates an un-interceptable Normally Closed (NC) Fail-Safe Loop Pattern to handle life-safety events. The hardware microcontroller continuously holds its tracking lines HIGH to maintain a complete, closed circuit.

If a tractor experiences a physical polyhedral property line breach, a tool arm registers an extreme torque load fault, or the Edwards FireWatch video analytical engines catch a visual flame indicator via parallel NVIDIA CUDA threads, the control loop pops OPEN instantly. The circuit falls mechanically within `<100ns`, causing the Edwards EST3/FireWorks platform to trigger a building-wide Priority 1 alert, disengage primary electrical contactors, and broadcast non-abbreviated radio-style voice warnings over control room speakers.

* * * * *

Empowering International Agricultural Communities
----------------------------------------------------

By abstracting complex aerospace kinematics and microclimatological fluid equations into an interactive, visual Unreal Engine 5 scene, we empower any community, cooperative, or territory to manage advanced autonomous farming. The user places their vehicles *inside a drawn shape* on a viewport canvas; the underlying native hexadecimal processors handle the environmental stress factors, suppress circuit ripple via thick copper guard rings, and mathematically guarantee the machinery cuts with absolute precision without ever "coloring over the lines" or trespassing on adjacent boundaries.

* * * * *
Industrial Session Engineering Checkpoints
---------------------------------------------

For the engineering cohorts gathered at the UW Medicine Ballard office table, please utilize the following testing scripts to verify hardware parameters before triggering a production fabrication pass:

-   Run `python src/hardware/test_system_suite.py` to launch the automated end-to-end telemetry injection suite and assert Edwards bitmask routing accuracy.
-   Review `docs/ue5_blueprint_json_receiver.md` to map out the C++ asynchronous network component handlers for custom viewport HUD overlays.
