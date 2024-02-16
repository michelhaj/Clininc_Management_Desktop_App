import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
import resources_rc
import icons_rc
import sys
from os import path
import matplotlib.pyplot as plt
import pyqtgraph as pg
from qt_material import apply_stylesheet
from PyQt5.uic import loadUiType

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

####ctrl + space for documenntation
FORM_CLASS, _ = loadUiType('try.ui')
import sqlite3
from datetime import datetime, timedelta,date
import re

db_name = 'clients.db'
# db_history = 'history.db'
import os, sys, random, time


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')

def getMachine_addr():
    os_type = sys.platform.lower()
    if 'win' in os_type:
        command = 'wmic bios get serialnumber'
    else:
        if 'linux' in os_type:
            command = 'hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid'
        else:
            if 'darwin' in os_type:
                command = 'ioreg -l | grep IOPlatformSerialNumber'
    return os.popen(command).read().replace('\n', '').replace('  ', '').replace(' ', '')


def verify(key):
    global score
    score = 0
    check_digit = key[2]
    check_digit_count = 0
    chunks = key.split("-")
    for chunk in chunks:
        if len(chunk) != 4:
            return False
        for char in chunk:
            if char == check_digit:
                check_digit_count += 1
            score += ord(char)
    if score > 1700 and score < 1800 and check_digit_count == 3:
        return True
    else:
        return False


def generate():
    global key
    key = ''
    section = ''
    check_digit = 0
    alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890'
    while len(key) < 25:
        char = random.choice(alphabet)
        key += char
        section += char
        if len(section) == 4:
            key += '-'
            section = ''

    key = key[:-1]
    return key
#this combo box scrolls only if opend before.
#if the mouse is over the combobox and the mousewheel is turned,
# the mousewheel event of the scrollWidget is triggered


