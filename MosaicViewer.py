import os
import unittest
from __main__ import vtk, qt, ctk, slicer

# ===========================================
#
# MosaicViewer
#

class MosaicViewer:
  def __init__(self, parent):
    parent.title        = "Mosaic Viewer"
    parent.categories   = ["Wizards"]
    parent.dependencies = []
    parent.contributors = ["Siqi Liu (USYD), Sidong Liu (USYD, BWH), Sonia Pujol (BWH)"]
    parent.helpText     = """
    This module creates mosaic views of multiple scene views
    """
    parent.acknowledgementText = """
    This module was developed by Siqi Liu, University of Sydney, Sidong Liu, University of Sydney and Brigham and Women's
    Hospital, and Sonia Pujol, Brigham and Women's Hospital, and was partially supported by ARC, AADRF, NIH NA-MIC
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

# =====================================================
#
# Numeric parameter input
#
def numericInputFrame(parent, label, tooltip, minimum, maximum, step, decimals):
  inputFrame              = qt.QFrame(parent)
  inputFrame.setLayout(qt.QHBoxLayout())
  inputLabel              = qt.QLabel(label, inputFrame)
  inputLabel.setToolTip(tooltip)
  inputFrame.layout().addWidget(inputLabel)
  inputSpinBox            = qt.QDoubleSpinBox(inputFrame)
  inputSpinBox.setToolTip(tooltip)
  inputSpinBox.minimum    = minimum
  inputSpinBox.maximum    = maximum
  inputSpinBox.singleStep = step
  inputSpinBox.decimals   = decimals
  inputFrame.layout().addWidget(inputSpinBox)
  inputSlider             = ctk.ctkDoubleSlider(inputFrame)
  inputSlider.minimum     = minimum
  inputSlider.maximum     = maximum
  inputSlider.orientation = 1
  inputSlider.singleStep  = step
  inputSlider.setToolTip(tooltip)
  inputFrame.layout().addWidget(inputSlider)
  return inputFrame, inputSlider, inputSpinBox


#=======================================================
#
# MosaicViewerWidget
#
class MosaicViewerWidget:
  # ---------------------------
  def __init__(self, parent = None):
    self.developerMode = True # change this to 'True' to get reload and test
    self.state = None
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

# -------------------------------------------
  def setup(self):
    if self.developerMode:
      #
      # Reload and Test area
      #
      reloadCollapsibleButton       = ctk.ctkCollapsibleButton()
      reloadCollapsibleButton.text  = "Reload && Test"
      self.layout.addWidget(reloadCollapsibleButton)
      reloadFormLayout              = qt.QFormLayout(reloadCollapsibleButton)

      self.clearButton              = qt.QPushButton("Clear Scene")
      self.clearButton.toolTip      = "Clear all the volumes and models in 3D views"
      self.clearButton.name         = "MosaicViewer Clear"
      reloadFormLayout.addWidget(self.clearButton)
      self.clearButton.connect('clicked()', self.onClear)

      # reload button
      # (use this during development, but remove it when delivering
      #  your module to users)
      self.reloadButton             = qt.QPushButton("Reload")
      self.reloadButton.toolTip     = "Reload this Mosaic Viewer"
      self.reloadButton.name        = "MosaicViewer Reload"
      reloadFormLayout.addWidget(self.reloadButton)
      self.reloadButton.connect('clicked()', self.onReload)

      # reload and test button
      # (use this during development, but remove it when delivering your module to users)
      # reload and run specific tests
      # scenarios                     = ('All', 'Model', 'Volume', 'SceneView_Simple', 'SceneView_Complex')
      scenarios                     = ('SceneView_Simple', 'SceneView_Complex')

      for scenario in scenarios:
        button                      = qt.QPushButton("Reload and Test %s" % scenario)
        button.toolTip              = "Reload this module and then run the self test on %s." % scenario
        reloadFormLayout.addWidget(button)
        button.connect('clicked()', lambda s = scenario: self.onReloadAndTest(scenario = s))

    """
    #
    # Input Data Selection Area
    #
    dataSelectionCollapsibleButtion       = ctk.ctkCollapsibleButton()
    dataSelectionCollapsibleButtion.text  = "Select the Volumes && Models"
    self.layout.addWidget(dataSelectionCollapsibleButtion)
    dataSelectionFormLayout               = qt.QFormLayout(dataSelectionCollapsibleButtion)

    dataSelectionFrame                    = qt.QFrame(self.parent)
    dataSelectionFrame.setLayout(qt.QGridLayout())
    dataSelectionFormLayout.addWidget(dataSelectionFrame)

    selectAll                             = qt.QRadioButton("Select All")
    dataSelectionFrame.layout().addWidget(selectAll, 0, 0)

    selectAllVolumes                      = qt.QRadioButton("Select All Volumes")
    dataSelectionFrame.layout().addWidget(selectAllVolumes, 1, 0)

    selectAllModels                       = qt.QRadioButton("Select All Models")
    dataSelectionFrame.layout().addWidget(selectAllModels, 0, 1)

    selectCustomized                      = qt.QRadioButton("Select From Drop List")
    dataSelectionFrame.layout().addWidget(selectCustomized, 1, 1)

    # TODO: add a data check list, enable to select the data from the list.
    # Top three options should be 'Select All', 'Select All Volumes', 'Select All Models'

    """    
    #
    # Layout Option Area
    #
    changeLayoutOptionCollapsibleButtion      = ctk.ctkCollapsibleButton()
    changeLayoutOptionCollapsibleButtion.text = "Choose the Layout"
    self.layout.addWidget(changeLayoutOptionCollapsibleButtion)
    changeLayoutFormLayout                    = qt.QFormLayout(changeLayoutOptionCollapsibleButtion)

    changeLayoutFrame                         = qt.QFrame(self.parent)
    changeLayoutFrame.setLayout(qt.QVBoxLayout())
    changeLayoutFormLayout.addWidget(changeLayoutFrame)

    chooseDefault                             = qt.QRadioButton("Default Layout")
    changeLayoutFrame.layout().addWidget(chooseDefault)
    chooseDefault.setChecked(True)

    chooseCustomized                          = qt.QRadioButton("Customized Layout")
    changeLayoutFrame.layout().addWidget(chooseCustomized)

    chooseRowFrame, chooseRowSlider, chooseRowSliderSpinBox = numericInputFrame(self.parent, "Number of Rows:     ", "Choose Number of Rows", 1, 20, 1, 0)
    changeLayoutFrame.layout().addWidget(chooseRowFrame)

    chooseColumnFrame, chooseColumnSlider, chooseColumnSliderSpinBox = numericInputFrame(self.parent, "Number of Columns:", "Choose Number of Columns", 1, 20, 1, 0)
    changeLayoutFrame.layout().addWidget(chooseColumnFrame)

    class state(object):
      layoutMethod  = 'Default'
      nRows         = 1
      nColumns      = 1

    scope_locals    = locals()

    def connect(obj, evt, cmd):
      def callback(*args):
        current_locals = scope_locals.copy()
        current_locals.update({'args':args})
        exec cmd in globals(), current_locals
        updateGUI()
      obj.connect(evt, callback)

    def updateGUI():
      chooseRowFrame.visible          = state.layoutMethod == "Customized"
      chooseColumnFrame.visible       = state.layoutMethod == "Customized"
      chooseRowSlider.value           = state.nRows
      chooseRowSliderSpinBox.value    = state.nRows
      chooseColumnSlider.value        = state.nColumns
      chooseColumnSliderSpinBox.value = state.nColumns

    connect(chooseDefault, 'clicked(bool)', 'state.layoutMethod = "Default"')
    connect(chooseCustomized, 'clicked(bool)', 'state.layoutMethod = "Customized"')    
    connect(chooseRowSlider, 'valueChanged(double)', 'state.nRows = args[0]')
    connect(chooseRowSliderSpinBox, 'valueChanged(double)', 'state.nRows = args[0]')
    connect(chooseColumnSlider, 'valueChanged(double)', 'state.nColumns = args[0]')
    connect(chooseColumnSliderSpinBox, 'valueChanged(double)', 'state.nColumns = args[0]')

    updateGUI()
    self.updateGUI  = updateGUI
    self.state      = state

    #
    # Execution Area
    #
    # Add vertical spacer
    self.layout.addStretch(1)

    buttonFrame                   = qt.QFrame(self.parent)
    buttonFrame.setLayout(qt.QHBoxLayout())
    self.layout.addWidget(buttonFrame)

    self.restoreDefaults          = qt.QPushButton("Restore Defaults")
    self.restoreDefaults.toolTip  = "Restore the default settings"
    buttonFrame.layout().addWidget(self.restoreDefaults)
    self.restoreDefaults.connect('clicked()', self.onRestore)

    self.applyButton              = qt.QPushButton("Apply")
    self.applyButton.toolTip      = "Apply Mosaic Viewer"
    buttonFrame.layout().addWidget(self.applyButton)
    self.applyButton.connect('clicked()', self.onApply)


  # -------------------------------------
  def onClear(self):
    slicer.mrmlScene.Clear(0)

  # ----------------------------------------------
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
    globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()

  # ---------------------------------------------
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

  # ------------------------------------------
  # def onRenderAllNodes(self, pattern):
  #   logic = MosaicViewerLogic()
  #   logic.renderAllNodes(pattern)

  # -----------------------------------
  def onRestore(self):
    self.onReload("MosaicViewer")

  # ------------------------------------
  def onApply(self):
    logic = MosaicViewerLogic()
    logic.renderAllSceneViewNodes(self.state)

# ============================================================
#
# MosaicViewerLogic
#
class MosaicViewerLogic:
  # -------------------------------
  def __init__(self):
    self.threeDViewPattern = """
      <item><view class="vtkMRMLViewNode" singletontag="{viewName}">
        <property name="viewlabel" action="default">{viewName}</property>
      </view></item>
     """
    # use a nice set of colors
    self.colors = slicer.util.getNode('GenericColors')
    self.lookupTable = self.colors.GetLookupTable()
  
  # ----------------------------------  
  def updateNViewNode(self):
    lviewnode = slicer.util.getNodes("*ViewNode*")
    self.nViewNode =  len(lviewnode.keys())

  # ----------------------------------
  def assignLayoutDescription(self,layoutDescription):
    """assign the xml to the user-defined layout slot"""
    layoutNode = slicer.util.getNode('*LayoutNode*')
    if layoutNode.IsLayoutDescription(layoutNode.SlicerLayoutUserView):
      layoutNode.SetLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    else:
      layoutNode.AddLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    layoutNode.SetViewArrangement(layoutNode.SlicerLayoutUserView)

  # ------------------------------------
  def makeLayout(self, nNodes, sceneviewNames, nRows = 1, nColumns = 1):
    
    import math
    # make an default display layout array, e.g.:
    # nvolumes = 3 -> 2 x 2 (nrows = ncolumes, with only one volume in second row)
    # nvolumes = 5 -> 2 x 3 (nrows < ncolumes, with only two volumes in second row)
    # nvoluems = 11 -> 3 x 4 (nrows < ncolums, with only three volumes in the third row)
    
    if nNodes > nRows * nColumns or nRows is None or nColumns is None:
      qNNodes = math.sqrt(nNodes)
      nRows = math.floor(qNNodes)
      nColumns = math.ceil(qNNodes)
      if nNodes > nRows * nColumns:
          nRows = nRows + 1;

    # construct the XML for the layout
    # - one viewer per volume
    # - default orientation as specified
    #
    actualsceneviewNames = []
    index = 1
    layoutDescription = ''
    layoutDescription += '<layout type="vertical">\n'
    for row in range(int(nRows)):
      layoutDescription += ' <item> <layout type="horizontal">\n'
      for column in range(int(nColumns)):
        try:
          viewName = sceneviewNames[index - 1]
        except IndexError:
          viewName = '%d-%d' % (row,column)
          # viewName = 'null'
        layoutDescription += self.threeDViewPattern.format(viewName = viewName)
        actualsceneviewNames.append(viewName)
        index += 1
      layoutDescription += '</layout></item>\n'
    layoutDescription += '</layout>'
    self.assignLayoutDescription(layoutDescription)

    return actualsceneviewNames

  # -------------------------------------------
  def viewerPerNode(self, nodes = None, sceneviewNames = [], nodeType = ""):
    """ Load each volume in the scene into its own
    3D viewer and link them all together.
    """
    if not nodes:
      nodes = slicer.util.getNodes('*VolumeNode*')

    if len(nodes) == 0:
      return

    actualsceneviewNames = self.makeLayout(nodes, sceneviewNames)

    # put one of the volumes into each view, or none if it should be blank
    threeDNodesByViewName = {}
    layoutManager = slicer.app.layoutManager()

    for index in range(len(nodes)):
      # obtain the name and ID of the current Node
      viewName = actualsceneviewNames[index]

      try:
        nodeID = slicer.util.getNode(viewName)
      except IndexError:
        nodeID = ""

      # get the index-th 3D view node
      threeDWidget = layoutManager.threeDWidget(index)
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
      else:
        raise Exception("Unknown Node Type")

      print "Node Index: ", index, '\nView Node ID: ', viewNode.GetID(),\
         '\nView Name: ', viewName, '\nDisplay Node Visible:', \
         displayNode.GetVisibility(), '\n'

      threeDNodesByViewName[viewName] = threeDView

    return threeDNodesByViewName


  # --------------------------------------
  def renderAllNodes(self, pattern = "vtkMRMLModelNode*"):
    '''
    Search all models which are currently loaded in the mrml scene and 
    render them in the a grid view
    '''
    nodesDict = slicer.util.getNodes(pattern)
    nodes = [n for n in nodesDict.values() if "Slice" not in n.GetName()]
    nodeType = lambda nt: "Model" if pattern == 'vtkMRMLModelNode*' else "Volume" 
    self.viewerPerNode(nodes = nodes, sceneviewNames = [n.GetName() for n in nodes], nodeType = nodeType(pattern))

  # -----------------------------------------
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

  # ------------------------------------------
  def _getCamera(self, sv_nodes, nodes_dict, sceneviewNames):
    """
    Extract the camera nodes from the scene views
    """
    cameraNodeCollection              = [] # cameraNode collection
    for s in range(len(sv_nodes)):
      c_sceneview                     = nodes_dict[sceneviewNames[s]] 
      sceneviewCameraNode             = c_sceneview.GetNodesByClass('vtkMRMLCameraNode').GetItemAsObject(0)
      newCameraNode                   = sceneviewCameraNode.CreateNodeInstance()
      newCameraNode.Copy(sceneviewCameraNode)
      cameraNodeCollection.append(newCameraNode)
    for i in range(len(sv_nodes)):
      print '= Camera Position: ', i, ' ', cameraNodeCollection[i].GetCamera().GetPosition()

    return cameraNodeCollection

  # ------------------------------------------
  def renderAllSceneViewNodes(self, state = None):

      print '*************** Start loading the scene views ***************'

      """ @ Deprecated
      # get all model and fiber nodes from scene
      scene = slicer.mrmlScene
      scene_model_collection = scene.GetNodesByClass('vtkMRMLModelNode')
      scene_fiber_collection = scene.GetNodesByClass('vtkMRMLFiberBundleNode')
      n_scene_model          = scene_model_collection.GetNumberOfItems()
      n_scene_fiber          = scene_fiber_collection.GetNumberOfItems()
      iter_scene_model       = scene_model_collection.NewIterator()
      iter_scene_fiber       = scene_fiber_collection.NewIterator()
      """
      
      print '------------------------------------------'
      if state is not None:
        print state.layoutMethod, 'Layout: ', state.nRows, ' * ', state.nColumns
        self.makeLayout(1, 'dummy', 1, 1)

    
      # new implementation using vtkMRMLModelDisplayNode instead of vtkMRMLModelNode
      scene                     = slicer.mrmlScene

      # remove all previous view nodes
      lViewNode   = scene.GetNodesByClass('vtkMRMLViewNode')

      for v in range(lViewNode.GetNumberOfItems()):
        viewNodeToRemove    = lViewNode.GetItemAsObject(v)
        print ' - Removing view: ', viewNodeToRemove.GetName()
        scene.RemoveNode(viewNodeToRemove)

      lCameraNode = scene.GetNodesByClass('vtkMRMLCameraNode')
      for c in range(lCameraNode.GetNumberOfItems()):
        cameraNodeToRemove  = lCameraNode.GetItemAsObject(c)
        print ' - Remove camera: ', cameraNodeToRemove.GetName()
        scene.RemoveNode(cameraNodeToRemove)
        
      
      # original number of view nodes for each display node, '0' means associated with all view nodes
      # numberOfViews       = []
      # print '--------------------------------'
      # for d in range(n_scene_display):
      #   displayi          = iter_scene_display.GetCurrentObject()
      #   iter_scene_display.GoToNextItem()
      #   numberOfViews.append(displayi.GetNumberOfViewNodeIDs())
      #   print displayi.GetName(), ': ', numberOfViews[d]

      # Find loaded sceneviews
      nodes_dict = slicer.util.getNodes('*vtkMRMLSceneViewNode*')
      
      # Filter out the 'Slice Data Bundle Scene' which were saved at MRML file save point
      sv_nodes   = [n for n in nodes_dict.values() if "Slice" not in n.GetName()]
      
      # Retun if no scene view
      if len(sv_nodes) == 0 :
        return 

      # Scene view names, sorted in alphabetical order
      sceneviewNames = [n.GetName() for n in sv_nodes]
      sceneviewNames.sort()

      # extract the camera nodes and add to the scene, must be done before making layout
      # cameraNodeCollection              = self._getCamera(sv_nodes, nodes_dict, sceneviewNames)
      
      # Make the layout according to the # scene view nodes
      if state is None or state.layoutMethod == 'Default':
        self.makeLayout(len(sv_nodes), sceneviewNames)
      else:
        self.makeLayout(len(sv_nodes), sceneviewNames, state.nRows, state.nColumns)

      layoutManager                     = slicer.app.layoutManager()
      nview                             = layoutManager.threeDViewCount 
      threeDViewMap                     = {} # ThreeDView <ID, Node>
      viewMap                           = {} # View Node <Name, ID>

      sceneCameraNodeCollection         = scene.GetNodesByClass('vtkMRMLCameraNode')

      for v in range(nview):
        threeDWidget                    = layoutManager.threeDWidget(v)
        threeDView                      = threeDWidget.threeDView() 
        viewNode                        = threeDView.mrmlViewNode()
        scene.AddNode(viewNode)
        viewMap[viewNode.GetName()]     = viewNode.GetID()   
        threeDViewMap[viewNode.GetName()] = threeDView   

      # iterate all loaded scene view nodes
      for s in range(len(sv_nodes)):

        # get current sceneview
        # c_sceneview                = sv_nodes[s]
        c_sceneview           = nodes_dict[sceneviewNames[s]] 
        # find the view with the same name as the sceneview
        viewName              = 'View' + c_sceneview.GetName()
        viewID                = viewMap[viewName]
        threeDView            = threeDViewMap[viewName]
        
        # add nodes in sceneview to scene
        print '-------------------------------------------'
        sceneview_node_collection       = c_sceneview.GetNodesByClass('vtkMRMLNode')
        n_sceneview_node                = sceneview_node_collection.GetNumberOfItems()

        for n in range(n_sceneview_node):
          sv_nodei                      = sceneview_node_collection.GetItemAsObject(n)
          if scene.GetNodeByID(sv_nodei.GetID()) is None:
            # nodei                       = sv_nodei.CreateNodeInstance()
            # nodei.CopyWithScene(sv_nodei)
            scene.AddNode(sv_nodei)
            print ' + Adding node  : ', sv_nodei.GetID()
          else:
            print ' = Existing node: ', sv_nodei.GetID()

        # find the display models are in this scene view
        sceneview_display_collection    = c_sceneview.GetNodesByClass('vtkMRMLDisplayNode')
        n_sceneview_display             = sceneview_display_collection.GetNumberOfItems()
        for d in range(n_sceneview_display):
          displayi                      = sceneview_display_collection.GetItemAsObject(d)
          s_displayi                    = scene.GetNodeByID(displayi.GetID())
          if displayi.GetVisibility():
            s_displayi.AddViewNodeID(viewID)
            s_displayi.SetVisibility(1)
          else:
            s_displayi.RemoveViewNodeID(viewID)

        # find the 2D slices in the scene view
        sceneview_slice_collection      = c_sceneview.GetNodesByClass('vtkMRMLSliceNode')
        n_sceneview_slice               = sceneview_slice_collection.GetNumberOfItems()
        for d in range(n_sceneview_slice):
          slicei                        = sceneview_slice_collection.GetItemAsObject(d)
          s_slicei                      = scene.GetNodeByID(slicei.GetID())
          if slicei.GetSliceVisible():
            s_slicei.AddThreeDViewID(viewID)
            s_slicei.SetSliceVisible(1)
          else:
            print ' * Missing node : ', slicei.GetID()
            s_slicei.RemoveThreeDViewID(viewID)


        # copy the attributes of the original view nodes to the new view node
        sceneview_view_collection       = c_sceneview.GetNodesByClass('vtkMRMLViewNode')
        n_sceneview_view                = sceneview_view_collection.GetNumberOfItems()
        originalViewNode                = sceneview_view_collection.GetItemAsObject(0)
        # viewNode                        = scene.GetNodeByID(viewID)
        # viewNode.Copy(originalViewNode)
        # viewNode.SetName(viewName)
        
        # Restore the position
        print '-------------------------------------------'
        sceneCameraNode               = sceneCameraNodeCollection.GetItemAsObject(s)
        sceneviewCameraNodeCollection = c_sceneview.GetNodesByClass('vtkMRMLCameraNode')
        nsvcamera                     = sceneviewCameraNodeCollection.GetNumberOfItems()
        print ' Number of Camera Nodes:', nsvcamera
        
        for svc in range(nsvcamera):
          sceneviewCameraNode         = sceneviewCameraNodeCollection.GetItemAsObject(svc)
          if sceneviewCameraNode.GetActiveTag() == originalViewNode.GetID():
            print ' Found the camera node:    ', originalViewNode.GetID(), ' - ', sceneviewCameraNode.GetID()
            c_sceneCameraNode         = scene.GetNodeByID(sceneCameraNode.GetID())
            c_sceneCameraNode.Copy(sceneviewCameraNode)
            c_sceneCameraNode.UpdateScene(scene)
            print ' Restore camera position:  ', sceneviewCameraNode.GetCamera().GetPosition()

        # print 'Scene Camera Node Reference vs. Sceneview Camera Node Reference'
        # print sceneCameraNode.GetReferenceCount(),     ' vs. ', sceneviewCameraNode.GetReferenceCount()

        """
        # get the scene camera nodes and the sceneview camera node 
        sceneview_node_collection       = c_sceneview.GetNodesByClass('vtkMRMLNode')
        n_sceneview_node                = sceneview_node_collection.GetNumberOfItems()


        for t in range(n_sceneview_camera):
          node = sceneview_node_collection.GetItemAsObject(t)
          sv_node = scene.GetNodeByID(node.GetID())
          if sv_node is not None:
            print '= ', sv_node.GetID()
            sv_node.UpdateScene(scene)
          else:
            print '+ ', node.GetClassName()
            sv_node = node.CreateNodeInstance()
            sv_node.CopyWithScene(node)
            scene.AddNode(sv_node)
            sv_node.UpdateScene(scene)

        # """
        

      print '*********** Finish loading all scene views *************'

