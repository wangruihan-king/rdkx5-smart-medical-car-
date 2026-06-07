#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音播报节点
作者: [队伍名称]
日期: 2025
功能: 将任务信息、检测结果等通过语音播报出来
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os
import platform

class VoiceOutputNode(Node):
    """
    语音播报节点类
    负责接收各种信息，通过TTS引擎播报出来
    """
    def __init__(self):
        """
        初始化节点，订阅需要播报的话题
        """
        super().__init__('voice_output_node')
        
        # 订阅二维码识别的任务信息
        self.qr_subscription = self.create_subscription(
            String,
            '/qr_detector/task_info',
            self.qr_callback,
            10
        )
        
        # 订阅大模型生成的图像描述
        self.llm_subscription = self.create_subscription(
            String,
            '/llm_interface/image_caption',
            self.llm_callback,
            10
        )
        
        # 订阅任务管理节点的状态信息
        self.task_subscription = self.create_subscription(
            String,
            '/task_manager/status',
            self.task_callback,
            10
        )
        
        self.get_logger().info('语音播报节点已启动')
    
    def qr_callback(self, msg):
        """
        二维码信息回调函数
        播报任务信息
        
        参数:
            msg: String消息，任务信息
        """
        text = f'任务信息：{msg.data}'
        self.speak(text)
    
    def llm_callback(self, msg):
        """
        大模型描述回调函数
        播报人形检测和描述结果
        
        参数:
            msg: String消息，图像描述
        """
        text = f'检测到人物：{msg.data}'
        self.speak(text)
    
    def task_callback(self, msg):
        """
        任务状态回调函数
        播报任务执行状态
        
        参数:
            msg: String消息，状态信息
        """
        self.speak(msg.data)
    
    def speak(self, text):
        """
        语音播报核心函数
        根据不同平台选择合适的TTS引擎
        
        参数:
            text: 要播报的文本
        """
        try:
            # Linux系统使用espeak
            if platform.system() == 'Linux':
                os.system(f'espeak "{text}"')
            # Windows系统使用System.Speech
            elif platform.system() == 'Windows':
                os.system(f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"')
            else:
                self.get_logger().warn(f'{platform.system()}平台暂不支持语音播报')
        except Exception as e:
            self.get_logger().error(f'语音播报失败: {e}')

def main(args=None):
    """
    主函数
    """
    rclpy.init(args=args)
    node = VoiceOutputNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
