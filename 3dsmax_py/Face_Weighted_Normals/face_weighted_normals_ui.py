from colossus.Utils.DCC.max import face_weighted_normals
from colossus.Utils.Qt import uic
from colossus.APIs.agnostic.translator.max_trans import Translator
import os

BASE,FORM = uic.loadUiType(os.path.join(os.path.dirname(__file__),'main.ui'))

class MainApp(BASE,FORM):
	def __init__(self):
		parent = Translator.get_main_window()
		super(MainApp,self).__init__(parent=parent)
		self.setupUi(self)
		self._connect_signals()
		
		
	def _connect_signals(self):
		self.pushButton.clicked.connect(self.run)
		
	def run(self):
		thresh_hold = self.doubleSpinBox.value()
		face_weighted_normals.apply_face_weigheted_surface_normals(coplanear_threshold=thresh_hold)
	
if __name__ == '__main__':
	MYAPP = MainApp()
	MYAPP.show()