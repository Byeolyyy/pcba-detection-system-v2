# PCBA智能缺陷检测系统

基于YOLO的PCBA缺陷检测全栈Web应用系统。

🌐 **在线访问**：[点击这里访问系统](https://YOUR_USERNAME.github.io/pcba-detection-system/)

📖 **部署文档**：查看 [部署步骤详细版.md](./部署步骤详细版.md)

## 功能特性

- ✅ 图片上传和实时检测
- ✅ 检测结果可视化展示
- ✅ 检测历史记录管理
- ✅ 缺陷统计和分析
- ✅ 数据库存储检测结果

## 技术栈

### 后端
- Flask - Web框架
- SQLAlchemy - ORM
- SQLite - 数据库
- Ultralytics YOLO - 目标检测
- OpenCV - 图像处理

### 前端
- HTML5/CSS3/JavaScript
- Bootstrap 5 - UI框架
- Fetch API - HTTP请求

## 项目结构

```
pcba-detection-system/
├── backend/              # 后端代码
│   ├── app.py           # Flask主应用
│   ├── models.py        # 数据库模型
│   ├── routes.py        # API路由
│   ├── detection_service.py  # 检测服务
│   └── config.py        # 配置文件
├── frontend/            # 前端代码
│   ├── index.html       # 主页面
│   ├── history.html     # 历史记录页
│   ├── css/             # 样式文件
│   └── js/              # JavaScript文件
├── database/            # 数据库文件
├── models/              # YOLO模型文件
│   └── best.pt          # 训练好的模型
├── uploads/             # 上传文件目录
│   ├── images/          # 原图
│   └── results/         # 检测结果图
└── requirements.txt     # Python依赖
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备模型文件

将训练好的YOLO模型文件 `best.pt` 放到 `models/` 目录下。

### 3. 运行后端服务

```bash
cd backend
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 4. 访问前端

打开浏览器访问 `http://localhost:5000`

## API接口

### 检测接口
- `POST /api/detect` - 上传图片进行检测

### 记录接口
- `GET /api/records` - 获取检测记录列表
- `GET /api/records/<id>` - 获取单条记录
- `DELETE /api/records/<id>` - 删除记录

### 统计接口
- `GET /api/statistics` - 获取统计信息

## 数据库

使用SQLite数据库，数据库文件位于 `database/pcba_detection.db`

### 表结构

**detection_records** - 检测记录表
- id: 主键
- defect_name: 缺陷名称
- defect_code: 缺陷编号
- confidence: 置信度
- x1, y1, x2, y2: 坐标
- image_path: 原图路径
- result_image_path: 结果图路径
- created_at: 创建时间

## 部署

### 本地部署
直接运行 `python backend/app.py` 即可

### 生产部署
推荐使用以下平台：
- **Railway** - 免费额度，易于部署
- **Render** - 免费方案
- **Heroku** - 需要信用卡

前端可以部署到：
- **GitHub Pages** - 免费静态网站托管

## 注意事项

1. 确保模型文件 `best.pt` 存在于 `models/` 目录
2. 首次运行会自动创建数据库
3. 上传的图片会保存在 `uploads/` 目录
4. 建议在生产环境中使用PostgreSQL替代SQLite

## 许可证

MIT License

## 作者

PCBA检测系统开发团队

