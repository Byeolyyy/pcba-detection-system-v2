"""
API路由
"""
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import os
import sys

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.models import db, DetectionRecord
from backend.detection_service import detection_service

# 配置路径
UPLOAD_FOLDER = BASE_DIR / 'uploads' / 'images'
RESULT_FOLDER = BASE_DIR / 'uploads' / 'results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'mp4', 'avi'}

api = Blueprint('api', __name__)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/detect', methods=['POST'])
def detect_image():
    """
    上传图片进行检测
    
    Request:
        - file: 图片文件 (multipart/form-data)
    
    Response:
        {
            'success': bool,
            'message': str,
            'data': {
                'record_id': int,
                'detections': list,
                'result_image_url': str
            }
        }
    """
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有上传文件',
                'data': None
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件名为空',
                'data': None
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'不支持的文件类型，支持的类型: {", ".join(ALLOWED_EXTENSIONS)}',
                'data': None
            }), 400
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = UPLOAD_FOLDER / filename
        file.save(str(file_path))
        
        # 执行检测
        result_filename = f"result_{timestamp}_{Path(file.filename).stem}.jpg"
        result_path = RESULT_FOLDER / result_filename
        
        detection_result = detection_service.detect_image(
            file_path,
            save_result=True,
            result_path=result_path
        )
        
        if not detection_result['success']:
            return jsonify({
                'success': False,
                'message': f"检测失败: {detection_result['error']}",
                'data': None
            }), 500
        
        # 保存检测记录到数据库
        records = []
        for detection in detection_result['detections']:
            record = DetectionRecord(
                defect_name=detection['defect_name'],
                defect_code=detection['defect_code'],
                confidence=detection['confidence'],
                x1=detection['x1'],
                y1=detection['y1'],
                x2=detection['x2'],
                y2=detection['y2'],
                image_path=str(file_path.relative_to(UPLOAD_FOLDER.parent)),
                result_image_path=str(result_path.relative_to(RESULT_FOLDER.parent)) if detection_result['result_image_path'] else None
            )
            db.session.add(record)
            records.append(record)
        
        db.session.commit()
        
        # 返回结果
        return jsonify({
            'success': True,
            'message': '检测完成',
            'data': {
                'record_ids': [r.id for r in records],
                'detections': detection_result['detections'],
                'result_image_url': f"/api/result/{result_filename}" if detection_result['result_image_path'] else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


@api.route('/records', methods=['GET'])
def get_records():
    """
    获取所有检测记录
    
    Query Parameters:
        - page: 页码 (默认1)
        - per_page: 每页数量 (默认20)
        - defect_name: 缺陷名称筛选
        - defect_code: 缺陷编号筛选
    
    Response:
        {
            'success': bool,
            'data': {
                'records': list,
                'total': int,
                'page': int,
                'per_page': int
            }
        }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        defect_name = request.args.get('defect_name', None)
        defect_code = request.args.get('defect_code', None)
        
        query = DetectionRecord.query
        
        # 筛选
        if defect_name:
            query = query.filter(DetectionRecord.defect_name.like(f'%{defect_name}%'))
        if defect_code:
            query = query.filter(DetectionRecord.defect_code == defect_code)
        
        # 排序（最新的在前）
        query = query.order_by(DetectionRecord.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'records': [record.to_dict() for record in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}',
            'data': None
        }), 500


@api.route('/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    """
    获取单条检测记录
    
    Response:
        {
            'success': bool,
            'data': dict
        }
    """
    try:
        record = DetectionRecord.query.get_or_404(record_id)
        return jsonify({
            'success': True,
            'data': record.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'记录不存在: {str(e)}',
            'data': None
        }), 404


@api.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """
    删除检测记录
    
    Response:
        {
            'success': bool,
            'message': str
        }
    """
    try:
        record = DetectionRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '删除成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500


@api.route('/statistics', methods=['GET'])
def get_statistics():
    """
    获取统计信息
    
    Response:
        {
            'success': bool,
            'data': {
                'total_records': int,
                'defect_types': dict,
                'avg_confidence': float
            }
        }
    """
    try:
        from sqlalchemy import func
        
        # 总记录数
        total_records = DetectionRecord.query.count()
        
        # 缺陷类型统计
        defect_stats = db.session.query(
            DetectionRecord.defect_name,
            func.count(DetectionRecord.id).label('count'),
            func.avg(DetectionRecord.confidence).label('avg_confidence')
        ).group_by(DetectionRecord.defect_name).all()
        
        defect_types = {
            stat.defect_name: {
                'count': stat.count,
                'avg_confidence': float(stat.avg_confidence) if stat.avg_confidence else 0
            }
            for stat in defect_stats
        }
        
        # 平均置信度
        avg_conf = db.session.query(func.avg(DetectionRecord.confidence)).scalar()
        avg_confidence = float(avg_conf) if avg_conf else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_records': total_records,
                'defect_types': defect_types,
                'avg_confidence': round(avg_confidence, 2)
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'统计失败: {str(e)}',
            'data': None
        }), 500


@api.route('/result/<filename>', methods=['GET'])
def get_result_image(filename):
    """获取检测结果图片"""
    try:
        return send_from_directory(str(RESULT_FOLDER), filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'图片不存在: {str(e)}'
        }), 404


@api.route('/image/<filename>', methods=['GET'])
def get_original_image(filename):
    """获取原始图片"""
    try:
        return send_from_directory(str(UPLOAD_FOLDER), filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'图片不存在: {str(e)}'
        }), 404

