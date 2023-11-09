import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir


def generate_launch_description():
    # Specify the name of the package
    pkg_name = 'scout_cartographer'
    namespace = 'scout_mini'

    pkg_scout_cartographer = get_package_share_directory(pkg_name)
    rviz_config_dir = os.path.join(get_package_share_directory(pkg_name),
                                   'rviz', 'scout_cartographer.rviz')

    # Arguments and parameters
    use_rviz = LaunchConfiguration('use_rviz', default='true')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir', default=os.path.join(
                                                  pkg_scout_cartographer, 'config'))
    configuration_basename = LaunchConfiguration('configuration_basename',
                                                 default='scout_rplidar_2d.lua')
    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')

    declare_cartographer_config_dir_arg = DeclareLaunchArgument(
            'cartographer_config_dir',
            default_value=cartographer_config_dir,
            description='Full path to config file to load')
            
    declare_configuration_basename_arg = DeclareLaunchArgument(
            'configuration_basename',
            default_value=configuration_basename,
            description='Name of lua file for cartographer')
            
    declare_use_sim_time_arg = DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='Use simulation (Gazebo) clock if true')

    declare_resolution_arg = DeclareLaunchArgument(
            'resolution',
            default_value=resolution,
            description='Resolution of a grid cell in the published occupancy grid')

    declare_publish_period_sec_arg = DeclareLaunchArgument(
            'publish_period_sec',
            default_value=publish_period_sec,
            description='OccupancyGrid publishing period')

    # Nodes
    occupancy_grid_cmd = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [ThisLaunchFileDir(), '/occupancy_grid.launch.py']
            ),
            launch_arguments={'use_sim_time': use_sim_time, 'resolution': resolution,
                              'publish_period_sec': publish_period_sec}.items()
    )

    cartographer_node = Node(
            namespace=namespace,
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-configuration_directory', cartographer_config_dir,
                       '-configuration_basename', configuration_basename],
            remappings=[
                ('/tf', '/scout_mini/tf'),
                ('/tf_static', '/scout_mini/tf_static'),
                ('/scout_mini/fix','/scout_mini/gps')
            ]
    )

    rviz2_node = Node(
            namespace=namespace,
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(get_package_share_directory(pkg_name),
                                   'rviz', 'scout_cartographer.rviz')],
            parameters=[{'use_sim_time': use_sim_time}],
            condition=IfCondition(use_rviz),
            output='screen',
            remappings=[
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static')
            ]
    )
 
    ld = LaunchDescription()
    
    # Declare the launch options
    ld.add_action(declare_cartographer_config_dir_arg)
    ld.add_action(declare_configuration_basename_arg)
    ld.add_action(declare_use_sim_time_arg)
    ld.add_action(declare_resolution_arg)
    ld.add_action(declare_publish_period_sec_arg)

    # Add the commands to the launch description
    ld.add_action(occupancy_grid_cmd)

    # Add the nodes to the launch description
    ld.add_action(cartographer_node)
    ld.add_action(rviz2_node)
    
    return ld
    
