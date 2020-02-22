from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout,
                            QGroupBox, QPushButton, QComboBox,QStackedWidget,
                            QFormLayout, QLabel, QSlider,QDoubleSpinBox, QFileDialog)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from os.path import join

from simulator import Run
from fuzzy_system import Fuzzy_system, get_member_funtion

class Information_frame(QFrame):
    def __init__(self, display):
        super().__init__()
        self.display_frame = display
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.load_data()
        self.thread_running = False
        self.running_option()
        self.variable_setting()
        self.monitor_setting()
    def running_option(self):
        group = QGroupBox("Run and save")
        group_layout = QHBoxLayout()
        group.setLayout(group_layout)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.start_simulation)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setDisabled(True)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setDisabled(True)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setDisabled(True)

        group_layout.addWidget(self.run_btn)
        group_layout.addWidget(self.pause_btn)
        group_layout.addWidget(self.stop_btn)
        group_layout.addWidget(self.save_btn)
        self.layout.addWidget(group)
    def variable_setting(self):
        group = QGroupBox("fuzzy variable setting")
        group_layout = QVBoxLayout()
        self.var_setting_stack = QStackedWidget()

        self.front_dist_frame = Variable_setting_frame()
        self.LR_dist_frame = Variable_setting_frame()
        self.angle_frame = Variable_setting_frame()

        self.front_dist_frame.small.mean.setValue(5)
        self.front_dist_frame.large.mean.setValue(16)
        self.front_dist_frame.small.dev.setValue(2.5)
        self.front_dist_frame.large.dev.setValue(2.5)
        self.front_dist_frame.medium.setDisabled(True)

        self.LR_dist_frame.small.mean.setValue(-12)
        self.LR_dist_frame.medium.mean.setValue(0)
        self.LR_dist_frame.large.mean.setValue(12)
        self.LR_dist_frame.small.dev.setValue(2.5)
        self.LR_dist_frame.medium.dev.setValue(2.5)
        self.LR_dist_frame.large.dev.setValue(2.5)

        self.angle_frame.small.mean.setValue(-10)
        self.angle_frame.medium.mean.setValue(0)
        self.angle_frame.large.mean.setValue(10)
        self.angle_frame.small.dev.setValue(8)
        self.angle_frame.medium.dev.setValue(8)
        self.angle_frame.large.dev.setValue(8)

        self.var_setting_stack.addWidget(self.front_dist_frame)
        self.var_setting_stack.addWidget(self.LR_dist_frame)
        self.var_setting_stack.addWidget(self.angle_frame)

        self.select_var_box = QComboBox()
        self.select_var_box.addItems(['Front Distance','LR-Distance difference', 'Wheel angle'])
        self.select_var_box.activated.connect(self.var_setting_stack.setCurrentIndex)

        group_layout.addWidget(self.select_var_box)
        group_layout.addWidget(self.var_setting_stack)
        group.setLayout(group_layout)
        self.layout.addWidget(group)
    def monitor_setting(self):
        group = QGroupBox("Simulation imformation")
        group_layout = QFormLayout()
        
        self.l_car_pos = QLabel("0 , 0")
        self.l_front_dist = QLabel("0.0")
        self.label_l_dist = QLabel("0.0")
        self.label_r_dist = QLabel("0.0")
        self.l_car_angle = QLabel("0.0")
        self.l_wheel_angle = QLabel("0.0")
        group_layout.addRow(QLabel("Car position :"), self.l_car_pos)
        group_layout.addRow(QLabel("Car angle :"), self.l_car_angle)
        group_layout.addRow(QLabel("Front distance :"), self.l_front_dist)
        group_layout.addRow(QLabel("Left side distance :"), self.label_l_dist)
        group_layout.addRow(QLabel("Right side distance :"), self.label_r_dist)
        group_layout.addRow(QLabel("Wheel angle :"), self.l_wheel_angle)

        group.setLayout(group_layout)
        self.layout.addWidget(group)
    @pyqtSlot()
    def start_simulation(self):
        front_dist = {}
        Fuzzy_system.set_fuzzy_var(front_dist, 'small', self.front_dist_frame.small.mean.value(), self.front_dist_frame.small.dev.value(), 'small')
        Fuzzy_system.set_fuzzy_var(front_dist, 'large', self.front_dist_frame.large.mean.value(), self.front_dist_frame.large.dev.value(), 'large')
        lr_dist = {}
        Fuzzy_system.set_fuzzy_var(lr_dist, 'small', self.LR_dist_frame.small.mean.value(), self.LR_dist_frame.small.dev.value(), 'small')
        Fuzzy_system.set_fuzzy_var(lr_dist, 'medium', self.LR_dist_frame.medium.mean.value(), self.LR_dist_frame.medium.dev.value(), 'medium')
        Fuzzy_system.set_fuzzy_var(lr_dist, 'large', self.LR_dist_frame.large.mean.value(), self.LR_dist_frame.large.dev.value(), 'large')
        wheel = {}
        Fuzzy_system.set_fuzzy_var(wheel, 'small', self.angle_frame.small.mean.value(), self.angle_frame.small.dev.value(), )
        Fuzzy_system.set_fuzzy_var(wheel, 'medium', self.angle_frame.medium.mean.value(), self.angle_frame.medium.dev.value(), 'medium')
        print(self.angle_frame.large.mean.value())
        Fuzzy_system.set_fuzzy_var(wheel, 'large', self.angle_frame.large.mean.value(), self.angle_frame.large.dev.value(), )

        former_vars = [front_dist, lr_dist]
        self.system = Fuzzy_system(wheel, former_vars)
        self.rule_setting()
        self.simulator_thread = Run(self.system, self.dataset)
        self.simulator_thread.started.connect(self.__init_controller)
        self.simulator_thread.finished.connect(self.__reset_controller)
        self.simulator_thread.sig_connect(p_init = self.display_frame.init_walls, 
                                        p_car = self.move_car,
                                        collide = self.display_frame.collide,
                                        log = self.simulation_log)

        self.thread_running = True
        self.simulator_thread.start()
    def rule_setting(self):
        self.system.set_rule('large',('small','small'))
        self.system.set_rule('small',('small','medium'))
        self.system.set_rule('small',('small','large'))
        self.system.set_rule('large',('large','small'))
        self.system.set_rule('medium',('large','medium'))
        self.system.set_rule('small',('large','large'))
    @pyqtSlot()
    def __init_controller(self):
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.run_btn.setDisabled(True)
        self.save_btn.setDisabled(True)

        self.pause_btn.clicked.connect(self.simulator_thread.paused)
        self.stop_btn.clicked.connect(self.simulator_thread.stop)

    @pyqtSlot()
    def __reset_controller(self):
        self.pause_btn.setDisabled(True)
        self.stop_btn.setDisabled(True)
        self.run_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.thread_running = False
    @pyqtSlot(list, list, list, float)
    def move_car(self, pos_angle, inters, dists, wheel_ouput):
        self.l_car_pos.setText("{:.3f},{:.3f}".format(*pos_angle[:2]))
        self.l_car_angle.setText(str(pos_angle[2]))
        self.l_front_dist.setText(str(dists[0]))
        self.label_l_dist.setText(str(dists[1]))
        self.label_r_dist.setText(str(dists[2]))
        self.l_wheel_angle.setText(str(wheel_ouput))

        self.display_frame.update_car(pos_angle, inters)
    @pyqtSlot(dict)
    def simulation_log(self, log):
        self.log = log
        self.display_frame.show_path(self.log['x'], self.log['y'])
    @pyqtSlot()
    def save_data(self):
        save_dir = QFileDialog.getExistingDirectory(self, 'Save As')
        path_4d = join(save_dir, 'train4D.txt')
        path_6d = join(save_dir, 'train6D.txt')
        data_lines = list(zip(*self.log.values()))
        with open(path_6d, 'w') as f6d:
            for line in data_lines:
                f6d.write("{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}\n".format(
                    line[0], line[1], line[2], line[3], line[4], line[5]))
        
        with open(path_4d, 'w') as f4d:
            for l in data_lines:
                f4d.write("{:.3f} {:.3f} {:.3f} {:.3f}\n".format(
                    l[2], l[3], l[4], l[5]))
        
            
    def load_data(self, path = './data/case01.txt'):
        data = []
        with open(path, 'r', encoding = 'utf8') as f:
            for line in f:
                data.append(tuple(line.strip().split(',')))
        self.dataset = {
            "start_pos" : data[0][:2],
            "start_wheel_angle" : data[0][2],
            "finishline_l" : data[1],
            "finishline_r" : data[2],
            "walls" : data[3:]
        }
    def load_path
            
class Variable_setting_frame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel | QFrame.Plain)
        layout = QFormLayout()
        self.setLayout(layout)

        self.small = Parameter()
        self.medium = Parameter()
        self.large = Parameter()

        layout.addRow(QLabel("Small"), self.small)
        layout.addRow(QLabel("Medium"), self.medium)
        layout.addRow(QLabel("Large"), self.large)
class Parameter(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.mean = QDoubleSpinBox()
        self.dev = QDoubleSpinBox()
        self.mean.setRange(-50, 50)
        self.dev.setMinimum(0.1)
        layout.addWidget(QLabel("Mean"))
        layout.addWidget(self.mean)
        layout.addWidget(QLabel("deviation"))
        layout.addWidget(self.dev)        

