from PySide2 import QtWidgets, QtCore

import MaxPlus
import pymxs

_MXS  = pymxs.runtime

class CallBacksUI(QtWidgets.QDialog):
	def __init__(self):
		parent =QtWidgets.QWidget(MaxPlus.GetQMaxMainWindow(),QtCore.Qt.Dialog)
		super(CallBacksUI,self).__init__(parent=parent)
		
		self._call_backs = []
		self._gen_list_box()
		self._register_call_back()
		
		
	def _gen_list_box(self):
		self._layout = QtWidgets.QHBoxLayout()
		self.setLayout(self._layout)
		self._list_widget = QtWidgets.QListWidget()
		self._layout.addWidget(self._list_widget)

		
	def _scene_change(self,*args,**kwargs):
		self._list_widget.clear()
		items = [o.name for o in _MXS.objects]
		self._list_widget.addItems(items)

		
	def _register_call_back(self):
		codes = MaxPlus.NotificationCodes
		self._call_backs.append(MaxPlus.NotificationManager.Register(codes.SceneAddedNode,self._scene_change))
	
	
	def closeEvent(self,event):
		super(CallBacksUI,self).closeEvent(event)
		
		for cbid in self._call_backs: 
			MaxPlus.NotificationManager.Unregister(cbid)

	
	
if __name__ == '__main__':
	UI = CallBacks()
	UI.show()
	UI._scene_change()
