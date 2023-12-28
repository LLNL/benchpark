# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.23)

option(USE_OPNEMP "Use OpenMP" OFF)
option(USE_CUDA "Use CUDA" OFF)
option(USE_HIP "Use HIP" OFF)

if(USE_CUDA)
  project(saxpy VERSION 1.0 LANGUAGES CXX CUDA)
else()
  project(saxpy VERSION 1.0 LANGUAGES CXX)
endif()

set(SOURCES saxpy.cc)
add_executable(${PROJECT_NAME} ${SOURCES})

if(USE_OPENMP)
    target_compile_options(saxpy PRIVATE -DUSE_OPENMP -fopenmp)
    target_link_options(${PROJECT_NAME} PRIVATE -fopenmp)
endif()

if(USE_HIP)
    include_directories(${ROCM_PATH}/include)
    target_compile_options(saxpy PRIVATE -x hip -DUSE_HIP --offload-arch=${ROCM_ARCH})
    target_link_libraries(${PROJECT_NAME} PRIVATE -L${ROCM_PATH}/lib -lamdhip64)
endif()

if(USE_CUDA)
    set_source_files_properties(saxpy.cc PROPERTIES LANGUAGE "CUDA")
    set(CMAKE_CUDA_STANDARD_REQUIRED TRUE)
    set(CMAKE_CXX_STANDARD_REQUIRED TRUE)
    set(CMAKE_CUDA_FLAGS "-Xcompiler -DUSE_CUDA")
    set_target_properties(saxpy PROPERTIES CUDA_SEPARABLE_COMPILATION ON)
endif()

install(TARGETS saxpy
        DESTINATION bin
)
