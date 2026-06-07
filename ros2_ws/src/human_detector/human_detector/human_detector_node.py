#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人形检测节点
作者: [队伍名称]
日期: 2025
功能: 使用YOLOv8模型检测摄像头图像中的人形目标
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
import base64
import json

class HumanDetectorNode(Node):
    """
    人形检测器节点类
    负责检测摄像头图像，识别人形目标，裁剪并发送给大模型进行图生文
    """
    def __init__(self):
        """
        初始化节点，加载YOLO模型，订阅摄像头图像
        """
        super().__init__('human_detector_node')
        
        # 图像转换桥接器
        self.bridge = CvBridge()
        
        # 加载YOLOv8n模型，用于目标检测
        self.model = YOLO('yolov8n.pt')
        
        # 记录上次检测到人形的时间
        self.last_detection_time = 0.0
        
        # 检测间隔（秒），避免频繁检测
        self.detection_interval = 2.0
        
        # 订阅摄像头图像
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        # 发布裁剪后的人形图像（base64编码）
        self.human_image_publisher = self.create_publisher(
            String,
            '/human_detector/human_image',
            10
        )
        
        # 发布检测结果（位置和置信度
        self.detection_publisher = self.create_publisher(
            String,
            '/human_detector/detection_result',
            10
        )
        
        self.get_logger().info('人形检测器节点已启动，YOLOv8模型已加载')
    
    def image_callback(self, msg):
        """
        摄像头图像回调函数
        使用YOLO检测图像，识别人形目标
        
        参数:
            msg: Image消息
        """
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'图像转换失败: {e}')
            return
        
        current_time = self.get_clock().now().nanoseconds / 1e9
        
        # 检查是否达到检测间隔，避免频繁检测
        if current_time - self.last_detection_time < self.detection_interval:
            return
        
        # 使用YOLO模型进行目标检测
        results = self.model(cv_image)
        
        # 遍历检测结果
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # 获取类别ID和置信度
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # 类别0是person，且置信度大于0.5才算有效检测
                if class_id == 0 and confidence > 0.5:
                    self.last_detection_time = current_time
                    
                    # 获取检测框坐标
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # 裁剪出人形区域
                    human_crop = cv_image[y1:y2, x1:x2]
                    
                    # 将裁剪后的图像编码为base64字符串
                    _, img_encoded = cv2.imencode('.jpg', human_crop)
                    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
                    
                    # 创建检测结果消息（JSON格式）
                    detection_msg = String()
                    detection_msg.data = json.dumps({
                        'confidence': confidence,
                        'bbox': [x1, y1, x2, y2],
                        'timestamp': current_time
                    })
                    self.detection_publisher.publish(detection_msg)
                    
                    # 发布base64编码的图像
                    image_msg = String()
                    image_msg.data = img_base64
                    self.human_image_publisher.publish(image_msg)
                    
                    self.get_logger().info(f'成功检测到人形，置信度: {confidence:.2f}')
                    break

def main(args=None):
    """
    主函数
    """
    rclpy.init(args=args)
    node = HumanDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
