from setuptools import setup

package_name = 'human_detector'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/human_detector.launch.py']),
        ('share/' + package_name + '/models', ['models/yolov8n.pt']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='team',
    maintainer_email='team@example.com',
    description='Human Detection Package with LLM Integration for OriginCar Competition',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'human_detector_node = human_detector.human_detector_node:main',
            'llm_interface_node = human_detector.llm_interface_node:main',
        ],
    },
)
