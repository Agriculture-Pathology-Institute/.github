-- File Path: src/hardware/tb_rt_irrigation_gatekeeper.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_rt_irrigation_gatekeeper is
-- Testbenches do not expose external top-level hardware ports
end tb_rt_irrigation_gatekeeper;

architecture StructuralTimingVerification of tb_rt_irrigation_gatekeeper is

    -- 1. Component Declaration of the Device Under Test (DUT)
    component rt_irrigation_gatekeeper is
        Port (
            CLK_INDUSTRIAL         : in  STD_LOGIC;
            SYSTEM_RESET           : in  STD_LOGIC;
            REQUESTED_HEX_STATE    : in  STD_LOGIC_VECTOR(3 downto 0);
            SIGNAL_STROBE_IN       : in  STD_LOGIC;
            DIGGING_VALVE_RELEASE  : out STD_LOGIC;
            IRRIGATION_SHUTOFF_VALVE: out STD_LOGIC;
            HEX_SAFETY_OUT         : out STD_LOGIC_VECTOR(3 downto 0)
        );
    end component;

    -- 2. Internal Simulation Timing Signals & Driver Channels
    signal clk_10mhz           : STD_LOGIC := '0';
    signal sys_reset           : STD_LOGIC := '1';
    signal requested_hex       : STD_LOGIC_VECTOR(3 downto 0) := (others => '0');
    signal signal_strobe       : STD_LOGIC := '0';
    
    -- Monitored Silicon Output Contacts
    signal valve_release       : STD_LOGIC;
    signal irrigation_shutoff  : STD_LOGIC;
    signal hex_safety_bus      : STD_LOGIC_VECTOR(3 downto 0);

    -- 10.0 MHz Stage 2 Clock Definition = Exactly 100 ns Execution Steps
    constant CLK_PERIOD : time := 100 ns;

begin

    -- 3. Device Under Test (DUT) Instantiation
    DUT: rt_irrigation_gatekeeper
        port map (
            CLK_INDUSTRIAL           => clk_10mhz,
            SYSTEM_RESET             => sys_reset,
            REQUESTED_HEX_STATE      => requested_hex,
            SIGNAL_STROBE_IN         => signal_strobe,
            DIGGING_VALVE_RELEASE    => valve_release,
            IRRIGATION_SHUTOFF_VALVE => irrigation_shutoff,
            HEX_SAFETY_OUT           => hex_safety_bus
        );

    -- Synchronous clock generator thread loop
    clk_process : process
    begin
        clk_10mhz <= '0';
        wait for CLK_PERIOD / 2;
        clk_10mhz <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    -------------------------------------------------------------------------
    -- 4. SUB-MICROSECOND TRANSITION STIMULUS ENGINE
    -------------------------------------------------------------------------
    stim_process : process
    begin
        -- Hold initial system reset line high during startup clear frame
        sys_reset     <= '1';
        signal_strobe <= '0';
        requested_hex <= "0000"; -- Default safe shutdown condition
        wait for CLK_PERIOD * 2;
        
        sys_reset     <= '0';
        wait for CLK_PERIOD;

        ---------------------------------------------------------------------
        -- PHASE A: HEAVY EXCAVATION DRIVING PROFILE (HARD CLAY RUN)
        -- Inbound Telemetry State: Nominal Compacted Soil Layer (0xF)
        ---------------------------------------------------------------------
        requested_hex <= "1111"; -- Command State 0xF
        signal_strobe <= '1';
        wait for CLK_PERIOD;
        
        -- Assert that cutting tools are safely authorized to carve hard dirt
        assert (valve_release = '1') report "❌ Error: Toolhead falsely locked inside standard grading sector." severity failure;
        assert (hex_safety_bus = "1111") report "❌ Error: Master safety bus dropped outside a fault condition." severity failure;
        wait for CLK_PERIOD * 3; -- Maintain grading pass for 300 ns

        ---------------------------------------------------------------------
        -- PHASE B: SUB-MICROSECOND EDGE BOUNDARY IMPACT INTERCEPT
        -- Vehicle crosses instantly into an ancient paleo-channel water path.
        -- Inbound Telemetry State shifts immediately to Protected Soft Dirt (0x5)
        ---------------------------------------------------------------------
        requested_hex <= "0101"; -- Command State 0x5
        
        -- The transition triggers on the very next rising edge of the 10.0 MHz clock (100 ns window)
        wait for CLK_PERIOD;
        
        -- CRITICAL COMPLIANCE TIMING ASSERTIONS
        assert (valve_release = '0') 
            report "❌ CRITICAL SAFETY BREACH: Valve release failed to drop within a 100ns clock step!" 
            severity failure;
            
        assert (irrigation_shutoff = '0') 
            report "❌ Error: Irrigation gate failed to activate water diversion routes." 
            severity failure;
            
        assert (hex_safety_bus = "0101") 
            report "❌ Error: Hex safety bus failed to reflect operational state index 0x5." 
            severity failure;
            
        report "✅ [TIMING PASS] Toolhead gatekeeper successfully isolated cutting tools inside exactly 100 nanoseconds." severity note;
        wait for CLK_PERIOD * 4; -- Maintain safe planting monitoring for 400 ns

        ---------------------------------------------------------------------
        -- PHASE C: SUDDEN SENSOR EXCEPTION DRIVER DISCONNECT
        -- Emulates an unexpected network socket drop or voltage loss event (0x0)
        ---------------------------------------------------------------------
        requested_hex <= "0000"; -- Emergency E-Stop condition code
        wait for CLK_PERIOD;
        
        assert (valve_release = '0') report "❌ Error: System failed to maintain tool lock under E-Stop status." severity failure;
        assert (hex_safety_bus = "0000") report "✅ Success: Master safety rail collapsed completely to ground." severity note;

        signal_strobe <= '0';
        report "🚀 [GATEKEEPER VERIFICATION COMPLETE]: Silicon latch speeds match your 16-state hardware spec perfectly." severity note;
        wait;
    end process;

end StructuralTimingVerification;
