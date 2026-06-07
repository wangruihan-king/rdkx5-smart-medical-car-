#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径规划节点
作者: [队伍名称]
日期: 2025
功能: 根据任务指令生成机器人的行驶路径（顺时针/逆时针）
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped, Point
from std_msgs.msg import String, Int32

class PathPlannerNode(Node):
    """
    路径规划节点类
    负责根据任务指令（顺时针/逆时针）生成竞赛场地的行驶路径
    """
    def __init__(self):
        """
        初始化节点，设置路径关键点
        """
        super().__init__('path_planner_node')
        
        # 订阅任务信息
        self.subscription = self.create_subscription(
            String,
            '/task_manager/task_info',
            self.task_callback,
            10
        )
        
        # 发布规划好的路径
        self.path_publisher = self.create_publisher(
            Path,
            '/path_planner/path',
            10
        )
        
        # 发布当前路点索引
        self.current_waypoint_publisher = self.create_publisher(
            Int32,
            '/path_planner/current_waypoint',
            10
        )
        
        # 存储任务信息和路径
        self.task_info = None
        self.path = None
        
        # 竞赛场地关键路径点定义
        # 起点P（发车点）
        self.POINT_P = (0.0, 0.0)
        # 任务发布点
        self.TASK_POINT = (5.0, 2.0)
        # 黄色通道入口
        self.CHANNEL_ENTRY = (5.0, 2.25)
        # 诊疗区C环形通道起点
        self.C_CHANNEL_START = (5.0, 2.5)
        # 诊疗区C环形通道终点
        self.C_CHANNEL_END = (5.0, 5.0)
        
        self.get_logger().info('路径规划节点已启动')
    
    def task_callback(self, msg):
        """
        任务信息回调函数
        接收二维码识别的任务信息，生成对应路径
        
        参数:
            msg: String消息，包含任务信息
        """
        self.task_info = msg.data
        self.get_logger().info(f'接收到任务: {self.task_info}')
        self.generate_path()
    
    def generate_path(self):
        """
        主路径生成函数
        根据任务指令选择顺时针或逆时针路径
        """
        if not self.task_info:
            return
        
        path = Path()
        path.header.frame_id = 'map'
        path.header.stamp = self.get_clock().now().to_msg()
        
        waypoints = []
        
        # 根据任务信息选择路径
        if 'clockwise' in self.task_info.lower():
            waypoints = self.get_clockwise_path()
        elif 'counterclockwise' in self.task_info.lower():
            waypoints = self.get_counterclockwise_path()
        else:
            waypoints = self.get_default_path()
        
        # 生成路径消息
        for i, (x, y) in enumerate(waypoints):
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position = Point(x=x, y=y, z=0.0)
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        
        self.path = path
        self.path_publisher.publish(path)
        self.get_logger().info(f'已生成包含{len(waypoints)}个路点的路径')
    
    def get_clockwise_path(self):
        """
        生成顺时针绕行路径
        沿着诊疗区C的黄色通道顺时针绕行
        
        返回:
            list: 路径点列表
        """
        return [
            self.POINT_P,                    # 从起点出发
            self.TASK_POINT,                 # 前往任务发布点
            self.CHANNEL_ENTRY,              # 进入黄色通道
            self.C_CHANNEL_START,            # 到达环形通道起点
            (4.5, 2.5),                     # 转向右侧
            (4.5, 5.0),                     # 向下行驶
            (0.5, 5.0),                     # 向左行驶
            (0.5, 2.5),                     # 向上行驶
            (4.5, 2.5),                     # 向右行驶
            self.C_CHANNEL_END,              # 到达环形通道终点
            self.CHANNEL_ENTRY,              # 离开黄色通道
            self.POINT_P                     # 返回起点
        ]
    
    def get_counterclockwise_path(self):
        """
        生成逆时针绕行路径
        沿着诊疗区C的黄色通道逆时针绕行
        
        返回:
            list: 路径点列表
        """
        return [
            self.POINT_P,                    # 从起点出发
            self.TASK_POINT,                 # 前往任务发布点
            self.CHANNEL_ENTRY,              # 进入黄色通道
            self.C_CHANNEL_START,            # 到达环形通道起点
            (0.5, 2.5),                     # 转向左侧
            (0.5, 5.0),                     # 向下行驶
            (4.5, 5.0),                     # 向右行驶
            (4.5, 2.5),                     # 向上行驶
            self.C_CHANNEL_END,              # 到达环形通道终点
            self.CHANNEL_ENTRY,              # 离开黄色通道
            self.POINT_P                     # 返回起点
        ]
    
    def get_default_path(self):
        """
        生成默认路径（无绕行）
        
        返回:
            list: 路径点列表
        """
        return [
            self.POINT_P,                    # 从起点出发
            self.TASK_POINT,                 # 前往任务发布点
            self.CHANNEL_ENTRY,              # 进入黄色通道
            self.C_CHANNEL_START,            # 到达环形通道起点
            self.C_CHANNEL_END,              # 到达环形通道终点
            self.CHANNEL_ENTRY,              # 离开黄色通道
            self.POINT_P                     # 返回起点
        ]

def main(args=None):
    """
    主函数
    """
    rclpy.init(args=args)
    node = PathPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
