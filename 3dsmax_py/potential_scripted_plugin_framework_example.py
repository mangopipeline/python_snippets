"""
Dummy Example of what a "scripted Plugin could look like

this example could apply for custom attributes ass well

developer would inherit from a CusttomAttribute class instead of ScriptedPlugin class

i'm using this scrpted material as referernec for the example...

https://help.autodesk.com/view/3DSMAX/2016/ENU/?guid=__files_GUID_7EAD66B1_29BE_4EC7_AC82_7D2831062856_htm
"""
from PySide2 import QtWidgets
from mxs_plugin_util import ScriptedPlugin, register_scripted_plugin, ParameterBlock, FloatParam
from pymxs import runtime as mxs


class MyGameMaterial(ScriptedPlugin):
    name = "My Game Material"
    plugin_type = mxs.material
    set_class_id = [695425, 446581]
    extends = mxs.Standard
    replaceUi = True
    version = 1

    def __init__(self):
        super(MyGameMaterial, self).__init__()

        # make some parameters
        self.main = ParameterBlock('main',  # ui name for the parameter block
                                   self)  # link to the plug-in instance it is to be attached too

        # add a float parameter to main ParameterBlock
        self.trans = FloatParam('trans',  # name of the parameter as displayed in the ui (track view)
                                self.main,  # parent parameter block
                                default=27,  # default value
                                ui=self.trans_spinner)  # QtWidget that drives it (should rely on QProperty for custom widgets) this widgets are declared in the re-implemented ui method

        # connect set event for parameter block
        self.trans.set.connect(lambda x: setattr(self.delegate, 'opacity', x))  # PySide 'style' connection to parameter set event

    def ui(self):
        """
        this would be a method in the ScriptedPlugin Class that would be optionally
        re implemented by the developer to add custom ui items

        the expectation is that the instance would already have a main_widget available with a main layout (vertical) we could add qt widgets too 
        """
        # add a widget (spinner) to the UI
        self.trans_spinner = QtWidgets.QDoubleSpinBox(parent=self.main_widget)
        self.main_widget.main_layout.addWidget(self.trans_spinner)

    def create(self):
        """
        "create" and other plug in event callback types could  be methods of the ScriptedPlugin class
        that could be "re implemented" by the developer
        """
        self.delegate.opacityFalloff = 75


# make this plug-in visible to max
register_scripted_plugin(MyGameMaterial)
