################################################################################
# Set minimum required version of cmake, project name and compile options
################################################################################
cmake_minimum_required(VERSION 3.16) 
project(wens_ugv LANGUAGES CXX C)

# Default to C99 for C files (from wens_ugv)
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

if(MSVC)
  add_compile_definitions(
    _USE_MATH_DEFINES
  )
endif()

set(SLLIDAR_SDK_PATH "./sdk/")

FILE(GLOB SLLIDAR_SDK_SRC 
  "${SLLIDAR_SDK_PATH}/src/arch/linux/*.cpp"
  "${SLLIDAR_SDK_PATH}/src/hal/*.cpp"
  "${SLLIDAR_SDK_PATH}/src/*.cpp"
  "${SLLIDAR_SDK_PATH}/src/dataunpacker/*.cpp"
  "${SLLIDAR_SDK_PATH}/src/dataunpacker/unpacker/*.cpp"
)

################################################################################
# Find ament packages and libraries for ament and system dependencies
################################################################################
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# diffdrive_arduino 관련 패키지 추가
set(THIS_PACKAGE_INCLUDE_DEPENDS
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
)

foreach(Dependency IN ITEMS ${THIS_PACKAGE_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()

################################################################################
# Build
################################################################################
include_directories(
  ${SLLIDAR_SDK_PATH}/include
  ${SLLIDAR_SDK_PATH}/src
  ${Boost_INCLUDE_DIRS}
)

add_executable(sllidar_node src/sllidar_node.cpp ${SLLIDAR_SDK_SRC})
ament_target_dependencies(sllidar_node
  rclcpp
  std_srvs
  sensor_msgs
)

add_executable(sllidar_client src/sllidar_client.cpp)
ament_target_dependencies(sllidar_client
  rclcpp
  std_srvs
  sensor_msgs
)

add_library(
  diffdrive_arduino
  SHARED
  hardware/diffbot_system.cpp
)
target_compile_features(diffdrive_arduino PUBLIC cxx_std_17)
target_include_directories(diffdrive_arduino PUBLIC
  $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/hardware/include>
  $<INSTALL_INTERFACE:include/diffdrive_arduino>
)
ament_target_dependencies(diffdrive_arduino PUBLIC
  ${THIS_PACKAGE_INCLUDE_DEPENDS}
)

target_link_libraries(diffdrive_arduino PUBLIC serial)

# Causes the visibility macros to use dllexport rather than dllimport
target_compile_definitions(diffdrive_arduino PRIVATE "DIFFDRIVE_ARDUINO_BUILDING_DLL")

# Export hardware plugins for diffdrive_arduino
pluginlib_export_plugin_description_file(hardware_interface hardware/diffdrive_arduino.xml)

################################################################################
# Install
################################################################################
install(
  DIRECTORY description launch map params hardware/include/
  DESTINATION share/${PROJECT_NAME}
)

install(
  TARGETS sllidar_node sllidar_client
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS diffdrive_arduino
  EXPORT export_diffdrive_arduino
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

################################################################################
# Macro for ament package
################################################################################
ament_export_dependencies(rclcpp)
ament_export_dependencies(std_msgs)
ament_export_dependencies(sensor_msgs)
ament_export_include_directories(include)

ament_export_targets(export_diffdrive_arduino HAS_LIBRARY_TARGET)
ament_export_dependencies(${THIS_PACKAGE_INCLUDE_DEPENDS})

################################################################################
# Testing (if needed)
################################################################################
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest REQUIRED)
endif()

ament_package()
