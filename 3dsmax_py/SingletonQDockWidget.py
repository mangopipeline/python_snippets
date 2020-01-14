'''
this code is an example of how a singleton qdialog could be implemented in max
singleton are useful when you are trying to make sure that only one instnace of the particular tool can exist during the session.
they are also helpful when trying to quickly retrive that instance anywhere in the session...
'''
from PySide2 import QtWidgets
import shiboken2  as shibo 
from pymxs import runtime as mxs 

#this is a generic method for getting the max parent window... you could store this in a global libarary
def max_parent_window():
    main_window=QtWidgets.QWidget.find(pymxs.runtime.windows.getMAXHWND())
    return shibo.wrapInstance(shibo.getCppPointer(main_window)[0], QtWidgets.QMainWindow)

#this is a  super simlple singleton mechanism  this could also live in a global libarary you reuse
class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            print('creating instance for the first time')
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            print('instnace allready exists returning that!')

        return cls._instance


# this is a new QWidget Meta class it combines our singleton metaclass with the metaclass allready built into the qtDockWidget
#this class could live in a seperate lib that devs can reuse
class SingletonDockWidgetType(Singleton, type(QtWidgets.QDockWidget)):
    pass

# implement a simple single dock widget we can use instead of the default max one...
#this could live in a seprate lib that devs can reuse 

class CustomMaxDockWiget(SingletonDockWidgetType('CustomMaxDockWiget', (QtWidgets.QDockWidget, ), {})):
    def __init__(self, *args, **kwargs):
        super(CustomMaxDockWiget, self).__init__(*args, **kwargs)

'''
out actual tool we will be writting!

'''
class MyMaxTool(CustomMaxDockWiget):
    def __init__(self, *args, **kwargs):
        super(MyMaxTool, self).__init__(*args, **kwargs)

        # set a master widget to work with...
        self._master_widget = QtWidgets.QWidget(parent=self)
        self.setWidget(self._master_widget)

        self._master_layout = QtWidgets.QVBoxLayout(self)
        self._master_widget.setLayout(self._master_layout)
        self._label = QtWidgets.QLabel('Yo this is a custom singleton tool!', parent=self)
        self._master_layout.addWidget(self._label)    
        
def open_my_tool():
    tool = MyMaxTool(parent=max_parent_window())
    if not tool.isHidden():
        print ("tool is allready opened!!")
        return tool 
    tool.show()
    return tool
    
