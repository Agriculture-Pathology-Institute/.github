-- File Path: src/hardware/rt_chrysler_tractor_bridge.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity rt_chrysler_tractor_bridge is
    Generic (
        -- Mechanical scaling factors mapped in millimeter fixed-point integers
        TRACTOR_WHEELBASE_MM   : signed(31 downto 0) := to_signed(3200, 32); -- 3.2m front-to-rear axle center
        CHRYSLER_INERTIA_GAIN  : signed(15 downto 0) := to_signed(256, 16)   -- Fixed-point multiplier (1.0 scaling baseline)
    );
    Port (
        -- High-Speed Timing & Synchronization Interfaces
        CLK_INDUSTRIAL         : in  STD_LOGIC; -- Driven by the 10.0 MHz industrial clock line
        SYSTEM_RESET           : in  STD_LOGIC;
        
        -- Ingested Chrysler Aerospace Monorail Kinematics Variables (32-Bit Parallel)
        MONORAIL_VELOCITY_MM_S : in  STD_LOGIC_VECTOR(31 downto 0); -- Active velocity input
        MONORAIL_CURVATURE_RADIUS : in  STD_LOGIC_VECTOR(31 downto 0); -- Target curvature footprint
        MONORAIL_LEAN_ANGLE_RAD   : in  STD_LOGIC_VECTOR(31 downto 0); -- Gyroscopic roll/tilt data
        KINEMATICS_VALID_IN    : in  STD_LOGIC;
        
        -- Master VHDL Polyhedral Border Interlock Status
        BOUNDARY_CLAMP_ACTIVE  : in  STD_LOGIC; -- Intercepts feedback logs from the clipper
        
        -- Synchronized Steering Output Array to Tractor Steering Actuators
        STEERING_ANGLE_OUT     : out STD_LOGIC_VECTOR(31 downto 0); -- Target wheel turn angle (milliradians)
        SLIP_COMPENSATION_OUT  : out STD_LOGIC_VECTOR(31 downto 0); -- Dynamic differential torque shift
        
        -- Native 16-State Control Bus Interface Connection
        HEX_SAFETY_OUT         : out STD_LOGIC_VECTOR(3 downto 0)
    );
end rt_chrysler_tractor_bridge;

architecture AerospaceTranslation of rt_chrysler_tractor_bridge is
    signal speed_signed       : signed(31 downto 0);
    signal radius_signed      : signed(31 downto 0);
    signal lean_signed        : signed(31 downto 0);
    
    -- Intermediate calculation pipelines
    signal calculated_ackermann : signed(63 downto 0) := (others => '0');
    signal dynamic_slip_offset  : signed(63 downto 0) := (others => '0');
    signal final_steering_angle : signed(31 downto 0) := (others => '0');
begin
    -- Unpack raw bus inputs into mathematical signed integer tracks
    speed_signed  <= signed(MONORAIL_VELOCITY_MM_S);
    radius_signed <= signed(MONORAIL_CURVATURE_RADIUS);
    lean_signed   <= signed(MONORAIL_LEAN_ANGLE_RAD);

    -------------------------------------------------------------------------
    -- KINEMATICS SYNC & ALWEG-TO-AG IMPLEMENT TRANSLATION PIPELINE
    -------------------------------------------------------------------------
    process(CLK_INDUSTRIAL, SYSTEM_RESET)
        variable target_angle_mrad : signed(31 downto 0);
        variable slip_modifier     : signed(31 downto 0);
    begin
        if SYSTEM_RESET = '1' then
            calculated_ackermann <= (others => '0');
            dynamic_slip_offset  <= (others => '0');
            final_steering_angle <= (others => '0');
            STEERING_ANGLE_OUT   <= (others => '0');
            SLIP_COMPENSATION_OUT <= (others => '0');
            HEX_SAFETY_OUT       <= "1111"; -- Default to nominal operational run state (0xF)
        elsif rising_edge(CLK_INDUSTRIAL) then
            
            -- Intercept loop: If the polyhedral clipper drops due to property boundaries, override instantly
            if BOUNDARY_CLAMP_ACTIVE = '1' then
                final_steering_angle <= (others => '0');
                STEERING_ANGLE_OUT   <= (others => '0');
                SLIP_COMPENSATION_OUT <= (others => '0');
                HEX_SAFETY_OUT       <= "0000"; -- Force complete system shutdown lock (0x0)
            
            elsif KINEMATICS_VALID_IN = '1' then
                
                -- 1. Standard Ackermann Core Steering Base Geometry Extraction
                -- Formula: Angle = Wheelbase / Radius
                if radius_signed /= 0 then
                    calculated_ackermann <= (TRACTOR_WHEELBASE_MM * to_signed(1000, 32)) / radius_signed; -- Converted to milliradians
                else
                    calculated_ackermann <= (others => '0');
                end if;
                
                -- 2. Aerospace Centripetal Slip Correction
                -- Incorporates Chrysler lean metrics to offset wheel drift under high-current torque loads
                -- Formula: Slip_Offset = (Velocity^2 * Lean) / 1000000
                dynamic_slip_offset <= (speed_signed * lean_signed) / to_signed(10000, 32);

                -- Scale the aerodynamic/centripetal correction via the gain parameter register
                slip_modifier := resize(dynamic_slip_offset(47 downto 16) * CHRYSLER_INERTIA_GAIN / to_signed(256, 16), 32);
                target_angle_mrad := resize(calculated_ackermann, 32);

                -- 3. Composite Vector Mixing
                -- Blends the path requirements with real-time drift stabilization values
                final_steering_angle <= target_angle_mrad + slip_modifier;

                -- Output execution frames directly to hydraulic steering controllers
                STEERING_ANGLE_OUT    <= std_logic_vector(final_steering_angle);
                SLIP_COMPENSATION_OUT <= std_logic_vector(slip_modifier);
                
                -- Assess system state thresholds to assign hexadecimal health metrics
                if final_steering_angle > to_signed(600, 32) or final_steering_angle < to_signed(-600, 32) then
                    HEX_SAFETY_OUT <= "0011"; -- Set state to 0x3 (Valve Actuation: Open 25% for tight corner adjustments)
                else
                    HEX_SAFETY_OUT <= "1111"; -- Keep state at nominal full parallel run capacity (0xF)
                end if;

            end if;
        end if;
    end process;

end AerospaceTranslation;
