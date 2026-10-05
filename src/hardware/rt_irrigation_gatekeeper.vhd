-- File Path: src/hardware/rt_irrigation_gatekeeper.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_irrigation_gatekeeper is
    Port (
        -- High-Speed Timing & Control Rails
        CLK_INDUSTRIAL         : in  STD_LOGIC; -- Synchronized to 10.0 MHz clock line
        SYSTEM_RESET           : in  STD_LOGIC;
        
        -- Inbound 16-State Hexadecimal Command Register from the network bridge
        REQUESTED_HEX_STATE    : in  STD_LOGIC_VECTOR(3 downto 0);
        SIGNAL_STROBE_IN       : in  STD_LOGIC;
        
        -- Physical Hardware Valve Drivers routed to Tractor Hydraulic Manifolds
        DIGGING_VALVE_RELEASE  : out STD_LOGIC; -- Held high to authorize active excavation cutting
        IRRIGATION_SHUTOFF_VALVE: out STD_LOGIC; -- Controls water routing actuators
        
        -- Native 16-State Master Safety Bus Link Indicator
        HEX_SAFETY_OUT         : out STD_LOGIC_VECTOR(3 downto 0)
    );
end rt_irrigation_gatekeeper;

architecture NaturalFlowControl of rt_irrigation_gatekeeper is
    signal current_state : unsigned(3 downto 0);
begin

    process(CLK_INDUSTRIAL, SYSTEM_RESET)
    begin
        if SYSTEM_RESET = '1' then
            DIGGING_VALVE_RELEASE    <= '0'; -- Secure all hydraulic toolheads on boot
            IRRIGATION_SHUTOFF_VALVE <= '1'; -- Default shutoff closed
            HEX_SAFETY_OUT           <= "0000"; -- Safe state zero-x-zero (0x0)
        elsif rising_edge(CLK_INDUSTRIAL) then
            if SIGNAL_STROBE_IN = '1' then
                current_state <= unsigned(REQUESTED_HEX_STATE);
                
                case REQUESTED_HEX_STATE is
                    when "0101" => -- State 0x5: Protected Soft Natural Planting/Water Channel
                        DIGGING_VALVE_RELEASE    <= '0'; -- Hard-lock excavator implements to safeguard topsoil
                        IRRIGATION_SHUTOFF_VALVE <= '0'; -- Open local irrigation gates to guide natural flow
                        HEX_SAFETY_OUT           <= "0101"; -- Transmit operational index 0x5 down-line
                        
                    when "1111" => -- State 0xF: Normal Compacted Grading Matrix
                        DIGGING_VALVE_RELEASE    <= '1'; -- Authorize active land carving and ditch digging
                        IRRIGATION_SHUTOFF_VALVE <= '1'; -- Close irrigation loop diversion gates
                        HEX_SAFETY_OUT           <= "1111"; -- Maximum nominal run capacity
                        
                    when others => -- Severe anomaly or sudden system interlock shutdown command (0x0)
                        DIGGING_VALVE_RELEASE    <= '0';
                        IRRIGATION_SHUTOFF_VALVE <= '1';
                        HEX_SAFETY_OUT           <= "0000"; -- Instantly fall to grounding safety loop
                end case;
            end if;
        end if;
    end process;

end NaturalFlowControl;
