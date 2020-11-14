# 3.11.0 is from scikit-build documentation
cmake_minimum_required(VERSION 3.11.0)

# Get consistent behavior out of all the compilers
# pybind11 requires the 11 standard or newer
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project(jeweler LANGUAGES CXX)

# Add 'src' to install path so compiled modules go to the right place
file(TO_NATIVE_PATH "${CMAKE_INSTALL_PREFIX}/src" CMAKE_INSTALL_PREFIX)

include_directories(include)
add_subdirectory(src)

