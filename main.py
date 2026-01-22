import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QProgressBar,
    QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QTextEdit,
    QFileDialog, QFrame, QListWidgetItem
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 移除: sys.path.append(r"E:/PCB/newPCB/yolov12") 
# 说明: 打包时应直接使用 pip 安装的 ultralytics 库。
# 如果 yolov12 是你自己修改过的库，你需要把那个文件夹复制到当前项目根目录。
from ultralytics import YOLO

class DetectionThread(QThread):
    update_original = pyqtSignal(QImage)
    update_frame = pyqtSignal(QImage)
    update_progress = pyqtSignal(int)
    detection_results = pyqtSignal(list)

    def __init__(self, model_path, parent=None):
        super().__init__(parent)
        # 确保路径是绝对路径，防止库加载出错
        abs_model_path = os.path.abspath(model_path)
        if not os.path.exists(abs_model_path):
            print(f"Error: Model not found at {abs_model_path}")
        
        try:
            self.model = YOLO(abs_model_path)
        except Exception as e:
            print(f"加载YOLO模型失败: {e}")
            raise
        
        self.cap = None
        self.source = None
        self.running = False

    def set_source(self, source):
        self.source = source
        self.cap = None

    def run(self):
        if self.source is None:
            return

        self.running = True
        
        # 判断是图片还是视频/摄像头
        is_image = False
        if isinstance(self.source, str):
            # 检查文件扩展名
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
            is_image = self.source.lower().endswith(image_extensions)
        
        if is_image:
            # 处理图片
            self._process_image(self.source)
        else:
            # 处理视频或摄像头
            self._process_video(self.source)
    
    def _process_image(self, image_path):
        """处理单张图片"""
        try:
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"无法读取图片: {image_path}")
                return
            
            # 显示原始图片
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if not rgb.flags['C_CONTIGUOUS']:
                    rgb = np.ascontiguousarray(rgb)
                h, w, ch = rgb.shape
                # 复制数据确保QImage有效
                rgb_copy = rgb.copy()
                original_qimg = QImage(rgb_copy.data, w, h, ch * w, QImage.Format_RGB888)
                if original_qimg.isNull():
                    print("创建原始图片QImage失败")
                    return
                # 创建QPixmap副本确保数据持久
                original_qimg = QPixmap.fromImage(original_qimg).toImage()
                self.update_original.emit(original_qimg)
            except Exception as e:
                print(f"处理原始图片时出错: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # 执行检测
            try:
                results = self.model.predict(frame, verbose=False, imgsz=640, device='cpu')
            except Exception as e:
                print(f"预测出错: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # 检查结果
            if results is None or len(results) == 0:
                print("检测结果为空")
                return
            
            try:
                annotated = results[0].plot()
                boxes = results[0].boxes
            except Exception as e:
                print(f"绘制检测结果时出错: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # 处理检测结果
            try:
                detection_data = self._extract_detection_data(boxes)
            except Exception as e:
                print(f"提取检测数据时出错: {e}")
                import traceback
                traceback.print_exc()
                detection_data = []
            
            # 显示检测结果
            try:
                if isinstance(annotated, np.ndarray):
                    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    if not annotated_rgb.flags['C_CONTIGUOUS']:
                        annotated_rgb = np.ascontiguousarray(annotated_rgb)
                    h, w, ch = annotated_rgb.shape
                    # 复制数据确保QImage有效
                    annotated_rgb_copy = annotated_rgb.copy()
                    bytes_per_line = ch * w
                    detect_qimg = QImage(annotated_rgb_copy.data, w, h, bytes_per_line, QImage.Format_RGB888)
                else:
                    # 如果是其他格式，先转换为numpy再处理
                    if hasattr(annotated, 'numpy'):
                        annotated = annotated.numpy()
                    if isinstance(annotated, np.ndarray):
                        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                        annotated_rgb_copy = annotated_rgb.copy()
                        h, w, ch = annotated_rgb_copy.shape
                        bytes_per_line = ch * w
                        detect_qimg = QImage(annotated_rgb_copy.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    else:
                        detect_qimg = QImage(annotated.data, annotated.shape[1], annotated.shape[0], annotated.strides[0], QImage.Format_RGB888).rgbSwapped()
                
                if detect_qimg.isNull():
                    print("创建检测结果QImage失败")
                    return
                
                # 创建QPixmap副本确保数据持久
                detect_qimg = QPixmap.fromImage(detect_qimg).toImage()
                
                self.update_frame.emit(detect_qimg)
                self.update_progress.emit(100)
                self.detection_results.emit(detection_data)
            except Exception as e:
                print(f"显示检测结果时出错: {e}")
                import traceback
                traceback.print_exc()
            
        except Exception as e:
            print(f"处理图片时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_video(self, source):
        """处理视频或摄像头"""
        try:
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                return
            
            # 获取视频信息
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30  # 默认帧率
            frame_delay = int(1000 / fps)  # 毫秒
            
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) if self.cap.get(cv2.CAP_PROP_FRAME_COUNT) > 0 else 0
            
            while self.running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # 显示原始帧
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if not rgb.flags['C_CONTIGUOUS']:
                    rgb = np.ascontiguousarray(rgb)
                h, w, ch = rgb.shape
                original_qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                self.update_original.emit(original_qimg)
                
                # 执行检测
                try:
                    results = self.model.predict(frame, verbose=False, imgsz=640, device='cpu')
                except Exception as e:
                    print(f"预测出错: {e}")
                    import traceback
                    traceback.print_exc()
                    continue  # 视频处理中出错继续下一帧
                
                # 检查结果
                if results is None or len(results) == 0:
                    continue
                
                annotated = results[0].plot()
                boxes = results[0].boxes
                
                # 处理检测结果
                detection_data = self._extract_detection_data(boxes)
                
                # 显示检测结果
                if isinstance(annotated, np.ndarray):
                    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    if not annotated_rgb.flags['C_CONTIGUOUS']:
                        annotated_rgb = np.ascontiguousarray(annotated_rgb)
                    h, w, ch = annotated_rgb.shape
                    bytes_per_line = ch * w
                    detect_qimg = QImage(annotated_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                else:
                    detect_qimg = QImage(annotated.data, annotated.shape[1], annotated.shape[0], annotated.strides[0], QImage.Format_RGB888).rgbSwapped()
                
                self.update_frame.emit(detect_qimg)
                
                # 更新进度
                if total_frames > 0:
                    current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                    progress = int((current_frame / total_frames) * 100)
                    self.update_progress.emit(progress)
                else:
                    self.update_progress.emit(0)
                
                self.detection_results.emit(detection_data)
                
                # 控制帧率，避免处理太快导致UI卡顿
                # 对于摄像头，使用较小的延迟；对于视频文件，可以适当加快
                if isinstance(source, int):  # 摄像头
                    delay = max(30, frame_delay // 3)
                    self.msleep(delay)
                else:  # 视频文件
                    delay = max(10, frame_delay // 5)
                    self.msleep(delay)
                
        except Exception as e:
            print(f"处理视频时出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.cap:
                self.cap.release()
    
    def _extract_detection_data(self, boxes):
        """提取检测数据"""
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
                        
                        detection_data.append({
                            'id': str(i + 1),
                            'class': class_name,
                            'confidence': f"{conf:.2f}",
                            'coordinates': f"x1:{x1}, y1:{y1}, x2:{x2}, y2:{y2}"
                        })
                    except Exception as e:
                        print(f"处理第{i}个检测框时出错: {e}")
                        continue
        except Exception as e:
            print(f"提取检测数据时出错: {e}")
            import traceback
            traceback.print_exc()
        return detection_data

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self, model_path):
        super().__init__()
        self.setWindowTitle("PCBA智能检测系统")
        self.setMinimumSize(1200, 850)
        
        # 这里的样式表保持不变，省略以节省空间...
        # (保持原有的 __init__ UI 代码不变)
        # ...
        
        # 为了完整性，这里简写 UI 部分，你需要保留你原有的 UI 代码
        self.setStyleSheet("""
            QLabel { font-size: 18px; color: #333; }
            QPushButton { font-size: 17px; padding: 8px 18px; background-color: #2B6CB0; color: white; border-radius: 6px; }
            QProgressBar { height: 24px; text-align: center; }
        """)

        self.detection_thread = DetectionThread(model_path)
        self.detection_thread.update_original.connect(self.update_original_frame)
        self.detection_thread.update_frame.connect(self.update_detection_frame)
        self.detection_thread.update_progress.connect(self.update_progress_bar)
        self.detection_thread.detection_results.connect(self.update_detection_info)

        # 初始化 UI 组件 (复制你原本的代码即可)
        self.original_label = QLabel()
        self.original_label.setFixedSize(540, 400)
        self.original_label.setStyleSheet("background-color: black;")
        self.detection_label = QLabel()
        self.detection_label.setFixedSize(540, 400)
        self.detection_label.setStyleSheet("background-color: black;")
        
        self.progress_bar = QProgressBar()
        self.id_list = QListWidget()
        self.class_list = QListWidget()
        self.confidence_text = QTextEdit()
        self.coordinates_text = QTextEdit()
        
        self.load_button = QPushButton("图片/视频检测")
        self.camera_button = QPushButton("摄像头检测")
        self.start_button = QPushButton("开始检测")
        self.stop_button = QPushButton("停止检测")

        self.load_button.clicked.connect(self.load_file)
        self.camera_button.clicked.connect(self.load_camera)
        self.start_button.clicked.connect(self.start_detection)
        self.stop_button.clicked.connect(self.stop_detection)

        # 布局代码 (简写，保留原样)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.original_label)
        top_layout.addWidget(self.detection_label)
        
        title_layout = QHBoxLayout()
        # ... (保留原本的 title layout)
        
        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.addWidget(self.id_list, 1)
        bottom_layout.addWidget(self.class_list, 3)
        bottom_layout.addWidget(self.confidence_text, 2)
        bottom_layout.addWidget(self.coordinates_text, 4)

        button_layout = QHBoxLayout()
        for btn in [self.load_button, self.camera_button, self.start_button, self.stop_button]:
            button_layout.addWidget(btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(title_layout) # 如果你之前定义了 title_layout
        main_layout.addWidget(bottom_frame)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # 保持原有的方法不变
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图像或视频", "", "Videos (*.mp4 *.avi);;Images (*.png *.jpg)")
        if file_path:
            self.detection_thread.set_source(file_path)
            # 简单的预览逻辑
            if file_path.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp')):
                image = cv2.imread(file_path)
                if image is not None:
                     rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                     # 确保数组是连续的（C风格）
                     if not rgb.flags['C_CONTIGUOUS']:
                         rgb = np.ascontiguousarray(rgb)
                     h, w, ch = rgb.shape
                     qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                     self.original_label.setPixmap(QPixmap.fromImage(qimg).scaled(self.original_label.size(), Qt.KeepAspectRatio))
            else:
                self.original_label.setText("视频已加载")

    def load_camera(self):
        self.detection_thread.set_source(0) # 0 代表第一个摄像头

    def start_detection(self):
        if self.detection_thread.source is None:
            print("请先选择图片/视频或摄像头")
            return
        if not self.detection_thread.isRunning():
            self.detection_thread.start()
        else:
            print("检测已在运行中")

    def stop_detection(self):
        self.detection_thread.stop()

    def update_original_frame(self, image):
        self.original_label.setPixmap(QPixmap.fromImage(image).scaled(self.original_label.size(), Qt.KeepAspectRatio))

    def update_detection_frame(self, image):
        self.detection_label.setPixmap(QPixmap.fromImage(image).scaled(self.detection_label.size(), Qt.KeepAspectRatio))

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def update_detection_info(self, results):
        try:
            self.id_list.clear()
            self.class_list.clear()
            self.confidence_text.clear()
            self.coordinates_text.clear()
            
            if results:
                for result in results:
                    try:
                        self.id_list.addItem(result.get('id', ''))
                        self.class_list.addItem(f"{result.get('id', '')}. {result.get('class', '')}")
                        self.confidence_text.append(result.get('confidence', ''))
                        self.coordinates_text.append(result.get('coordinates', ''))
                    except Exception as e:
                        print(f"更新检测信息时出错: {e}")
                        continue
        except Exception as e:
            print(f"更新检测信息列表时出错: {e}")
            import traceback
            traceback.print_exc()

    def closeEvent(self, event):
        self.stop_detection()
        event.accept()

# ==========================================
# 关键修改部分：自动判断路径
# ==========================================
def get_base_path():
    """获取程序运行的基础路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe，路径为 exe 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是源码运行，路径为当前脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # 强制设置 Qt 兼容性
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    app = QApplication(sys.argv)
    
    # 1. 获取当前基础路径
    base_dir = get_base_path()
    
    # 2. 拼接模型路径 (假设 best.pt 就在 exe 旁边)
    model_name = "best.pt"
    model_path = os.path.join(base_dir, model_name)
    
    # 打印路径方便调试
    print(f"Loading model from: {model_path}")

    # 3. 检查模型是否存在，不存在则提示
    if not os.path.exists(model_path):
        # 这里用 Qt 弹窗提示，或者直接打印
        print(f"Error: {model_name} not found in {base_dir}")
        # 为了防止闪退，你可以选择不退出，或者在这里抛出错误
    
    window = MainWindow(model_path)
    window.show()
    sys.exit(app.exec_())
