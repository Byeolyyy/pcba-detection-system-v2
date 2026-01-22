"""
数据库模型定义
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DetectionRecord(db.Model):
    """检测记录表"""
    __tablename__ = 'detection_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    defect_name = db.Column(db.String(100), nullable=False, comment='缺陷名称')
    defect_code = db.Column(db.String(50), comment='缺陷编号')
    confidence = db.Column(db.Numeric(5, 2), nullable=False, comment='置信度(0-100)')
    x1 = db.Column(db.Integer, nullable=False, comment='左上角x坐标')
    y1 = db.Column(db.Integer, nullable=False, comment='左上角y坐标')
    x2 = db.Column(db.Integer, nullable=False, comment='右下角x坐标')
    y2 = db.Column(db.Integer, nullable=False, comment='右下角y坐标')
    image_path = db.Column(db.String(500), comment='原图路径')
    result_image_path = db.Column(db.String(500), comment='检测结果图路径')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'defect_name': self.defect_name,
            'defect_code': self.defect_code,
            'confidence': float(self.confidence),
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'image_path': self.image_path,
            'result_image_path': self.result_image_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class DefectType(db.Model):
    """缺陷类型表（可选）"""
    __tablename__ = 'defect_types'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False, comment='缺陷编号')
    name = db.Column(db.String(100), nullable=False, comment='缺陷名称')
    description = db.Column(db.Text, comment='缺陷描述')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

