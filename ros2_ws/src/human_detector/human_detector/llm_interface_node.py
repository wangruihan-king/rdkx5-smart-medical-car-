#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型图生文接口节点
作者: [队伍名称]
日期: 2025
功能: 接收人形图像，调用本地或云端大模型生成文字描述
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import requests
import base64
import os

class LLMInterfaceNode(Node):
    """
    大模型接口节点类
    负责接收裁剪后的人形图像，调用大模型进行图生文描述
    支持本地部署的大模型和云端大模型（如GPT-4o）
    """
    def __init__(self):
        """
        初始化节点，配置大模型参数
        """
        super().__init__('llm_interface_node')
        
        # 订阅裁剪后的人形图像
        self.subscription = self.create_subscription(
            String,
            '/human_detector/human_image',
            self.image_callback,
            10
        )
        
        # 发布图生文结果
        self.result_publisher = self.create_publisher(
            String,
            '/llm_interface/image_caption',
            10
        )
        
        # 加载参数：是否使用本地大模型
        self.local_llm_enabled = self.declare_parameter('local_llm_enabled', False).value
        # 本地大模型地址
        self.local_llm_url = self.declare_parameter('local_llm_url', 'http://localhost:8080').value
        # 云端大模型API密钥
        self.api_key = self.declare_parameter('api_key', '').value
        
        self.get_logger().info(f'大模型接口节点已启动，使用本地大模型: {self.local_llm_enabled}')
    
    def image_callback(self, msg):
        """
        图像回调函数
        接收base64编码的图像，调用大模型生成描述
        
        参数:
            msg: String消息，包含base64编码的图像
        """
        try:
            image_base64 = msg.data
            # 调用大模型生成描述
            caption = self.generate_caption(image_base64)
            
            # 发布图生文结果
            result_msg = String()
            result_msg.data = caption
            self.result_publisher.publish(result_msg)
            self.get_logger().info(f'成功生成图像描述: {caption}')
            
        except Exception as e:
            self.get_logger().error(f'处理图像失败: {e}')
    
    def generate_caption(self, image_base64):
        """
        生成图像描述的主函数
        根据配置选择调用本地或云端大模型
        
        参数:
            image_base64: base64编码的图像数据
            
        返回:
            str: 图像的文字描述
        """
        if self.local_llm_enabled:
            return self.call_local_llm(image_base64)
        else:
            return self.call_cloud_llm(image_base64)
    
    def call_local_llm(self, image_base64):
        """
        调用本地部署的大模型
        
        参数:
            image_base64: base64编码的图像数据
            
        返回:
            str: 图像描述
        """
        try:
            # 构造请求数据
            payload = {
                'image': image_base64,
                'prompt': '请详细描述这张图片中的人形目标。'
            }
            # 发送HTTP POST请求
            response = requests.post(
                f'{self.local_llm_url}/generate',
                json=payload,
                timeout=30
            )
            # 检查请求是否成功
            response.raise_for_status()
            # 获取返回结果
            return response.json().get('caption', '未生成描述')
        except Exception as e:
            self.get_logger().error(f'调用本地大模型失败: {e}')
            return '本地大模型不可用'
    
    def call_cloud_llm(self, image_base64):
        """
        调用云端大模型（如OpenAI GPT-4o）
        
        参数:
            image_base64: base64编码的图像数据
            
        返回:
            str: 图像描述
        """
        try:
            # 设置请求头
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 构造请求数据
            payload = {
                'model': 'gpt-4o',
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': '请详细描述这张图片。'
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{image_base64}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 500
            }
            
            # 发送HTTP POST请求
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            # 检查请求是否成功
            response.raise_for_status()
            # 获取返回结果
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            self.get_logger().error(f'调用云端大模型失败: {e}')
            return '云端大模型不可用'

def main(args=None):
    """
    主函数
    """
    rclpy.init(args=args)
    node = LLMInterfaceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('接收到键盘中断，停止运行')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
