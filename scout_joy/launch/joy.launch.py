#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from nav2_common.launch import ReplaceString, RewrittenYaml


def generate_launch_description():
    # Specify the name of the package
    pkg_name = "scout_joy"

    # Arguments and parameters
    joy_dev = LaunchConfiguration("joy_dev", default="/dev/input/js0")
    namespace = LaunchConfiguration("namespace", default="scout_mini") 
    
    declare_joy_dev_arg = DeclareLaunchArgument(
        "joy_dev", default_value=joy_dev, description="Joystick device file"
    )

    declare_namespace_arg = DeclareLaunchArgument(
        "namespace", default_value=namespace, description="Node namespace"
    )

    # Add namespace to joy parameter file
    namespaced_joy_params = ReplaceString(
        source_file=os.path.join(
            get_package_share_directory(pkg_name), "config", "joy.config.yaml"
        ),
        replacements={"namespace": namespace},
    )

    # Nodes
    joy_node = Node(
        package="joy",
        executable="joy_node",
        namespace=namespace,
        name="joy_node",
        parameters=[{"dev": joy_dev, "deadzone": 0.1, "autorepeat_rate": 50.0}],
    )

    teleop_twist_joy_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        namespace=namespace,
        name="teleop_twist_joy_node",
        parameters=[namespaced_joy_params, {"use_sim_time": True}], 
        remappings={("/cmd_vel", "/cmd_vel_joypad")}, 
    )

    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_joy_dev_arg)
    ld.add_action(declare_namespace_arg)

    # Add the commands to the launch description
    ld.add_action(joy_node)
    ld.add_action(teleop_twist_joy_node)

    return ld
