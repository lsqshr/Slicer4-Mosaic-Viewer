import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# MosaicViewer
#

class MosaicViewer:
  def __init__(self, parent):
    parent.title = "Mosaic Viewer"
    parent.categories = ["Wizards"]
    parent.dependencies = []
    parent.contributors = ["Sidong Liu (UniSydney), UniSydney"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module helps organize layouts and volume compositing to help compare 3D images
    """
    parent.acknowledgementText = """blah blah
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['MosaicViewer'] = self.runTest

  def runTest(self):
    tester = MosaicViewerTest()
    tester.runTest()

#
# qMosaicViewerWidget
#

class MosaicViewerWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
    self.layerReveal = None

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
    self.reloadButton.name = "MosaicViewer Reload"
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

  def onLayerRevealToggled(self):
    if self.layerRevealCheck.checked:
      self.layerReveal = LayerReveal()
    else:
      self.layerReveal.tearDown()
      self.layerReveal = None

  def onReload(self,moduleName="MosaicViewer"):
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

  def onReloadAndTest(self,moduleName="MosaicViewer",scenario=None):
    try:
      self.onReload(moduleName)
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest(scenario=scenario)
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# MosaicViewerLogic
#

class MosaicViewerLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    self.threeDViewPattern = """
      <item><view class="vtkMRMLViewNode" singletontag="{viewName}">
        <property name="viewlabel" action="default">{viewName}</property>
      </view></item>
     """
    # use a nice set of colors
    self.colors = slicer.util.getNode('GenericColors')
    self.lookupTable = self.colors.GetLookupTable()

  def assignLayoutDescription(self,layoutDescription):
    """assign the xml to the user-defined layout slot"""
    layoutNode = slicer.util.getNode('*LayoutNode*')
    if layoutNode.IsLayoutDescription(layoutNode.SlicerLayoutUserView):
      layoutNode.SetLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    else:
      layoutNode.AddLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    layoutNode.SetViewArrangement(layoutNode.SlicerLayoutUserView)

  def viewerPerVolume(self,volumeNodes=None,background=None,label=None,viewNames=[],orientation='Axial'):
    """ Load each volume in the scene into its own
    slice viewer and link them all together.
    If background is specified, put it in the background
    of all viewers and make the other volumes be the
    forground.  If label is specified, make it active as
    the label layer of all viewers.
    Return a map of slice nodes indexed by the view name (given or generated).
    """

    import math

    if not volumeNodes:
      volumeNodes = slicer.util.getNodes('*VolumeNode*').values()

    if len(volumeNodes) == 0:
      return

    # make an array with wide screen aspect ratio
    # - e.g. 3 volumes in 3x1 grid
    # - 5 volumes 3x2 with only two volumes in second row
    N = len(volumeNodes)
    c = math.sqrt(N)
    rows = math.floor(c)
    if N is not rows * rows:
      columns = math.ceil((N - rows * rows)/rows) + rows

    print "rows: ", rows, '\tcolumns: ', columns, 'nvolumes: ', N

    # construct the XML for the layout
    # - one viewer per volume
    # - default orientation as specified
    #
    actualViewNames = []
    index = 1
    layoutDescription = ''
    layoutDescription += '<layout type="vertical">\n'
    for row in range(int(rows)):
      layoutDescription += ' <item> <layout type="horizontal">\n'
      for column in range(int(columns)):
        try:
          viewName = viewNames[index-1]
        except IndexError:
          viewName = '%d-%d' % (row,column)
        #rgb = [int(round(v*255)) for v in self.lookupTable.GetTableValue(index)[:-1]]
        #color = '#%0.2X%0.2X%0.2X' % tuple(rgb)
        layoutDescription += self.threeDViewPattern.format(viewName=viewName)
        actualViewNames.append(viewName)
        index += 1
      layoutDescription += '</layout></item>\n'
    layoutDescription += '</layout>'
    self.assignLayoutDescription(layoutDescription)

    # put one of the volumes into each view, or none if it should be blank
    threeDNodesByViewName = {}
    layoutManager = slicer.app.layoutManager()

    for index in range(len(actualViewNames)):
      # obtain the name and ID of the current Node
      viewName = actualViewNames[index]
      try:
        volumeNodeID = volumeNodes[index].GetID()
      except IndexError:
        volumeNodeID = ""

      threeDWidget = layoutManager.threeDWidget(index)
      threeDView = threeDWidget.threeDView() 
      viewNode = threeDView.mrmlViewNode()
      displayNode = volumeNodes[index].GetDisplayNode()

      if displayNode.IsDisplayableInView(viewNode.GetID()):
        print "Node:", viewNode.GetID(), ' is displayable for ', viewName 
        displayNode.AddViewNodeID(viewNode.GetID())
        displayNode.SetVisibility(True)
      else:
        print "Node:", viewNode.GetID(), ' is not displayable for ', viewName 

      #threeDNodesByViewName[viewName] = threeDView 

      print "Node ", index, ": ", '\tView Node ID: ', viewNode.GetID(),\
         '\tview name', viewName, '\tvolumeID:', volumeNodeID

    #return threeDNodesByViewName
    return

class MosaicViewerTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1500):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self,scenario=None):
    """Run as few or as many tests as needed here.
    """
    #self.setUp()
    self.test_MosaicViewer1()

  def test_MosaicViewer1(self):
    """ Test modes with 3 volumes.
    """
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    """
    Download the testing data
    """

    self.delayDisplay("Starting the test, download data")

    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    heads = []
    headNames = []
    for i in range(4):
	    heads.append(sampleDataLogic.downloadMRHead())
	    headNames.append("head" + str(i))


    logic = MosaicViewerLogic()
    self.delayDisplay("first with 4 volumes")
    logic.viewerPerVolume(volumeNodes=heads, viewNames=headNames)
