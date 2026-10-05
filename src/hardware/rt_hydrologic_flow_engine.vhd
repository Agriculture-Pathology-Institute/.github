-- File Path: src/hardware/rt_hydrologic_flow_engine.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_hydrologic_flow_engine is
    Port (
        -- High-Speed Timing & Control Interfaces
        CLK_INDUSTRIAL         : in  STD_LOGIC; -- Synchronized to 10.0 MHz clock line
        SYSTEM_RESET           : in  STD_LOGIC;
        
        -- Digitized Soil Moisture & Infiltration Potentials (12-bit Precision)
        RAW_MOISTURE_ADC_IN    : in  STD_LOGIC_VECTOR(11 downto 0);
        SIGNAL_STROBE_IN       : in  STD_LOGIC;
        
        -- Real-Time Hydrologic Output Despatches
        SATURATION_INDEX_HEX   : out STD_LOGIC_VECTOR(3 downto 0); -- 16-State Hex Scale
        FLASH_FLOOD_WARN       : out STD_LOGIC; -- Spikes high if surface pooling is imminent
        POOLING_INTERLOCK_OUT  : out STD_LOGIC; -- Master clamp command
        
        -- Native 16-State Master Safety Bus Link
        HEX_SAFETY_OUT         : out STD_LOGIC_VECTOR(3 downto 0)
    );
end rt_hydrologic_flow_engine;

architecture VolumetricHydrology of rt_hydrologic_flow_engine is
    signal adc_signed : signed(11 downto 0);
    signal saturated  : STD_LOGIC := '0';
begin
    adc_signed <= signed(RAW_MOISTURE_ADC_IN);

    process(CLK_INDUSTRIAL, SYSTEM_RESET)
        variable absolute_moisture : signed(11 downto 0);
    begin
        if SYSTEM_RESET = '1' then
            SATURATION_INDEX_HEX  <= "0000";
            FLASH_FLOOD_WARN      <= '0';
            POOLING_INTERLOCK_OUT <= '1'; -- Default to safe isolated state on reset
            HEX_SAFETY_OUT        <= "0000"; 
            saturated             <= '1';
        elsif rising_edge(CLK_INDUSTRIAL) then
            if SIGNAL_STROBE_IN = '1' then
                absolute_moisture := abs(adc_signed);
                
                -------------------------------------------------------------
                -- CRITICAL HYDROLOGIC THRESHOLD EVALUATION
                -- High ADC voltage fields map directly to complete pore saturation
                -------------------------------------------------------------
                if absolute_moisture >= to_signed(3800, 12) then
                    -- 100% Soil Saturation: Immediate Surface Pooling / Flash Flooding
                    SATURATION_INDEX_HEX  <= "1111"; -- Maximum Saturation State (0xF)
                    FLASH_FLOOD_WARN      <= '1';
                    POOLING_INTERLOCK_OUT <= '1';
                    saturated             <= '1';
                elif absolute_moisture >= to_signed(2500, 12) then
                    -- High Saturation: Advanced Runoff Phase
                    SATURATION_INDEX_HEX  <= "1010"; -- State 0xA
                    FLASH_FLOOD_WARN      <= '0';
                    POOLING_INTERLOCK_OUT <= '0';
                    saturated             <= '0';
                elif absolute_moisture <= to_signed(500, 12) then
                    -- Arid / High Absorption Capacity Available
                    SATURATION_INDEX_HEX  <= "0001"; -- State 0x1
                    FLASH_FLOOD_WARN      <= '0';
                    POOLING_INTERLOCK_OUT <= '0';
                    saturated             <= '0';
                else
                    -- Nominal Moisture Balance
                    SATURATION_INDEX_HEX  <= "0111"; -- State 0x7
                    FLASH_FLOOD_WARN      <= '0';
                    POOLING_INTERLOCK_OUT <= '0';
                    saturated             <= '0';
                end if;

                -------------------------------------------------------------
                -- HARDWARE INTERLOCK GENERATION
                -------------------------------------------------------------
                if saturated = '1' then
                    HEX_SAFETY_OUT <= "0000"; -- Collapse bus state to emergency E-Stop (0x0)
                else
                    HEX_SAFETY_OUT <= "1111"; -- Maintain normal operation run capacity (0xF)
                end if;
                
            end if;
        end if;
    end process;
end VolumetricHydrology;
