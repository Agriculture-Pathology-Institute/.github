library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_sawtooth_square_generator is
    Generic (
        -- Division targets for stepping down the 1.0 THz master clock to Modbus domains
        -- Steps a single wave cycle across 16 discrete analog amplitude intervals
        CYCLES_PER_STEP : integer := 542  -- Establishes the target sub-megahertz tracking frame
    );
    Port (
        -- High-Speed Resonator Interface
        PTC_CLK_P        : in  STD_LOGIC;
        PTC_CLK_N        : in  STD_LOGIC;
        SYSTEM_RESET     : in  STD_LOGIC;
        
        -- Native 4-Bit Parallel R-2R Analog Control Output
        -- Represents the raw voltage steps (0.0V to 1.0V in 0.0625V increments)
        HYBRID_WAVE_OUT  : out STD_LOGIC_VECTOR(3 downto 0);
        SYNC_SQUARE_TICK : out STD_LOGIC  -- Hard reference strobe on phase collapse
    );
end rt_sawtooth_square_generator;

architecture GeometricRamp of rt_sawtooth_square_generator is
    signal master_thz_clk : STD_LOGIC;
    signal step_counter   : integer range 0 to CYCLES_PER_STEP := 0;
    
    -- Internal 4-bit state machine tracking the wave's phase path
    signal amplitude_reg  : unsigned(3 downto 0) := (others => '0');
    
    type wave_phase_type is (SAW_RAMP, HARD_SQUARE_HIGH, HARD_SQUARE_LOW);
    signal current_phase : wave_phase_type := SAW_RAMP;
    signal phase_timer   : integer range 0 to 15 := 0;
begin
    -- Reconcile incoming differential optical clock lines
    master_thz_clk <= PTC_CLK_P and not PTC_CLK_N;

    process(master_thz_clk, SYSTEM_RESET)
    begin
        if SYSTEM_RESET = '1' then
            step_counter <= 0;
            amplitude_reg <= (others => '0');
            phase_timer <= 0;
            current_phase <= SAW_RAMP;
            SYNC_SQUARE_TICK <= '0';
        elsif rising_edge(master_thz_clk) then
            if step_counter >= CYCLES_PER_STEP - 1 then
                step_counter <= 0;
                
                -- State Machine driving the hybrid wave mechanics
                case current_phase is
                    when SAW_RAMP =>
                        SYNC_SQUARE_TICK <= '0';
                        if amplitude_reg = "1111" then
                            -- Transition instantly into the hard-square plateau phase
                            current_phase <= HARD_SQUARE_HIGH;
                            phase_timer <= 0;
                        else
                            -- Asymmetric incremental ramp step (0.0625V per interval)
                            amplitude_reg <= amplitude_reg + 1;
                        end if;
                        
                    when HARD_SQUARE_HIGH =>
                        if phase_timer = 4 then  -- Enforce an asymmetric plateau window
                            -- Instantly collapse from peak amplitude down to ground
                            amplitude_reg <= "0000";
                            SYNC_SQUARE_TICK <= '1'; -- Strobe the discharge synchronization edge
                            current_phase <= HARD_SQUARE_LOW;
                            phase_timer <= 0;
                        else
                            phase_timer <= phase_timer + 1;
                        end if;
                        
                    when HARD_SQUARE_LOW =>
                        SYNC_SQUARE_TICK <= '0';
                        if phase_timer = 4 then  -- Maintain ground clamp before repeating the ramp
                            current_phase <= SAW_RAMP;
                            phase_timer <= 0;
                        else
                            phase_timer <= phase_timer + 1;
                        end if;
                end case;
            else
                step_counter <= step_counter + 1;
            end if;
        end if;
    end process;

    -- Assign the internal digital representation directly to the R-2R pin ladder out
    HYBRID_WAVE_OUT <= STD_LOGIC_VECTOR(amplitude_reg);

end GeometricRamp;
