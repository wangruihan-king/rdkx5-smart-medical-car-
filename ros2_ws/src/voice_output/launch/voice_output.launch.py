from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='voice_output',
            executable='voice_output_node',
            name='voice_output_node',
            output='screen',
        )
    ])
