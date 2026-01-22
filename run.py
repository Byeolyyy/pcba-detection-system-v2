"""
启动脚本 - 在项目根目录运行
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("PCBA智能检测系统启动中...")
    print(f"访问地址: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

