import os
import time
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node

import xacro

def generate_launch_description():

    package_name = 'wens_ugv'

    # Process the URDF file
    xacro_file = os.path.join(get_package_share_directory(package_name), 'description', 'wens-ugv.urdf.xacro')
    robot_description_config = Command(['xacro ', str(xacro_file), ' ', 'use_ros2_control:=true', ' ', 'sim_mode:=false'])

    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config, 'use_sim_time': False}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )
    
    twist_mux_params = os.path.join(get_package_share_directory(package_name), 'params', 'twist_mux_params.yaml')
    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params],
            remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')]
    )

    controller_params_file = os.path.join(get_package_share_directory(package_name), 'params', 'controller_manager_params.yaml')
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_description_config},
                    controller_params_file]
    )
    
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )


    # Launch them all!
    return LaunchDescription([
        node_robot_state_publisher,
        twist_mux,
        controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
    ])
