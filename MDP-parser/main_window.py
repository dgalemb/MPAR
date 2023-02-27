import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QWidget, QFrame, QFileDialog
from PyQt5.QtGui import QPixmap, QDrag, QPainter, QIcon, QFont, QImage
from PyQt5.QtCore import pyqtSignal

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from pathlib import Path

from backend import Etat, gramPrintListener, load_mdp, simulation_rand


window_name, base_class = uic.loadUiType("main-window.ui")


class MainWindow(window_name, base_class):

    main_window_back_signal = pyqtSignal()
    # open_about_window_signal = pyqtSignal()
    # open_help_documentation_window_signal = pyqtSignal()
    file_path_stl_signal = pyqtSignal(str)
    # create_gcode_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1500, 900)
        self.setAcceptDrops(True)
        self.setupUi(self)
        self.init_gui()

        self.lastDir = None
        self.droppedFilename = None

        self.etats = None
        self.G = None
        self.n_transitions = 10

        self.current_image = None
        self.next_image = None
        self.previous_image = None

    def init_gui(self):

        self.actionOpen_File.triggered.connect(self.showDialog)

        self.btn_folder.clicked.connect(self.showDialog)
        # self.btn_each_action.clicked.connect(self.)
        self.btn_random_simulation.clicked.connect(self.random_simulation_print)
        # self.btn_pos_opponent.clicked.connect(self.)
        self.btn_next_image.clicked.connect(self.show_next_image)
        self.btn_previous_image.clicked.connect(self.show_previous_image)

        # btn.setFont(QFont("Ricty Diminished", 14))
        # layout2.addWidget(btn)
        #
        # btn1 = QPushButton(text="Hola 1")
        # btn1.setFont(QFont("Ricty Diminished", 14))
        # layout.addWidget(btn1)

        # self.viewer = gl.GLViewWidget()
        # layout.addWidget(self.viewer, 1)
        #
        # self.viewer.setWindowTitle('STL Viewer')
        # self.viewer.setCameraPosition(distance=80)
        #
        # g = gl.GLGridItem()
        # g.setSize(200, 200)
        # g.setSpacing(5, 5)
        # self.viewer.addItem(g)
        self.hide_options()
        self.clean_tmp()
        self.btn_next_image.hide()
        self.btn_previous_image.hide()

    def clean_tmp(self):
        directory = os.path.dirname(os.path.abspath(__file__)) + r'\tmp'
        files_in_directory = os.listdir(directory)

        filtered_files = [file for file in files_in_directory if file.endswith(".png")]

        for file in filtered_files:
            path_to_file = os.path.join(directory, file)

            os.remove(path_to_file)

    def add_init_image_to_screen(self):
        exist = False
        init_image = os.path.dirname(os.path.abspath(__file__)) + r'\tmp\image_init.png'
        while not exist:
            if os.path.exists(init_image):
                exist = True
                # show init image
                pixmap = QPixmap(init_image)
                self.label_image_init.setPixmap(pixmap)

    def hide_options(self):
        self.label_options.hide()
        self.btn_each_action.hide()
        self.btn_random_simulation.hide()
        self.btn_pos_opponent.hide()
        self.label_transitions.hide()
        self.number_transitions.hide()

    def show_options(self):
        self.label_options.show()
        self.btn_each_action.show()
        self.btn_random_simulation.show()
        self.btn_pos_opponent.show()
        self.label_transitions.show()
        self.number_transitions.show()

    def showDialog(self):
        directory = Path("")
        if self.lastDir:
            directory = self.lastDir
        fname = QFileDialog.getOpenFileName(self, "Open file", str(directory), "MDP (*.mdp)")
        # The signal with the path is emitted
        self.file_path_stl_signal.emit(fname[0])
        if fname[0]:
            # self.showSTL(fname[0])
            # self.lastDir = Path(fname[0]).parent
            # print(fname[0])
            self.etats, self. G = load_mdp(fname[0])
            self.add_init_image_to_screen()
            self.show_options()

    def option_selected(self):
        self.n_transitions = self.number_transitions.value()
        self.hide_options()

    def show_previous_image(self):
        current_number = self.current_image[self.current_image.find('image_')+6:self.current_image.find('.')]
        if int(current_number) > 0:
            self.current_image = self.current_image.replace(current_number, str(int(current_number) - 1))
            pixmap = QPixmap(self.current_image)
            self.label_image_next.setPixmap(pixmap)
            self.image_name.setText(self.current_image[self.current_image.find('image_'):self.current_image.find('.')])

    def show_next_image(self):
        current_number = self.current_image[self.current_image.find('image_')+6:self.current_image.find('.')]
        if int(current_number) < 2 * self.n_transitions + 1:
            self.current_image = self.current_image.replace(current_number, str(int(current_number) + 1))
            pixmap = QPixmap(self.current_image)
            self.label_image_next.setPixmap(pixmap)
            self.image_name.setText(self.current_image[self.current_image.find('image_'):self.current_image.find('.')])
        # else:
        #     self.btn_next_image.hide()

    def show_images_roullette(self):
        self.current_image = os.path.dirname(os.path.abspath(__file__)) + r'\tmp\image_0.png'
        pixmap = QPixmap(self.current_image)
        self.label_image_next.setPixmap(pixmap)
        self.btn_next_image.show()
        self.btn_previous_image.show()
        self.image_name.setText('image_0')

    def random_simulation_print(self):
        self.option_selected()
        simulation_rand(self.etats, self.G, self.n_transitions)

        # verify creation of images
        directory = os.path.dirname(os.path.abspath(__file__)) + r'\tmp'

        images_created = False

        while not images_created:
            files_in_directory = os.listdir(directory)
            filtered_files = [file for file in files_in_directory if file.endswith(".png")]
            if len(filtered_files) == 2 * self.n_transitions + 3:
                images_created = True
                self.show_images_roullette()

    def dragEnterEvent(self, e):
        print("enter")
        mimeData = e.mimeData()
        mimeList = mimeData.formats()
        filename = None

        if "text/uri-list" in mimeList:
            filename = mimeData.data("text/uri-list")
            filename = str(filename, encoding="utf-8")
            filename = filename.replace("file:///", "").replace("\r\n", "").replace("%20", " ")
            filename = Path(filename)

        if filename.exists() and filename.suffix == ".stl":
            e.accept()
            self.droppedFilename = filename
        else:
            e.ignore()
            self.droppedFilename = None

    def dropEvent(self, e):
        if self.droppedFilename:
            self.showSTL(self.droppedFilename)


    def show_up(self):
        self.show()

    # def send_process_gcode_order(self):
    #     self.create_gcode_signal.emit()


if __name__ == '__main__':

    # sys.__excepthook__ = hook
    app = QApplication(sys.argv)

    # windows instances
    main_window = MainWindow()

    main_window.show()
    app.exec()