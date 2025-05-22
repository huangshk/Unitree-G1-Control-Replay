import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QGridLayout,QLabel,QVBoxLayout
from .inspire_hand_defaut import *
import colorcet  # 确保安装 colorcet 库
import numpy as np
import time

class ImageTab(QWidget):
    def __init__(self,datas=data_sheet):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)  
        
        self.grid_layout=QGridLayout()   
        self.layout.addLayout(self.grid_layout)   
        self.data_sheet=datas
        
        self.create_images()

    def create_images(self):
        num_cols = 4  # 每行的列数
        num_rows = (len(data_sheet) + num_cols - 1) // num_cols  # 计算行数
        self.plots = []
        self.color_maps = []
        self.color_bars = []
        for i, (name, addr, length, size, var) in enumerate(self.data_sheet):
                
            row = i // num_cols  # 计算当前行
            col = i % num_cols  # 计算当前列            # 创建随机大小的图像数据
            # width = random.randint(50, 100)
            # height = random.randint(50, 150)
            # image_data = np.random.rand(height, width)  # 生成二维图像数据

            # 创建图形布局窗口
            layout_widget = pg.GraphicsLayoutWidget(show=True)
            plot_item = layout_widget.addPlot(row=0, col=0)
            # 为图块设置名字
            plot_item.setTitle(name)
            img_item = pg.ImageItem(np.random.rand(size[0],size[1]))
            plot_item.addItem(img_item)
            self.plots.append(img_item)

            # 创建颜色映射
            color_map = pg.ColorMap(pos=np.linspace(0, 1, 256), color=colorcet.fire[:256])
            self.color_maps.append(color_map)

            # 创建颜色条
            color_bar = pg.ColorBarItem(colorMap=color_map, values=(0, 1), width=5, orientation='h')
            self.color_bars.append(color_bar)
            layout_widget.addItem(color_bar, row=1, col=0)

            # 将图形布局添加到网格
            self.grid_layout.addWidget(layout_widget, row, col)
    def update_plot(self,data_dict):
        for i, (name, addr, length, size,var) in enumerate(self.data_sheet):
            self.plots[i].setImage(data_dict[var], autoLevels=True)  # 更新图像数据
            max_val = np.max(data_dict[var])
            self.plots[i].setLevels((0, max_val))  # 设置图像颜色范围
            # 更新颜色条
            self.color_bars[i].setLevels((0, max_val))  # 更新颜色条的范围
            self.plots[i].setColorMap(self.color_maps[i])  # 设置颜色映射

