# -*- coding: utf-8 -*-

"""
Module implementing TabWidget.
"""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QTabWidget, QApplication, QFileDialog

from Ui_tab import Ui_TabWidget


class TabWidget(QTabWidget, Ui_TabWidget):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(TabWidget, self).__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        my_file_path = QFileDialog.getOpenFileName(self, '导入水印', './')
        print(my_file_path)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = TabWidget()
    ui.show()
    sys.exit(app.exec_())
