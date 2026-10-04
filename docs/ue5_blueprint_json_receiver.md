# UE5 Blueprint Asynchronous JSON Telemetry Receiver Framework
## Cross-Server TCP Socket & Viewport HUD Link Specifications
**Document Class:** System Integration Blueprint Manual  
**Core Infrastructure Target:** Unreal Engine 5.4 / 5.5 Visual Telemetry Room  

---

### 1. Conceptual Blueprint Data Flow Architecture

To maintain high, non-blocking frame rates inside your virtual control landscape, all socket tasks bypass the main Game Thread using an asynchronous event-driven layout. The graph loop below defines how the virtual workspace cameras and tractor actors handle message handshakes with your servers:

[ UE5 Viewport Actor Tick ] ──> Gathers XYZ Transform & Wind Metrics Object


│


▼


[ Async TCP Client Component ] ──> Converts data to string ──> Sends to Port 8080 (JSON Bridge)

│

▼

[ Viewport HUD / Red Alert UI ] <── Fires custom UI Event  <── Recovers return JSON string status


---

### 2. High-Level Blueprint Node Structure & Logic Steps

To build this architecture inside the Unreal Engine Blueprint editor without writing low-level C++, your teams should implement the following node execution loops using standard engine networking and JSON plugins (such as the native *WebX / Json Blueprint Utilities*):

#### A. Outbound Telemetry Dispatch Loop (Tractor Character Blueprint)
1. **Event Tick / Timer Event:** Fires every 100 milliseconds to drive uniform sampling frames.
2. **Get Actor Location:** Pulls the active vector position of your tractor pawn or camera rig.
3. **Break Vector:** Separates the coordinate components into distinct floating-point `X`, `Y`, and `Z` variables.
4. **Construct JSON Object:**
   * Append Array Field named `ue5_position_cm` containing the `X`, `Y`, and `Z` centimeter values.
   * Append Number Field named `wind_speed_kts` hooked to your environmental actor parameters.
   * Append Number Field named `volume_cut_m3` from your actual field displacement calculus metrics.
   * Append String Field named `request_hex_state` defaulting to `"0xC"` or `"0xF"`.
5. **Stringify JSON:** Converts the structured object container into a single unpadded network string payload.
6. **Send Socket Data:** Pumps the generated string string across your established TCP connection array.

#### B. Inbound Override Listener Loop (Asynchronous Network Event)
1. **On Data Received Event:** Triggers automatically the microsecond a return string payload packet bounces back from the `RtJsonNetworkBridge` server port.
2. **Construct JSON Object from String:** Feeds the raw string array into a string parser node.
3. **Get Field (Boolean):** Extracts the target field flag named `syntax_valid`.
4. **Get Field (String):** Extracts the target field string named `assigned_register`.
5. **Switch on String (Register Verification Routing):**
   * **If Output Matches `"0x0"` (Emergency Isolation Interlock Locked):**
     * **Call Custom Event:** `Trigger_Hard_Brake_Clamps` (Halts the physical autonomous driving simulation path).
     * **Get Player Controller → Get HUD Component:** Fires an animation node to force the main viewport canopy overlay tint to flash a warning **Crimson Red Alert color map matrix**.
   * **If Output Matches `"0xF"` or `"0xC"` (Nominal In-Bounds Execution Zone):**
     * Maintains normal vector calculation tracking paths and displays a **Bright Green Tracking Stable text log** on your terminal screens.

---

### 3. C++ Socket Network Component Blueprint Ingestion Interface

If the university engineering groups gathered at the Ballard tables prefer to pack the engine execution loop into a reusable, high-performance **Blueprint Custom Actor Component**, paste the following implementation file configuration directly into your source folder to expose clean execution pins to the editor viewports:

```cpp
// File Path: Source/Private/RtJsonSocketComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Interfaces/IPv4/IPv4Address.h"
#include "Sockets.h"
#include "Common/TcpSocketBuilder.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "RtJsonSocketComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTelemetryResponseReceived, bool, bSyntaxValid, FString, AssignedRegister);

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class URtJsonSocketComponent : public UActorComponent
{
    GENERATED_BODY()

public:	
    URtJsonSocketComponent();

    // Blueprint Event Node Hook allowing immediate link placement inside character graph scripts
    UPROPERTY(BlueprintAssignment, Category = "UNIVAC IX Telemetry")
    FOnTelemetryResponseReceived OnResponseReceived;

    UFUNCTION(BlueprintCallable, Category = "UNIVAC IX Telemetry")
    bool ConnectToUnivacFabricBridge(FString IPAddress, int32 Port);

    UFUNCTION(BlueprintCallable, Category = "UNIVAC IX Telemetry")
    void StreamJsonFrameAsync(FVector VehiclePosition, float WindKts, float MassCutM3, FString RequestHex);

private:
    FSocket* ClientSocket;
    void AsyncReceiverWorker();
};
```
