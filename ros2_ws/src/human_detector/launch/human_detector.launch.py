from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='human_detector',
            executable='human_detector_node',
            name='human_detector_node',
            output='screen',
        ),
        Node(
            package='human_detector',
            executable='llm_interface_node',
            name='llm_interface_node',
            output='screen',
            parameters=[
                {'local_llm_enabled': False},
                {'local_llm_url': 'http://localhost:8080'},
                {'api_key': ''}
            ]
        )
    ])
