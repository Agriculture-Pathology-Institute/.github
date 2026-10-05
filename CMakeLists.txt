# Append this build target section inside your core CMakeLists.txt file:

# =========================================================================
# TARGET MODULE: RHEINMETALL COMPLIANT SHARED ENGINEERING PLUGIN
# Enforces native C++20 thread-safe performance compilation flags
# =========================================================================
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(rt_rheinmetall_filter_bridge SHARED 
    src/hardware/rt_rheinmetall_filter_bridge.cpp
)

target_include_directories(rt_rheinmetall_filter_bridge PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Optimize for tactical execution speed while stripping legacy symbolic overhead
if(MSVC)
    target_compile_options(rt_rheinmetall_filter_bridge PRIVATE /O2 /W4 /NXCOMPAT)
else()
    target_compile_options(rt_rheinmetall_filter_bridge PRIVATE -O3 -Wall -fPIC)
endif()
