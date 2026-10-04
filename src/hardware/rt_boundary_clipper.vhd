-- File Path: src/hardware/rt_boundary_clipper.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_boundary_clipper is
    Generic (
        -- Spatial units are mapped as signed fixed-point integers 
        -- Represents coordinates down to millimeter-scale precision
        COORD_MIN_X : signed(31 downto 0) := to_signed(100000, 32);  -- Hard Property Boundary Left (mm)
        COORD_MAX_X : signed(31 downto 0) := to_signed(500000, 32);  -- Hard Property Boundary Right (mm)
        COORD_MIN_Y : signed(31 downto 0) := to_signed(100000, 32);  -- Hard Property Boundary Bottom (mm)
        COORD_MAX_Y : signed(31 downto 0) := to_signed(500000, 32)   -- Hard Property Boundary Top (mm)
    );
    Port (
        -- System Interlock & Clock Networks
        CLK_INDUSTRIAL   : in  STD_LOGIC; -- Driven by the 10.0 MHz Stage 2 Divider
        SYSTEM_RESET     : in  STD_LOGIC;
        
        -- Target Path Generation Input from Path Planner (Unreal Engine Matrix)
        TARGET_X_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        TARGET_Y_IN      : in  STD_LOGIC_VECTOR(31 downto 0);
        PATH_VALID_IN    : in  STD_LOGIC;
        
        -- Enforced & Safely Clipped Output to Mobile Fleet Implement Controllers
        ENFORCED_X_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
        ENFORCED_Y_OUT   : out STD_LOGIC_VECTOR(31 downto 0);
        BOUNDARY_VIOLATION: out STD_LOGIC; -- High flag interrupts tractor drive profile
        
        -- Native 16-State Control Bus Interface Connection
        HEX_SAFETY_OUT   : out STD_LOGIC_VECTOR(3 downto 0)
    );
end rt_boundary_clipper;

architecture PreciseEnforcement of rt_boundary_clipper is
    signal signed_x_in  : signed(31 downto 0);
    signal signed_y_in  : signed(31 downto 0);
    signal clamped_x    : signed(31 downto 0) := (others => '0');
    signal clamped_y    : signed(31 downto 0) := (others => '0');
    signal safety_fault : STD_LOGIC := '0';
begin
    -- Cast raw incoming target bus bits to signed mathematical channels
    signed_x_in <= signed(TARGET_X_IN);
    signed_y_in <= signed(TARGET_Y_IN);

    process(CLK_INDUSTRIAL, SYSTEM_RESET)
    begin
        if SYSTEM_RESET = '1' then
            clamped_x <= (others => '0');
            clamped_y <= (others => '0');
            safety_fault <= '0';
            BOUNDARY_VIOLATION <= '0';
            HEX_SAFETY_OUT <= "1111"; -- Default to nominal interlock state (0xF)
        elsif rising_edge(CLK_INDUSTRIAL) then
            if PATH_VALID_IN = '1' then
                
                -------------------------------------------------------------
                -- CRITICAL BOUNDARY CLIPPING LOGIC (X-AXIS ENFORCEMENT)
                -------------------------------------------------------------
                if signed_x_in < COORD_MIN_X then
                    clamped_x    <= COORD_MIN_X; -- Force exact precision clamp to boundary edge
                    safety_fault <= '1';
                elsif signed_x_in > COORD_MAX_X then
                    clamped_x    <= COORD_MAX_X; -- Force exact precision clamp to boundary edge
                    safety_fault <= '1';
                else
                    clamped_x    <= signed_x_in; -- Path is inside allowable shape bounds
                end if;

                -------------------------------------------------------------
                -- CRITICAL BOUNDARY CLIPPING LOGIC (Y-AXIS ENFORCEMENT)
                -------------------------------------------------------------
                if signed_y_in < COORD_MIN_Y then
                    clamped_y    <= COORD_MIN_Y; -- Force exact precision clamp to boundary edge
                    safety_fault <= '1';
                elsif signed_y_in > COORD_MAX_Y then
                    clamped_y    <= COORD_MAX_Y; -- Force exact precision clamp to boundary edge
                    safety_fault <= '1';
                else
                    clamped_y    <= signed_y_in; -- Path is inside allowable shape bounds
                end if;

                -------------------------------------------------------------
                -- HARDWARE BUS ACTION TRIGGER DISPATCH
                -------------------------------------------------------------
                if safety_fault = '1' then
                    BOUNDARY_VIOLATION <= '1';
                    HEX_SAFETY_OUT     <= "0000"; -- Instantly drop bus state to E-Stop (0x0)
                else
                    BOUNDARY_VIOLATION <= '0';
                    HEX_SAFETY_OUT     <= "1111"; -- Maintain High Fast-Charge/Nominal Operational State (0xF)
                end if;
                
            end if;
        end if;
    end process;

    -- Map internal safely clamped vector structures directly to output ports
    ENFORCED_X_OUT <= std_logic_vector(clamped_x);
    ENFORCED_Y_OUT <= std_logic_vector(clamped_y);

end PreciseEnforcement;
