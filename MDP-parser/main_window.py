import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QWidget, QFrame, QFileDialog
from PyQt5.QtGui import QPixmap, QDrag, QPainter, QIcon, QFont, QImage
from PyQt5.QtCore import pyqtSignal

from pathlib import Path

from backend import Etat, gramPrintListener, load_mdp, simulation_rand, simulation_choice, simulation_choice_normal, simulation_choice_decision, simulation_adv, SMC_quantitatif, SMC_qualitatif, PCTL_CM, PCTL_MDP


window_name, base_class = uic.loadUiType("main-window.ui")


class MainWindow(window_name, base_class):

    main_window_back_signal = pyqtSignal()
    file_path_stl_signal = pyqtSignal(str)

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
        # self.previous_image = None

        self.etats_with_decision = None
        self.adv = {}
        self.image_in_screen_size = self.label_image_init.size()
        # print(f"self.image_in_screen_size: {self.image_in_screen_size}")

    def init_gui(self):

        self.actionOpen_File.triggered.connect(self.showDialog)

        # Init questions
        self.btn_simulate.clicked.connect(self.simulate_options)
        self.btn_modelchecking.clicked.connect(self.modelchecking_options)
        self.hide_init_options()

        self.btn_folder.clicked.connect(self.showDialog)
        self.btn_each_action.clicked.connect(self.each_action_print)
        self.btn_random_simulation.clicked.connect(self.random_simulation_print)
        self.btn_pos_opponent.clicked.connect(self.adversaire_print)
        self.btn_next_image.clicked.connect(self.show_next_image)
        self.btn_previous_image.clicked.connect(self.show_previous_image)

        self.label_select_action.hide()
        self.box_actions.hide()
        self.btn_accept_choice.clicked.connect(self.decision_taken)
        self.btn_accept_choice.hide()
        self.btn_each_action_next.hide()
        self.btn_each_action_next.clicked.connect(self.create_new_image)

        # adversaire 
        self.label_create_adv.hide()
        self.label_state_options.hide()
        self.label_etat.hide()
        self.box_actions_adv.hide()
        self.btn_accept_action_adv.hide()
        self.btn_accept_action_adv.clicked.connect(self.action_adv_choosen)
        self.label_prob.hide()
        self.label_action_probabilities.hide()

        # model checking 
        # TODO: Add more items
        self.box_modelchecking.addItems(["SMC Quantitative", "SMC Qualitatif", "PCTL for CMs", "PCTL for MDPs"])
        self.btn_accept_modelchecking.clicked.connect(self.model_checking_selected)
        self.hide_modelchecking_options()
        self.modelchecking_result.hide()
        
        # model checking : smc quantitative
        self.btn_smc_quant.clicked.connect(self.smc_quantitatif_calculate)
        self.smc_quantitative_widget.hide()

        # model checking : smc qualitatif
        self.btn_smc_qual.clicked.connect(self.smc_qualitatif_calculate)
        self.smc_qualitatif_widget.hide()

        # others
        self.hide_simulate_options()
        self.clean_tmp()
        self.btn_next_image.hide()
        self.btn_previous_image.hide()
        

    def clean_tmp(self):  # clean the tmp folder.
        directory = os.path.dirname(os.path.abspath(__file__)) + r'/tmp'
        files_in_directory = os.listdir(directory)

        filtered_files = [file for file in files_in_directory if file.endswith(".png")]

        for file in filtered_files:
            path_to_file = os.path.join(directory, file)

            os.remove(path_to_file)

    def add_init_image_to_screen(self):
        exist = False
        init_image = os.path.dirname(os.path.abspath(__file__)) + r'/tmp/image_init.png'
        while not exist:
            if os.path.exists(init_image):
                exist = True
                # show init image
                pixmap = QPixmap(init_image)
                pixmap = pixmap.scaled(590, 560)
                self.label_image_init.setPixmap(pixmap)
    
    def simulate_options(self):
        self.show_simulate_options()

    def modelchecking_options(self):
        self.show_modelchecking_options()

    def show_modelchecking_options(self):
        self.hide_init_options()
        self.label_options.setText("Model Checking options")
        self.label_options.show()
        self.box_modelchecking.show()
        self.btn_accept_modelchecking.show()
    
    def hide_modelchecking_options(self):
        self.label_options.hide()
        self.box_modelchecking.hide()
        self.btn_accept_modelchecking.hide()

    def show_init_options(self):
        self.label_options.show()
        self.btn_modelchecking.show()
        self.btn_simulate.show()
    
    def hide_init_options(self):
        self.label_options.hide()
        self.btn_modelchecking.hide()
        self.btn_simulate.hide()
    
    def hide_simulate_options(self):
        # TO DO: change label_options text
        self.label_options.hide()
        self.btn_each_action.hide()
        self.btn_random_simulation.hide()
        self.btn_pos_opponent.hide()
        self.label_transitions.hide()
        self.number_transitions.hide()

    def show_simulate_options(self):
        self.hide_init_options()
        self.label_options.setText("What would you like to simulate?")
        self.label_options.show()
        self.btn_each_action.show()
        self.btn_random_simulation.show()
        self.btn_pos_opponent.show()
        self.label_transitions.show()
        self.number_transitions.show()

    def model_checking_selected(self):
        # TODO: add functions from mdp.py to backend.py
        option_selected = self.box_modelchecking.currentText()
        if option_selected == "SMC Quantitative":
            self.smc_quantitative_option()
        elif option_selected == "SMC Qualitatif":
            self.smc_qualitatif_option()
        elif option_selected == "PCTL for CMs":
            self.pctl_for_cms()
        elif option_selected == "PCTL for MDPs":
            self.pctl_for_mdps()

    def smc_quantitative_option(self):
        # TODO: Add layout into widget. Add double layout.
        # TODO: Adapt function for interface controller
        # TODO: create labels and buttons of this function
        # For add unicode characters into qt designer: https://stackoverflow.com/questions/52592663/unicode-characters-in-qt-designer-for-python
        # TODO: create a function to show labels and buttons
        # TODO: create a function to hide labels and buttons
        self.hide_modelchecking_options()
        self.label_options.setText("SMC Quantitatif")
        self.label_options.show()
        self.smc_quant_states.clear()
        self.smc_quant_states.addItems(self.etats)
        self.smc_quantitative_widget.move(740, 210)
        self.smc_quantitative_widget.show()

    def smc_quantitatif_calculate(self):
        goal_state = self.smc_quant_states.currentText()
        turns = self.smc_quant_n_transitions.value()
        epsilon = self.smc_quant_epsilon.value()
        delta = self.smc_quant_delta.value()
        result_smc_quant1, result_smc_quant2  = SMC_quantitatif(self.etats, self.G, goal_state, turns, epsilon, delta)

        self.smc_quantitative_widget.hide()
        self.modelchecking_result.move(780, 210)
        self.modelchecking_answer1.setText(result_smc_quant1)
        self.modelchecking_answer2.setText(result_smc_quant2)
        self.modelchecking_result.show()

    def smc_qualitatif_option(self):
        # TODO: Adapt function for interface controller
        # TODO: create labels and buttons of this function
        # TODO: create a function to show labels and buttons
        # TODO: create a function to hide labels and buttons
        self.hide_modelchecking_options()
        self.label_options.setText("SMC Qualitatif")
        self.label_options.show()
        self.smc_qual_states.clear()
        self.smc_qual_states.addItems(self.etats)
        self.smc_qualitatif_widget.move(740, 210)
        self.smc_qualitatif_widget.show()

    def smc_qualitatif_calculate(self):
        goal_state = self.smc_qual_states.currentText()
        turns = self.smc_qual_n_transitions.value()
        epsilon = self.smc_qual_epsilon.value()
        alpha = self.smc_qual_alpha.value()
        beta = self.smc_qual_beta.value()
        theta = self.smc_qual_theta.value()
        result_smc_qual1, result_smc_qual2  = SMC_qualitatif(self.etats, self.G, goal_state, turns, epsilon, alpha, beta, theta)

        self.smc_qualitatif_widget.hide()
        self.modelchecking_result.move(780, 210)
        self.modelchecking_answer1.setText(result_smc_qual1)
        self.modelchecking_answer2.setText(result_smc_qual2)
        self.modelchecking_result.show()

    def pctl_for_cms(self):
        # TODO: Adapt function for interface controller
        # TODO: create labels and buttons of this function
        # TODO: create a function to show labels and buttons
        # TODO: create a function to hide labels and buttons
        pass

    def pctl_for_mdps(self):
        # TODO: Adapt function for interface controller
        # TODO: create labels and buttons of this function
        # TODO: create a function to show labels and buttons
        # TODO: create a function to hide labels and buttons
        pass

    def showDialog(self):
        directory = Path("")
        if self.lastDir:
            directory = self.lastDir
        fname = QFileDialog.getOpenFileName(self, "Open file", str(directory), "MDP (*.mdp)")
        # The signal with the path is emitted
        self.file_path_stl_signal.emit(fname[0])
        if fname[0]:
            self.etats, self.G = load_mdp(fname[0])
            self.add_init_image_to_screen()
            self.show_init_options()
            # self.show_simulate_options()

    def option_selected(self):
        self.n_transitions = self.number_transitions.value()
        self.hide_simulate_options()

    def show_previous_image(self):
        current_number = self.current_image[self.current_image.find('image_')+6:self.current_image.find('.')]
        if int(current_number) > 0:
            self.current_image = self.current_image.replace(current_number, str(int(current_number) - 1))
            pixmap = QPixmap(self.current_image)
            pixmap = pixmap.scaled(590, 560)
            self.label_image_next.setPixmap(pixmap)
            self.image_name.setText(self.current_image[self.current_image.find('image_'):self.current_image.find('.')])

    def show_next_image(self):
        current_number = self.current_image[self.current_image.find('image_')+6:self.current_image.find('.')]
        if int(current_number) < 2 * self.n_transitions + 1:
            self.current_image = self.current_image.replace(current_number, str(int(current_number) + 1))
            pixmap = QPixmap(self.current_image)
            pixmap = pixmap.scaled(590, 560)
            self.label_image_next.setPixmap(pixmap)
            self.image_name.setText(self.current_image[self.current_image.find('image_'):self.current_image.find('.')])
        # else:
        #     self.btn_next_image.hide()

    def decision_taken(self):
        directory = os.path.dirname(os.path.abspath(__file__)) + r'/tmp'
        files_in_directory = os.listdir(directory)
        filtered_files = [file for file in files_in_directory if file.endswith(".png")]
        actual_image_number = int((len(filtered_files) - 1))
        simulation_choice_decision(self.etats, self.G, actual_image_number, self.box_actions.currentText())
        self.show_image_created(actual_image_number)
        self.label_select_action.hide()
        self.box_actions.clear()
        self.box_actions.hide()
        self.btn_accept_choice.hide()
        self.btn_each_action_next.show()

    def create_new_image(self):
        directory = os.path.dirname(os.path.abspath(__file__)) + r'/tmp'
        files_in_directory = os.listdir(directory)
        filtered_files = [file for file in files_in_directory if file.endswith(".png")]
        if len(filtered_files) < 2 * self.n_transitions + 3:
            actual_image_number = int((len(filtered_files) - 1))
            decision_possible, actions = simulation_choice(self.etats, self.G)
            if decision_possible == 'decision':
                self.btn_each_action_next.hide()
                self.label_select_action.show()
                self.box_actions.addItems(actions)
                self.box_actions.show()
                self.btn_accept_choice.show()
            elif decision_possible == 'normal':
                simulation_choice_normal(self.etats, self.G, actual_image_number)
                self.show_image_created(actual_image_number)
        else:
            self.btn_each_action_next.hide()
            self.btn_next_image.show()
            self.btn_previous_image.show()

    def show_image_created(self, image_number):
        directory = os.path.dirname(os.path.abspath(__file__)) + r'/tmp'
        image_created = False
        self.btn_each_action_next.setEnabled(False)
        while not image_created:
            files_in_directory = os.listdir(directory)
            filtered_files = [file for file in files_in_directory if file.endswith(".png")]
            if 'image_' + str(image_number) + '.png' in filtered_files:
                image_created = True
                self.current_image = os.path.dirname(os.path.abspath(__file__)) + r'/tmp/image_' + f'{image_number + 1}.png'
                pixmap = QPixmap(self.current_image)
                pixmap = pixmap.scaled(590, 560)
                self.label_image_next.setPixmap(pixmap)
                self.image_name.setText(f'image_{image_number+1}')
                self.btn_each_action_next.setEnabled(True)

    def each_action_print(self):
        self.option_selected()
        simulation_choice(self.etats, self.G, 0)
        self.btn_each_action_next.show()

        self.show_image_created(0)

    def show_images_roullette(self):
        self.current_image = os.path.dirname(os.path.abspath(__file__)) + r'/tmp/image_0.png'
        pixmap = QPixmap(self.current_image)
        pixmap = pixmap.scaled(590, 560)
        self.label_image_next.setPixmap(pixmap)
        self.btn_next_image.show()
        self.btn_previous_image.show()
        self.image_name.setText('image_0')

    def random_simulation_print(self):
        self.option_selected()
        simulation_rand(self.etats, self.G, self.n_transitions)

        # verify creation of images
        directory = os.path.dirname(os.path.abspath(__file__)) + r'/tmp'

        images_created = False

        while not images_created:
            files_in_directory = os.listdir(directory)
            filtered_files = [file for file in files_in_directory if file.endswith(".png")]
            if len(filtered_files) == 2 * self.n_transitions + 3:
                images_created = True
                self.show_images_roullette()

    def show_adv_option(self):
        action = self.etats_with_decision.pop(0)
        self.label_etat.setText(action.nom)
        self.box_actions_adv.clear()
        self.box_actions_adv.addItems(list(action.transitions.keys()))
        #self.label_action_probabilities.setText(', '.join(list(action.transitions.keys())) + ' = ' + ', '.join(map(str, list(action.transitions.values()))))

    def action_adv_choosen(self):
        self.adv[self.label_etat.text()] = self.box_actions_adv.currentText()
        if len(self.etats_with_decision) > 0:
            self.label_state_options.show()
            self.label_etat.show()
            self.box_actions_adv.show()
            self.btn_accept_action_adv.show()
            #self.label_prob.show()
            #self.label_action_probabilities.show()
            self.show_adv_option()
        else:
            self.label_create_adv.hide()
            self.label_state_options.hide()
            self.label_etat.hide()
            self.box_actions_adv.hide()
            self.btn_accept_action_adv.hide()
            #self.label_prob.hide()
            #self.label_action_probabilities.hide()

            simulation_adv(self.etats, self.adv, self.G, self.n_transitions)
            # verify creation of images
            directory = os.path.dirname(os.path.abspath(__file__)) + r'/tmp'

            images_created = False

            while not images_created:
                files_in_directory = os.listdir(directory)
                filtered_files = [file for file in files_in_directory if file.endswith(".png")]
                if len(filtered_files) == 2 * self.n_transitions + 3:
                    images_created = True
                    self.show_images_roullette()

    def adversaire_print(self):
        self.option_selected()
        self.etats_with_decision = [k for k in self.etats.values() if k.have_decision]

        self.label_create_adv.show()
        self.label_state_options.show()
        self.label_etat.show()
        self.box_actions_adv.show()
        self.btn_accept_action_adv.show()
        #self.label_prob.show()
        #self.label_action_probabilities.show()

        self.show_adv_option()

    def show_up(self):
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # windows instances
    main_window = MainWindow()

    main_window.showMaximized()
    app.exec()
