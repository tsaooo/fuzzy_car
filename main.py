import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QMainWindow

from display import Plot_canvas
from controller import Information_frame
class Base_widget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.center_widget = QWidget()
        layout = QHBoxLayout()
        self.display = Plot_canvas()
        self.information = Information_frame(self.display)
        layout.addWidget(self.display)
        layout.addWidget(self.information)
        self.center_widget.setLayout(layout)

        self.setCentralWidget(self.center_widget)
        self.setWindowTitle('Fuzzy system simulator!!')
    def closeEvent(self, event):
        if self.information.thread_running:
            self.information.simulator_thread.stop()
            self.information.simulator_thread.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    base = Base_widget()
    base.show()
    sys.exit(app.exec_())
