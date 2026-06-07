#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激光雷达避障节点
作者: [队伍名称]
日期: 2025
功能: 使用单线TOF激光雷达检测障碍物，控制机器人安全行驶
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool

class ObstacleAvoidanceNode(Node):
    """
    避障节点类
    负责接收激光雷达数据，检测障碍物，发布避障控制指令
    """
    def __init__(self):
        """
        初始化节点，订阅激光雷达话题，创建控制发布者
        """
        super().__init__('obstacle_avoidance_node')
        
        # 订阅激光雷达扫描话题
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        
        # 发布避障控制指令
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel_obstacle',
            10
        )
        
        # 发布障碍物检测状态
        self.obstacle_publisher = self.create_publisher(
            Bool,
            '/obstacle_detected',
            10
        )
        
        # 加载安全距离参数
        self.safety_distance = self.declare_parameter('safety_distance', 0.5).value
        # 加载最大速度参数
        self.max_speed = self.declare_parameter('max_speed', 0.3).value
        # 加载转向速度参数
        self.turn_speed = self.declare_parameter('turn_speed', 0.5).value
        
        self.get_logger().info('激光雷达避障节点已启动')
    
    def scan_callback(self, msg):
        """
        激光雷达数据回调函数
        处理扫描数据，判断是否有障碍物
        
        参数:
            msg: LaserScan消息，包含激光雷达扫描数据
        """
        ranges = msg.ranges
        # 找出最近的障碍物距离
        min_range = min(ranges)
        
        # 判断是否检测到障碍物（小于安全距离）
        obstacle_detected = min_range < self.safety_distance
        
        # 发布障碍物检测状态
        obstacle_msg = Bool()
        obstacle_msg.data = obstacle_detected
        self.obstacle_publisher.publish(obstacle_msg)
        
        # 如果检测到障碍物，执行避障；否则清除路径
        if obstacle_detected:
            self.avoid_obstacle(ranges)
        else:
            self.clear_path()
    
    def avoid_obstacle(self, ranges):
        """
        避障策略函数
        选择障碍物较少的方向进行转向
        
        参数:
            ranges: 激光雷达扫描距离数组
        """
        # 将激光雷达数据分为左右两部分
        left_ranges = ranges[:len(ranges)//3]
        right_ranges = ranges[-len(ranges)//3:]
        
        # 计算左右两侧的平均距离
        left_avg = sum(left_ranges) / len(left_ranges)
        right_avg = sum(right_ranges) / len(right_ranges)
        
        twist = Twist()
        
        # 选择平均距离更大的一侧进行转向
        if left_avg > right_avg:
            twist.angular.z = self.turn_speed
        else:
            twist.angular.z = -self.turn_speed
        
        # 发布避障控制指令
        self.cmd_vel_publisher.publish(twist)
        self.get_logger().warn(f'检测到障碍物！正在转向避障。')
    
    def clear_path(self):
        """
        清除路径，停止机器人
        """
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_publisher.publish(twist)

def main(args=None):
    """
    主函数
    """
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
