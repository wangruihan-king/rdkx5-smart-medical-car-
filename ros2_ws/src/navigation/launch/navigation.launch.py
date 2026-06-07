from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='navigation',
            executable='obstacle_avoidance_node',
            name='obstacle_avoidance_node',
            output='screen',
            parameters=[
                {'safety_distance': 0.5},
                {'max_speed': 0.3},
                {'turn_speed': 0.5}
            ]
        ),
        Node(
            package='navigation',
            executable='path_planner_node',
            name='path_planner_node',
            output='screen',
        ),
        Node(
            package='navigation',
            executable='motion_controller_node',
            name='motion_controller_node',
            output='screen',
            parameters=[
                {'target_position_tolerance': 0.3},
                {'max_speed': 0.5},
                {'max_angular_speed': 1.0}
            ]
        )
    ])
