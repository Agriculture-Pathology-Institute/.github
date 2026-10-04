-- File Path: src/hardware/rt_poly_array_clipper.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_poly_array_clipper is
    Generic (
        -- Maximum allowable polyhedral vertex array size for keeping boundaries
        -- Adjust this baseline to scale with your property plot coordinates
        MAX_VERTICES : integer := 8
    );
    Port (
        -- High-Speed Timing & Control Rails
        CLK_INDUSTRIAL   : in  STD_LOGIC; -- Synchronized to 10.0 MHz clock line
        SYSTEM_RESET     : in  STD_LOGIC;
        
        -- Live Dynamic Polyhedral Geometry Arrays Ingested from Unreal Scene Space
        -- Loaded on system setup to match the county registered boundary lines
        LOAD_VERTEX_EN   : in  STD_LOGIC;
        VERTEX_INDEX_IN  : in  integer range 0 to MAX_VERTICES-1;
        VERTEX_X_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        VERTEX_Y_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        
        -- Active Tool/Tractor Target Vectors (Millimeter Fixed-Point Structure)
        TARGET_X_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        TARGET_Y_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        PATH_VALID_IN    : in  STD_LOGIC;
        
        -- Safely Truncated Output to Machine Steering & Implement Actuators
        ENFORCED_X_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
        ENFORCED_Y_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
        LINE_CLAMP_ACTIVE: out STD_LOGIC; -- Strobe high stops onward forward tractor motion
        
        -- Native 16-State Hexadecimal Status Indicator Bus
        HEX_SAFETY_OUT   : out STD_LOGIC_VECTOR(3 downto 0)
    );
end rt_poly_array_clipper;

architecture SystolicArrayEnforcement of rt_poly_array_clipper is
    -- Internal memory array holding the dynamic polyhedral tracking vertices
    type coordinate_array is array (0 to MAX_VERTICES-1) of signed(31 downto 0);
    signal poly_x_registers : coordinate_array := (others => (others => '0'));
    signal poly_y_registers : coordinate_array := (others => (others => '0'));
    
    -- Processing pipeline vectors
    signal current_x : signed(31 downto 0);
    signal current_y : signed(31 downto 0);
    
    type sign_bits_type is array (0 to MAX_VERTICES-1) of STD_LOGIC;
    signal edge_signs : sign_bits_type := (others => '0');
    signal out_of_polygon : STD_LOGIC := '0';
begin
    current_x <= signed(TARGET_X_IN);
    current_y <= signed(TARGET_Y_IN);

    -------------------------------------------------------------------------
    -- HARDWARE REGISTRY STORAGE & CROSS-PRODUCT INTERCEPT PIPELINE
    -------------------------------------------------------------------------
    process(CLK_INDUSTRIAL, SYSTEM_RESET)
        variable dx, dy : signed(31 downto 0);
        variable px, py : signed(31 downto 0);
        variable cross_eval : signed(63 downto 0);
        variable next_idx : integer range 0 to MAX_VERTICES-1;
        variable breach_accumulation : STD_LOGIC;
    begin
        if SYSTEM_RESET = '1' then
            poly_x_registers <= (others => (others => '0'));
            poly_y_registers <= (others => (others => '0'));
            ENFORCED_X_OUT    <= (others => '0');
            ENFORCED_Y_OUT    <= (others => '0');
            LINE_CLAMP_ACTIVE <= '0';
            HEX_SAFETY_OUT    <= "1111"; -- Nominal state (0xF)
            out_of_polygon    <= '0';
        elsif rising_edge(CLK_INDUSTRIAL) then
            
            -- Dynamic registration configuration write loop
            if LOAD_VERTEX_EN = '1' then
                poly_x_registers(VERTEX_INDEX_IN) <= signed(VERTEX_X_IN);
                poly_y_registers(VERTEX_INDEX_IN) <= signed(VERTEX_Y_IN);
            end if;

            if PATH_VALID_IN = '1' then
                breach_accumulation := '0';
                
                -- Parallel Unrolled Cross-Product Evaluation Loop (Systolic Ray Trace)
                for i in 0 to MAX_VERTICES-1 loop
                    if i = MAX_VERTICES-1 then
                        next_idx := 0;
                    else
                        next_idx := i + 1;
                    end if;
                    
                    dx := poly_x_registers(next_idx) - poly_x_registers(i);
                    dy := poly_y_registers(next_idx) - poly_y_registers(i);
                    px := current_x - poly_x_registers(i);
                    py := current_y - poly_y_registers(i);
                    
                    cross_eval := (dx * py) - (dy * px);
                    
                    -- Capture sign bit to assess if target has drifted to outer border vector
                    edge_signs(i) <= cross_eval(63);
                    breach_accumulation := breach_accumulation or cross_eval(63);
                end loop;
                
                out_of_polygon <= breach_accumulation;

                -------------------------------------------------------------
                -- EXTRUSION PROTECTION CLAMP INTERLOCK DISPATCH
                -------------------------------------------------------------
                if out_of_polygon = '1' then
                    LINE_CLAMP_ACTIVE <= '1';
                    HEX_SAFETY_OUT    <= "0000"; -- Instantly force absolute E-Stop state (0x0)
                    
                    -- Hard trace fallback target to the origin seed waypoint (Vertex 0 safety hook)
                    ENFORCED_X_OUT <= std_logic_vector(poly_x_registers(0));
                    ENFORCED_Y_OUT <= std_logic_vector(poly_y_registers(0));
                else
                    LINE_CLAMP_ACTIVE <= '0';
                    HEX_SAFETY_OUT    <= "1111"; -- Keep high fast-charge interlock operational mode (0xF)
                    ENFORCED_X_OUT    <= TARGET_X_IN;
                    ENFORCED_Y_OUT    <= TARGET_Y_IN;
                end if;
                
            end if;
        end if;
    end process;

end SystolicArrayEnforcement;
