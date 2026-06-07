#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理主节点
作者: [队伍名称]
日期: 2025
功能: 协调整个竞赛任务流程，监控任务状态，管理时间
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Int32
from geometry_msgs.msg import Twist
import time

class TaskManagerNode(Node):
    """
    任务管理节点类
    负责协调整个竞赛流程：任务1前往任务点 -> 任务2执行任务 -> 任务3返回起点 -> 完成
    """
    def __init__(self):
        """
        初始化节点，设置发布者和订阅者
        """
        super().__init__('task_manager_node')
        
        # 任务状态变量
        self.task_info = None              # 二维码任务信息
        self.current_task = 0              # 当前任务阶段（0:待机,1:前往任务点,2:执行任务,3:返回起点,4:完成）
        self.human_detected = False        # 是否检测到人形
        self.image_caption = None          # 大模型描述
        self.path_completed = False        # 路径是否完成
        self.current_waypoint = 0          # 当前路点
        self.task_start_time = None        # 阶段开始时间
        
        # 订阅二维码识别结果
        self.qr_subscription = self.create_subscription(
            String,
            '/qr_detector/task_info',
            self.qr_callback,
            10
        )
        
        # 订阅人形检测结果
        self.human_subscription = self.create_subscription(
            String,
            '/human_detector/detection_result',
            self.human_callback,
            10
        )
        
        # 订阅大模型描述结果
        self.caption_subscription = self.create_subscription(
            String,
            '/llm_interface/image_caption',
            self.caption_callback,
            10
        )
        
        # 订阅运动控制路点
        self.path_subscription = self.create_subscription(
            Int32,
            '/motion_controller/current_waypoint',
            self.path_callback,
            10
        )
        
        # 发布任务信息给路径规划
        self.task_info_publisher = self.create_publisher(
            String,
            '/task_manager/task_info',
            10
        )
        
        # 发布任务状态
        self.status_publisher = self.create_publisher(
            String,
            '/task_manager/status',
            10
        )
        
        # 发布控制指令（用于紧急停止）
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        # 创建定时器，1Hz任务状态监控
        self.timer = self.create_timer(1.0, self.task_loop)
        
        # 比赛时间管理
        self.start_time = None
        self.max_time = 180  # 3分钟
        
        self.get_logger().info('任务管理节点已启动')
        self.publish_status('系统就绪，等待发车指令')
    
    def qr_callback(self, msg):
        """
        二维码识别回调函数
        
        参数:
            msg: String消息，任务信息
        """
        if self.current_task == 1:  # 只有在任务1阶段才处理
            self.task_info = msg.data
            self.get_logger().info(f'接收到任务：{self.task_info}')
            self.publish_status(f'任务获取成功：{self.task_info}')
            # 转发任务信息给路径规划
            self.task_info_publisher.publish(msg)
            # 切换到任务2阶段
            self.current_task = 2
            self.task_start_time = time.time()
            self.get_logger().info('切换到任务2：执行任务')
    
    def human_callback(self, msg):
        """
        人形检测回调函数
        
        参数:
            msg: String消息，检测结果
        """
        if self.current_task == 2:  # 任务2阶段才记录
            self.human_detected = True
            self.get_logger().info('检测到人形目标')
    
    def caption_callback(self, msg):
        """
        大模型描述回调函数
        
        参数:
            msg: String消息，图像描述
        """
        if self.current_task == 2 and self.human_detected:
            self.image_caption = msg.data
            self.publish_status(f'人物识别结果：{msg.data}')
            self.get_logger().info(f'图像描述：{msg.data}')
    
    def path_callback(self, msg):
        """
        运动控制路点回调函数
        
        参数:
            msg: Int32消息，当前路点索引
        """
        if self.current_task >= 1:
            self.current_waypoint = msg.data
            # 检查是否走完路径（简化判断，实际应根据总路点数）
            # 这里可以根据需要调整路径完成逻辑
            if self.current_task == 2 and self.current_waypoint > 8:
                self.current_task = 3  # 切换到任务3：返回起点
                self.task_start_time = time.time()
                self.get_logger().info('切换到任务3：返回起点')
    
    def task_loop(self):
        """
        主任务状态监控循环（1Hz）
        """
        # 如果比赛未开始，不处理
        if self.start_time is None:
            return
        
        # 检查比赛时间
        elapsed = time.time() - self.start_time
        if elapsed >= self.max_time:
            self.publish_status('时间到，比赛结束')
            self.stop_robot()
            return
        
        # 根据当前任务阶段发布状态
        if self.current_task == 0:
            self.publish_status('系统待机中')
        elif self.current_task == 1:
            self.publish_status('正在前往任务发布点...')
        elif self.current_task == 2:
            self.publish_status('正在执行任务，请等待...')
        elif self.current_task == 3:
            self.publish_status('正在返回起点...')
            # 简化判断：到达某个路点后认为完成
            if self.current_waypoint > 10:
                self.current_task = 4
                self.get_logger().info('切换到任务4：任务完成')
        elif self.current_task == 4:
            total_time = time.time() - self.start_time
            self.publish_status(f'任务完成！总用时：{total_time:.2f}秒')
            self.stop_robot()
    
    def start_task(self):
        """
        开始比赛任务
        """
        self.start_time = time.time()
        self.current_task = 1
        self.task_start_time = time.time()
        self.publish_status('比赛开始，正在前往任务发布点')
        self.get_logger().info('竞赛任务已启动')
    
    def stop_robot(self):
        """
        停止机器人
        """
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_publisher.publish(twist)
    
    def publish_status(self, status):
        """
        发布任务状态信息
        
        参数:
            status: 状态文本
        """
        msg = String()
        msg.data = status
        self.status_publisher.publish(msg)

def main(args=None):
    """
    主函数
    """
    rclpy.init(args=args)
    node = TaskManagerNode()
    
    # 自动开始任务（实际可以通过外部消息触发）
    node.start_task()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
