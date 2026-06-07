from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='qr_detector',
            executable='qr_detector_node',
            name='qr_detector_node',
            output='screen',
            parameters=[
                {'rate': 10.0}
            ]
        )
    ])
