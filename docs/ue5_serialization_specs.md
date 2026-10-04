# UE5 Virtual Workspace Camera & Vector Serialization Protocol
## 32-Bit Fixed-Point Millimeter Register Interface Specifications
**Document Class:** Aerospace & Industrial Telemetry Standards Matrix  
**Core System Target:** UNIVAC IX Core Fabric & VHDL Boundary Clippers  

---

### 1. Architectural Conversion Mathematics

Unreal Engine 5 manages virtual scene coordinates as double-precision floating-point scalars (`double`, `FVector`) mapped in centimeters (1 Unit = 1 cm). Conversely, your custom VHDL systolic arrays and Teletank controllers process hardware coordinates as 32-bit signed fixed-point integers mapped in millimeters (1 LSB = 1 mm). 

To transform virtual vectors into physical registers without causing data rounding drift or arithmetic boundary overflows, all coordinate nodes must process through the following transformation pipeline:

\[\text{Register Value} = \text{floor}\left( \text{UE5 Coordinate (cm)} \times 10.0 \right)\]

#### Conversion Range Constraints
*   **Maximum Positive Bound:** +2,147,483,647 mm (≈ +2,147.48 km from the coordinate origin base)
*   **Maximum Negative Bound:** -2,147,483,648 mm (≈ -2,147.48 km from the coordinate origin base)
*   **Precision Threshold:** Exactly ± 1.0 mm absolute spatial matching.

---

### 2. Binary Telemetry Packet Frame Mapping

All data streamed out of the Unreal Engine 5 network socket thread must be packed into a raw, unpadded binary payload containing the following **36-byte structured frame**. The wire protocol forces a strict **Network Byte Order (Big Endian)** byte-alignment configuration to prevent endianness mismatch faults on the Univac IX mainframe interfaces.

| Byte Offset | Data Field Identifier | Virtual C++ Type | Physical Target Bus Layer | Register Bit Width |
| :--- | :--- | :--- | :--- | :--- |
| **0x00 – 0x03** | `PACKET_HEADER_MAGIC` | `uint32` | Mainframe Validation Identifier (`0x554E4956`) | 32-Bit Unsigned |
| **0x04 – 0x07** | `TIMESTAMP_MS_LOWER`  | `uint32` | Epoch Timing Lower Double-Word | 32-Bit Unsigned |
| **0x08 – 0x0B** | `VECTOR_TARGET_X`     | `double` → `int32` | `TARGET_X_IN` Fixed-Point Millimeters | 32-Bit Signed |
| **0x0C – 0x0F** | `VECTOR_TARGET_Y`     | `double` → `int32` | `TARGET_Y_IN` Fixed-Point Millimeters | 32-Bit Signed |
| **0x10 – 0x13** | `VECTOR_TARGET_Z`     | `double` → `int32` | Subsurface Conduit Elevation Depth | 32-Bit Signed |
| **0x14 – 0x17** | `VEHICLE_VELOCITY_X`  | `float` → `int32`  | `MONORAIL_VELOCITY_MM_S` Bridge Bus | 32-Bit Signed |
| **0x18 – 0x1B** | `CURVATURE_RADIUS`     | `float` → `int32`  | `MONORAIL_CURVATURE_RADIUS` Bridge Bus | 32-Bit Signed |
| **0x1C – 0x1F** | `CHASSIS_ROLL_LEAN`   | `float` → `int32`  | `MONORAIL_LEAN_ANGLE_RAD` (Scaled 10⁶) | 32-Bit Signed |
| **0x20 – 0x23** | `PACKET_FOOTER_CRC`   | `uint32` | Cyclical Redundancy Check Hardware Interlock| 32-Bit Unsigned |

---

### 3. C++ Reference Serialization Struct (UE5 Source Implementation)

The following structure can be pasted into your custom Unreal Engine 5 C++ movement plugin component folder to manage the byte serialization step natively before piping data streams out over the serial or TCP socket layer:

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Serialization/Archive.h"
#include "ue5_serialization_specs.h"

// Enforce strict 1-byte structural compilation alignment packing
#pragma pack(push, 1)
struct FUnivacTelemetryFrame
{
    uint32 MagicHeader;          // Fixed value: 0x554E4956 (UNIV)
    uint32 LowerTimestamp;       // Unix epoch lower 32-bits milliseconds
    int32  TargetX_mm;           // Converted Target X Coordinate
    int32  TargetY_mm;           // Converted Target Y Coordinate
    int32  TargetZ_mm;           // Converted Target Z Coordinate (Elevation/Depth)
    int32  Velocity_mm_s;        // Converted Longitudinal Speed Vector
    int32  CurveRadius_mm;       // Converted Local Turn Radius Index
    int32  ChassisRoll_mrad;     // Converted Chassis Cant/Lean (Scale: Rad * 1000000)
    uint32 ChecksumCRC;          // Hardware-validated boundary error bitmask

    /**
     * Serializes structural elements to Big Endian wire format byte alignments.
     */
    void SerializeToWire(TArray<uint8>& OutBinaryBuffer)
    {
        OutBinaryBuffer.Empty(sizeof(FUnivacTelemetryFrame));
        OutBinaryBuffer.AddUninitialized(sizeof(FUnivacTelemetryFrame));

        uint8* FramePointer = OutBinaryBuffer.GetData();

        // Convert data fields natively to Network Byte Order using standard bit-shifts
        *(uint32*)(FramePointer + 0)  = FGenericPlatformProperties::ByteSwap(MagicHeader);
        *(uint32*)(FramePointer + 4)  = FGenericPlatformProperties::ByteSwap(LowerTimestamp);
        *(int32*)(FramePointer + 8)   = FGenericPlatformProperties::ByteSwap(TargetX_mm);
        *(int32*)(FramePointer + 12)  = FGenericPlatformProperties::ByteSwap(TargetY_mm);
        *(int32*)(FramePointer + 16)  = FGenericPlatformProperties::ByteSwap(TargetZ_mm);
        *(int32*)(FramePointer + 20)  = FGenericPlatformProperties::ByteSwap(Velocity_mm_s);
        *(int32*)(FramePointer + 24)  = FGenericPlatformProperties::ByteSwap(CurveRadius_mm);
        *(int32*)(FramePointer + 28)  = FGenericPlatformProperties::ByteSwap(ChassisRoll_mrad);
        *(uint32*)(FramePointer + 32) = FGenericPlatformProperties::ByteSwap(ChecksumCRC);
    }
};
#pragma pack(pop)
```

---

### 4. Hardware Interlock Fault Handshake Overrides

If your physical hardware layer (`src/hardware/rt_poly_array_clipper.vhd`) reports a line-clamp flag boundary trip (`BOUNDARY_CLAMPED = '1'`), the Univac Operating Fabric sends an immediate reverse-injection frame byte back to the virtual scene layer over the control line:

*   **Override Command Byte Payload:** `0x00000000` broadcast continuously across all data arrays.
*   **Unreal Engine Action Behavior:** The virtual actor pawn instantly overrides its current vehicle movement stack, triggers a `HARD_BRAKE_STOP` sequence in the physical vehicle simulation component viewport, and shifts the control interface dashboard visibility parameter to a bright warning red color map index.
