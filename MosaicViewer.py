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
    parent.contributors = ["Sidong Liu (USYD, BWH), Siqi Liu (USYD), Sonia Pujol (BWH)"]
    parent.helpText = """
    This module creates mosaic views of multiple volumes and models
    """
    parent.acknowledgementText = """
    This f was developed by Siqi Liu, University of Sydney, Sidong Liu, University of Sydney and Brigham and Women's
    Hospital and Sonia Pujol, Brigham and Women's Hospital, and was partially supported by ARC, AADRF, NIH NA-MIC
    (U54EB005149) and NIH NAC (P41EB015902).
    """ 

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

def numericInputFrame(parent, label, tooltip, minimum, maximum, step, decimals):
  inputFrame = qt.QFrame(parent)
  inputFrame.setLayout(qt.QHBoxLayout())
  inputLabel = qt.QLabel(label, inputFrame)
  inputLabel.setToolTip(tooltip)
  inputFrame.layout().addWidget(inputLabel)
  inputSpinBox = qt.QDoubleSpinBox(inputFrame)
  inputSpinBox.setToolTip(tooltip)
  inputSpinBox.minimum = minimum
  inputSpinBox.maximum = maximum
  inputSpinBox.singleStep = step
  inputSpinBox.decimals = decimals
  inputFrame.layout().addWidget(inputSpinBox)
  inputSlider = ctk.ctkDoubleSlider(inputFrame)
  inputSlider.minimum = minimum
  inputSlider.maximum = maximum
  inputSlider.orientation = 1
  inputSlider.singleStep = step
  inputSlider.setToolTip(tooltip)
  inputFrame.layout().addWidget(inputSlider)
  return inputFrame, inputSlider, inputSpinBox