# ================================================
#
# MosaicViewerTest
#   
class MosaicViewerTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """ 
  # -------------------------------
  def delayDisplay(self,message,msec = 1500):
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

  # -----------------------------------
  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  # ----------------------------------------
  def runTest(self, scenario = None):
    """Run as few or as many tests as needed here.
    """
    self.setUp()

    if scenario   == "Volume":
      self.test_MosaicViewer_Volume()
    elif scenario == "Model":
      self.test_MosaicViewer_Model()
    elif scenario == 'SceneView_Simple':
      self.test_MosaicViewer_SceneView('SeneView_Simple')      
    elif scenario == 'SceneView_Complex':
      self.test_MosaicViewer_SceneView('SeneView_Complex')      
    elif scenario == 'All':
      self.test_MosaicViewer_All()
    else:
      self.test_MosaicViewer_All()

  # -------------------------------------
  def test_MosaicViewer_All(self):
      self.test_MosaicViewer_Volume()
      self.test_MosaicViewer_Model()
      self.test_MosaicViewer_SceneView('SceneView_Simple')
      self.test_MosaicViewer_SceneView('SceneView_Complex')

  # ----------------------------------------
  def test_MosaicViewer_Volume(self):
    """ Test modes with 7 volumes.
    """
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    volumes = []
    volumeNames = []

    self.delayDisplay("Starting the test, loading data")

    fPath = eval('slicer.modules.mosaicviewer.path')
    fDir = os.path.dirname(fPath) + '/Resources/SampleVolumes'

    for f in os.listdir(fDir):
      if f.endswith(".nrrd"):
          slicer.util.loadVolume(fDir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          volumes.append(fName)
          volumeNames.append(fName)

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes = volumes, sceneviewNames = volumeNames, nodeType = "Volume")

  # --------------------------------------
  def test_MosaicViewer_Model(self):
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    models = []
    modelNames = []

    self.delayDisplay("Starting the test, loading data")

    fPath = eval('slicer.modules.mosaicviewer.path')

    fDir = os.path.dirname(fPath) + '/Resources/SampleModels'

    for f in os.listdir(fDir):
      if f.endswith(".vtk"):
          slicer.util.loadModel(fDir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loading " + fName
          models.append(slicer.util.getNode(fName))
          modelNames.append(fName)

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes = models, sceneviewNames = modelNames, nodeType = "Model")

  # -------------------------------------
  def test_MosaicViewer_SceneView(self, sub_scenario):
    
    self.setUp()

    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    sceneViews = []
    svNames = []

    self.delayDisplay("Starting the test, loading data")

    fPath = eval('slicer.modules.mosaicviewer.path')
    if sub_scenario == 'SeneView_Simple':
      fDir = os.path.dirname(fPath) + '/Resources/SampleSceneViewsSimple'
    elif sub_scenario == 'SeneView_Complex':
      fDir = os.path.dirname(fPath) + '/Resources/SampleSceneViewsComplex'

    for f in os.listdir(fDir):
      if f.endswith(".mrb"):
        slicer.util.loadScene(fDir + '/' + f)
        fName, fExtension = os.path.splitext(f)
        print "loading " + fName
        sceneViews.append(slicer.util.getNode(fName))
        svNames.append(fName)

    logic = MosaicViewerLogic()
    logic.renderAllSceneViewNodes()


