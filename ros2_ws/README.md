# OriginCar 智慧医疗竞赛方案

## 项目结构

```
ros2_ws/
├── src/
│   ├── qr_detector/          # 二维码识别功能包
│   ├── human_detector/       # 人形检测与大模型接口
│   ├── navigation/           # 导航与避障功能包
│   ├── voice_output/         # 语音播报功能包
│   └── task_manager/         # 任务管理主节点
├── install_dependencies.sh   # 依赖安装脚本
└── README.md                 # 项目说明
```

## 功能模块

### 1. 二维码识别 (qr_detector)
- 使用 pyzbar 库进行二维码解码
- 发布任务信息到 `/qr_detector/task_info` 话题

### 2. 人形检测与大模型接口 (human_detector)
- 使用 YOLOv8 进行人形检测
- 支持本地大模型和云端大模型（如 GPT-4o）
- 将检测到的人形图像发送给大模型进行图生文
- 发布识别结果到 `/llm_interface/image_caption` 话题

### 3. 导航与避障 (navigation)
- 激光雷达避障
- 路径规划（支持顺时针/逆时针）
- 运动控制

### 4. 语音播报 (voice_output)
- 支持任务信息播报
- 支持人形识别结果播报
- 支持任务状态播报

### 5. 任务管理 (task_manager)
- 协调整个竞赛任务流程
- 任务状态管理
- 时间管理

## 启动命令

### 启动完整竞赛系统
```bash
ros2 launch task_manager competition.launch.py
```

### 启动单个功能包
```bash
ros2 launch qr_detector qr_detector.launch.py
ros2 launch human_detector human_detector.launch.py
ros2 launch navigation navigation.launch.py
ros2 launch voice_output voice_output.launch.py
ros2 launch task_manager task_manager.launch.py
```

## 参数配置

### 导航参数 (navigation/config/navigation_params.yaml)
- `safety_distance`: 安全距离（默认 0.5m）
- `max_speed`: 最大速度（默认 0.5m/s）
- `target_position_tolerance`: 目标位置容差（默认 0.3m）

### 大模型参数
- `local_llm_enabled`: 是否启用本地大模型
- `local_llm_url`: 本地大模型地址
- `api_key`: 云端大模型 API 密钥

## 竞赛任务流程

1. **子任务1**: 车模从发车点(P)出发，前往任务发布点扫描二维码获取任务
2. **子任务2**: 根据任务要求（顺时针/逆时针）沿黄色通道行驶，检测人形立牌并进行图生文
3. **子任务3**: 返回发车点(P)完成任务

## 依赖安装

```bash
bash install_dependencies.sh
```

## 硬件要求

- OriginCar 系列智能机器人套件
- RDK X3/X5/S100 主控板
- 单线TOF激光雷达（VP100L/轮趣N10）
- 深度相机（光鉴aurora930）
- 单目相机
