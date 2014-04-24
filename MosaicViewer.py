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
    """ 
    # replace with organization, grant and thanks.
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
    # Render Data Area
    #
    renderCollapsibleButton = ctk.ctkCollapsibleButton()
    renderCollapsibleButton.text = "Render Volumes && Models"
    self.layout.addWidget(renderCollapsibleButton)
    renderFormLayout = qt.QFormLayout(renderCollapsibleButton)

    #
    # Load all models in mrml scene
    #
    self.renderAllModelsButton = qt.QPushButton("Load All Models")
    self.renderAllModelsButton.toolTip = "Load all models in the mrml scene in Mosaic Viewer"
    renderFormLayout.addWidget(self.renderAllModelsButton)
    self.renderAllModelsButton.connect('clicked()', lambda p='vtkMRMLModelNode*' : self.onRenderAllNodes(pattern=p))

    #
    # Load all volumes in mrml scene
    #
    self.renderAllVolumesButton = qt.QPushButton("Load All Volumes")
    self.renderAllVolumesButton.toolTip = "Load all volumess in the mrml scene in Mosaic Viewer"
    renderFormLayout.addWidget(self.renderAllVolumesButton)
    self.renderAllVolumesButton.connect('clicked()', lambda p='vtkMRMLVolumeNode*' : self.onRenderAllNodes(pattern=p))

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    self.clearButton = qt.QPushButton("clear scene")
    self.clearButton.toolTip = "Clear the models rendered in 3D views."
    self.clearButton.name = "MosaicViewer Clear"
    reloadFormLayout.addWidget(self.clearButton)
    self.clearButton.connect('clicked()', self.onClear)

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

    # reload and run specific tests
    scenarios = ('MR', 'DTI',)
    for scenario in scenarios:
      button = qt.QPushButton("Reload and Test %s" % scenario)
      self.reloadAndTestButton.toolTip = "Reload this module and then run the %s self test." % scenario
      reloadFormLayout.addWidget(button)
      button.connect('clicked()', lambda s=scenario: self.onReloadAndTest(scenario=s)) 

    # Add vertical spacer
    #self.layout.addStretch(1)


    # Add vertical spacer
    self.layout.addStretch(1)

  def onLayerRevealToggled(self):
    if self.layerRevealCheck.checked:
      self.layerReveal = LayerReveal()
    else:
      self.layerReveal.tearDown()
      self.layerReveal = None

  def onClear(self):
    slicer.mrmlScene.Clear(0)

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

  def onRenderAllNodes(self, pattern):
    logic = MosaicViewerLogic()
    logic.renderAllNodes(pattern)

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

  def makeLayout(self, nodes, viewNames):
    import math
    # make an array with wide screen aspect ratio
    # - e.g. 3 volumes in 3x1 grid
    # - 5 volumes 3x2 with only two volumes in second row
    N = len(nodes)
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
        layoutDescription += self.threeDViewPattern.format(viewName=viewName)
        actualViewNames.append(viewName)
        index += 1
      layoutDescription += '</layout></item>\n'
    layoutDescription += '</layout>'
    self.assignLayoutDescription(layoutDescription)

    print "rows: ", rows, '\tcolumns: ', columns, '\nNumber of Volumes: ', N, " Number of View Names", len(actualViewNames)

    return actualViewNames

  def viewerPerNode(self, nodes=None, viewNames=[], nodeType="Volume"):
    """ Load each volume in the scene into its own
    3D viewer and link them all together.
    """
    print "view names:", viewNames

    if not nodes:
      nodes = slicer.util.getNodes('*VolumeNode*').values()

    if len(nodes) == 0:
      return

    actualViewNames = self.makeLayout(nodes, viewNames)

    # put one of the volumes into each view, or none if it should be blank
    threeDNodesByViewName = {}
    layoutManager = slicer.app.layoutManager()

    for index in range(len(nodes)):
      # obtain the name and ID of the current Node
      viewName = actualViewNames[index]
      try:
        nodeID = nodes[index].GetID()
      except IndexError:
        nodeID = ""
      # get the index-th 3D view node
      threeDWidget = layoutManager.threeDWidget(index + 1)
      threeDView = threeDWidget.threeDView() 
      viewNode = threeDView.mrmlViewNode()

      # use volumerendering module to make the volume rendering display node
      if nodeType == "Volume":
        logic = slicer.modules.volumerendering.logic()
        displayNode = logic.CreateVolumeRenderingDisplayNode()
        slicer.mrmlScene.AddNode(displayNode)      
        displayNode.UnRegister(logic)
        displayNode.AddViewNodeID(viewNode.GetID())
        logic.UpdateDisplayNodeFromVolumeNode(displayNode, nodes[index])
        displayNode.SetVisibility(True)
        nodes[index].AddAndObserveDisplayNodeID(displayNode.GetID())
      elif nodeType == "Model":
        # use models module to render the display node of this model
        logic = slicer.modules.models.logic()
        displayNode = nodes[index].GetDisplayNode()
        displayNode.AddViewNodeID(viewNode.GetID())
        slicer.mrmlScene.AddNode(displayNode)      
        nodes[index].AddAndObserveDisplayNodeID(displayNode.GetID())
      else:
        raise Exception("Unknown Node Type")

      print "Node ", index, ": ", '\tView Node ID: ', viewNode.GetID(),\
         '\tview name', viewName, '\tvolumeID:', nodeID, '\tdisplayNode Visible:', \
         displayNode.GetVisibility()

      threeDNodesByViewName[viewName] = threeDView 

    return threeDNodesByViewName

  def renderAllNodes(self, pattern = "vtkMRMLModelNode*"):
    '''
    Search all models which are currently loaded in the mrml scene and 
    render them in the a grid view
    '''
    nodesDict = slicer.util.getNodes(pattern)
    nodes = [n for n in nodesDict.values() if "Slice" not in n.GetName()]

    nodeType = lambda nt : "Model" if pattern=='vtkMRMLModelNode*' else "Volume"
    self.viewerPerNode(nodes=nodes, viewNames=[n.GetName() for n in nodes],\
       nodeType=nodeType(pattern))
    
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
    self.setUp()

    if scenario == "MR":
      self.test_MosaicViewer_MR()
    elif scenario == "DTI":
      self.test_MosaicViewer_DTI()
    elif scenario == "MRDTI":
      self.test_MosaicViewer_MR_DTI()
    else:
      self.test_MosaicViewer_MR()
      self.test_MosaicViewer_MR_DTI()


  def test_MosaicViewer_MR(self):
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
    for i in range(3):
	    heads.append(sampleDataLogic.downloadMRHead())
	    headNames.append("head" + str(i))

    for i in range(2):
      heads.append(sampleDataLogic.downloadMRBrainTumor1())
      headNames.append("tumor" + str(i))

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes=heads, viewNames=headNames, nodeType="Volume")

  def test_MosaicViewer_DTI(self):
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    heads = []
    headNames = []

    # try two models
    slicer.util.loadModel('D:\\data\\localworkspace\\Mosaic\\Resources\\SampleTracts\\bundle1.vtk') # change the path to your local path
    slicer.util.loadModel('D:\\data\\localworkspace\\Mosaic\\Resources\\SampleTracts\\wholefibre.vtk') # change the path to your local path
    slicer.util.loadModel('D:\\data\\localworkspace\\Mosaic\\Resources\\SampleTracts\\loosefibre.vtk') # change the path to your local path

    heads.append(slicer.util.getNode('bundle1'))
    headNames.append("tumor bundle")

    heads.append(slicer.util.getNode('wholefibre'))
    headNames.append("wholefibre")

    heads.append(slicer.util.getNode('loosefibre'))
    headNames.append("loosefibre")


    heads.append(slicer.util.getNode('wholefibre'))
    headNames.append("wholefibre2")

    heads.append(slicer.util.getNode('loosefibre'))
    headNames.append("loosefibre2")

    heads.append(slicer.util.getNode('bundle1'))
    headNames.append("tumor bundle2")


    heads.append(slicer.util.getNode('loosefibre'))
    headNames.append("loosefibre3")

    heads.append(slicer.util.getNode('bundle1'))
    headNames.append("tumor bundle3")
    
    heads.append(slicer.util.getNode('wholefibre'))
    headNames.append("wholefibre3")

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes=heads, viewNames=headNames, nodeType="Model")
