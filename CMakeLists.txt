cmake_minimum_required(VERSION 3.10)
project(SOPEVS VERSION 1.0)

# Set the C++ standard to C++11 or higher, as Crow requires C++11
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Include directories for Crow and Asio
include_directories(/opt/homebrew/Cellar/asio/1.28.1/include /Users/isi/RISOTTO/Crow/include)

# If you have a main.cpp and additional source files, list them all here
add_executable(SOPEVS main.cpp run_simulation.cc cheby.cc simulate_system.cc common.cc ev.cc)

# Link pthread
target_link_libraries(SOPEVS pthread)
