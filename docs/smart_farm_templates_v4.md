# Master Engineering Template Suite: Multi-Protocol Smart Farm Architecture
**Consortium Working Document**
*Location: UW Medicine Ballard Office, Seattle, WA*
*Cooperating Entities: UW, EWU, SPU, CWU, Baylor, K-State, UK, UMinn, UMich, LSU, Caltech, Trufant, Fox Rothschild LLP*

---

## 1. Multi-Protocol Unified Communication Topology

To reconcile the dual-bus requirement between Fox Rothschild's infrastructure layout and the academic field machinery, the system integrates a dual-bus gateway topology.

```
                                 +---------------------------------------+
                                 |  Unreal Engine 5 Control Environment  |
                                 +-------------------+-------------------+
                                                     |
                                                     v (Telemetry / UART)
                                 +-------------------+-------------------+
                                 | Custom Electronic Control Board (VHDL)|
                                 +-------------------+-------------------+
                                                     |
                                                     v (System Data Bus)
                                 +-------------------+-------------------+
                                 |   Dual-Protocol Smart Farm Gateway   |
                                 +---------+-------------------+---------+
                                           |                   |
                                           v                   v
                        +------------------+----+    +---------+-------------------+
                        | Modbus RTU / RS-485   |    | ISOBUS / SAE J1939 CAN Bus  |
                        | (Fox Rothschild Spec) |    | (UW & University Spec)      |
                        +------------------+----+    +---------+-------------------+
                                           |                   |
                     +---------------------+-----+             +----------+----------+
                     | - GE Wind Turbines        |                        |          |
                     | - LED Greenhouses         |                        v          v
                     | - Subsurface Drainage Sys |              +---------+-----+  +-+---------------+
                     +---------------------------+              | Rheinmetall   |  | Electric CAT & |
                                                                | Kodiak AEV    |  | John Deere Fleet|
                                                                +---------------+  +-----------------+
```

---

## 2. Low-Voltage Electrical & Protocol Mapping Matrix

| Subsystem Component | Physical Layer / Bus | Protocol Layer | Nominal Voltage | Target VHDL I/O Pin Group |
| :--- | :--- | :--- | :--- | :--- |
| **GE Wind Turbine** | RS-485 Balanced Pair | Modbus RTU | 24V DC Signalling | `EXT_MODBUS_TX/RX_P0` |
| **LED Greenhouse Controller**| RS-485 Multi-drop | Modbus RTU | 24V DC Control Bus| `EXT_MODBUS_TX/RX_P1` |
| **Subsurface Drainage Nodes**| RS-485 Low-Power | Modbus RTU | 12V DC Sensor Power| `EXT_MODBUS_TX/RX_P2` |
| **Rheinmetall Kodiak AEV** | ISO 11783 / CAN 2.0B | SAE J1939 ISOBUS| 12V DC Differential| `MCU_CAN_H/L_P0` |
| **Electric CAT Equipment** | ISO 11783 / CAN 2.0B | SAE J1939 ISOBUS| 12V DC Differential| `MCU_CAN_H/L_P1` |
| **John Deere Implements** | ISO 11783 / CAN 2.0B | SAE J1939 ISOBUS| 12V DC Differential| `MCU_CAN_H/L_P2` |

---

## 3. Custom Board Signal Conditioning Circuit Diagram

```
                [RS-485 / Modbus Side]                                [ISOBUS / J1939 CAN Side]
         
         Data A (+)  o-------------------+                      CAN High o-------------------+
                                         |                                                    |
                                     [TVS Diode]                                          [TVS Diode]
                                         |                                                    |
         Data B (-)  o----+--------------+                      CAN Low  o----+--------------+
                          |              |                                    |              |
                       [120R]            |                                 [120R]            |
                          |              |                                    |              |
                         === GND        === GND                              === GND        === GND
                          |              |                                    |              |
                    +-----+--------------+-----+                        +-----+--------------+-----+
                    | MAX485 Transceiver       |                        | TJA1050 CAN Transceiver  |
                    |                          |                        |                          |
                    | RO   DI   DE   RE        |                        | RXD       TXD            |
                    +--+----+----+----+--------+                        +----+-------+-------------+
                       |    |    |    |                                      |       |
                       v    v    v    v                                      v       v
                    [Optocoupler Isolation]                               [Optocoupler Isolation]
                       |    |    |    |                                      |       |
                       +----+----+----+----------> [To FPGA/VHDL] <----------+-------+
```

---

## 4. VHDL Top-Level Architecture (`farm_controller.vhd`)

```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity farm_controller is
    Port (
        clk             : in  STD_LOGIC;
        reset           : in  STD_LOGIC;
        -- Modbus/RS-485 Physical Pins (Fox Rothschild Infrastructure)
        modbus_rx       : in  STD_LOGIC;
        modbus_tx       : out STD_LOGIC;
        modbus_re_de    : out STD_LOGIC;
        -- ISOBUS/J1939 CAN Physical Pins (University Machinery Fleet)
        can_rx          : in  STD_LOGIC;
        can_tx          : out STD_LOGIC;
        -- Unreal Engine Telemetry UART Interconnect
        ue_uart_rx      : in  STD_LOGIC;
        ue_uart_tx      : out STD_LOGIC
    );
end farm_controller;

architecture Behavioral of farm_controller is
    signal internal_modbus_data : std_logic_vector(7 downto 0);
    signal internal_can_frame    : std_logic_vector(63 downto 0);
    signal ue_command_bus       : std_logic_vector(31 downto 0);
begin
    process(clk, reset)
    begin
        if reset = '1' then
            modbus_tx <= '1';
            can_tx    <= '1';
        elsif rising_edge(clk) then
            -- Internal FPGA Routing Protocol Engine
        end if;
    end process;
end Behavioral;
```

---

## 5. Production Smart Farm Layout Schema (JSON)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ConsortiumSmartFarmConfiguration",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "office_location": { "type": "string" },
        "coordinate_system": { "type": "string" }
      }
    },
    "infrastructure_modbus_rs485": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "node_id": { "type": "integer" },
          "node_type": { "type": "string" },
          "modbus_register_start": { "type": "string" },
          "spatial_center_scad": { "type": "array", "items": { "type": "number" } }
        }
      }
    },
    "machinery_isobus_j1939": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "ecu_address": { "type": "string" },
          "equipment_brand": { "type": "string" },
          "can_pgn_mapping": { "type": "integer" }
        }
      }
    }
  }
}
```
