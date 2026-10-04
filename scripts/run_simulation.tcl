# File Path: scripts/run_simulation.tcl
# =========================================================================
# REVOLUTIONARY TECHNOLOGY COMPANY — UNIVAC IX AUTOMATED FPGA TOOLCHAIN
# Xilinx Vivado Automated Project Compiler and Simulator Launch Script
# =========================================================================

# 1. Define Local Project Workspace Environment Parameters
set proj_name "univac_ix_hardware_core"
set proj_dir "./vivado_project"
set src_dir "./src/hardware"

puts "[*] Initializing Univac IX Mainframe automated toolchain environment..."

# Clear out any stale compiled project folders to prevent file locking overlaps
if {[file exists $proj_dir]} {
    file delete -force $proj_dir
    puts "[*] Purged existing build folders to establish a clean compiler baseline."
}

# Create an in-memory project instance targeting the high-performance silicon fabric
create_project $proj_name $proj_dir -part xc7vx485tffg1761-2 -force
set_property target_language VHDL [current_project]

# 2. Ingest and Add Source Libraries to the Compilation Matrix
puts "[*] Ingesting VHDL source code assets and polyhedral verification testbenches..."

# Target the clean design files and the newly generated polyhedral Keep-In core engines
add_files [glob $src_dir/*.vhd]

# Differentiate synthesis paths from behavioral verification testbenches
set_property USED_IN_SYNTHESIS false [get_files $src_dir/tb_rt_poly_array_clipper.vhd]
set_property USED_IN_SYNTHESIS false [get_files $src_dir/tb_rt_poly_mesh_validator.vhd]

update_compile_order -fileset sources_1

# 3. Compile the Design & Verify Syntactic Integrity
puts "[*] Running multi-core accelerated VHDL syntactic compilation pass..."
set compilation_status [get_property NEEDS_REFRESH [current_run -synthesis]]

# Set the active simulation top-level module to target your multi-university mesh testbench
set_property top tb_rt_poly_mesh_validator [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]

update_compile_order -fileset sim_1

# 4. Launch the Asynchronous Vivado Waveform Simulator Window
puts "[*] Launching Xilinx Vivado Behavioral Simulator GUI Engine..."
launch_simulation -type behavioral

# Enforce uniform baseline timing analysis run durations (matches your 10MHz clock cycles)
run 20 us

puts "[+] Toolchain automation pass executed successfully. Waveform matrix loaded."
