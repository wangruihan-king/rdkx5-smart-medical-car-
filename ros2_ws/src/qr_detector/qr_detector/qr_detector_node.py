#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码识别节点
作者: [队伍名称]
日期: 2025
功能: 使用pyzbar库解析摄像头图像中的二维码信息，获取竞赛任务指令
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
from pyzbar import pyzbar

class QRDetectorNode(Node):
    """
    二维码检测器节点类
    负责接收摄像头图像，解析二维码信息，发布任务指令
    """
    def __init__(self):
        """
        初始化节点，订阅摄像头话题，创建任务信息发布者
        """
        super().__init__('qr_detector_node')
        
        # 图像转换桥接器，用于ROS图像和OpenCV图像之间的转换
        self.bridge = CvBridge()
        
        # 存储解码后的二维码数据
        self.qr_data = None
        
        # 记录上次识别到二维码的时间（秒），用于防止重复识别
        self.last_qr_time = 0.0
        
        # 订阅摄像头原始图像话题
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        # 创建任务信息发布者，发布解码后的二维码内容
        self.publisher = self.create_publisher(
            String,
            '/qr_detector/task_info',
            10
        )
        
        self.get_logger().info('二维码检测器节点已启动')
    
    def image_callback(self, msg):
        """
        摄像头图像回调函数
        处理接收到的图像数据，检测并解码二维码
        
        参数:
            msg: Image消息，包含原始摄像头图像
        """
        try:
            # 将ROS图像消息转换为OpenCV格式的图像
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'图像转换失败: {e}')
            return
        
        # 使用pyzbar库解析图像中的二维码
        barcodes = pyzbar.decode(cv_image)
        
        # 获取当前时间戳（秒）
        current_time = self.get_clock().now().nanoseconds / 1e9
        
        # 遍历检测到的所有二维码
        for barcode in barcodes:
            # 解码二维码数据
            data = barcode.data.decode('utf-8')
            
            # 检查数据是否有效，且距离上次识别超过2秒（防止重复发布）
            if data and (current_time - self.last_qr_time > 2.0):
                self.qr_data = data
                self.last_qr_time = current_time
                
                # 创建并发布任务信息消息
                msg = String()
                msg.data = data
                self.publisher.publish(msg)
                self.get_logger().info(f'成功识别到二维码，任务信息: {data}')

def main(args=None):
    """
    主函数，初始化节点并开始运行
    """
    rclpy.init(args=args)
    node = QRDetectorNode()
    
    try:
        # 进入ROS2消息循环
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        # 清理资源
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
