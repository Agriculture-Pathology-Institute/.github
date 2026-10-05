-- File Path: src/hardware/rt_anemometer_digitizer.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_anemometer_digitizer is
    Port (
        -- High-Speed Timing and Control Lines
        CLK_INDUSTRIAL         : in  STD_LOGIC; -- Synchronized to 10.0 MHz Industrial Divider
        SYSTEM_RESET           : in  STD_LOGIC;
        
        -- Physical Anemometer Pulse Line (1 pulse per cup rotation)
        ANEMOMETER_PULSE_IN    : in  STD_LOGIC;
        
        -- High-Speed Digitized Telemetry Outputs
        WIND_VELOCITY_KTS_OUT  : out STD_LOGIC_VECTOR(15 downto 0); -- Scaled fixed-point (x100)
        GALE_FORCE_TRIP_OUT    : out STD_LOGIC; -- Spikes high if velocity > 45 Knots [1.1]
        
        -- Master 16-State Hexadecimal Bus State Register
        HEX_SAFETY_OUT         : out STD_LOGIC_VECTOR(3 downto 0)
    );
end rt_anemometer_digitizer;

architecture PulsePeriodCalculus of rt_anemometer_digitizer is
    signal cycle_counter   : unsigned(31 downto 0) := (others => '0');
    signal latched_period  : unsigned(31 downto 0) := (others => '0');
    signal last_pulse_state: STD_LOGIC := '0';
    
    constant GALE_THRESHOLD_10MHZ_LIMIT : unsigned(31 downto 0) := to_unsigned(114300, 32); -- Corresponds to 45 Knots
begin

    process(CLK_INDUSTRIAL, SYSTEM_RESET)
        variable calculated_knots : unsigned(31 downto 0);
    begin
        if SYSTEM_RESET = '1' then
            cycle_counter        <= (others => '0');
            latched_period       <= (others => '0');
            last_pulse_state     <= '0';
            WIND_VELOCITY_KTS_OUT <= (others => '0');
            GALE_FORCE_TRIP_OUT   <= '1'; -- Lock out tools on reset safety default
            HEX_SAFETY_OUT       <= "0000";
        elsif rising_edge(CLK_INDUSTRIAL) then
            last_pulse_state <= ANEMOMETER_PULSE_IN;
            
            -- Detect rising edge of sensor physical signal pulse line
            if ANEMOMETER_PULSE_IN = '1' and last_pulse_state = '0' then
                latched_period <= cycle_counter;
                cycle_counter  <= (others => '0');
                
                -- Dynamic conversion algorithm: Knots = 5,144,440 / latched_period
                if cycle_counter /= 0 then
                    calculated_knots := to_unsigned(5144440, 32) / cycle_counter;
                    WIND_VELOCITY_KTS_OUT <= std_logic_vector(calculated_knots(15 downto 0));
                    
                    -- Evaluate critical wind speed limits [1.1]
                    if cycle_counter <= GALE_THRESHOLD_10MHZ_LIMIT then
                        GALE_FORCE_TRIP_OUT <= '1';
                        HEX_SAFETY_OUT      <= "0000"; -- Force emergency ground mode shutdown (0x0) [1.1, 1.20]
                    else
                        GALE_FORCE_TRIP_OUT <= '0';
                        HEX_SAFETY_OUT      <= "1011"; -- Engages state 0xB (Wind Harvesting Active)
                    end if;
                end if;
            else
                -- Increment timing tick counter registers (1 tick = 100ns)
                if cycle_counter < x"FFFFFFFF" then
                    cycle_counter <= cycle_counter + 1;
                end if;
            end if;
        end if;
    end process;

end PulsePeriodCalculus;
