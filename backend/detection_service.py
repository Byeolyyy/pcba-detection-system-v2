"""
检测服务 - 复用现有检测逻辑
"""
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import sys
import os

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'best.pt'


class DetectionService:
    """检测服务类"""
    
    def __init__(self):
        """初始化检测模型"""
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载YOLO模型"""
        try:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(f"模型文件不存在: {MODEL_PATH}")
            self.model = YOLO(str(MODEL_PATH))
            print(f"模型加载成功: {MODEL_PATH}")
        except Exception as e:
            print(f"加载模型失败: {e}")
            raise
    
    def detect_image(self, image_path, save_result=True, result_path=None):
        """
        检测图片
        
        Args:
            image_path: 图片路径
            save_result: 是否保存检测结果图
            result_path: 结果图保存路径
            
        Returns:
            dict: {
                'success': bool,
                'detections': list,  # 检测结果列表
                'result_image_path': str,  # 结果图路径
                'error': str  # 错误信息
            }
        """
        try:
            # 读取图片
            frame = cv2.imread(str(image_path))
            if frame is None:
                return {
                    'success': False,
                    'detections': [],
                    'result_image_path': None,
                    'error': f'无法读取图片: {image_path}'
                }
            
            # 执行检测
            results = self.model.predict(frame, verbose=False, imgsz=640, device='cpu')
            
            if results is None or len(results) == 0:
                return {
                    'success': False,
                    'detections': [],
                    'result_image_path': None,
                    'error': '检测结果为空'
                }
            
            # 处理检测结果
            boxes = results[0].boxes
            detections = self._extract_detection_data(boxes)
            
            # 绘制检测结果
            annotated = results[0].plot()
            
            # 保存结果图
            result_image_path = None
            if save_result:
                if result_path is None:
                    result_path = BASE_DIR / 'uploads' / 'results' / f"result_{Path(image_path).stem}.jpg"
                
                # 确保是BGR格式保存
                if isinstance(annotated, np.ndarray):
                    cv2.imwrite(str(result_path), annotated)
                    result_image_path = str(result_path)
            
            return {
                'success': True,
                'detections': detections,
                'result_image_path': result_image_path,
                'error': None
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'detections': [],
                'result_image_path': None,
                'error': str(e)
            }
    
    def _extract_detection_data(self, boxes):
        """
        提取检测数据
        
        Args:
            boxes: YOLO检测框对象
            
        Returns:
            list: 检测结果列表
        """
        detection_data = []
        try:
            if boxes is not None and len(boxes) > 0:
                for i in range(len(boxes)):
                    try:
                        # 正确访问类别ID
                        cls_val = boxes.cls[i]
                        if hasattr(cls_val, 'item'):
                            cls_id = int(cls_val.item())
                        elif hasattr(cls_val, 'cpu'):
                            cls_id = int(cls_val.cpu().item())
                        else:
                            cls_id = int(cls_val)
                        
                        # 正确访问置信度
                        conf_val = boxes.conf[i]
                        if hasattr(conf_val, 'item'):
                            conf = float(conf_val.item())
                        elif hasattr(conf_val, 'cpu'):
                            conf = float(conf_val.cpu().item())
                        else:
                            conf = float(conf_val)
                        
                        # 正确访问坐标
                        xyxy = boxes.xyxy[i]
                        if hasattr(xyxy, 'cpu'):
                            xyxy = xyxy.cpu().numpy()
                        elif hasattr(xyxy, 'numpy'):
                            xyxy = xyxy.numpy()
                        x1, y1, x2, y2 = map(int, xyxy)
                        
                        # 安全获取类别名称
                        class_name = self.model.names[cls_id] if self.model.names and cls_id in self.model.names else str(cls_id)
                        
                        # 生成缺陷编号（使用类别ID）
                        defect_code = f"DEFECT_{cls_id:03d}"
                        
                        detection_data.append({
                            'defect_name': class_name,
                            'defect_code': defect_code,
                            'confidence': round(conf * 100, 2),  # 转换为百分比
                            'x1': x1,
                            'y1': y1,
                            'x2': x2,
                            'y2': y2
                        })
                    except Exception as e:
                        print(f"处理第{i}个检测框时出错: {e}")
                        continue
        except Exception as e:
            print(f"提取检测数据时出错: {e}")
            import traceback
            traceback.print_exc()
        
        return detection_data


# 全局检测服务实例
detection_service = DetectionService()

