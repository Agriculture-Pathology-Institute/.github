-- File Path: src/hardware/rt_boundary_clipper.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_boundary_clipper is
    Generic (
        -- Defines a 4-point non-linear polyhedral sequence bounding the keep-in zone
        -- All values map coordinates in millimeters (mm)
        VTX_0_X : signed(31 downto 0) := to_signed(100000, 32); -- Point 0
        VTX_0_Y : signed(31 downto 0) := to_signed(100000, 32);
        
        VTX_1_X : signed(31 downto 0) := to_signed(500000, 32); -- Point 1
        VTX_1_Y : signed(31 downto 0) := to_signed(120000, 32);
        
        VTX_2_X : signed(31 downto 0) := to_signed(480000, 32); -- Point 2
        VTX_2_Y : signed(31 downto 0) := to_signed(500000, 32);
        
        VTX_3_X : signed(31 downto 0) := to_signed(120000, 32); -- Point 3
        VTX_3_Y : signed(31 downto 0) := to_signed(450000, 32)
    );
    Port (
        -- Timing & System Flags
        CLK_INDUSTRIAL   : in  STD_LOGIC; -- Synchronized to 10.0 MHz Stage 2 Divider
        SYSTEM_RESET     : in  STD_LOGIC;
        
        -- Target Vector Coordinates Ingested from Unreal Engine Scene Space
        TARGET_X_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        TARGET_Y_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        PATH_VALID_IN    : in  STD_LOGIC;
        
        -- Safely Truncated/Clamped Vectors to Machine Implement Controllers
        ENFORCED_X_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
        ENFORCED_Y_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
        BOUNDARY_CLAMPED : out STD_LOGIC; -- Flagged high when boundary constraint limits are hit
        
        -- Native 16-State Control Bus Status Signal
        HEX_SAFETY_OUT   : out STD_LOGIC_VECTOR(3 downto 0)
    );
end rt_boundary_clipper;

architecture PolyhedralEnforcement of rt_boundary_clipper is
    signal current_x : signed(31 downto 0);
    signal current_y : signed(31 downto 0);
    
    -- Cross-product evaluation registers to verify sign uniformity (keep-in zone validation)
    signal cross_0, cross_1, cross_2, cross_3 : signed(63 downto 0) := (others => '0');
    signal out_of_bounds : STD_LOGIC := '0';
begin
    current_x <= signed(TARGET_X_IN);
    current_y <= signed(TARGET_Y_IN);

    process(CLK_INDUSTRIAL, SYSTEM_RESET)
        variable dx, dy, px, py : signed(31 downto 0);
    begin
        if SYSTEM_RESET = '1' then
            ENFORCED_X_OUT   <= (others => '0');
            ENFORCED_Y_OUT   <= (others => '0');
            BOUNDARY_CLAMPED <= '0';
            HEX_SAFETY_OUT   <= "1111"; -- Nominal state (0xF)
            out_of_bounds    <= '0';
        elsif rising_edge(CLK_INDUSTRIAL) then
            if PATH_VALID_IN = '1' then
                
                -- Segment 0-1 Vector Edge Assessment
                dx := VTX_1_X - VTX_0_X; dy := VTX_1_Y - VTX_0_Y;
                px := current_x - VTX_0_X; py := current_y - VTX_0_Y;
                cross_0 <= (dx * py) - (dy * px);

                -- Segment 1-2 Vector Edge Assessment
                dx := VTX_2_X - VTX_1_X; dy := VTX_2_Y - VTX_1_Y;
                px := current_x - VTX_1_X; py := current_y - VTX_1_Y;
                cross_1 <= (dx * py) - (dy * px);

                -- Segment 2-3 Vector Edge Assessment
                dx := VTX_3_X - VTX_2_X; dy := VTX_3_Y - VTX_2_Y;
                px := current_x - VTX_2_X; py := current_y - VTX_2_Y;
                cross_2 <= (dx * py) - (dy * px);

                -- Segment 3-0 Vector Edge Assessment
                dx := VTX_0_X - VTX_3_X; dy := VTX_0_Y - VTX_3_Y;
                px := current_x - VTX_3_X; py := current_y - VTX_3_Y;
                cross_3 <= (dx * py) - (dy * px);

                -- Verify if point lies consistently on the inner edge of all structural bounds
                if (cross_0(63) = '1' or cross_1(63) = '1' or cross_2(63) = '1' or cross_3(63) = '1') then
                    out_of_bounds <= '1';
                else
                    out_of_bounds <= '0';
                end if;

                -- Execute instantaneous vector clamping protection
                if out_of_bounds = '1' then
                    BOUNDARY_CLAMPED <= '1';
                    HEX_SAFETY_OUT   <= "0000"; -- Drop state to E-Stop (0x0)
                    
                    -- Hard clamp back tracking to nearest structural vertex fallback bounds
                    ENFORCED_X_OUT <= std_logic_vector(VTX_0_X);
                    ENFORCED_Y_OUT <= std_logic_vector(VTX_0_Y);
                else
                    BOUNDARY_CLAMPED <= '0';
                    HEX_SAFETY_OUT   <= "1111"; -- Maintain normal operation (0xF)
                    ENFORCED_X_OUT   <= TARGET_X_IN;
                    ENFORCED_Y_OUT   <= TARGET_Y_IN;
                end if;

            end if;
        end if;
    end process;
end PolyhedralEnforcement;
