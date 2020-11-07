# 3.11.0 is from scikit-build documentation
cmake_minimum_required(VERSION 3.11.0)

# Get consistent behavior out of all the compilers
# pybind11 requires the 11 standard or newer
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

project(jeweler LANGUAGES C CXX)

include_directories(include)
add_subdirectory(c)
add_subdirectory(pybind11)
