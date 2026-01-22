"""
配置文件
"""
import os
from pathlib import Path

# 项目根目录（backend的父目录）
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/database/pcba_detection.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 文件上传配置
UPLOAD_FOLDER = BASE_DIR / 'uploads' / 'images'
RESULT_FOLDER = BASE_DIR / 'uploads' / 'results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'mp4', 'avi'}

# 模型路径
MODEL_PATH = BASE_DIR / 'models' / 'best.pt'

# 确保目录存在
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)
(BASE_DIR / 'database').mkdir(parents=True, exist_ok=True)
(BASE_DIR / 'models').mkdir(parents=True, exist_ok=True)

# Flask配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

