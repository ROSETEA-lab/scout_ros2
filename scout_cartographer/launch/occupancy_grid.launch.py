from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Arguments and parameters
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')

    declare_resolution_arg = DeclareLaunchArgument(
            'resolution',
            default_value=resolution,
            description='Resolution of a grid cell in the published occupancy grid')

    declare_publish_period_sec_arg = DeclareLaunchArgument(
            'publish_period_sec',
            default_value=publish_period_sec,
            description='OccupancyGrid publishing period')

    declare_use_sim_time_arg = DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true')

    occupancy_grid_node = Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='cartographer_occupancy_grid_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-resolution', resolution, '-publish_period_sec', publish_period_sec])
            
    ld = LaunchDescription()
    
    # Declare the launch options
    ld.add_action(declare_resolution_arg)
    ld.add_action(declare_publish_period_sec_arg)
    ld.add_action(declare_use_sim_time_arg)

    # Add the nodes to the launch description
    ld.add_action(occupancy_grid_node)
    
    return ld
    