#
# MosaicViewerWidget
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

    self.clearButton = qt.QPushButton("Clear Scene")
    self.clearButton.toolTip = "Clear all the volumes and models in 3D views"
    self.clearButton.name = "MosaicViewer Clear"
    reloadFormLayout.addWidget(self.clearButton)
    self.clearButton.connect('clicked()', self.onClear)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this Mosaic Viewer"
    self.reloadButton.name = "MosaicViewer Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering your module to users)
    # reload and run specific tests
    scenarios = ('All', 'Model', 'Volume', 'SceneView', 'Selected')
    for scenario in scenarios:
      button = qt.QPushButton("Reload and Test %s" % scenario)
      button.toolTip = "Reload this module and then run the self test on %s." % scenario
      reloadFormLayout.addWidget(button)
      button.connect('clicked()', lambda s = scenario: self.onReloadAndTest(scenario = s))

    '''
    #
    # Input Data Selection Area
    #
    dataSelectionCollapsibleButtion = ctk.ctkCollapsibleButton()
    dataSelectionCollapsibleButtion.text = "Select the Volumes && Models"
    self.layout.addWidget(dataSelectionCollapsibleButtion)
    dataSelectionFormLayout = qt.QFormLayout(dataSelectionCollapsibleButtion)

    dataSelectionFrame = qt.QFrame(self.parent)
    dataSelectionFrame.setLayout(qt.QGridLayout())
    dataSelectionFormLayout.addWidget(dataSelectionFrame)

    selectAll = qt.QRadioButton("Select All")
    dataSelectionFrame.layout().addWidget(selectAll, 0, 0)

    selectAllVolumes = qt.QRadioButton("Select All Volumes")
    dataSelectionFrame.layout().addWidget(selectAllVolumes, 1, 0)

    selectAllModels = qt.QRadioButton("Select All Models")
    dataSelectionFrame.layout().addWidget(selectAllModels, 0, 1)

    selectCustomized = qt.QRadioButton("Select From Drop List")
    dataSelectionFrame.layout().addWidget(selectCustomized, 1, 1)

    # TODO: add a data check list, enable to select the data from the list.
    # Top three options should be 'Select All', 'Select All Volumes', 'Select All Models'

    #
    # Layout Option Area
    #
    changeLayoutOptionCollapsibleButtion = ctk.ctkCollapsibleButton()
    changeLayoutOptionCollapsibleButtion.text = "Choose the Layout"
    self.layout.addWidget(changeLayoutOptionCollapsibleButtion)
    changeLayoutFormLayout = qt.QFormLayout(changeLayoutOptionCollapsibleButtion)

    changeLayoutFrame = qt.QFrame(self.parent)
    changeLayoutFrame.setLayout(qt.QGridLayout())
    changeLayoutFormLayout.addWidget(changeLayoutFrame)

    chooseDefault = qt.QRadioButton("Choose Default Viewer Layout")
    changeLayoutFrame.layout().addWidget(chooseDefault, 0, 0)

    chooseCustomized = qt.QRadioButton("Choose Customized Layout")
    changeLayoutFrame.layout().addWidget(chooseCustomized, 0, 1)

    chooseRowFrame, chooseRowSlider, chooseRowSliderSpinBox = numericInputFrame(self.parent, "Number of Rows:", "Choose Number of Rows", 0, 20, 1, 1)
    changeLayoutFrame.layout().addWidget(chooseRowFrame)
    chooseColumnFrame, chooseColumnSlider, chooseColumnSliderSpinBox = numericInputFrame(self.parent, "Number of Columns:", "Choose Number of Columns", 0, 20, 1, 1)
    changeLayoutFrame.layout().addWidget(chooseColumnFrame)
    '''

    # TODO: add two radials, one for default and one for customized layout. If 'customized' is selected, generate a grid to enable the users to customize the viewer layout.
    # chooseCustomizedTable = qt.QTableWidget(5, 5)
    # changeLayoutFormLayout.addWidget(chooseCustomizedTable)

    #
    # Execution Area
    #

    # Add vertical spacer
    self.layout.addStretch(1)

    buttonFrame = qt.QFrame(self.parent)
    buttonFrame.setLayout(qt.QHBoxLayout())
    self.layout.addWidget(buttonFrame)

    self.restoreDefaults = qt.QPushButton("Restore Defaults")
    self.restoreDefaults.toolTip = "Restore the default settings"
    buttonFrame.layout().addWidget(self.restoreDefaults)
    self.restoreDefaults.connect('clicked()', self.onRestore)

    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Apply Mosaic Viewer"
    buttonFrame.layout().addWidget(self.applyButton)
    self.applyButton.connect('clicked()', self.onApply)

  #
  # Define the attributes
  #

  def onClear(self):
    slicer.mrmlScene.Clear(0)

  def onReload(self, moduleName = "MosaicViewer"):
    """
    Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source f path
    # - load the module to the global space
    fPath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(fPath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(fPath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, fPath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    print "the module name to be reloaded,", moduleName
    parent = slicer.util.findChildren(name = '%s Reload' % moduleName)[0].parent().parent()
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


  def onReloadAndTest(self, moduleName = "MosaicViewer", scenario = None):
    try:
      self.onReload(moduleName)
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest(scenario = scenario)
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


  def onRenderAllNodes(self, pattern):
    logic = MosaicViewerLogic()
    logic.renderAllNodes(pattern)

  def onRestore(self):
      self.onReload("MosaicViewer")

  def onApply(self):
      logic = MosaicViewerLogic()
      logic.renderAllSceneViewNodes()

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

  def updateNViewNode(self):
    lviewnode = slicer.util.getNodes("*ViewNode*")
    self.nViewNode =  len(lviewnode.keys())

  def assignLayoutDescription(self,layoutDescription):
    """assign the xml to the user-defined layout slot"""
    layoutNode = slicer.util.getNode('*LayoutNode*')
    if layoutNode.IsLayoutDescription(layoutNode.SlicerLayoutUserView):
      layoutNode.SetLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    else:
      layoutNode.AddLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    layoutNode.SetViewArrangement(layoutNode.SlicerLayoutUserView)

  def makeLayout(self, nodes, viewNames):
    self.updateNViewNode()

    import math
    # make an default display layout array, e.g.:
    # nvolumes = 3 -> 2 x 2 (nrows = ncolumes, with only one volume in second row)
    # nvolumes = 5 -> 2 x 3 (nrows < ncolumes, with only two volumes in second row)
    # nvoluems = 11 -> 3 x 4 (nrows < ncolums, with only three volumes in the third row)
    nNodes = len(nodes)
    qNNodes = math.sqrt(nNodes)
    nRows = math.floor(qNNodes)
    nColumns = math.ceil(qNNodes)
    if nNodes > nRows * nColumns:
        nRows = nRows + 1;

    # construct the XML for the layout
    # - one viewer per volume
    # - default orientation as specified
    #
    actualViewNames = []
    index = 1
    layoutDescription = ''
    layoutDescription += '<layout type="vertical">\n'
    for row in range(int(nRows)):
      layoutDescription += ' <item> <layout type="horizontal">\n'
      for column in range(int(nColumns)):
        try:
          viewName = viewNames[index - 1]
        except IndexError:
          viewName = '%d-%d' % (row,column)
        layoutDescription += self.threeDViewPattern.format(viewName = viewName)
        actualViewNames.append(viewName)
        index += 1
      layoutDescription += '</layout></item>\n'
    layoutDescription += '</layout>'
    self.assignLayoutDescription(layoutDescription)

    return actualViewNames


  def viewerPerNode(self, nodes = None, viewNames = [], nodeType = ""):
    """ Load each volume in the scene into its own
    3D viewer and link them all together.
    """
    if not nodes:
      nodes = slicer.util.getNodes('*VolumeNode*')

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
        nodeID = slicer.util.getNode(viewName)
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
        logic.UpdateDisplayNodeFromVolumeNode(displayNode, nodeID)
        displayNode.SetVisibility(True)
        nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())
      elif nodeType == "Model":
        # use models module to render the display node of this model
        displayNode = nodeID.GetDisplayNode()
        # slicer.mrmlScene.AddNode(displayNode)
        nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())
        displayNode.AddViewNodeID(viewNode.GetID())
        displayNode.SetVisibility(True)
      elif nodeType == "SceneView":
        print "SceneView mosaic viewer is not fully supported yet!"
        displayNode = nodeID.GetDisplayNode()
        nodeID.AddAndObserveDisplayNodeID(displayNode.GetID())
        displayNode.AddViewNodeID(viewNode.GetID())
        displayNode.SetVisibility(True)
      else:
        raise Exception("Unknown Node Type")

      print "Node Index: ", index, '\nView Node ID: ', viewNode.GetID(),\
         '\nView Name: ', viewName, '\nDisplay Node Visible:', \
         displayNode.GetVisibility(), '\n'

      threeDNodesByViewName[viewName] = threeDView

    return threeDNodesByViewName

  
  def renderAllNodes(self, pattern="vtkMRMLModelNode*"):
    '''
    Search all models which are currently loaded in the mrml scene and 
    render them in the a grid view
    '''
    nodesDict = slicer.util.getNodes(pattern)
    nodes = [n for n in nodesDict.values() if "Slice" not in n.GetName()]
    nodeType = lambda nt: "Model" if pattern == 'vtkMRMLModelNode*' else "Volume" 
    self.viewerPerNode(nodes=nodes, viewNames=[n.GetName() for n in nodes], nodeType=nodeType(pattern))

  def _getViewIndex(self, sceneViewIndex, nSceneViewNode):
    '''
    get the starting index of view node by filtering rubbish
    '''
    lViewNode   = slicer.util.getNodes('vtkMRMLViewNode*');
    keys2Remove = []

    for key in lViewNode:
      viewName = lViewNode[key].GetName()
      if viewName in ["Red", "Yellow", "Green"]:
        keys2Remove.append(key)

    for key in keys2Remove:
      lViewNode.pop(key)

    print '#view nodes after removing slices:', lViewNode.keys()
    return len(lViewNode.keys()) - (nSceneViewNode - sceneViewIndex)


  def renderAllSceneViewNodes(self):
      print '=================================='
      scene = slicer.mrmlScene

      # Find loaded sceneviews
      nodes_dict = slicer.util.getNodes('*vtkMRMLSceneViewNode*')
      sv_nodes   = [n for n in nodes_dict.values() if "Slice" not in n.GetName()]

      # Make the layout according to the # scene view nodes
      self.makeLayout(sv_nodes, [n.GetName() for n in sv_nodes])
      layoutManager = slicer.app.layoutManager()

      # Get all the model nodes in the scene
      if len(sv_nodes) == 0 :
        return 

      # iterate all scene view nodes
      for s in range(len(sv_nodes)):
        sceneview = sv_nodes[s]

        # get the models and fibre bundles from sceneview
        sceneview_model_collection = sv_nodes[s].GetNodesByClass('vtkMRMLModelNode')
        sceneview_fibre_collection = sv_nodes[s].GetNodesByClass('vtkMRMLfibreBundleNode')
        n_sceneview_model          = sceneview_model_collection.GetNumberOfItems()
        n_sceneview_fibre          = sceneview_fibre_collection.GetNumberOfItems()
        
        # get the index-th 3D view node
        # TODO: not sure if the index is right
        viewIndex                  = self._getViewIndex(s, len(sv_nodes))
        #print viewIndex
        threeDWidget               = layoutManager.threeDWidget(viewIndex)
        threeDView                 = threeDWidget.threeDView() 
        viewNode                   = threeDView.mrmlViewNode()
        
        # initialize the model and fibre iterators
        iter_sceneview_model       = sceneview_model_collection.NewIterator()
        iter_sceneview_fibre       = sceneview_fibre_collection.NewIterator()
        
        modelMap         = {}
        fibreMap         = {}

        # DEBUG
        print '\n', sceneview.GetName(), ':', viewNode.GetName() 

        # save scene view models and fibres to dictionary of <ID,node>
        for m in range(n_sceneview_model):
          modeli = iter_sceneview_model.GetCurrentObject()
          iter_sceneview_model.GoToNextItem()
          # remove this model from all renders          
          modeli.GetDisplayNode().RemoveAllViewNodeIDs()

          # add this model to scene if it is not in it
          if scene.GetNodeByID(modeli.GetID()) == None:
            print 'add ', modeli.GetName(), 'to the scene'
            slicer.mrmlScene.AddNode(modeli)
            #modeli.UpdateScene(scene)

          modelMap[modeli.GetID()] = modeli

        # get all model and fibre nodes from scene
        scene_model_collection = scene.GetNodesByClass('vtkMRMLModelNode')
        scene_fibre_collection = scene.GetNodesByClass('vtkMRMLfibreBundleNode')
        n_scene_model          = scene_model_collection.GetNumberOfItems()
        n_scene_fibre          = scene_fibre_collection.GetNumberOfItems()
        iter_scene_model           = scene_model_collection.NewIterator()
        iter_scene_fibre           = scene_fibre_collection.NewIterator()

        for f in range(n_sceneview_fibre):
          fibrei = iter_sceneview_fibre.GetCurrentObject()
          iter_sceneview_fibre.GoToNextItem()
          # remove this fibre from all renders          
          fibrei.GetDisplayNode().RemoveAllViewNodeIDs()
          fibreMap[fibrei.GetID()] = fibrei

        slicer.mrmlScene.StartState(0x0001)

        for m in range(n_scene_model):
          modeli = iter_scene_model.GetCurrentObject()

          # see if this node is in the current sceneview
          if modeli.GetID() in modelMap:
            displayNode = modeli.GetDisplayNode()
            #slicer.mrmlScene.AddNode(displayNode)
            #displayNode.RemoveAllViewNodeIDs()
            modeli.AddAndObserveDisplayNodeID(displayNode.GetID()) 
            displayNode.AddViewNodeID(viewNode.GetID())
            displayNode.SetVisibility(False)
            modeli.SetDisplayVisibility(0)

            print 'Add model ', modeli.GetName(), 'to ', viewNode.GetName()
            #print modeli.GetName(), ': ' , displayNode.GetNumberOfViewNodeIDs()

          else:
            print modeli.GetName(), 'not in the scene!!!!!!!'

          modeli.UpdateScene(scene)

          iter_scene_model.GoToNextItem()

        slicer.mrmlScene.EndState(0x0001)


        '''
        for f in range(nfibre):
          fibrei = iter_fibre.GetCurrentObject()
          print 'Add fibre ', fibrei.GetName(), 'to ', viewNode.GetName()
          displayNode = fibrei.GetDisplayNode()
          displayNode.RemoveAllViewNodeIDs()
          fibrei.AddAndObserveDisplayNodeID(displayNode.GetID()) 
          displayNode.AddViewNodeID(viewNode.GetID())
          displayNode.SetVisibility(False)
          print 'After Adding ID',fibrei.GetName(), ': ' , displayNode.GetNumberOfViewNodeIDs()
          iter_fibre.GoToNextItem()
        '''

    
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

  def runTest(self,scenario = None):
    """Run as few or as many tests as needed here.
    """
    self.setUp()

    if scenario == "Volume":
      self.test_MosaicViewer_Volume()
    elif scenario == "Model":
      self.test_MosaicViewer_Model()
    elif scenario == "Selected":
      self.test_MosaicViewer_Customized()
    elif scenario == 'SceneView':
      self.test_MosaicViewer_SceneView()      
    elif scenario == 'All':
      self.test_MosaicViewer_All()
    else:
      self.test_MosaicViewer_All()


  def test_MosaicViewer_All(self):
      self.test_MosaicViewer_Volume()
      self.test_MosaicViewer_Model()

  def test_MosaicViewer_Volume(self):
    """ Test modes with 3 volumes.
    """
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    volumes = []
    volumeNames = []

    self.delayDisplay("Starting the test, loading data")

    fPath = eval('slicer.modules.mosaicviewer.path')
    fDirName = os.path.dirname(fPath) + '/Resources/SampleVolumes'

    for f in os.listdir(fDirName):
      if f.endswith(".nrrd"):
          slicer.util.loadVolume(fDirName + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          volumes.append(fName)
          volumeNames.append(fName)

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes = volumes, viewNames = volumeNames, nodeType = "Volume")

  def test_MosaicViewer_Model(self):
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    models = []
    modelNames = []

    self.delayDisplay("Starting the test, loading data")

    fPath = eval('slicer.modules.mosaicviewer.path')()
    fDirName = os.path.dirname(fPath) + '/Resources/SimpleSceneViews'

    for f in os.listdir(fDirName):
      if f.endswith(".vtk"):
          slicer.util.loadModel(fDirName + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          models.append(slicer.util.getNode(fName))
          modelNames.append(fName)

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes = models, viewNames = modelNames, nodeType = "Model")

  def test_MosaicViewer_SceneView(self):
    self.setUp()

    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    sceneViews = []
    svNames = []

    self.delayDisplay("Starting the test, loading data")

    fPath = eval('slicer.modules.mosaicviewer.path')
    fDirName = os.path.dirname(fPath) + '/Resources/SimpleSceneViews'

    for f in os.listdir(fDirName):
      if f.endswith(".mrb"):
        slicer.util.loadScene(fDirName + '/' + f)
        fName, fExtension = os.path.splitext(f)
        print "loading " + fName
        sceneViews.append(slicer.util.getNode(fName))
        svNames.append(fName)

    logic = MosaicViewerLogic()
    logic.renderAllSceneViewNodes()
