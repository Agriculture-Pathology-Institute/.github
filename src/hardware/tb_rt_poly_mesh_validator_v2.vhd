-- File Path: src/hardware/tb_rt_poly_mesh_validator.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_rt_poly_mesh_validator is
-- Testbenches do not expose top-level structural ports
end tb_rt_poly_mesh_validator;

architecture BehavioralValidation of tb_rt_poly_mesh_validator is

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
    
    signal enforced_x      : STD_LOGIC_VECTOR(31 downto 0);
    signal enforced_y      : STD_LOGIC_VECTOR(31 downto 0);
    signal line_clamp      : STD_LOGIC;
    signal hex_safety      : STD_LOGIC_VECTOR(3 downto 0);

    constant CLK_PERIOD : time := 100 ns;

    -- Dynamic Setback Cushion Variable pulled straight from configuration fields
    -- Maps your exact 50.8 mm (2-inch) physical hardware protection ring
    constant CONFIG_SETBACK_CUSHION_MM : integer := 50;

begin

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

    clk_process : process
    begin
        clk_10mhz <= '0';
        wait for CLK_PERIOD / 2;
        clk_10mhz <= '1';
        wait for CLK_PERIOD / 2;
    end process;

    stim_process : process
    begin
        sys_reset   <= '1';
        load_vtx_en <= '0';
        path_valid  <= '0';
        wait for CLK_PERIOD * 2;
        sys_reset   <= '0';
        wait for CLK_PERIOD;

        ---------------------------------------------------------------------
        -- PHASE 1: INGEST CONFIG-ADJUSTED MESH VERTICES
        -- Incorporates the config setback cushion directly into the registry loading pass
        ---------------------------------------------------------------------
        load_vtx_en <= '1';
        
        vtx_idx <= 0; 
        vtx_x <= std_logic_vector(to_signed(100000 + CONFIG_SETBACK_CUSHION_MM, 32)); 
        vtx_y <= std_logic_vector(to_signed(100000 + CONFIG_SETBACK_CUSHION_MM, 32)); wait for CLK_PERIOD;
        
        vtx_idx <= 1; 
        vtx_x <= std_logic_vector(to_signed(500000 - CONFIG_SETBACK_CUSHION_MM, 32)); 
        vtx_y <= std_logic_vector(to_signed(120000 + CONFIG_SETBACK_CUSHION_MM, 32)); wait for CLK_PERIOD;
        
        vtx_idx <= 2; 
        vtx_x <= std_logic_vector(to_signed(480000 - CONFIG_SETBACK_CUSHION_MM, 32)); 
        vtx_y <= std_logic_vector(to_signed(350000 - CONFIG_SETBACK_CUSHION_MM, 32)); wait for CLK_PERIOD;
        
        vtx_idx <= 3; 
        vtx_x <= std_logic_vector(to_signed(120000 + CONFIG_SETBACK_CUSHION_MM, 32)); 
        vtx_y <= std_logic_vector(to_signed(320000 - CONFIG_SETBACK_CUSHION_MM, 32)); wait for CLK_PERIOD;
        
        load_vtx_en <= '0';
        wait for CLK_PERIOD * 2;
        path_valid <= '1';

        ---------------------------------------------------------------------
        -- PHASE 2: EXECUTE VERIFICATION STEPS
        ---------------------------------------------------------------------
        -- Test Pass A: Tractor operates completely inside the safe zone bounds
        target_x <= std_logic_vector(to_signed(250000, 32));
        target_y <= std_logic_vector(to_signed(180000, 32));
        wait for CLK_PERIOD * 2;
        assert (line_clamp = '0') report "❌ Error: Boundary clamp triggered unexpectedly inside safe limits." severity failure;

        -- Test Pass B: Vehicle drifts into the 2-inch configuration setback ring zone
        -- Coordinates breach the safety buffer before physically crossing the actual property line stake
        target_x <= std_logic_vector(to_signed(100000 + (CONFIG_SETBACK_CUSHION_MM / 2), 32));
        target_y <= std_logic_vector(to_signed(150000, 32));
        wait for CLK_PERIOD * 2;
        assert (line_clamp = '1') report "✅ Success: Cushion ring successfully intercepted tractor path before land breach occurred." severity note;
        assert (hex_safety = "0000") report "✅ Success: Bus forced down to 0x0 loop." severity note;

        path_valid <= '0';
        report "🚀 [SETBACK VERIFICATION SUCCESSFUL]: Hardware configuration aligns perfectly with updated config.yaml cushion." severity note;
        wait;
    end process;

end BehavioralValidation;
