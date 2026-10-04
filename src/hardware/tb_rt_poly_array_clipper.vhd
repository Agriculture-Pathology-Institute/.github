-- File Path: src/hardware/tb_rt_poly_array_clipper.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_rt_poly_array_clipper is
-- Testbenches do not contain external port maps
end tb_rt_poly_array_clipper;

architecture SimulationTest of tb_rt_poly_array_clipper is

    -- 1. Component Declaration of the Device Under Test (DUT)
    component rt_poly_array_clipper is
        Generic (
            MAX_VERTICES : integer := 8
        );
        Port (
            CLK_INDUSTRIAL   : in  STD_LOGIC;
            SYSTEM_RESET     : in  STD_LOGIC;
            LOAD_VERTEX_EN   : in  STD_LOGIC;
            VERTEX_INDEX_IN  : in  integer range 0 to MAX_VERTICES-1;
            VERTEX_X_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
            VERTEX_Y_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
            TARGET_X_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
            TARGET_Y_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
            PATH_VALID_IN    : in  STD_LOGIC;
            ENFORCED_X_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
            ENFORCED_Y_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
            LINE_CLAMP_ACTIVE: out STD_LOGIC;
            HEX_SAFETY_OUT   : out STD_LOGIC_VECTOR(3 downto 0)
        );
    end component;

    -- 2. Internal Simulation Signals & Registers
    constant MAX_V : integer := 8;
    signal clk_10mhz       : STD_LOGIC := '0';
    signal sys_reset       : STD_LOGIC := '1';
    signal load_vtx_en     : STD_LOGIC := '0';
    signal vtx_idx         : integer range 0 to MAX_V-1 := 0;
    signal vtx_x           : STD_LOGIC_VECTOR(31 downto 0) := (others => '0');
    signal vtx_y           : STD_LOGIC_VECTOR(31 downto 0) := (others => '0');
    signal target_x        : STD_LOGIC_VECTOR(31 downto 0) := (others => '0');
    signal target_y        : STD_LOGIC_VECTOR(31 downto 0) := (others => '0');
    signal path_valid      : STD_LOGIC := '0';
    
    -- DUT Monitored Outputs
    signal enforced_x      : STD_LOGIC_VECTOR(31 downto 0);
    signal enforced_y      : STD_LOGIC_VECTOR(31 downto 0);
    signal line_clamp      : STD_LOGIC;
    signal hex_safety      : STD_LOGIC_VECTOR(3 downto 0);

    -- 10.0 MHz Industrial Clock Generation (100 ns period setup)
    constant CLK_PERIOD : time := 100 ns;

begin

    -- 3. Instantiate the Device Under Test (DUT)
    DUT: rt_poly_array_clipper
        generic map (
            MAX_VERTICES => MAX_V
        )
        port map (
            CLK_INDUSTRIAL    => clk_10mhz,
            SYSTEM_RESET      => sys_reset,
            LOAD_VERTEX_EN    => load_vtx_en,
            VERTEX_INDEX_IN   => vtx_idx,
            VERTEX_X_IN       => vtx_x,
            VERTEX_Y_IN       => vtx_y,
            TARGET_X_IN       => target_x,
            TARGET_Y_IN       => target_y,
            PATH_VALID_IN     => path_valid,
            ENFORCED_X_OUT    => enforced_x,
            ENFORCED_Y_OUT    => enforced_y,
            LINE_CLAMP_ACTIVE => line_clamp,
            HEX_SAFETY_OUT    => hex_safety
        );

    -- Clock Stimulus Driver
    clk_process : process
    begin
        clk_10mhz <= '0';
        wait for CLK_PERIOD / 2;
        clk_10mhz <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    -- 4. Functional Stimulus Test Matrix Pipeline
    stim_process : process
    begin
        -- Hold initialization reset state for two full clock frames
        sys_reset <= '1';
        load_vtx_en <= '0';
        path_valid <= '0';
        wait for CLK_PERIOD * 2;
        sys_reset <= '0';
        wait for CLK_PERIOD;

        ---------------------------------------------------------------------
        -- PHASE 1: LOAD MOCK POLYHEDRAL RIVERBANK BOUNDARY MATRIX
        -- Defines a non-linear geometric plot context in millimeters (mm)
        ---------------------------------------------------------------------
        -- Vertex 0 Base Anchor Point (100,000, 100,000)
        load_vtx_en <= '1'; vtx_idx <= 0;
        vtx_x <= std_logic_vector(to_signed(100000, 32));
        vtx_y <= std_logic_vector(to_signed(100000, 32)); wait for CLK_PERIOD;
        
        -- Vertex 1 Riverbank Sloped Step Edge (500,000, 120,000)
        vtx_idx <= 1;
        vtx_x <= std_logic_vector(to_signed(500000, 32));
        vtx_y <= std_logic_vector(to_signed(120000, 32)); wait for CLK_PERIOD;
        
        -- Vertex 2 Top Perimeter Limit (480,000, 500,000)
        vtx_idx <= 2;
        vtx_x <= std_logic_vector(to_signed(480000, 32));
        vtx_y <= std_logic_vector(to_signed(500000, 32)); wait for CLK_PERIOD;
        
        -- Vertex 3 Left Boundary Return Fence (120,000, 450,000)
        vtx_idx <= 3;
        vtx_x <= std_logic_vector(to_signed(120000, 32));
        vtx_y <= std_logic_vector(to_signed(450000, 32)); wait for CLK_PERIOD;
        
        -- Clear initialization strobe states
        load_vtx_en <= '0';
        wait for CLK_PERIOD * 2;

        ---------------------------------------------------------------------
        -- PHASE 2: RUN WAYPOINT VERIFICATION STREAMS
        ---------------------------------------------------------------------
        
        -- Test Case A: Fully Safe Waypoint Input Vector (Deep Inside Farm Shape)
        path_valid <= '1';
        target_x <= std_logic_vector(to_signed(200000, 32));
        target_y <= std_logic_vector(to_signed(200000, 32));
        wait for CLK_PERIOD * 2;
        -- Expected Response: line_clamp = '0', hex_safety = 0xF (1111), output tracking original values

        -- Test Case B: Boundary-Proximity Cut Verification (Right near riverbank segment)
        target_x <= std_logic_vector(to_signed(400000, 32));
        target_y <= std_logic_vector(to_signed(115000, 32));
        wait for CLK_PERIOD * 2;
        -- Expected Response: Still inside polygon. Output matches input targets.

        -- Test Case C: Critical Property Breach Violation (Tractor crosses neighbor boundary)
        -- Attempting to target waypoints past the non-linear left return fence line
        target_x <= std_logic_vector(to_signed(80000, 32));
        target_y <= std_logic_vector(to_signed(300000, 32));
        wait for CLK_PERIOD * 2;
        -- Expected Intercept: line_clamp = '1', hex_safety = 0x0 (0000), coordinates truncated to base point (100,000, 100,000)

        -- Test Case D: Recovering Vehicle to Valid Path Matrix Channel
        target_x <= std_logic_vector(to_signed(300000, 32));
        target_y <= std_logic_vector(to_signed(300000, 32));
        wait for CLK_PERIOD * 2;
        -- Expected Recovery: line_clamp automatically clears back to '0', hex restores to 0xF

        -- Disengage stimulation bus lines and complete testbed run
        path_valid <= '0';
        wait;
    end process;

end SimulationTest;
