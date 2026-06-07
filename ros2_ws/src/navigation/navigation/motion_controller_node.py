#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运动控制节点
作者: [队伍名称]
日期: 2025
功能: 实现路径跟踪控制，驱动机器人沿规划路径行驶
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped, Point
from nav_msgs.msg import Path
from std_msgs.msg import Bool, Int32
import math

class MotionControllerNode(Node):
    """
    运动控制节点类
    负责接收规划路径，计算控制指令，驱动机器人行驶
    """
    def __init__(self):
        """
        初始化节点，设置控制参数
        """
        super().__init__('motion_controller_node')
        
        # 订阅规划路径
        self.path_subscription = self.create_subscription(
            Path,
            '/path_planner/path',
            self.path_callback,
            10
        )
        
        # 订阅障碍物检测状态
        self.obstacle_subscription = self.create_subscription(
            Bool,
            '/obstacle_detected',
            self.obstacle_callback,
            10
        )
        
        # 订阅避障控制指令
        self.cmd_vel_obstacle_subscription = self.create_subscription(
            Twist,
            '/cmd_vel_obstacle',
            self.cmd_vel_obstacle_callback,
            10
        )
        
        # 发布机器人控制指令
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        # 发布当前路点索引
        self.current_waypoint_publisher = self.create_publisher(
            Int32,
            '/motion_controller/current_waypoint',
            10
        )
        
        # 存储路径和当前路点
        self.path = None
        self.current_waypoint = 0
        
        # 障碍物检测相关
        self.obstacle_detected = False
        self.obstacle_cmd_vel = Twist()
        
        # 控制参数
        # 目标位置容差（米）
        self.target_position_tolerance = 0.3
        # 最大线速度（米/秒）
        self.max_speed = 0.5
        # 最大角速度（弧度/秒）
        self.max_angular_speed = 1.0
        # 线速度比例系数
        self.kp_linear = 0.5
        # 角速度比例系数
        self.kp_angular = 1.0
        
        # 创建定时器，100Hz控制循环
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info('运动控制节点已启动')
    
    def path_callback(self, msg):
        """
        路径接收回调函数
        
        参数:
            msg: Path消息，包含规划路径
        """
        self.path = msg
        self.current_waypoint = 0
        self.get_logger().info(f'接收到新路径，包含{len(msg.poses)}个路点')
    
    def obstacle_callback(self, msg):
        """
        障碍物检测状态回调函数
        
        参数:
            msg: Bool消息，是否检测到障碍物
        """
        self.obstacle_detected = msg.data
    
    def cmd_vel_obstacle_callback(self, msg):
        """
        避障控制指令回调函数
        
        参数:
            msg: Twist消息，避障控制指令
        """
        self.obstacle_cmd_vel = msg
    
    def control_loop(self):
        """
        主控制循环（100Hz）
        计算控制指令，发布机器人运动控制
        """
        # 如果没有路径或路径已经走完，停止机器人
        if self.path is None or self.current_waypoint >= len(self.path.poses):
            self.stop()
            return
        
        # 如果检测到障碍物，执行避障控制
        if self.obstacle_detected:
            self.cmd_vel_publisher.publish(self.obstacle_cmd_vel)
            return
        
        # 获取当前目标路点
        target_pose = self.path.poses[self.current_waypoint]
        target_x = target_pose.pose.position.x
        target_y = target_pose.pose.position.y
        
        # 当前机器人位置（这里简化为原点，实际应从里程计获取）
        current_x = 0.0
        current_y = 0.0
        current_yaw = 0.0
        
        # 计算到目标的距离和角度
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        # 如果到达目标，切换到下一个路点
        if distance < self.target_position_tolerance:
            self.current_waypoint += 1
            self.current_waypoint_publisher.publish(Int32(data=self.current_waypoint))
            
            # 检查是否走完所有路点
            if self.current_waypoint >= len(self.path.poses):
                self.stop()
                self.get_logger().info('路径已完成')
            return
        
        # 计算目标航向角
        target_yaw = math.atan2(dy, dx)
        yaw_error = target_yaw - current_yaw
        # 角度归一化到[-π, π]
        yaw_error = math.atan2(math.sin(yaw_error), math.cos(yaw_error))
        
        # 计算控制指令（P控制）
        twist = Twist()
        # 线速度与距离成正比，不超过最大值
        twist.linear.x = min(self.kp_linear * distance, self.max_speed)
        # 角速度与角度误差成正比
        twist.angular.z = self.kp_angular * yaw_error
        
        # 当角度误差较大时，降低线速度，先转向
        if abs(yaw_error) > 0.3:
            twist.linear.x *= 0.3
        
        # 发布控制指令
        self.cmd_vel_publisher.publish(twist)
    
    def stop(self):
        """
        停止机器人
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
    node = MotionControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
