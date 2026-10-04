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
    
    -- Monitored DUT Outputs
    signal enforced_x      : STD_LOGIC_VECTOR(31 downto 0);
    signal enforced_y      : STD_LOGIC_VECTOR(31 downto 0);
    signal line_clamp      : STD_LOGIC;
    signal hex_safety      : STD_LOGIC_VECTOR(3 downto 0);

    -- 10.0 MHz Industrial Clock Generation (100 ns period setup)
    constant CLK_PERIOD : time := 100 ns;

    -- Simulation Tracking Vectors for Crosswind Displacements
    -- Tracks absolute position in millimeters (mm)
    signal ideal_path_x    : integer := 200000;
    signal ideal_path_y    : integer := 200000;
    signal wind_drift_y    : integer := 0;
    signal combined_y      : integer := 200000;

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

    -- Clock Stimulus Driver Process
    clk_process : process
    begin
        clk_10mhz <= '0';
        wait for CLK_PERIOD / 2;
        clk_10mhz <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    -- Update dynamic coordinate mapping node parameters instantly
    combined_y <= ideal_path_y + wind_drift_y;
    target_x   <= std_logic_vector(to_signed(ideal_path_x, 32));
    target_y   <= std_logic_vector(to_signed(combined_y, 32));

    -- 4. Environmental Stress Test & Recovery Stimulus Pipeline
    stim_process : process
    begin
        -- Hold initialization master reset state during boot sequence
        sys_reset   <= '1';
        load_vtx_en <= '0';
        path_valid  <= '0';
        wind_drift_y <= 0;
        wait for CLK_PERIOD * 2;
        sys_reset   <= '0';
        wait for CLK_PERIOD;

        ---------------------------------------------------------------------
        -- PHASE 1: LOAD PROPERTY VERIOR MESH BOUNDARIES
        -- Defines a non-linear riverbank layout boundary envelope (mm)
        ---------------------------------------------------------------------
        load_vtx_en <= '1'; 
        
        -- Vertex 0: Origin Baseline Hub
        vtx_idx <= 0; vtx_x <= std_logic_vector(to_signed(100000, 32)); vtx_y <= std_logic_vector(to_signed(100000, 32)); wait for CLK_PERIOD;
        
        -- Vertex 1: Low Eastern Edge Stake
        vtx_idx <= 1; vtx_x <= std_logic_vector(to_signed(500000, 32)); vtx_y <= std_logic_vector(to_signed(120000, 32)); wait for CLK_PERIOD;
        
        -- Vertex 2: Northern Critical Boundary Limit Fence
        vtx_idx <= 2; vtx_x <= std_logic_vector(to_signed(480000, 32)); vtx_y <= std_logic_vector(to_signed(350000, 32)); wait for CLK_PERIOD;
        
        -- Vertex 3: Left Return Fencing Node
        vtx_idx <= 3; vtx_x <= std_logic_vector(to_signed(120000, 32)); vtx_y <= std_logic_vector(to_signed(320000, 32)); wait for CLK_PERIOD;
        
        load_vtx_en <= '0';
        wait for CLK_PERIOD * 2;
        path_valid <= '1';

        ---------------------------------------------------------------------
        -- PHASE 2: RUN WEATHER GRADIENT IMPACT SIMULATION
        ---------------------------------------------------------------------
        
        -- Step A: Nominal Operations Under Calm Conditions
        ideal_path_x <= 300000;
        ideal_path_y <= 250000; -- Safely inside the polyhedral grid
        wind_drift_y <= 0;
        wait for CLK_PERIOD * 2;
        -- Expected: line_clamp = '0', hex_safety = 0xF, enforced paths match ideal paths

        -- Step B: Sudden Microclimate Gale Event (55-Knot Crosswind Hit)
        -- The aerodynamic wind pressure pushes the machine sideways (+Y direction)
        ideal_path_x <= 305000;
        ideal_path_y <= 260000;
        wind_drift_y <= 450000; -- Massive 450-mm physical shift vector applied by wind pressure
        wait for CLK_PERIOD * 2;
        -- Expected: Total Y reaches 710,000, breaching Vertex 2 limits.
        -- Intercept Result: line_clamp spikes high ('1'), hex_safety drops to 0x0, brakes engage.
        -- Vehicle output vectors immediately snap back to Vertex 0 safety fallback (100,000, 100,000).

        -- Step C: Maintaining Brake Lock While Gale Sustains
        ideal_path_x <= 310000;
        wait for CLK_PERIOD * 2;
        -- Expected: Wind continues pushing tool head out of bounds. 
        -- Hardware maintains the absolute 0x0 clamp state, preventing any further cut progression.

        -- Step D: Wind Shear Subsides (Tractor Drive Control Recovers)
        -- Aerodynamic drift forces drop back to zero; steering correction centers the tool head
        wind_drift_y <= 0;
        ideal_path_x <= 300000;
        ideal_path_y <= 200000; -- Repositioned safely within keeping bounds
        wait for CLK_PERIOD * 2;
        -- Expected Recovery: line_clamp automatically clears back to '0'.
        -- Bus restores immediately to maximum voltage indicator 0xF. Machine resumes nominal cutting pass.

        path_valid <= '0';
        wait;
    end process;

end SimulationTest;