class Main(QMainWindow, FORM_CLASS, QtWidgets.QMessageBox):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        QtWidgets.QMessageBox.__init__(self)
        self.setupUi(self)
        ####################
        self.initUI()
        ########################
        

        self.weight.wheelEvent = lambda event: None
        self.height.wheelEvent = lambda event: None
        self.age.wheelEvent = lambda event: None
        self.smoking.wheelEvent = lambda event: None
        self.filter_pateint_val.wheelEvent = lambda event: None
        self.handel_buttons()
        # self.refresh_fn()
        self.patients_table_fill()
        self.p_to_appt_flag = False
        #       spinbox id read only
        self.id_spinbox.setReadOnly(True)
        # self.label_33.setPixmap(QPixmap(".\icons\support.svg"))
        # self.resize(1600, 700)
        self.setWindowTitle('Scheduler')
        db = sqlite3.connect('license.db')
        self.no_clicked = False
        cursor = db.cursor()
        cursor_getserialnummber = db.cursor()
        command_get = 'SELECT serial_number from license'
        result = cursor_getserialnummber.execute(command_get)
        result = result.fetchall()
        for i in result:
            if i[0] == getMachine_addr():
                self.stackedWidget.setCurrentWidget(self.main_page)
                break
        ##################################
        self.tabwidget.tabBar().setVisible(False)
        self.advanced_search_gb.hide()
        self.stats_total()
        self.stats_yesterday_tomorrow_today_nextweek()
        ##################################
        self.validation_error.setStyleSheet("QLabel{font-size: 18pt;color: rgb(255, 0, 0);}")
        self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.date_check_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.date_search_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.list_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.start.setDateTime(QtCore.QDateTime.currentDateTime())
        self.end.setDateTime(QtCore.QDateTime.currentDateTime())
        self.patient_id.setValue(0)
        self.list_date_edit.setCalendarPopup(True)
        self.date_edit.setCalendarPopup(True)
        self.date_check_edit.setCalendarPopup(True)
        self.date_search_edit.setCalendarPopup(True)
        self.price_spinbox.setSuffix(' JOD')
        self.age.setSuffix(' Years')
        self.weight.setSuffix(' Kg')
        self.height.setSuffix(' CM')
        self.price_spinbox.setMaximum(10000)
        ############################
        self.add_new_p_msgbox = QMessageBox(self)
        self.type_of_patient.currentTextChanged.connect(self.p_choosen)
        self.y=self.add_new_p_msgbox.addButton("Yes Create new patient with the appointment info that I inserted", QMessageBox.YesRole)
        self.y.setStyleSheet("background-color: rgb(0, 170, 255); color: rgb(0, 0, 0);")
        self.n=self.add_new_p_msgbox.addButton("No don't create a new patient, it's only once", QMessageBox.NoRole)
        self.n.setStyleSheet("background-color: rgb(0, 170, 255); color: rgb(0, 0, 0);")
        self.yes = False
        ############################
        self.Generate_flag = True
        self.isclicked=False
        self.check_fn()
        self.auto_fill_time()
        self.check_table.selectionModel().currentRowChanged.connect(self.rows_selected)
        self.patients_table.selectionModel().currentRowChanged.connect(self.patient_table_row_selected)
        self.fill_search_table()
        self.n_msgbox = QMessageBox(self)
        self.msgBox = QMessageBox(self)
        self.errormsgbox = QMessageBox(self)
        self.patient_info_mb = QMessageBox(self)
        self.add_p_msgbox = QMessageBox(self)
        self.l = QtWidgets.QVBoxLayout()
        self.tableWidget = QtWidgets.QTableWidget(self.msgBox)
        self.tableWidget.selectionModel().currentRowChanged.connect(self.rows_selected_popup)
        self.p_id_not_in_plist = True
        db_id = sqlite3.connect(db_name)
        cursor_id = db_id.cursor()
        get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
        id_result = cursor_id.execute(get_id)
        id_result = id_result.fetchone()
        try:
            self.id_spinbox.setValue(id_result[0] + 1)
        except TypeError:
            self.id_spinbox.setValue(0)
        ###########################################
        #figure bar chart
        ###########################################
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)

        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.layout = QtWidgets.QGridLayout(self.bar_chart_frame)
        self.layout.addWidget(self.canvas)
        self.names = []
        self.values = []
        # ###############################################################
        ###############################################################
        #fig line chart
        self.fig2 = Figure()
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvas(self.fig2)

        self.canvas2.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        self.canvas2.updateGeometry()
        self.layout2 = QtWidgets.QGridLayout(self.line_chart_frame)
        self.layout2.addWidget(self.canvas2)
        self.names1=[]
        self.values1=[]
        ###############################################################
        ###############################################################
            # to check the last id and add one to it to make it
        # db_id = sqlite3.connect(db_name)
        # cursor_id = db_id.cursor()
        # get_id = 'select patient_id from patients order by patient_id desc limit 1 '
        # id_case_selected_and_changedid = cursor_id.execute(get_id)
        # id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
        # db_id.close()
        # try:
        #     new_id = id_case_selected_and_changedid[0] + 1
        #     self.patient_id.setValue(new_id)
        # except:
        #     self.patient_id.setValue(0)
        # db_id.close()
        self.search_edit.textChanged.connect(self.search_by_fn)
        self.search_edit_2.textChanged.connect(self.search_by_fn_patient)
        self.search_edit_appt.textChanged.connect(self.search_by_fn_appt)

    def initUI(self):
        self.center()


    def center(self):
        self.resize(1650, self.frameGeometry().height())
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def setColortoRow(self, table, rowIndex, color):
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)

    def fill_search_table(self):
        current_date = datetime.today().date()
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        if self.checkbox.isChecked() == False:
            command = 'select * from appointments order by DATE(date),time(from_) asc '
            result = cursor.execute(command)
            result = result.fetchall()
            self.search_table.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.search_table.insertRow(row_number)
                row_data = list(row_data)
                row_data[4] = datetime.strptime(row_data[4], '%H:%M').time().strftime('%I:%M %p')
                row_data[5] = datetime.strptime(row_data[5], '%H:%M').time().strftime('%I:%M %p')
                if datetime.strptime(row_data[3], '%Y-%m-%d').date() < current_date:
                    for column_number, data in enumerate(row_data):
                        self.search_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                        self.search_table.item(row_number, column_number).setBackground(QtGui.QColor('#d45050'))
                        # self.search_table.item(row_number, column_number).setForeground(QtGui.QColor('#c30000'))
                else:
                    for column_number, data in enumerate(row_data):
                        self.search_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                        #green
                        self.search_table.item(row_number, column_number).setBackground(QtGui.QColor('#83c27a'))
        else:
            command = 'select * from appointments where date >= ? order by DATE(date),time(from_) asc '
            result = cursor.execute(command, [current_date])
            result = result.fetchall()
            self.search_table.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.search_table.insertRow(row_number)
                row_data = list(row_data)
                row_data[4] = datetime.strptime(row_data[4], '%H:%M').time().strftime('%I:%M %p')
                row_data[5] = datetime.strptime(row_data[5], '%H:%M').time().strftime('%I:%M %p')
                for column_number, data in enumerate(row_data):
                    self.search_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                    #green
                    self.search_table.item(row_number, column_number).setBackground(QtGui.QColor('#83c27a'))
        db.commit()
        db.close()

    def fill_patient_history(self):
        try:

            current_date = datetime.today().date()
            db = sqlite3.connect(db_name)
            patient_id = self.patient_id.value()
            cursor = db.cursor()
            command = 'select appointment_id,first_name,date,from_,to_,note from appointments  where patient_id=?  order by DATE(date),time(from_) asc'
            result = cursor.execute(command, [patient_id])
            result = result.fetchall()
            self.patient_hisory_table.setRowCount(0)
            for row_number, row_data in enumerate(result):
                self.patient_hisory_table.insertRow(row_number)
                row_data = list(row_data)
                row_data[3] = datetime.strptime(row_data[3], '%H:%M').time().strftime('%I:%M %p')
                row_data[4] = datetime.strptime(row_data[4], '%H:%M').time().strftime('%I:%M %p')
                for column_number, data in enumerate(row_data):
                    self.patient_hisory_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        except Exception as e:
            print(e)

    def reset(self):
        for i in range(self.search_table.rowCount()):
            self.search_table.setRowHidden(i, False)
        self.date_search_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.search_edit.setText("")

    def new_p_id_fn(self):
        try:
            db_id = sqlite3.connect(db_name)
            cursor_id = db_id.cursor()
            get_id = 'select patient_id from patients order by patient_id desc limit 1 '
            id_case_selected_and_changedid = cursor_id.execute(get_id)
            id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
            new_id = id_case_selected_and_changedid[0] + 1
            db_id.close()
            return new_id
        except Exception as e:
            print(e)
            return 1

    def set_generate_patient_id(self):
        if self.Generate_flag:
            self.patient_id.setValue(self.new_p_id_fn())
            #new_edit

            # new_edit
            self.Generate_flag = False
        else:
            pass

    def reset_patient_info(self):
        self.patient_id.setValue(0)
        self.patient_name.setText("")
        self.patient_idd.setText("")
        self.fn.setText('')
        self.ln.setText('')
        self.pn.setText('')
        self.addr.setText('')
        self.email.setText('')
        self.notes.setText('')
        self.age.setValue(0)
        self.height.setValue(0)
        self.weight.setValue(0)
        self.allergies.setText("")
        self.conditions.setText("")
        self.smoking.setCurrentText("")
        self.Generate_flag = True
        
        
        


    def reset_appt_filter(self):
        self.check_fn()
        self.search_edit_appt.setText('')

    def search_by_fn(self):
        if self.values_combobox.currentText() == 'First Name':
            fn = self.search_edit.text().lower()
            for row in range(self.search_table.rowCount()):
                item = self.search_table.item(row, 1)
                self.search_table.setRowHidden(row, fn not in item.text().lower())

        else:
            if self.values_combobox.currentText() == 'Last Name':
                ln = self.search_edit.text().lower()
                for row in range(self.search_table.rowCount()):
                    item = self.search_table.item(row, 2)
                    self.search_table.setRowHidden(row, ln not in item.text().lower())

            else:
                if self.values_combobox.currentText() == 'Phone Number':
                    fn = self.search_edit.text()
                    for row in range(self.search_table.rowCount()):
                        item = self.search_table.item(row, 6)
                        self.search_table.setRowHidden(row, fn not in item.text())

                else:
                    if self.values_combobox.currentText() == 'Appointment ID':
                        id = self.search_edit.text()
                        for row in range(self.search_table.rowCount()):
                            item = self.search_table.item(row, 0)
                            self.search_table.setRowHidden(row, id not in item.text())

                    else:
                        pass
                    if self.values_combobox.currentText() == 'Note':
                        note = self.search_edit.text().lower()
                        for row in range(self.search_table.rowCount()):
                            item = self.search_table.item(row, 7)
                            self.search_table.setRowHidden(row, note not in item.text().lower())

    def search_by_fn_patient(self):
        if self.filter_pateint_val.currentText() == 'First Name':
            fn = self.search_edit_2.text().lower()
            for row in range(self.patients_table.rowCount()):
                item = self.patients_table.item(row, 1)
                self.patients_table.setRowHidden(row, fn not in item.text().lower())

        else:
            if self.filter_pateint_val.currentText() == 'Last Name':
                ln = self.search_edit_2.text().lower()
                for row in range(self.patients_table.rowCount()):
                    item = self.patients_table.item(row, 2)
                    self.patients_table.setRowHidden(row, ln not in item.text().lower())

            else:
                if self.filter_pateint_val.currentText() == 'Phone Number':
                    fn = self.search_edit_2.text()
                    for row in range(self.patients_table.rowCount()):
                        item = self.patients_table.item(row, 3)
                        self.patients_table.setRowHidden(row, fn not in item.text())

                else:
                    if self.filter_pateint_val.currentText() == 'Patient ID':
                        id = self.search_edit_2.text()
                        for row in range(self.patients_table.rowCount()):
                            item = self.patients_table.item(row, 0)
                            self.patients_table.setRowHidden(row, id not in item.text())

                    else:
                        pass
                    if self.filter_pateint_val.currentText() == 'Note':
                        note = self.search_edit_2.text().lower()
                        for row in range(self.patients_table.rowCount()):
                            item = self.patients_table.item(row, 6)
                            self.patients_table.setRowHidden(row, note not in item.text().lower())

    def search_by_fn_appt(self):
        if self.filter_values_combobox.currentText() == 'First Name':
            fn = self.search_edit_appt.text().lower()
            for row in range(self.check_table.rowCount()):
                item = self.check_table.item(row, 1)
                self.check_table.setRowHidden(row, fn not in item.text().lower())

        else:
            if self.filter_values_combobox.currentText() == 'Last Name':
                ln = self.search_edit_appt.text().lower()
                for row in range(self.check_table.rowCount()):
                    item = self.check_table.item(row, 2)
                    self.check_table.setRowHidden(row, ln not in item.text().lower())

            else:
                if self.filter_values_combobox.currentText() == 'Phone Number':
                    fn = self.search_edit_appt.text()
                    for row in range(self.check_table.rowCount()):
                        item = self.check_table.item(row, 6)
                        self.check_table.setRowHidden(row, fn not in item.text())

                else:
                    if self.filter_values_combobox.currentText() == 'Appointment ID':
                        id = self.search_edit_appt.text()
                        for row in range(self.check_table.rowCount()):
                            item = self.check_table.item(row, 0)
                            self.check_table.setRowHidden(row, id not in item.text())

                    else:
                        pass
                    # if self.filter_values_combobox.currentText() == 'Note':
                    #     note = self.search_edit_appt.text().lower()
                    #     for row in range(self.check_table.rowCount()):
                    #         item = self.check_table.item(row, 7)
                    #         self.check_table.setRowHidden(row, note not in item.text().lower())

    def patient_table_row_selected(self, current, previos):
        try:
            selected_row = current.row()
            if selected_row >= 0:
                id = self.patients_table.item(selected_row, 0).text()
                conn = sqlite3.connect(db_name)
                id = int(id)
                cur = conn.cursor()
                command = 'select * from patients where patient_id=?'
                result = cur.execute(command, [id])
                result = result.fetchone()
                self.patient_name.setText("{} {}".format(result[1], result[2]))
                self.patient_idd.setText(str(result[0]))
                self.patient_id.setValue(result[0])
                self.fn.setText(result[1])
                self.ln.setText(result[2])
                self.pn.setText(result[3])
                self.addr.setText(result[4])
                self.email.setText(result[5])
                self.notes.setText(result[6])
                self.age.setValue(0) if result[7] is None else self.age.setValue(int(result[7]))
                self.height.setValue(0)   if result[8] is None else self.height.setValue(result[8])
                self.weight.setValue(0) if result[9] is None  else self.weight.setValue(result[9])
                self.allergies.setText("") if result[10] is None  else self.smoking.setCurrentText(result[10])
                self.smoking.setCurrentText("") if result[11] is None  else self.allergies.setText(result[11])
                self.conditions.setText("") if result[12] is None else self.conditions.setText(result[12])
                self.Generate_flag = True
        except Exception as e:
            print(e.__class__)

    def rows_selected(self, current, previos):
        selected_row = current.row()
        if selected_row >= 0:
            ##########################
            self.isclicked=True
            self.type_of_patient.setCurrentIndex(0)
            ##########################
            id = self.check_table.item(selected_row, 0).text()
            conn = sqlite3.connect(db_name)
            cur = conn.cursor()
            command = 'select * from appointments where appointment_id=?'
            result = cur.execute(command, [id])
            result = result.fetchone()
            self.id_spinbox.setValue(result[0])
            self.firstname_lineedit.setText(result[1])
            self.lastname_lineedit.setText(result[2])
            self.date_edit.setDateTime(datetime.strptime(result[3], '%Y-%m-%d'))
            self.from_edit.setDateTime(datetime.strptime(result[4], '%H:%M'))
            self.to_edit.setDateTime(datetime.strptime(result[5], '%H:%M'))
            self.phone_lineedit.setText(result[6])
            self.note_edit.setText(result[7])
            self.price_spinbox.setValue(result[8])
            self.patient_id_fk.setValue(result[9])
            if result[9]==0:
                self.firstname_lineedit.setReadOnly(False)
                self.lastname_lineedit.setReadOnly(False)
            else:
                self.firstname_lineedit.setReadOnly(True)
                self.lastname_lineedit.setReadOnly(True)

    def mb_btn_clicked(self, btn):
        try:
            conn = sqlite3.connect(db_name)
            id = self.patient_id.value()
            id = int(id)
            cur = conn.cursor()
            command = 'select patient_id,first_name,last_name,phone_number,notes from patients where patient_id=?'
            result = cur.execute(command, [id])
            result = result.fetchone()
            if btn.text() == "&Yes":
                self.tabwidget.setCurrentIndex(1)
                self.patient_id_fk.setValue(result[0])
                self.firstname_lineedit.setText(result[1])
                self.lastname_lineedit.setText(result[2])
                self.phone_lineedit.setText(result[3])
                self.note_edit.setText(result[4])
                self.price_spinbox.setValue(0)
                self.firstname_lineedit.setReadOnly(True)
                self.lastname_lineedit.setReadOnly(True)
                self.p_to_appt_flag = True
                #new
                db_id = sqlite3.connect(db_name)
                cursor_id = db_id.cursor()
                get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
                id_case_selected_and_changedid = cursor_id.execute(get_id)
                id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
                self.id_spinbox.setValue(id_case_selected_and_changedid[0] + 1)
                self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
                self.auto_fill_time
                db_id.close()
                #new
            else:
                pass
        except Exception as e:
            print(e)

    def handel_buttons(self):
        # self.refresh_btn.clicked.connect(self.refresh_fn)
        #self.add_btn.clicked.connect(self.add_btn_clicked_new)
        ################
        self.show_advanced_search.clicked.connect(lambda:self.advanced_search_gb.show())
        self.show_advanced_search.clicked.connect(lambda:self.advanced_search_gb.setMinimumHeight(500))
        self.show_advanced_search.clicked.connect(lambda: self. groupBox_2.setMaximumHeight(0))
        self.hide_advanced_search.clicked.connect(lambda: self.advanced_search_gb.hide())
        #self.hide_advanced_search.clicked.connect(lambda: self.advanced_search_gb.setMinimumHeight(0))
        self.hide_advanced_search.clicked.connect(lambda: self.groupBox_2.setMaximumHeight(350))

        ################
        self.reset_patient.clicked.connect(self.reset_patient_info)
        self.add_btn.clicked.connect(self.add)
        self.check_btn.clicked.connect(self.sort_by_date_fn_appt)
        self.search_by_date_btn.clicked.connect(self.search_btn_clicked)
        self.modify_btn.clicked.connect(self.modify)
        self.delete_btn.clicked.connect(self.delete_fn)
        self.list_btn.clicked.connect(self.list_fn)
        self.enter_btn.clicked.connect(self.enter_fn)
        self.reset_btn.clicked.connect(self.reset)
        self.add_btn_2.clicked.connect(self.patient_add_fn)
        self.delete_btn_2.clicked.connect(self.del_patient)
        self.modify_btn_2.clicked.connect(self.modify_patient)
        self.add_patient_info.clicked.connect(self.add_patient_info_to_appt)
        self.p_history.clicked.connect(self.fill_patient_history)
        self.generate_patient_id.clicked.connect(self.set_generate_patient_id)
        self.checkbox.stateChanged.connect(self.fill_search_table)
        self.reset_btn_appt.clicked.connect(self.reset_appt_filter)
        self.show_statistics.clicked.connect(self.stats_fn)
        self.stats.clicked.connect(lambda : self.stackedWidget_stats.setCurrentIndex(0))
        self.charts.clicked.connect(lambda: self.stackedWidget_stats.setCurrentIndex(1))
        self.bar_chart.clicked.connect(lambda: self.charts_stacked_widget.setCurrentIndex(1))
        self.line_chart.clicked.connect(lambda: self.charts_stacked_widget.setCurrentIndex(0))
        self.bar_chart.clicked.connect(self.bar_chart_fn)
        self.line_chart.clicked.connect(self.line_chart_fn)
        self.search_pb.clicked.connect(lambda: self.tabwidget.setCurrentIndex(0))
        self.appointments_pb.clicked.connect(lambda: self.tabwidget.setCurrentIndex(1))
        self.patients_pb.clicked.connect(lambda: self.tabwidget.setCurrentIndex(2))
        self.statistics_pb.clicked.connect(lambda: self.tabwidget.setCurrentIndex(3))
    def stats_total(self):
        try:

            db_check = sqlite3.connect(db_name)
            cursor_check = db_check.cursor()
            total_app= 'select count(appointment_id) from appointments '
            total_check = cursor_check.execute(total_app)
            total_check = total_check.fetchone()
            total_patients= 'select count(patient_id) from patients '
            total_p = cursor_check.execute(total_patients)
            total_p = total_p.fetchone()
            db_check.close()
            self.total_patients.setText(str(total_p[0]))
            self.total_app.setText(str(total_check[0]))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
    def stats_yesterday_tomorrow_today_nextweek(self):
        try:
            td=date.today()
            tm=td + timedelta(days=1)
            yd= td - timedelta(days=1)
            nw=td + timedelta(days=7)
            db_check = sqlite3.connect(db_name)
            cursor_check = db_check.cursor()
            app_td= 'select count(appointment_id) from appointments where date==?'
            td_check = cursor_check.execute(app_td,[td])
            td_check = td_check.fetchone()
            app_tm= 'select count(appointment_id) from appointments where date==? '
            tm_check = cursor_check.execute(app_tm,[tm])
            tm_check = tm_check.fetchone()
            app_yd = 'select count(appointment_id) from appointments where date==? '
            yd_check = cursor_check.execute(app_yd,[yd])
            yd_check = yd_check.fetchone()
            app_nw = 'select count(appointment_id) from appointments where date>? and date<=?'
            nw_check = cursor_check.execute(app_nw, [td,nw])
            nw_check = nw_check.fetchone()
            db_check.close()
            print("#######################")
            print(td_check,tm_check,yd_check,nw_check)
            print(td,nw)
            print(nw-td)

            self.num_app_td.setText(str(td_check[0]))
            self.num_app_tm.setText(str(tm_check[0]))
            self.num_app_yd.setText(str(yd_check[0]))
            self.num_app_nw.setText(str(nw_check[0]))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)

    def stats_fn(self):
        try:

            st=str(self.start.date().toPyDate())
            en=str(self.end.date().toPyDate())
            db_check = sqlite3.connect(db_name)
            cursor_check = db_check.cursor()
            command_check = 'select count(appointment_id),sum(price) from appointments where date>=? and date<=? '
            result_check = cursor_check.execute(command_check, [st,en])
            result_check = result_check.fetchall()
            db_check.close()
            print(result_check)
            self.revenue.setText(str(result_check[0][1]))
            self.num_patients.setText(str(result_check[0][0]))
            self.period_of_stats.setText("These are the stats of the period from: {} to: {}".format(st,en))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
    def update_mpl(self):
        self.ax1.clear()
        self.ax1.bar(self.names,self.values)

        self.ax1.set_ylabel("Number of Appointments")
        if self.d_m_y.currentText()=="daily":
            b="Days of the Week"
        elif self.d_m_y.currentText()=="monthly":
            b = "Months of the Year"
        elif self.d_m_y.currentText()=="yearly":
            b = "Years"
        self.ax1.set_title("{} Appointments Bar Chart".format(self.d_m_y.currentText()))
        self.ax1.set_xlabel(b)
        self.fig.canvas.draw_idle()

    def bar_chart_fn(self):
        try:

            db_check = sqlite3.connect(db_name)
            cursor_check = db_check.cursor()
            if self.d_m_y.currentText()=="daily":
                self.d='days'
                command_check = """select count(appointment_id),case cast(strftime('%w', date) as integer) 
                                                          when 0 then 'Sunday'
                                                          when 1 then 'Monday'
                                                          when 2 then 'Tuesday'
                                                          when 3 then 'Wednesday'
                                                          when 4 then 'Thursday'
                                                          when 5 then 'Friday'
                                                          else 'Saturday' end
                                    from appointments group by case cast(strftime('%w', date) as integer) 
                                                          when 0 then 'Sunday'
                                                          when 1 then 'Monday'
                                                          when 2 then 'Tuesday'
                                                          when 3 then 'Wednesday'
                                                          when 4 then 'Thursday'
                                                          when 5 then 'Friday'
                                                          else 'Saturday' end """
            elif self.d_m_y.currentText()=="monthly":
                self.d="months"
                command_check="""select count(appointment_id),case cast(strftime('%m', date) as integer) 
                                                          when 1 then 'Jan'
                                                          when 2 then 'Feb'
                                                          when 3 then 'Mar'
                                                          when 4 then 'Apr'
                                                          when 5 then 'May'
                                                          when 6 then 'Jun'
                                                          when 7 then 'Jul'
                                                          when 8 then 'Aug'
                                                          when 9 then 'Sep'
                                                          when 10 then 'Oct'
                                                          when 11 then 'NOv'
                                                          else 'Dec' end
                                    from appointments group by case cast(strftime('%m', date) as integer) 
                                                          when 1 then 'Jan'
                                                          when 2 then 'Feb'
                                                          when 3 then 'Mar'
                                                          when 4 then 'Apr'
                                                          when 5 then 'May'
                                                          when 6 then 'Jun'
                                                          when 7 then 'Jul'
                                                          when 8 then 'Aug'
                                                          when 9 then 'Sep'
                                                          when 10 then 'Oct'
                                                          when 11 then 'NOv'
                                                          else 'Dec' end """
            elif self.d_m_y.currentText()=="yearly":
                self.d="years"
                command_check="""select count(appointment_id) , strftime('%Y', date) from appointments group by strftime('%Y', date) """

            result_check = cursor_check.execute(command_check)
            result_check = result_check.fetchall()
            db_check.close()
            for i in range(len(result_check)):
                self.values.append(result_check[i][0])
                self.names.append(result_check[i][1])

            send_fig = QtCore.pyqtSignal(str)
            self.update_mpl()
            self.show()
            self.names = []
            self.values = []
        #
        #     print(result_check)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
    def update_line_chart(self):
        self.ax2.clear()
        self.ax2.plot(self.names1,self.values1)

        self.ax2.set_ylabel("Revenue")

        self.ax2.set_title("revenue by time Chart")
        self.ax2.set_xlabel("Time/Date")
        self.fig2.canvas.draw_idle()

    def line_chart_fn(self):
        try:
            db_check2 = sqlite3.connect(db_name)
            cursor_check2 = db_check2.cursor()
            command_check2 = """select sum(price) , date from appointments group by date """

            result_check2 = cursor_check2.execute(command_check2)
            result_check2 = result_check2.fetchall()
            db_check2.close()
            for i in range(len(result_check2)):
                self.values1.append(result_check2[i][0])
                self.names1.append(result_check2[i][1])
            #send_fig = QtCore.pyqtSignal(str)
            # print(len(self.names1))
            # print(len(self.values1))
            # self.Widget.LinePlot([30,20,60],[50,60,20])
            self.update_line_chart()
            self.names1 = []
            self.values1 = []

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)


        #self.select_date.clicked.connect(lambda: self.minmax())
    # def minmax(self):
    #     try:
    #         height=self.select_date_frame.height()
    #         size=self.select_date_frame.size()
    #         #width=self.select_date_frame.width()
    #         print(height)
    #         print(size)
    #         if height ==0:
    #             s=QSize(569, 300)
    #         else:
    #             newHeight =28
    #             s=QSize(569, 0)
    #         self.animation=QPropertyAnimation(self.select_date_frame,b"size")
    #         self.animation.setDuration(100)
    #         self.animation.setStartValue(size)
    #         self.animation.setEndValue(s)
    #         #self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
    #         self.animation.start()
    #     except Exception as e:
    #
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #         print(exc_type, fname, exc_tb.tb_lineno, e)

    def add_patient_info_to_appt(self):
        try:
            conn = sqlite3.connect(db_name)
            id = self.patient_idd.text()
            # id=self.patient_id.value()
            id = int(id)
            cur = conn.cursor()
            command = 'select patient_id,first_name,last_name,phone_number,notes from patients where patient_id=?'
            result = cur.execute(command, [id])
            result = result.fetchone()
            sp = "the patient with the following info will be added to the appointmet:\n\nPatient ID: {}\nFirst name: {}\nLast Name: {}\nPhone Number: {}\nNote: {} ".format(
                result[0], result[1], result[2], result[3], result[4])
            popup = self.patient_info_mb
            popup.setIcon(QMessageBox.Question)
            popup.setText(sp)
            #popup.move(self.frameGeometry().x() + self.frameGeometry().width() / 2, 400)
            popup.setSizeGripEnabled(True)
            popup.setWindowTitle('Patients information')
            popup.setStyleSheet('QLabel{font-weight:bold;}')
            popup.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            popup.buttonClicked.connect(self.mb_btn_clicked)
            popup.exec_()

        except Exception as e:
            print(e)
            self.patients_error.setStyleSheet('color: red')
            self.patients_error.setText("the patient is not registered so it can't be added to the appointments")

    def del_patient(self):
        try:
            db_check_id = sqlite3.connect(db_name)
            cursor_check_id = db_check_id.cursor()
            command_check_id = 'select patient_id from patients '
            result_check_id = cursor_check_id.execute(command_check_id).fetchall()
            db_check_id.close()

            id = self.patient_id.value()
            id_list = []
            for i in result_check_id:
                id_list.append(i[0])

            if id in id_list:
                db = sqlite3.connect(db_name)
                cursor = db.cursor()
                command = 'DELETE from patients where patient_id=?'
                cursor.execute(command, [id])
                db.commit()
                db.close()
                self.patients_table_fill()
                self.stats_total()
                db_id = sqlite3.connect(db_name)
                cursor_id = db_id.cursor()
                get_id = 'select patient_id from patients order by patient_id desc limit 1 '
                id_case_selected_and_changedid = cursor_id.execute(get_id)
                id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
                db_id.close()
                self.patients_error.setStyleSheet('color: green')
                self.patients_error.setText('The patient has been deleted')
                self.patient_name.setText("")
                try:
                    self.patient_idd.setText("")
                    self.patient_id.setValue(0)
                    self.fn.setText('')
                    self.ln.setText('')
                    self.pn.setText('')
                    self.addr.setText('')
                    self.email.setText('')
                    self.notes.setText('')
                    self.age.setValue(0)
                    self.height.setValue(0)
                    self.weight.setValue(0)
                    self.allergies.setText("")
                    self.conditions.setText("")
                except:
                    self.patient_id.setValue(1)
                    self.fn.setText('')
                    self.ln.setText('')
                    self.pn.setText('')
                    self.addr.setText('')
                    self.email.setText('')
                    self.notes.setText('')
                    self.age.setValue(0)
                    self.height.setValue(0)
                    self.weight.setValue(0)
                    self.allergies.setText("")
                    self.conditions.setText("")
            else:
                self.patients_error.setStyleSheet('color: red')
                self.patients_error.setText("the patient is not registered so it can't be deleted")
        except Exception as e:
            print(e.__class__)

    def patient_add_fn(self):
        try:
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            patient_id = self.patient_id.value()
            first_name = self.fn.text().lower()
            last_name = self.ln.text().lower()
            phone_number = self.pn.text()
            address = self.addr.text()
            email = self.email.text()
            note = self.notes.text()
            age = self.age.value()
            height = self.height.value()
            weight = self.weight.value()
            smoking = self.smoking.currentText()
            allergies = self.allergies.text()
            conditions = self.conditions.text()
            row = (patient_id, first_name, last_name, phone_number, address, email, note, age, height, weight, smoking,
                   allergies, conditions)
            command = 'insert into patients (patient_id,first_name,last_name,phone_number,address,email,notes,dob,height,weight,smoking,allergies,conditions) values (?,?,?,?,?,?,?,?,?,?,?,?,?)'
            if first_name == "":
                self.patients_error.setStyleSheet('color: red')
                self.patients_error.setText("The First Name Cannot be Empty")
            else:
                if patient_id == 0:
                    self.errormsgbox.setIcon(QMessageBox.Question)
                    self.errormsgbox.setText(
                        "The Patient ID Cannot be 0, Please click on the Generate New Patient Id Button")
                    self.errormsgbox.setWindowTitle('Error')
                    self.errormsgbox.setSizeGripEnabled(True)
                    self.errormsgbox.move(self.frameGeometry().x() + self.frameGeometry().width() / 2, 400)
                    self.errormsgbox.exec_()
                else:
                    result = cursor.execute(command, row)
                    db.commit()
                    db.close()
                    self.stats_total()
                    self.patients_table_fill()
                    # to check the last id and add one to it to make it
                    self.patient_name.setText("")
                    self.patient_idd.setText("")
                    self.patient_id.setValue(0)
                    self.fn.setText('')
                    self.ln.setText('')
                    self.pn.setText('')
                    self.addr.setText('')
                    self.email.setText('')
                    self.notes.setText('')
                    self.age.setValue(0)
                    self.height.setValue(0)
                    self.weight.setValue(0)
                    self.allergies.setText("")
                    self.conditions.setText("")
                    self.patients_error.setStyleSheet('color: green')
                    self.patients_error.setText("The Patient Has Been Added Successfully")
                    self.Generate_flag = True
        except sqlite3.IntegrityError:
            db_id = sqlite3.connect(db_name)
            cursor_id = db_id.cursor()
            get_id = 'select patient_id from patients order by patient_id desc limit 1 '
            id_case_selected_and_changedid = cursor_id.execute(get_id)
            id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
            new_id = id_case_selected_and_changedid[0] + 1
            db_id.close()
            self.patients_error.setStyleSheet('color: red')
            self.patients_error.setText("the patient already exist the next available id is {}".format(new_id))

    def modify_patient(self):
        try:
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            patient_id = int(self.patient_idd.text())
            first_name = self.fn.text().lower()
            last_name = self.ln.text().lower()
            phone_number = self.pn.text()
            address = self.addr.text()
            email = self.email.text()
            note = self.notes.text()
            age = self.age.value()
            height = self.height.value()
            weight = self.weight.value()
            smoking = self.smoking.currentText()
            allergies = self.allergies.text()
            conditions = self.conditions.text()
            row = (first_name, last_name, phone_number, address, email, note, age, height, weight, smoking, allergies,
                   conditions, patient_id)
            command = 'update  patients set first_name=?,last_name=?,phone_number=?,address=?,email=?,notes=?,dob=?,height=?,weight=?,smoking=?,allergies=?,conditions=? where patient_id==?'
            row_update_appointment = (first_name, last_name, phone_number, note, patient_id)
            command_updating_appointmnet = "update appointments set first_name=?,last_name=?,phone_number=? ,note=? where patient_id=?"

            db_check_id = sqlite3.connect(db_name)
            cursor_check_id = db_check_id.cursor()
            command_check_id = 'select patient_id from patients '
            result_check_id = cursor_check_id.execute(command_check_id).fetchall()
            db_check_id.close()

            id = self.patient_id.value()
            id_list = []
            for i in result_check_id:
                id_list.append(i[0])

            if id in id_list:
                if first_name == "":
                    self.patients_error.setStyleSheet('color: red;')
                    self.patients_error.setText("The First Name Cannot be Empty")
                else:

                    result = cursor.execute(command, row)
                    result2 = cursor.execute(command_updating_appointmnet, row_update_appointment)
                    db.commit()
                    db.close()
                    self.check_fn()
                    self.patients_table_fill()
                    self.fill_search_table()
                    # to check the last id and add one to it to make it
                    self.patient_name.setText("{} {}".format(first_name, last_name))
                    self.patient_id.setValue(0)
                    self.fn.setText('')
                    self.ln.setText('')
                    self.pn.setText('')
                    self.addr.setText('')
                    self.email.setText('')
                    self.notes.setText('')
                    self.age.setValue(0)
                    self.height.setValue(0)
                    self.weight.setValue(0)
                    self.allergies.setText("")
                    self.conditions.setText("")
                    self.patients_error.setStyleSheet('color: green')
                    self.patients_error.setText("The Patient Record has been Modified Successfully")
            else:
                self.patients_error.setStyleSheet('color: red')
                self.patients_error.setText("The Patient Doesn't Exist")

        except Exception as e:
            self.patients_error.setStyleSheet('color: red')
            self.patients_error.setText("The Patient Doesn't Exist")
            print(e)

    def patients_table_fill(self):
        current_date = datetime.today().date()
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        command = 'SELECT * from patients  '
        result = cursor.execute(command)
        result = result.fetchall()
        self.patients_table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.patients_table.insertRow(row_number)
            row_data = list(row_data)
            for column_number, data in enumerate(row_data):
                self.patients_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        db.commit()
        db.close()

    def enter_fn(self):
        key = self.license_edit.text()
        try:
            if verify(key):
                db = sqlite3.connect('license.db')
                cursor = db.cursor()
                cursor_getserialnummber = db.cursor()
                command_get = 'SELECT serial_number from license where license_key=?'
                command = 'insert into license values(?,?)'
                result = cursor_getserialnummber.execute(command_get, [key])
                result = result.fetchone()
                if result is None:
                    cursor.execute(command, [key, getMachine_addr()])
                    db.commit()
                    db.close()
                    self.stackedWidget.setCurrentWidget(self.main_page)
                else:
                    if result[0] == getMachine_addr():
                        print('good')
                        self.stackedWidget.setCurrentWidget(self.main_page)
                        db.close()
                    else:
                        self.validation_error.setText('the key is not yours')
                        db.close()
            else:
                self.validation_error.setText('the key is invalid')
        except IndexError:
            self.validation_error.setText('the key is invalid')

    def search_btn_clicked(self):
        date = str(self.date_search_edit.date().toPyDate())
        item_row = []
        for row in range(self.search_table.rowCount()):
            item = self.search_table.item(row, 3)
            if date == item.text():
                item_row.append(row)

        for i in range(self.search_table.rowCount()):
            self.search_table.setRowHidden(i, i not in item_row)

    def auto_fill_time(self):
        start_time = datetime.strptime('8:00', '%H:%M')
        close_time = datetime.strptime('18:00', '%H:%M')
        delta = timedelta(hours=1)
        try:
            date = str(QtCore.QDateTime.currentDateTime().date().toPyDate())
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            command = 'SELECT from_,to_ FROM appointments where date=? order by time(from_) ASC '
            result = cursor.execute(command, [date])
            result = result.fetchall()
            db.close()
            available_times = []
            delta = timedelta(hours=1)
            slot = ()
            popup = ''
            for i in range(len(result)):
                if datetime.strptime(result[i][0], '%H:%M') < start_time:
                    start_time = datetime.strptime(result[i][0], '%H:%M')
                if close_time < datetime.strptime(result[i][1], '%H:%M'):
                    close_time = datetime.strptime(result[i][1], '%H:%M')

            if len(result) != 0:
                if datetime.strptime(str(datetime.strptime(result[0][0], '%H:%M') - start_time),
                                     '%H:%M:%S') > datetime.strptime('0:00', '%H:%M'):
                    free_time_in_hours = int(
                        (datetime.strptime(result[0][0], '%H:%M') - start_time).total_seconds() / (60.0 * 60.0))
                    if free_time_in_hours >= 1:
                        fr = start_time
                        delta = timedelta(hours=1)
                        to = fr + delta
                        for i in range(free_time_in_hours):
                            slot = (fr.time().strftime('%I:%M %p'), to.time().strftime('%I:%M %p'))
                            available_times.append(slot)
                            # if to<datetime.strptime(result[0][0], '%H:%M'):
                            fr, to = to, to + delta
                            # else:
                    else:
                        slot = (
                            start_time.strftime('%I:%M %p'),
                            datetime.strptime(result[0][0], '%H:%M').time().strftime('%I:%M %p'))
                        available_times.append(slot)
                for number, value in enumerate(result):
                    if number < len(result) - 1:
                        if datetime.strptime(
                                str(datetime.strptime(result[(number + 1)][0], '%H:%M') - datetime.strptime(
                                        result[number][1], '%H:%M')), '%H:%M:%S') > datetime.strptime('0:00', '%H:%M'):
                            free_time_in_hours = int(
                                (datetime.strptime(result[(number + 1)][0], '%H:%M') - datetime.strptime(
                                    result[number][1], '%H:%M')).total_seconds() / (60.0 * 60.0))
                            if free_time_in_hours >= 1:
                                fr = datetime.strptime(result[number][1], '%H:%M')
                                delta = timedelta(hours=1)
                                to = fr + delta
                                for i in range(free_time_in_hours):
                                    slot = (fr.time().strftime('%I:%M %p'), to.time().strftime('%I:%M %p'))
                                    available_times.append(slot)
                                    fr, to = to, to + delta
                            else:
                                slot = (datetime.strptime(result[number][1], '%H:%M').time().strftime('%I:%M %p'),
                                        datetime.strptime(result[(number + 1)][0], '%H:%M').time().strftime(
                                            '%I:%M %p'))
                                available_times.append(slot)

                if datetime.strptime(str(close_time - datetime.strptime(result[(len(result) - 1)][1], '%H:%M')),
                                     '%H:%M:%S') > datetime.strptime('0:00', '%H:%M'):
                    free_time_in_hours = int(
                        (close_time - datetime.strptime(result[(len(result) - 1)][1], '%H:%M')).total_seconds() / (
                                    60.0 * 60.0))
                    if free_time_in_hours >= 1:
                        fr = datetime.strptime(result[(len(result) - 1)][1], '%H:%M')
                        delta = timedelta(hours=1)
                        to = fr + delta
                        for i in range(free_time_in_hours):
                            slot = (fr.time().strftime('%I:%M %p'), to.time().strftime('%I:%M %p'))
                            available_times.append(slot)
                            # if to<datetime.strptime(result[0][0], '%H:%M'):
                            fr, to = to, to + delta
                            # else:
                    else:

                        slot = (datetime.strptime(result[(len(result) - 1)][1], '%H:%M').time().strftime('%I:%M %p'),
                                close_time.strftime('%I:%M %p'))
                        available_times.append(slot)
                self.from_edit.setDateTime(datetime.strptime(available_times[0][0], '%I:%M %p'))
                self.to_edit.setDateTime(datetime.strptime(available_times[0][1], '%I:%M %p'))
            else:

                self.from_edit.setDateTime(datetime.strptime(start_time.strftime('%I:%M %p'), '%I:%M %p'))
                self.to_edit.setDateTime(datetime.strptime((start_time + delta).strftime('%I:%M %p'), '%I:%M %p'))

        except Exception as e:
            print("okkk")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
            self.from_edit.setDateTime(datetime.strptime(start_time.strftime('%I:%M %p'), '%I:%M %p'))
            self.to_edit.setDateTime(datetime.strptime((start_time + delta).strftime('%I:%M %p'), '%I:%M %p'))

    def modify(self):
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        first_name = self.firstname_lineedit.text().lower()
        last_name = self.lastname_lineedit.text().lower()
        date = str(self.date_edit.date().toPyDate())
        fromm = str(self.from_edit.time().toPyTime().strftime('%H:%M'))
        to = str(self.to_edit.time().toPyTime().strftime('%H:%M'))
        phone_number = self.phone_lineedit.text()
        note = self.note_edit.text()
        price = self.price_spinbox.value()
        id = self.id_spinbox.value()
        patient_id = self.patient_id_fk.value()
        row = (first_name, last_name, date, fromm, to, phone_number, note, price, id)
        command = 'update  appointments set first_name=?,last_name=?,date=?,from_=?,to_=?,phone_number=?,note=?,price=? where appointment_id=?'
        db_check = sqlite3.connect('clients.db')
        cursor_check = db_check.cursor()
        command_check = 'select from_,to_ from appointments where date=? and appointment_id!=?'
        result_check = cursor_check.execute(command_check, [date, id])
        result_check = result_check.fetchall()
        db_check.close()
        db_id = sqlite3.connect(db_name)
        cursor_id = db_id.cursor()
        get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
        db_check_id = sqlite3.connect(db_name)
        cursor_check_id = db_check_id.cursor()
        command_check_id = 'select appointment_id from appointments '
        result_check_id = cursor_check_id.execute(command_check_id).fetchall()
        db_check_id.close()
        flag_id = False
        for i in result_check_id:
            if i[0] == id:
                flag_id = True
                break

        flag = True
        error_message = ''
        for i, j in result_check:
            if not datetime.strptime(fromm, '%H:%M').time() < datetime.strptime(i, '%H:%M').time() < datetime.strptime(
                    to, '%H:%M').time():
                if not datetime.strptime(fromm, '%H:%M').time() < datetime.strptime(j,
                                                                                    '%H:%M').time() < datetime.strptime(
                        to, '%H:%M').time():
                    if not datetime.strptime(i, '%H:%M').time() < datetime.strptime(fromm,
                                                                                    '%H:%M').time() < datetime.strptime(
                            j, '%H:%M').time():
                        if not datetime.strptime(i, '%H:%M').time() < datetime.strptime(to,
                                                                                        '%H:%M').time() < datetime.strptime(
                                j, '%H:%M').time():
                            if datetime.strptime(fromm, '%H:%M').time() == datetime.strptime(i, '%H:%M').time():
                                if datetime.strptime(to, '%H:%M').time() == datetime.strptime(j, '%H:%M').time():
                                    pass
                                flag = False
                                error_message = 'it contradicts with a slot from {} to {}'.format(
                                    datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                                    datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                                break
                        else:
                            flag = False
                            error_message = 'it contradicts with a slot from {} to {}'.format(
                                datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                                datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                            break
                    else:
                        flag = False
                        error_message = 'it contradicts with a slot from {} to {}'.format(
                            datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                            datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                        break
                else:
                    flag = False
                    error_message = 'it contradicts with a slot from {} to {}'.format(
                        datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                        datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                    break
            else:
                flag = False
                error_message = 'it contradicts with a slot from {} to {}'.format(
                    datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                    datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                break

        if datetime.strptime(fromm, '%H:%M').time() < datetime.strptime(to, '%H:%M').time():
            if len(first_name) > 0:
                if flag_id == True:
                    if flag == True:

                        result = cursor.execute(command, row)
                        db.commit()
                        id_result = cursor_id.execute(get_id)
                        id_result = id_result.fetchone()
                        db_id.close()
                        self.firstname_lineedit.setText('')
                        self.lastname_lineedit.setText('')
                        self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
                        # change to first avalble times
                        self.auto_fill_time()
                        # self.from_edit.setDateTime(datetime.strptime('8:00am', '%I:%M%p'))
                        # self.to_edit.setDateTime(datetime.strptime('8:00pm', '%I:%M%p'))
                        self.phone_lineedit.setText('')
                        self.note_edit.setText('')
                        self.price_spinbox.setValue(0)
                        self.id_spinbox.setValue(id_result[0] + 1)
                        db.close()
                        self.error.setStyleSheet('color: green')
                        self.error.setText('The Appointment has been Modified')
                        self.fill_search_table()
                        self.check_fn()
                        self.stats_yesterday_tomorrow_today_nextweek()

                    else:
                        self.error.setStyleSheet('color: red')
                        self.error.setText(
                            'Time slot is not empty, ' + error_message + ', please choose another period')
                        db.close()
                else:
                    self.error.setStyleSheet('color: red')
                    self.error.setText("The appointment doesn't exist so it can't be modified")
            else:
                self.error.setStyleSheet('color: red')
                self.error.setText("The first name can't be empty")
        else:
            self.error.setStyleSheet('color: red')
            self.error.setText("the 'From time' can't be greater than or equal to the 'To time'")

    # def refresh_fn(self):
    #     current_date = datetime.today().date()
    #     db = sqlite3.connect(db_name)
    #     cursor = db.cursor()
    #     command = 'SELECT * from appointments where date>=? order by DATE(date),time(from_) asc '
    #     result = cursor.execute(command, [current_date])
    #     result = result.fetchall()
    #     self.table_schedule.setRowCount(0)
    #     for row_number, row_data in enumerate(result):
    #         self.table_schedule.insertRow(row_number)
    #         row_data = list(row_data)
    #         row_data[4] = datetime.strptime(row_data[4], '%H:%M').time().strftime('%I:%M %p')
    #         row_data[5] = datetime.strptime(row_data[5], '%H:%M').time().strftime('%I:%M %p')
    #         for column_number, data in enumerate(row_data):
    #             self.table_schedule.setItem(row_number, column_number, QTableWidgetItem(str(data)))
    #             self.table_schedule.item(row_number, column_number).setBackground(QtGui.QColor('green'))
    #
    #     db.commit()
    #     db.close()
    # def add_btn_clicked(self, btn):
    #     try:
    #         conn = sqlite3.connect(db_name)
    #         id = self.patient_id_fk.value()
    #         id = int(id)
    #         cur = conn.cursor()
    #         command = 'select patient_id,first_name,last_name,phone_number,notes from patients where patient_id=?'
    #         result = cur.execute(command, [id])
    #         result = result.fetchone()
    #         print(btn.text())
    #         if btn.text() == "&Yes":
    #             self.firstname_lineedit.setText(result[1])
    #             self.lastname_lineedit.setText(result[2])
    #             self.phone_lineedit.setText(result[3])
    #             self.note_edit.setText(result[4])
    #             # print(btn.text())
    #         else:
    #             print(btn.text())
    #             self.no_clicked = True
    #     except Exception as e:
    #         print("ok")
    #         print(e)

    # def add_existing_patient_info_to_appt(self):
    #     try:
    #         conn = sqlite3.connect(db_name)
    #         id = self.patient_id_fk.value()
    #         id = int(id)
    #         cur = conn.cursor()
    #         command = 'select patient_id,first_name,last_name,phone_number,notes from patients where patient_id=?'
    #         result = cur.execute(command, [id])
    #         result = result.fetchone()
    #         sp = "the patient exist and the following info will be added in the appointmet:\n\nPatient ID: {}\nFirst name: {}\nLast Name: {}\nPhone Number: {}\nNote: {} ".format(
    #             result[0], result[1], result[2], result[3], result[4])
    #         popup = self.patient_info_mb
    #         popup.setIcon(QMessageBox.Question)
    #         popup.setText(sp)
    #         popup.move(self.frameGeometry().x() + self.frameGeometry().width() / 2, 400)
    #         popup.setSizeGripEnabled(True)
    #         popup.setWindowTitle('Patients information')
    #         popup.setStyleSheet('QLabel{font-weight:bold;}')
    #         popup.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    #         # popup.setWindowFlags(QtCore.Qt.CustomizeWindowHint|QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowSystemMenuHint)
    #         popup.buttonClicked.connect(self.add_btn_clicked)
    #         b = popup.exec_()
    #
    #     except Exception as e:
    #         print(e)
    #         self.patients_error.setStyleSheet('color: red')
    #         self.patients_error.setText("the patient is not registered so it can't be added to the appointments")
    def check_p_id_in_p_table(self,idd):
        db_check_id = sqlite3.connect(db_name)
        cursor_check_id = db_check_id.cursor()
        command_check_id = 'select patient_id from patients '
        result_check_id = cursor_check_id.execute(command_check_id).fetchall()
        db_check_id.close()

        id_list = []
        for i in result_check_id:
            id_list.append(i[0])

        if idd in id_list:
            return True
        else:
            return False


    # def add_btn_clicked_new(self):
    #     #############################
    #     db_check_id = sqlite3.connect(db_name)
    #     cursor_check_id = db_check_id.cursor()
    #     command_check_id = 'select patient_id from patients '
    #     result_check_id = cursor_check_id.execute(command_check_id).fetchall()
    #     db_check_id.close()
    #
    #     id = self.patient_id_fk.value()
    #     id_list = []
    #     for i in result_check_id:
    #         id_list.append(i[0])
    #     if id in id_list:
    #         self.p_id_not_in_plist = False
    #     if id in id_list and self.p_to_appt_flag == False:
    #         self.add_existing_patient_info_to_appt()

    # self.p_id_check = True
    # self.p_id_not_in_plist = False
    # self.p_to_appt_flag == False

    def p_choosen(self):
        db_id = sqlite3.connect(db_name)
        cursor_id = db_id.cursor()
        get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
        id_case_selected_and_changedid = cursor_id.execute(get_id)
        id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
        try:

            self.id_spinbox.setValue(id_case_selected_and_changedid[0] + 1)
        except:
            self.id_spinbox.setValue(0)
        if self.type_of_patient.currentText()=="New Patient":
            if self.isclicked==True:
                db_id = sqlite3.connect(db_name)
                cursor_id = db_id.cursor()
                get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
                id_case_selected_and_changedid = cursor_id.execute(get_id)
                id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
                self.firstname_lineedit.setReadOnly(False)
                self.lastname_lineedit.setReadOnly(False)
                self.p_to_appt_flag = False
                self.firstname_lineedit.setText('')
                self.lastname_lineedit.setText('')
                self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
                # change to first avalble times
                self.auto_fill_time()
                self.phone_lineedit.setText('')
                self.note_edit.setText('')
                self.price_spinbox.setValue(0)
                self.isclicked=False
                try:
                    self.id_spinbox.setValue(id_case_selected_and_changedid[0] + 1)
                except:
                    self.id_spinbox.setValue(0)
                db_id.close()

            # self.firstname_lineedit.setText('')
            # self.lastname_lineedit.setText('')
            # self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
            # # change to first avalble times
            # self.auto_fill_time()
            # self.phone_lineedit.setText('')
            # self.note_edit.setText('')
            # self.price_spinbox.setValue(0)
            try:

                self.id_spinbox.setValue(id_case_selected_and_changedid[0] + 1)
            except:
                self.id_spinbox.setValue(0)
            print("New Patient")
            patient_id = self.new_p_id_fn()
            popup1=self.add_new_p_msgbox
            popup1.setText(
                "do you want to create a new patient record with this appointment information")

            popup1.setIcon(QMessageBox.Question)
            #popup1.move(int(self.frameGeometry().x() + self.frameGeometry().width() / 2), 400)
            popup1.setSizeGripEnabled(True)
            # # popup1.setWindowTitle('Patients information')
            popup1.setStyleSheet('QLabel{font-weight:bold;}')
            popup1.exec_()
            self.firstname_lineedit.setReadOnly(False)
            self.lastname_lineedit.setReadOnly(False)
            if popup1.clickedButton()==self.y:
                self.patient_id_fk.setValue(self.new_p_id_fn())
                self.yes=True

            else:
                self.patient_id_fk.setValue(0)
            # p_id = int(0)
        if self.type_of_patient.currentText()=="Existing Patient":
            print("existing patient")
            self.firstname_lineedit.setReadOnly(False)
            self.lastname_lineedit.setReadOnly(False)
            self.tabwidget.setCurrentIndex(2)
            popup2 = self.add_p_msgbox

            popup2.setText(
                "Please choose a patient from the patients table and then click on the 'Add Patient Info To Appointment' button ")

            popup2.setIcon(QMessageBox.Information)
            # popup2.addButton("Yes Create new patient with the appointment info that I inserted", QMessageBox.YesRole)
            # popup2.addButton("No don't create a new patient, it's only once", QMessageBox.NoRole)
            #popup2.move(self.frameGeometry().x() + self.frameGeometry().width() / 2, 400)
            popup2.exec_()
        
            


       
                
    def add(self):
        try:
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            first_name = self.firstname_lineedit.text().lower()
            last_name = self.lastname_lineedit.text().lower()
            date = str(self.date_edit.date().toPyDate())
            fromm = str(self.from_edit.time().toPyTime().strftime('%H:%M'))
            to = str(self.to_edit.time().toPyTime().strftime('%H:%M'))
            phone_number = self.phone_lineedit.text()
            note = self.note_edit.text()
            price = self.price_spinbox.value()
            id = self.id_spinbox.value()
            patient_id = self.patient_id_fk.value()
            row = (id, first_name, last_name, date, fromm, to, phone_number, note, price, patient_id)
            command = 'insert into appointments (appointment_id,first_name,last_name,date,from_,to_,phone_number,note,price,patient_id) values (?,?,?,?,?,?,?,?,?,?)'
            db_check = sqlite3.connect(db_name)
            cursor_check = db_check.cursor()
            command_check = 'select from_,to_ from appointments where date=? '
            result_check = cursor_check.execute(command_check, [date])
            result_check = result_check.fetchall()
            db_check.close()
            db_id = sqlite3.connect(db_name)
            cursor_id = db_id.cursor()
            get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
            id_case_selected_and_changedid = cursor_id.execute(get_id)
            id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()
            flag_add = True
            error_message = ''
            print(result_check)
            for i, j in result_check:
                if not datetime.strptime(fromm, '%H:%M').time() < datetime.strptime(i,
                                                                                    '%H:%M').time() < datetime.strptime(
                        to, '%H:%M').time():
                    if not datetime.strptime(fromm, '%H:%M').time() < datetime.strptime(j,
                                                                                        '%H:%M').time() < datetime.strptime(
                            to, '%H:%M').time():
                        if not datetime.strptime(i, '%H:%M').time() < datetime.strptime(fromm,
                                                                                        '%H:%M').time() < datetime.strptime(
                                j, '%H:%M').time():
                            if not datetime.strptime(i, '%H:%M').time() < datetime.strptime(to,
                                                                                            '%H:%M').time() < datetime.strptime(
                                    j, '%H:%M').time():
                                if datetime.strptime(fromm, '%H:%M').time() == datetime.strptime(i, '%H:%M').time():
                                    if datetime.strptime(to, '%H:%M').time() == datetime.strptime(j, '%H:%M').time():
                                        pass
                                    flag_add = False
                                    error_message = 'it contradicts with a slot from {} to {}'.format(
                                        datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                                        datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                                    break
                            else:
                                flag_add = False
                                error_message = 'it contradicts with a slot from {} to {}'.format(
                                    datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                                    datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                                break
                        else:
                            flag_add = False
                            error_message = 'it contradicts with a slot from {} to {}'.format(
                                datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                                datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                            break
                    else:
                        flag_add = False
                        error_message = 'it contradicts with a slot from {} to {}'.format(
                            datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                            datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                        break
                else:
                    flag_add = False
                    error_message = 'it contradicts with a slot from {} to {}'.format(
                        datetime.strptime(i, '%H:%M').time().strftime('%I:%M %p'),
                        datetime.strptime(j, '%H:%M').time().strftime('%I:%M %p'))
                    break
            if self.type_of_patient.currentText() !="" or self.p_to_appt_flag:
                if datetime.strptime(fromm, '%H:%M').time() < datetime.strptime(to, '%H:%M').time():
                    if len(first_name) > 0:
                        if flag_add == True:
                            try:
                                try:

                                    if self.yes:
                                        print("yes")
                                        cursor.execute(command, row)
                                        self.stats_total()
                                        db.commit()
                                        db.close
                                        ###############################
                                        dbP = sqlite3.connect(db_name)
                                        cursorP = dbP.cursor()
                                        rowP = (patient_id,first_name, last_name, phone_number, note)
                                        commandP = 'insert into patients (patient_id,first_name,last_name,phone_number,notes) values (?,?,?,?,?)'
                                        cursorP.execute(commandP, rowP)
                                        dbP.commit()
                                        print("first problem")
                                        dbP.close()
                                        self.patients_table_fill()
                                        print("second problem")
                                        self.stats_yesterday_tomorrow_today_nextweek()
                                        print("third problem")
                                        self.error.setStyleSheet('color: green')
                                        self.error.setText('The Appointment has been Added and The Patient Record has been Created')
                                        print("end of yes")
                                        self.yes=False
                                        #####################################
                                    elif self.yes==False and self.p_to_appt_flag ==False:
                                        print("elseif")
                                        p_id = int(0)
                                        row = (id, first_name, last_name, date, fromm, to, phone_number, note, price, patient_id)
                                        command = 'insert into appointments (appointment_id,first_name,last_name,date,from_,to_,phone_number,note,price,patient_id) values (?,?,?,?,?,?,?,?,?,?)'
                                        result = cursor.execute(command, row)
                                        db.commit()
                                        db.close()
                                        self.error.setStyleSheet('color: green')
                                        self.stats_total()
                                        self.error.setText('The Appointment has been Added and the Patient id is 0 which is Reserved for One Time Patients')
                                    else:
                                        print("else")
                                        result = cursor.execute(command, row)
                                        db.commit()
                                        db.close()
                                        self.error.setStyleSheet('color: green')
                                        self.error.setText('The Appointment has been Added')
                                        self.stats_total()

                                    db_id = sqlite3.connect(db_name)
                                    cursor_id = db_id.cursor()
                                    get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
                                    id_case_selected_and_changedid = cursor_id.execute(get_id)
                                    id_case_selected_and_changedid = id_case_selected_and_changedid.fetchone()

                                    self.type_of_patient.setCurrentIndex(0)
                                    self.firstname_lineedit.setReadOnly(False)
                                    self.lastname_lineedit.setReadOnly(False)
                                    self.p_to_appt_flag = False
                                    self.firstname_lineedit.setText('')
                                    self.lastname_lineedit.setText('')
                                    self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
                                    # change to first avalble times
                                    self.auto_fill_time()
                                    self.phone_lineedit.setText('')
                                    self.note_edit.setText('')
                                    self.price_spinbox.setValue(0)
                                    try:
                                        self.id_spinbox.setValue(id_case_selected_and_changedid[0] + 1)
                                    except:
                                        self.id_spinbox.setValue(0)
                                    db.close()

                                    self.fill_search_table()
                                    self.stats_yesterday_tomorrow_today_nextweek()
                                    self.check_fn()
                                except sqlite3.IntegrityError:
                                    print("ingerity check error")
                                    self.id_spinbox.setValue(id_case_selected_and_changedid[0] + 1)
                                    self.error.setStyleSheet('color: red')
                                    self.error.setText('The appointment already exist the next available id is {}'.format(
                                        id_case_selected_and_changedid[0] + 1))
                                    self.fill_search_table()
                                    self.check_fn()
                                    self.stats_yesterday_tomorrow_today_nextweek()
                                    db_id.close()
                                    db.close()
                            except Exception as e:
                                print("lol")
                                print(e)

                        else:
                            self.error.setStyleSheet('color: red')
                            self.error.setText(
                                'Time slot is not empty, ' + error_message + ', please choose another period')
                            db.close()
                    else:
                        self.error.setStyleSheet('color: red')
                        self.error.setText("The first name can't be empty")
                else:
                    self.error.setStyleSheet('color: red')
                    self.error.setText("the 'From time' can't be greater than or equal to the 'To time'")
            else:
                self.error.setStyleSheet('color: red')
                self.error.setText("The Appointmnet Can't be Added, Please Choose the Type of Patient from the drop down list")
        except Exception as e:
            print(e.__class__)

    def sort_by_date_fn_appt(self):
        date = str(self.date_check_edit.date().toPyDate())
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        command = 'SELECT appointment_id,first_name,last_name,date,from_,to_,phone_number,patient_id FROM appointments where date=? order by DATE(date) ,time(from_) ASC '
        result = cursor.execute(command, [date])
        result = result.fetchall()
        self.check_table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.check_table.insertRow(row_number)
            row_data = list(row_data)
            row_data[4] = datetime.strptime(row_data[4], '%H:%M').time().strftime('%I:%M %p')
            row_data[5] = datetime.strptime(row_data[5], '%H:%M').time().strftime('%I:%M %p')
            for column_number, data in enumerate(row_data):
                self.check_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        db.commit()
        db.close()

    def check_fn(self):
        # date = str(self.date_check_edit.date().toPyDate())
        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        command = 'SELECT appointment_id,first_name,last_name,date,from_,to_,phone_number,patient_id FROM appointments order by DATE(date) desc ,time(from_) ASC '
        result = cursor.execute(command)
        result = result.fetchall()
        self.check_table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            current_date = datetime.today().date()
            self.check_table.insertRow(row_number)
            row_data = list(row_data)
            row_data[4] = datetime.strptime(row_data[4], '%H:%M').time().strftime('%I:%M %p')
            row_data[5] = datetime.strptime(row_data[5], '%H:%M').time().strftime('%I:%M %p')

            if datetime.strptime(row_data[3], '%Y-%m-%d').date() < current_date:
                for column_number, data in enumerate(row_data):
                    self.check_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                    self.check_table.item(row_number, column_number).setBackground(QtGui.QColor('#d45050'))
                    # self.search_table.item(row_number, column_number).setForeground(QtGui.QColor('#c30000'))
            else:
                for column_number, data in enumerate(row_data):
                    self.check_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                    # green
                    self.check_table.item(row_number, column_number).setBackground(QtGui.QColor('#83c27a'))

                #self.check_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        db.commit()
        db.close()

    def delete_fn(self):
        db_check_id = sqlite3.connect(db_name)
        cursor_check_id = db_check_id.cursor()
        command_check_id = 'select appointment_id from appointments '
        result_check_id = cursor_check_id.execute(command_check_id).fetchall()
        db_check_id.close()
        id = self.id_spinbox.value()
        id_list = []
        for i in result_check_id:
            id_list.append(i[0])

        if id in id_list:
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            command = 'DELETE from appointments where appointment_id=?'
            cursor.execute(command, [id])
            db.commit()
            db.close()
            db_id = sqlite3.connect(db_name)
            cursor_id = db_id.cursor()
            get_id = 'select appointment_id from appointments order by appointment_id desc limit 1 '
            id_result = cursor_id.execute(get_id)
            id_result = id_result.fetchone()
            db_id.close()
            self.firstname_lineedit.setText('')
            self.lastname_lineedit.setText('')
            self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
            # change to first avalble times
            self.auto_fill_time()
            # self.from_edit.setDateTime(datetime.strptime('8:00am', '%I:%M%p'))
            # self.to_edit.setDateTime(datetime.strptime('8:00pm', '%I:%M%p'))
            self.phone_lineedit.setText('')
            self.note_edit.setText('')
            self.price_spinbox.setValue(0)
            self.error.setStyleSheet('color: green')
            self.error.setText('The appointment has been deleted')
            # self.refresh_fn()
            self.check_fn()
            self.fill_search_table()
            self.stats_total()
            self.stats_yesterday_tomorrow_today_nextweek()
            try:
                self.id_spinbox.setValue(id_result[0] + 1)
            except:
                self.id_spinbox.setValue(0)

        else:
            self.error.setStyleSheet('color: red')
            self.error.setText("the appointment is not registered so it can't be deleted")

    def list_fn(self):
        try:
            start_time = datetime.strptime('8:00', '%H:%M')
            close_time = datetime.strptime('18:30', '%H:%M')
            date = str(self.list_date_edit.date().toPyDate())
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            command = 'SELECT from_,to_ FROM appointments where date=? order by time(from_) ASC '
            result = cursor.execute(command, [date])
            result = result.fetchall()
            db.close()
            available_times = []
            slot = ()
            popup = ''

            for i in range(len(result)):
                if datetime.strptime(result[i][0], '%H:%M') < start_time:
                    start_time = datetime.strptime(result[i][0], '%H:%M')
                if close_time < datetime.strptime(result[i][1], '%H:%M'):
                    close_time = datetime.strptime(result[i][1], '%H:%M')

            try:
                if datetime.strptime(str(datetime.strptime(result[0][0], '%H:%M') - start_time),
                                     '%H:%M:%S') > datetime.strptime('0:00', '%H:%M'):
                    free_time_in_hours = int(
                        (datetime.strptime(result[0][0], '%H:%M') - start_time).total_seconds() / (60.0 * 60.0))
                    if free_time_in_hours >= 1:
                        fr = start_time
                        delta = timedelta(hours=1)
                        to = fr + delta
                        for i in range(free_time_in_hours):
                            slot = (fr.time().strftime('%I:%M %p'), to.time().strftime('%I:%M %p'))
                            available_times.append(slot)
                            # if to<datetime.strptime(result[0][0], '%H:%M'):
                            fr, to = to, to + delta
                            # else:
                    else:
                        slot = (
                            start_time.strftime('%I:%M %p'),
                            datetime.strptime(result[0][0], '%H:%M').time().strftime('%I:%M %p'))
                        available_times.append(slot)
                for number, value in enumerate(result):
                    if number < len(result) - 1:
                        if datetime.strptime(
                                str(datetime.strptime(result[(number + 1)][0], '%H:%M') - datetime.strptime(
                                    result[number][1], '%H:%M')), '%H:%M:%S') > datetime.strptime('0:00',
                                                                                                  '%H:%M'):
                            free_time_in_hours = int(
                                (datetime.strptime(result[(number + 1)][0], '%H:%M') - datetime.strptime(
                                    result[number][1], '%H:%M')).total_seconds() / (60.0 * 60.0))
                            if free_time_in_hours >= 1:
                                fr = datetime.strptime(result[number][1], '%H:%M')
                                delta = timedelta(hours=1)
                                to = fr + delta
                                for i in range(free_time_in_hours):
                                    slot = (fr.time().strftime('%I:%M %p'), to.time().strftime('%I:%M %p'))
                                    available_times.append(slot)
                                    fr, to = to, to + delta
                            else:
                                slot = (datetime.strptime(result[number][1], '%H:%M').time().strftime('%I:%M %p'),
                                        datetime.strptime(result[(number + 1)][0], '%H:%M').time().strftime(
                                            '%I:%M %p'))
                                available_times.append(slot)

                if datetime.strptime(str(close_time - datetime.strptime(result[(len(result) - 1)][1], '%H:%M')),
                                     '%H:%M:%S') > datetime.strptime('0:00', '%H:%M'):
                    free_time_in_hours = int(
                        (close_time - datetime.strptime(result[(len(result) - 1)][1], '%H:%M')).total_seconds() / (
                                60.0 * 60.0))
                    if free_time_in_hours >= 1:
                        fr = datetime.strptime(result[(len(result) - 1)][1], '%H:%M')
                        delta = timedelta(hours=1)
                        to = fr + delta
                        for i in range(free_time_in_hours):
                            slot = (fr.time().strftime('%I:%M %p'), to.time().strftime('%I:%M %p'))
                            available_times.append(slot)
                            # if to<datetime.strptime(result[0][0], '%H:%M'):
                            fr, to = to, to + delta
                            # else:
                    else:

                        slot = (
                            datetime.strptime(result[(len(result) - 1)][1], '%H:%M').time().strftime('%I:%M %p'),
                            close_time.strftime('%I:%M %p'))
                        available_times.append(slot)

                self.msgbox(available_times, date)

            except Exception as e:

                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno, e)
                sp = "There is no available slots"
                slot = (
                    start_time.strftime('%I:%M %p'), close_time.strftime('%I:%M %p'))
                available_times.append(slot)
                self.msgbox(available_times, date)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, e)
            slot = (
                start_time.strftime('%I:%M %p'), close_time.strftime('%I:%M %p'))
            available_times.append(slot)
            self.msgbox(available_times, date)
            # self.n_msgbox.setIcon(QMessageBox.Information)
            # self.n_msgbox.setText(sp)
            # self.n_msgbox.exec_()
        #     print("Oops!", e.__class__, "occurred.")
        # except IndexError:
        #     slot = (
        #      start_time.strftime('%I:%M %p'), close_time.strftime('%I:%M %p'))
        #     available_times.append(slot)
        #     self.msgbox(available_times, date)

    def msgbox(self, popup, date):
        sp = 'Here are the Available times slots in the working day {} \n\n\n\n\n\n\n\n\n\n'.format(date)
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText(sp)
        self.msgBox.move(self.frameGeometry().x() + self.frameGeometry().width() / 2, 400)
        self.msgBox.setSizeGripEnabled(True)
        self.msgBox.setWindowTitle('Available time slots')
        self.msgBox.setStyleSheet('QLabel{font-weight:bold;}')
        self.tableWidget.setObjectName('tableWidget')
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('From'))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('To'))
        self.tableWidget.move(0, 80)
        self.tableWidget.resize(300, 250)
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(popup):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.l.addWidget(self.tableWidget)
        self.setLayout(self.l)
        self.msgBox.exec_()

    def rows_selected_popup(self, current, previos):
        selected_row = current.row()
        if selected_row >= 0:
            fromm = self.tableWidget.item(selected_row, 0).text()
            to = self.tableWidget.item(selected_row, 1).text()
            self.from_edit.setDateTime(datetime.strptime(fromm, '%I:%M %p'))
            self.to_edit.setDateTime(datetime.strptime(to, '%I:%M %p'))


def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()


main()
