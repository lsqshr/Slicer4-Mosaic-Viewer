from CompareVolumes import *

class Compare3DVolumes(CompareVolumes):
	'''
	This module helps organize layouts and volume compositing to help compare 3D images
	'''
	def __init__(self, parent):
		CompareVolumes.__init__(self, parent)
		self.parent.title = "Compare 3D Volumes"
		self.parent.contributors = ["Sidong Liu (UniSydney), Siqi Liu (UniSydney)"] # replace with "Firstname Lastname (Org)"
		self.parent.helpText = ""
		self.parent.acknowledgementText = "blah blah blah"

	def runTest(self):
		tester = Compare3DVolumesTest()
		tester.runTest()

class Compare3DVolumesWidget(CompareVolumesWidget):
	def __init__(self, parent=None):
		CompareVolumesWidget.__init__(self, parent)

	def setup(self):
		# Instantiate and connect widgets ...

		#
		# Reload and Test area
		#
		reloadCollapsibleButton = ctk.ctkCollapsibleButton()
		reloadCollapsibleButton.text = "Reload && Test"
		self.layout.addWidget(reloadCollapsibleButton)
		reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

		# reload button
		# (use this during development, but remove it when delivering
		#  your module to users)
		self.reloadButton = qt.QPushButton("Reload")
		self.reloadButton.toolTip = "Reload this module."
		self.reloadButton.name = "CompareVolumes Reload"
		reloadFormLayout.addWidget(self.reloadButton)
		self.reloadButton.connect('clicked()', self.onReload)

		# reload and test button
		# (use this during development, but remove it when delivering
		#  your module to users)
		self.reloadAndTestButton = qt.QPushButton("Reload and Test All")
		self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
		reloadFormLayout.addWidget(self.reloadAndTestButton)
		self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

		# Add vertical spacer
		self.layout.addStretch(1)

	def onReload(self,moduleName="Compare3DVolumes"):
	    """Generic reload method for any scripted module.
	    ModuleWizard will subsitute correct default moduleName.
	    """
	    import imp, sys, os, slicer

	    widgetName = moduleName + "Widget"

	    # reload the source code
	    # - set source file path
	    # - load the module to the global space
	    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
	    p = os.path.dirname(filePath)
	    if not sys.path.__contains__(p):
	      sys.path.insert(0,p)
	    fp = open(filePath, "r")
	    globals()[moduleName] = imp.load_module(
	        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
	    fp.close()

	    # rebuild the widget
	    # - find and hide the existing widget
	    # - create a new widget in the existing parent
	    print "the module name to be reloaded,", moduleName
	    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
	    for child in parent.children():
	      try:
	        child.hide()
	      except AttributeError:
	        pass
	    # Remove spacer items
	    item = parent.layout().itemAt(0)
	    while item:
	      parent.layout().removeItem(item)
	      item = parent.layout().itemAt(0)
	    # create new widget inside existing parent
	    globals()[widgetName.lower()] = eval(
	        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
	    globals()[widgetName.lower()].setup()

class Compare3DVolumesLogic(CompareVolumesLogic):
	"""This class should implement all the actual
	computation done by your module.  The interface
	should be such that other python code can import
	this class and make use of the functionality without
	requiring an instance of the Widget
	"""	
	def __init__(self, parent=None):
		CompareVolumesLogic.__init__(self, parent)
		# TODO: replace the self.slicerViewItemPattern to fit 3D Volumes

	def viewerPerVolume(self,volumeNodes=None,background=None,label=None,viewNames=[],orientation='Axial'):
		# TODO:
		pass
