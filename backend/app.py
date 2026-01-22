"""
Flask主应用
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.config import SQLALCHEMY_DATABASE_URI, BASE_DIR
from backend.models import db
from backend.routes import api

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                static_folder=str(BASE_DIR / 'frontend'),
                static_url_path='')
    
    # 配置
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)  # 允许跨域请求
    
    # 注册蓝图
    app.register_blueprint(api, url_prefix='/api')
    
    # 前端路由
    @app.route('/')
    def index():
        return send_from_directory(str(BASE_DIR / 'frontend'), 'index.html')
    
    @app.route('/history')
    def history():
        return send_from_directory(str(BASE_DIR / 'frontend'), 'history.html')
    
    # 初始化数据库
    with app.app_context():
        db.create_all()
        print("数据库初始化完成")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

