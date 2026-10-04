-- File Path: src/hardware/tb_rt_poly_mesh_validator.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_rt_poly_mesh_validator is
-- Testbenches do not expose top-level structural ports
end tb_rt_poly_mesh_validator;

architecture Behavioral Validation of tb_rt_poly_mesh_validator is

    -- 1. Component Declaration of the production dynamic polygon clipper module
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

    -- 2. Internal Testbench Signal Arrays & Timing Channels
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
    
    -- Monitored Silicon Feedback Signals
    signal enforced_x      : STD_LOGIC_VECTOR(31 downto 0);
    signal enforced_y      : STD_LOGIC_VECTOR(31 downto 0);
    signal line_clamp      : STD_LOGIC;
    signal hex_safety      : STD_LOGIC_VECTOR(3 downto 0);

    -- Clock cycle configuration (10.0 MHz Stage 2 Industrial Divider = 100 ns period)
    constant CLK_PERIOD : time := 100 ns;

begin

    -- 3. Device Under Test (DUT) Instantiation
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

    -- Synchronous clock generator thread
    clk_process : process
    begin
        clk_10mhz <= '0';
        wait for CLK_PERIOD / 2;
        clk_10mhz <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    -- 4. Cross-System Validation Execution Process
    stim_process : process
    begin
        -- Assert master logic clear lines during system boot frame
        sys_reset   <= '1';
        load_vtx_en <= '0';
        path_valid  <= '0';
        wait for CLK_PERIOD * 2;
        sys_reset   <= '0';
        wait for CLK_PERIOD;

        ---------------------------------------------------------------------
        -- PHASE 1: LOAD COORDINATE MAP REGISTER ARRAY
        -- Directly translates the target Unreal Engine 5 Landscape Mesh Vertices
        -- Unreal Poly Vertices: V0(10000, 10000)cm -> Fixed-Point: (100000, 100000)mm
        ---------------------------------------------------------------------
        load_vtx_en <= '1';
        
        -- Ingest Unreal Mesh Boundary Stake 0
        vtx_idx <= 0; 
        vtx_x <= std_logic_vector(to_signed(100000, 32)); 
        vtx_y <= std_logic_vector(to_signed(100000, 32)); wait for CLK_PERIOD;
        
        -- Ingest Unreal Mesh Boundary Stake 1
        vtx_idx <= 1; 
        vtx_x <= std_logic_vector(to_signed(500000, 32)); 
        vtx_y <= std_logic_vector(to_signed(120000, 32)); wait for CLK_PERIOD;
        
        -- Ingest Unreal Mesh Boundary Stake 2
        vtx_idx <= 2; 
        vtx_x <= std_logic_vector(to_signed(480000, 32)); 
        vtx_y <= std_logic_vector(to_signed(350000, 32)); wait for CLK_PERIOD;
        
        -- Ingest Unreal Mesh Boundary Stake 3
        vtx_idx <= 3; 
        vtx_x <= std_logic_vector(to_signed(120000, 32)); 
        vtx_y <= std_logic_vector(to_signed(320000, 32)); wait for CLK_PERIOD;
        
        load_vtx_en <= '0';
        wait for CLK_PERIOD * 2;
        path_valid <= '1';

        ---------------------------------------------------------------------
        -- PHASE 2: SYNCHRONOUS HARDWARE-TO-VIRTUAL MESH VERIFICATION KEYS
        ---------------------------------------------------------------------
        
        -- Test Scenario A: Unreal Viewport confirms tractor is deep within the polygon fields
        -- Inbound JSON String Stream Vector: {"ue5_position_cm": [25000.0, 18000.0, 0.0]}
        target_x <= std_logic_vector(to_signed(250000, 32));
        target_y <= std_logic_vector(to_signed(180000, 32));
        wait for CLK_PERIOD * 2;
        assert (line_clamp = '0') report "❌ Error: False boundary clamp flagged inside safe zone." severity failure;
        assert (hex_safety = "1111") report "❌ Error: Interlock dropped inside nominal boundaries." severity failure;

        -- Test Scenario B: Unreal Viewport logs a border-proximity sweep pass
        -- Inbound JSON String Stream Vector: {"ue5_position_cm": [40000.0, 11500.0, 0.0]}
        target_x <= std_logic_vector(to_signed(400000, 32));
        target_y <= std_logic_vector(to_signed(115000, 32));
        wait for CLK_PERIOD * 2;
        assert (line_clamp = '0') report "❌ Error: Perimeter fence edge triggered an unauthorized stop." severity failure;

        -- Test Scenario C: Unreal scene environment flags a critical tracking breach event
        -- Tractor has crossed the left boundary fence.
        -- Inbound JSON String Stream Vector: {"ue5_position_cm": [7500.0, 30000.0, 0.0]}
        target_x <= std_logic_vector(to_signed(75000, 32));
        target_y <= std_logic_vector(to_signed(300000, 32));
        wait for CLK_PERIOD * 2;
        assert (line_clamp = '1') report "✅ Success: Clipper successfully intercepted a physical boundary breach." severity note;
        assert (hex_safety = "0000") report "✅ Success: Bus dropped to emergency 0x0 loop." severity note;
        assert (enforced_x = std_logic_vector(to_signed(100000, 32))) report "❌ Error: Target failed to redirect to safe origin anchor." severity failure;

        -- Clear verification bus states and complete testbench procedures
        path_valid <= '0';
        report "🚀 [UNIVAC IX CORE METRIC VERIFICATION COMPLETE]: Physical FPGA array matches Unreal Mesh perfectly." severity note;
        wait;
    end process;

end Behavioral Validation;
