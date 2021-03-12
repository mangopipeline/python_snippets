from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore
import os 

my_ui = os.path.join(os.path.dirname(__file__),'loading_a_ui_file.ui')

class MyUi():
    def __init__(self,parent=None):
        self._main = self._open_ui_file(my_ui,
                                        parent=parent)
    
    def _open_ui_file(self, my_ui,parent=None):
        ui_file = QtCore.QFile(my_ui)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QUiLoader()
        return loader.load(ui_file,parent=parent)
    
    def show(self):
        self._main.show()



if __name__ == '__main__':
    window = MyUi()
    window.show()

    