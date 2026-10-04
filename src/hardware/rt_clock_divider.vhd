library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_clock_divider is
    Generic (
        -- Assumes a 1.0 THz Photonic Time Crystal Core Master Clock Input
        -- Targets a Standard Modbus RTU / RS-485 Baud Rate of 115,200 bps
        -- Division Factor: 1,000,000,000,000 / 115,200 = 8,680,555.56 (Rounded to 8680556)
        DIVISOR_STAGE_1 : integer := 1000;  -- 1.0 THz to 1.0 GHz Peripheral Domain
        DIVISOR_STAGE_2 : integer := 100;   -- 1.0 GHz to 10.0 MHz Industrial Automation Engine
        DIVISOR_STAGE_3 : integer := 87     -- 10.0 MHz to ~114,942 bps (0.22% Target Error Window)
    );
    Port (
        -- Ultra High-Speed Differential Optical Clock Interface
        PTC_CLK_P        : in  STD_LOGIC;
        PTC_CLK_N        : in  STD_LOGIC;
        SYSTEM_RESET     : in  STD_LOGIC;
        
        -- Synchronized Domain Output Clocks
        CLK_PERIPHERAL_GHZ : out STD_LOGIC; -- 1.0 GHz Clock for High-Speed Tensor Data
        CLK_INDUSTRIAL_MHZ : out STD_LOGIC; -- 10.0 MHz Clock for ISOBUS / J1939 CAN Pipelines
        TICK_MODBUS_BAUD   : out STD_LOGIC  -- 115,200 Hz Sampling Pulse for Modbus RS-485
    );
end rt_clock_divider;

architecture PipelinedArchitecture of rt_clock_divider is
    -- Internal Clock Domain Nodes
    signal master_thz_clk   : STD_LOGIC;
    signal internal_ghz_clk : STD_LOGIC := '0';
    signal internal_mhz_clk : STD_LOGIC := '0';
    signal internal_baud_tick: STD_LOGIC := '0';

    -- Pipelined Step-Down Counter Registers
    signal counter_stage_1 : integer range 0 to DIVISOR_STAGE_1 := 0;
    signal counter_stage_2 : integer range 0 to DIVISOR_STAGE_2 := 0;
    signal counter_stage_3 : integer range 0 to DIVISOR_STAGE_3 := 0;
begin
    -- Reconcile physical high-speed differential inputs from the optical die
    master_thz_clk <= PTC_CLK_P and not PTC_CLK_N;

    -------------------------------------------------------------------------
    -- STAGE 1: THz Core to GHz Peripheral Domain (1,000 GHz down to 1.0 GHz)
    -------------------------------------------------------------------------
    process(master_thz_clk, SYSTEM_RESET)
    begin
        if SYSTEM_RESET = '1' then
            counter_stage_1 <= 0;
            internal_ghz_clk <= '0';
        elsif rising_edge(master_thz_clk) then
            if counter_stage_1 >= (DIVISOR_STAGE_1 / 2) - 1 then
                internal_ghz_clk <= not internal_ghz_clk;
                counter_stage_1 <= 0;
            else
                counter_stage_1 <= counter_stage_1 + 1;
            end if;
        end if;
    end process;
    CLK_PERIPHERAL_GHZ <= internal_ghz_clk;

    -------------------------------------------------------------------------
    -- STAGE 2: GHz Domain to MHz Industrial Domain (1.0 GHz down to 10.0 MHz)
    -------------------------------------------------------------------------
    process(internal_ghz_clk, SYSTEM_RESET)
    begin
        if SYSTEM_RESET = '1' then
            counter_stage_2 <= 0;
            internal_mhz_clk <= '0';
        elsif rising_edge(internal_ghz_clk) then
            if counter_stage_2 >= (DIVISOR_STAGE_2 / 2) - 1 then
                internal_mhz_clk <= not internal_mhz_clk;
                counter_stage_2 <= 0;
            else
                counter_stage_2 <= counter_stage_2 + 1;
            end if;
        end if;
    end process;
    CLK_INDUSTRIAL_MHZ <= internal_mhz_clk;

    -------------------------------------------------------------------------
    -- STAGE 3: MHz Domain to Modbus Serial Baud Rate Tick (10.0 MHz to 115.2 kHz)
    -------------------------------------------------------------------------
    process(internal_mhz_clk, SYSTEM_RESET)
    begin
        if SYSTEM_RESET = '1' then
            counter_stage_3 <= 0;
            internal_baud_tick <= '0';
        elsif rising_edge(internal_mhz_clk) then
            if counter_stage_3 >= (DIVISOR_STAGE_3 - 1) then
                internal_baud_tick <= '1'; -- Generates a crisp single-cycle enable tick
                counter_stage_3 <= 0;
            else
                internal_baud_tick <= '0';
                counter_stage_3 <= counter_stage_3 + 1;
            end if;
        end if;
    end process;
    TICK_MODBUS_BAUD <= internal_baud_tick;

end PipelinedArchitecture;