class CurveTab(QWidget):
    def __init__(self,datas=data_sheet,history_len=100):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)  
        
        self.grid_layout=QGridLayout()   
        self.layout.addLayout(self.grid_layout)   
        self.data_sheet=datas
        self.history_length = history_len
        self.history = {
        'POS_ACT': [np.zeros(history_len) for _ in range(6)],   # 6 个数据点
        'ANGLE_ACT': [np.zeros(history_len) for _ in range(6)], # 6 个数据点
        'FORCE_ACT': [np.zeros(history_len) for _ in range(6)], # 6 个数据点
        'CURRENT': [np.zeros(history_len) for _ in range(6)],   # 6 个数据点
        'ERROR': [np.zeros(history_len) for _ in range(6)],     # 6 个数据点
        'STATUS': [np.zeros(history_len) for _ in range(6)],    # 6 个数据点
        'TEMP': [np.zeros(history_len) for _ in range(6)]       # 6 个数据点
        }
        self.create_curves()
        

    def create_curves(self):
        self.error_label = QLabel("ERROR: ")
        self.status_label = QLabel("STATUS: ")
        
        self.layout.addWidget(self.error_label)  # 添加ERROR标签
        self.layout.addWidget(self.status_label)  # 添加STATUS标签
        
        self.plot_items = {name: pg.PlotWidget() for name in ['POS_ACT', 'ANGLE_ACT', 'FORCE_ACT', 'CURRENT', 'ERROR', 'STATUS', 'TEMP']}
        for i, (name, plot_widget) in enumerate(self.plot_items.items()):
                self.grid_layout.addWidget(plot_widget, i // 2, i % 2)  # 每行两个图
                plot_widget.setTitle(name)
                plot_widget.setLabel('left', 'Y-axis')
                plot_widget.setLabel('bottom', 'X-axis')
                plot_widget.setBackground((0, 0, 0))
                plot_widget.addLegend()
                plot_widget.showButtons()
                plot_widget.enableAutoRange()
                plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.curves = {
                'POS_ACT': [self.plot_items['POS_ACT'].plot(pen=pg.mkPen(color),name=f'POS_ACT {i + 1}') for i, color in enumerate(colorcet.glasbey[:6])],
                'ANGLE_ACT': [self.plot_items['ANGLE_ACT'].plot(pen=pg.mkPen(color),name=f'ANGLE_ACT {i + 1}') for i, color in enumerate(colorcet.glasbey[:6])],
                'FORCE_ACT': [self.plot_items['FORCE_ACT'].plot(pen=pg.mkPen(color),name=f'FORCE_ACT {i + 1}') for i, color in enumerate(colorcet.glasbey[:6])],
                'CURRENT': [self.plot_items['CURRENT'].plot(pen=pg.mkPen(color),name=f'CURRENT {i + 1}') for i, color in enumerate(colorcet.glasbey[:6])],
                'ERROR': [self.plot_items['ERROR'].plot(pen=pg.mkPen(color),name=f'ERROR {i + 1}') for i, color in enumerate(colorcet.glasbey[:6])],  
                'STATUS': [self.plot_items['STATUS'].plot(pen=pg.mkPen(color),name=f'STATUS {i + 1}') for i, color in enumerate(colorcet.glasbey[:6])],  
                'TEMP': [self.plot_items['TEMP'].plot(pen=pg.mkPen(color),name=f'TEMP {i + 1}') for i, color in enumerate(colorcet.glasbey[:6])] 
            }
    #   data_dict = {
    #     'POS_ACT': POS_ACT,
    #     'ANGLE_ACT': ANGLE_ACT,
    #     'FORCE_ACT': FORCE_ACT,
    #     'CURRENT': CURRENT,
    #     'ERROR': ERROR,
    #     'STATUS': STATUS,
    #     'TEMP': TEMP
    # }
    def update_plot(self,data_dict):
        # 更新每个曲线的数据
        try:
            # 更新每个曲线的数据
            for category, datas in data_dict.items():
                if datas is not None:
                    for i in range(len(datas)):
                        # 追加新的数据点到历史记录，并移除最老的数据点
                        self.history[category][i] = np.roll(self.history[category][i], -1)
                        self.history[category][i][-1] = datas[i]
                        # 更新曲线
                        self.curves[category][i].setData(self.history[category][i])
                else:
                    raise ValueError(f"Data for category '{category}' is None")

            err = update_error_label(data_dict['ERROR'])
            self.error_label.setText(err)
            self.status_label.setText("STATUS: " + ', '.join(['%s' % status_codes[s] for s in data_dict['STATUS']]))

        except Exception as e:
            print(f"Error updating plot: {e}")  # 打印具体的错误信息
            print(f"Data received: {data_dict}")  # 打印接收到的数据以便调试
            raise RuntimeError(f"Failed to update plot due to: {e}")
  
  
  
class MainWindow(QMainWindow):
    def __init__(self, data_handler, data=data_sheet,dt=100,name="Qt with PyQtGraph",Plot_touch=True,run_time=False):
        super().__init__()
        self.setWindowTitle(name)
        self.setGeometry(100, 100, 800, 600)
        self.dt=dt
        self.data_handler = data_handler
        self.Plot_touch_=Plot_touch
        self.run_time=run_time
        self.tabs = QTabWidget()
        self.image_tab = ImageTab(data)
        self.curve_tab = CurveTab(data)
        if Plot_touch:
            self.tabs.addTab(self.image_tab, "Images")
        self.tabs.addTab(self.curve_tab, "Curves")

        self.setCentralWidget(self.tabs)
        
    def update_plot(self):
        start_time = time.time()  # 记录开始时间
        data_dict =self.data_handler.read()
        end_time = time.time()  # 记录结束时间
        self.curve_tab.update_plot(data_dict['states'])
        if self.Plot_touch_:
            self.image_tab.update_plot(data_dict['touch'])
        elapsed_time = end_time - start_time
        if self.run_time:
            print(f"update_plot execution time: {elapsed_time:.6f} seconds")

    def reflash(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.dt)  # Update every 100 ms