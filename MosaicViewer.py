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

    # Add this test to the SelfTest module's list for disscovery when the module
    # is created.  Since this module may be disscovered before SelfTests itself,
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
      # scenarios                     = ('All', 'Model', 'Volume', 'sceneViewSimple', 'sceneViewComplex')
      scenarios                     = ('sceneViewSimple', 'sceneViewComplex', 'syncCam')

      for scenario in scenarios:
        button                      = qt.QPushButton("Reload and Test %s" % scenario)
        button.toolTip              = "Reload this module and then run the self test on %s." % scenario
        reloadFormLayout.addWidget(button)
        button.connect('clicked()', lambda s = scenario: self.onReloadAndTest(scenario = s))
 
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
    changeLayoutFormLayout.addWidget(chooseDefault)
    chooseDefault.setChecked(True)

    chooseCustomized                          = qt.QRadioButton("Customized Layout")
    changeLayoutFormLayout.addWidget(chooseCustomized)

    chooseRowFrame, chooseRowSlider, chooseRowSliderSpinBox = numericInputFrame(self.parent, 
                                                              "Number of Rows:     ", "Choose Number of Rows", 1, 20, 1, 0)
    changeLayoutFormLayout.addWidget(chooseRowFrame)

    chooseColumnFrame, chooseColumnSlider, chooseColumnSliderSpinBox = numericInputFrame(self.parent, 
                                                                                         "Number of Columns:", 
                                                                                         "Choose Number of Columns", 1, 20, 1, 0)
    changeLayoutFormLayout.addWidget(chooseColumnFrame)

    #
    # Sync View Area
    #
    syncCamCollapsibleButtion      = ctk.ctkCollapsibleButton()
    syncCamCollapsibleButtion.text = 'synchronise all views'
    self.layout.addWidget(syncCamCollapsibleButtion)
    syncCamLayout                  = qt.QFormLayout(syncCamCollapsibleButtion)

    # sync camera button
    self.syncCamSelector                        = slicer.qMRMLNodeComboBox(syncCamCollapsibleButtion)
    self.syncCamSelector.nodeTypes              = ( ("vtkMRMLViewNode"), "" )
    self.syncCamSelector.selectNodeUponCreation = True
    self.syncCamSelector.addEnabled             = False
    self.syncCamSelector.removeEnabled          = False
    self.syncCamSelector.noneEnabled            = False
    self.syncCamSelector.showHidden             = False
    self.syncCamSelector.showChildNodeTypes     = False
    self.syncCamSelector.setMRMLScene( slicer.mrmlScene )
    self.syncCamSelector.setToolTip( "Pick the view to be synchronised." )
    syncCamLayout.addRow("View to synchronise", self.syncCamSelector) 

    self.syncCamButton         = qt.QPushButton("Sync Camera")
    self.syncCamButton.toolTip = "Sync all the cameras"
    self.syncCamButton.name    = "MosaicViewer syncCam"
    syncCamLayout.addRow(self.syncCamButton)
    self.syncCamButton.connect('clicked()', self.onsyncCam)

    class state(object):
      layoutMethod  = 'Default'
      nRows         = 1
      nColumns      = 1

    scopeLocals    = locals()

    def connect(obj, evt, cmd):
      def callback(*args):
        currentLocals = scopeLocals.copy()
        currentLocals.update({'args':args})
        exec cmd in globals(), currentLocals
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

  #------------------------------------
  def onsyncCam(self):
    logic = MosaicViewerLogic()
    logic.syncCam(self.syncCamSelector.currentNode())

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
    # make an default dissplay layout array, e.g.:
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

      # use volumerendering module to make the volume rendering dissplay node
      if nodeType == "Volume":
        logic = slicer.modules.volumerendering.logic()
        dissplayNode = logic.CreateVolumeRenderingdissplayNode()
        slicer.mrmlScene.AddNode(dissplayNode)
        dissplayNode.UnRegister(logic)
        dissplayNode.AddViewNodeID(viewNode.GetID())
        logic.UpdatedissplayNodeFromVolumeNode(dissplayNode, nodeID)
        dissplayNode.SetVisibility(True)
        nodeID.AddAndObservedissplayNodeID(dissplayNode.GetID())
      elif nodeType == "Model":
        # use models module to render the dissplay node of this model
        dissplayNode = nodeID.GetdissplayNode()
        # slicer.mrmlScene.AddNode(dissplayNode)
        nodeID.AddAndObservedissplayNodeID(dissplayNode.GetID())
        dissplayNode.AddViewNodeID(viewNode.GetID())
        dissplayNode.SetVisibility(True)
      else:
        raise Exception("Unknown Node Type")

      print "Node Index: ", index, '\nView Node ID: ', viewNode.GetID(),\
         '\nView Name: ', viewName, '\ndissplay Node Visible:', \
         dissplayNode.GetVisibility(), '\n'

      threeDNodesByViewName[viewName] = threeDView

    return threeDNodesByViewName


  # --------------------------------------
  def renderAllNodes(self, pattern = "vtkMRMLModelNode*"):
    '''
    Search all models which are currently loaded in the mrml scene and 
    render them in the a grid view
    '''
    nodesdisct = slicer.util.getNodes(pattern)
    nodes = [n for n in nodesdisct.values() if "Slice" not in n.GetName()]
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
  def _getCamera(self, svNodes, nodesdisct, sceneviewNames):
    """
    Extract the camera nodes from the scene views
    """
    cameraNodeCollection              = [] # cameraNode collection
    for s in range(len(svNodes)):
      cSceneView                     = nodesdisct[sceneviewNames[s]] 
      sceneviewCameraNode             = cSceneView.GetNodesByClass('vtkMRMLCameraNode').GetItemAsObject(0)
      newCameraNode                   = sceneviewCameraNode.CreateNodeInstance()
      newCameraNode.Copy(sceneviewCameraNode)
      cameraNodeCollection.append(newCameraNode)
    for i in range(len(svNodes)):
      print '= Camera Position: ', i, ' ', cameraNodeCollection[i].GetCamera().GetPosition()

    return cameraNodeCollection

  # ------------------------------------------
  def renderAllSceneViewNodes(self, state = None):

      print '*************** Start loadisng the scene views ***************'

      print '------------------------------------------'
      if state is not None:
        print state.layoutMethod, 'Layout: ', state.nRows, ' * ', state.nColumns
        self.makeLayout(1, 'dummy', 1, 1)

    
      # new implementation using vtkMRMLModeldissplayNode instead of vtkMRMLModelNode
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
        

      # Find loaded sceneviews
      nodesdisct = slicer.util.getNodes('*vtkMRMLSceneViewNode*')
      
      # Filter out the 'Slice Data Bundle Scene' which were saved at MRML file save point
      svNodes   = [n for n in nodesdisct.values() if "Slice" not in n.GetName()]
      
      # Return if no scene view
      if len(svNodes) == 0 :
        return 

      # Scene view names, sorted in alphabetical order
      sceneviewNames = [n.GetName() for n in svNodes]
      sceneviewNames.sort()

      # extract the camera nodes and add to the scene, must be done before making layout
      # cameraNodeCollection              = self._getCamera(svNodes, nodesdisct, sceneviewNames)
      
      # Make the layout accordisng to the # scene view nodes
      if state is None or state.layoutMethod == 'Default':
        self.makeLayout(len(svNodes), sceneviewNames)
      else:
        self.makeLayout(len(svNodes), sceneviewNames, state.nRows, state.nColumns)

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
      for s in range(len(svNodes)):

        # get current sceneview
        # cSceneView                = svNodes[s]
        cSceneView           = nodesdisct[sceneviewNames[s]] 
        # find the view with the same name as the sceneview
        viewName              = 'View' + cSceneView.GetName()
        viewID                = viewMap[viewName]
        threeDView            = threeDViewMap[viewName]
        
        # add nodes in sceneview to scene
        print '-------------------------------------------'
        sceneviewNodeCollection = cSceneView.GetNodesByClass('vtkMRMLNode')
        n_sceneview_node        = sceneviewNodeCollection.GetNumberOfItems()

        for n in range(n_sceneview_node):
          sv_nodei                      = sceneviewNodeCollection.GetItemAsObject(n)
          if scene.GetNodeByID(sv_nodei.GetID()) is None:
            # nodei                       = sv_nodei.CreateNodeInstance()
            # nodei.CopyWithScene(sv_nodei)
            scene.AddNode(sv_nodei)
            #print ' + Addisng node  : ', sv_nodei.GetID()
          else:
            #print ' = Existing node: ', sv_nodei.GetID()
            pass

        # find the dissplay models are in this scene view
        sceneviewdissplayCollection    = cSceneView.GetNodesByClass('vtkMRMLdissplayNode')
        nSceneviewdissplay             = sceneviewdissplayCollection.GetNumberOfItems()

        for d in range(nSceneviewdissplay):
          dis   = sceneviewdissplayCollection.GetItemAsObject(d)
          disInScene = scene.GetNodeByID(dis.GetID())
          if dis.GetVisibility():
            disInScene.AddViewNodeID(viewID)
            disInScene.SetVisibility(1)
          else:
            disInScene.RemoveViewNodeID(viewID)

        # find the 2D slices in the scene view
        sceneview_slice_collection      = cSceneView.GetNodesByClass('vtkMRMLSliceNode')
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
        
        # Restore the position
        print '-----------------Restore Cameras--------------------------'
        sceneview_view_collection     = cSceneView.GetNodesByClass('vtkMRMLViewNode')
        svViewNode              = sceneview_view_collection.GetItemAsObject(0)
        #sceneCameraNode               = sceneCameraNodeCollection.GetItemAsObject(s)
        sceneviewCameraNodeCollection = cSceneView.GetNodesByClass('vtkMRMLCameraNode')
        nsvcamera                     = sceneviewCameraNodeCollection.GetNumberOfItems()

        print ' Number of Camera Nodes:', nsvcamera
        
        svcam2restore = None

        for svc in range(nsvcamera):
          sceneviewCameraNode = sceneviewCameraNodeCollection.GetItemAsObject(svc)
          if sceneviewCameraNode.GetActiveTag() == svViewNode.GetID():
            print ' Found the camera node in sceneview: ', svViewNode.GetName(), ' - ', sceneviewCameraNode.GetID()
            svcam2restore = sceneviewCameraNode
            break

        if svcam2restore == None:
          raise Exception('No camera to restore for sceneview:' + cSceneView.GetName() )

        # Find the camera node of the current viewNode to apply 
        scam2restore = None
        viewNode = threeDView.mrmlViewNode()
        for c in range(sceneCameraNodeCollection.GetNumberOfItems()):
          cam = sceneCameraNodeCollection.GetItemAsObject(c)
          if cam.GetActiveTag() == viewNode.GetID():
            print ' Found the camera node in scene: ', viewNode.GetName(), ' - ', cam.GetID()
            scam2restore = cam
            break

        if scam2restore == None:
          raise Exception('No camera to restore for view:' + viewNode.GetName() )

        scam2restore.Copy(svcam2restore)
        scam2restore.SetActiveTag(viewNode.GetID())
        scam2restore.UpdateScene(scene)
        print ' Restore camera position: ', sceneviewCameraNode.GetCamera().GetPosition()
       
      print '*********** Finish loadisng all scene views *************'

      print 'DEBUG:'
      for c in range(sceneCameraNodeCollection.GetNumberOfItems()):
        cam = sceneCameraNodeCollection.GetItemAsObject(c)
        print cam.GetActiveTag()

  def syncCam(self, viewNode):
    # This function will retrieve the camera node of the specific ViewNode to all the ViewNodes
    scene = slicer.mrmlScene
    sceneCameraCollection = scene.GetNodesByClass("vtkMRMLCameraNode")
    ncam = sceneCameraCollection.GetNumberOfItems()

    cam2apply = None 
    
    print 'DEBUG find CAMNODE ========='
    # Get the node to be applied to all views
    for i in range(ncam):
      cam = sceneCameraCollection.GetItemAsObject(i)
      print cam.GetActiveTag(), viewNode.GetID()
      if cam.GetActiveTag() == viewNode.GetID():
        cam2apply = cam 
        break

    print 'DEBUG end find CAMNODE======'

    if cam2apply == None:
      raise Exception('No camera node is attached to this view')

    for i in range(ncam):
        cam = sceneCameraCollection.GetItemAsObject(i)
        atag = cam.GetActiveTag()
        if atag != cam2apply.GetActiveTag():
          cam.Copy(cam2apply)
          cam.SetActiveTag(atag) # Restore the previous active tag
          cam.UpdateScene(scene)


# ================================================
#
# MosaicViewerTest
#   
class MosaicViewerTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """ 
  # -------------------------------
  def delaydissplay(self,message,msec = 1500):
    """This utility method dissplays a small disalog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.Qdialog()
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
      self.testMosaicViewerVolume()
    elif scenario == "Model":
      self.testMosaicViewerModel()
    elif scenario == 'sceneViewSimple':
      self.testMosaicViewerSceneView('SeneView_Simple')      
    elif scenario == 'sceneViewComplex':
      self.testMosaicViewerSceneView('SeneView_Complex')      
    elif scenario == 'syncCam':
      self.testMosaicViewerSceneView('SeneView_Complex')      
      self.testMosaicViewerSyncCam()      
    elif scenario == 'All':
      self.testMosaicViewerAll()
    else:
      self.testMosaicViewerAll()

  # -------------------------------------
  def testMosaicViewerAll(self):
      self.testMosaicViewerVolume()
      self.testMosaicViewerModel()
      self.testMosaicViewerSceneView('sceneViewSimple')
      self.testMosaicViewerSceneView('sceneViewComplex')

  # ----------------------------------------
  def testMosaicViewerVolume(self):
    """ Test modes with 7 volumes.
    """
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    volumes = []
    volumeNames = []

    self.delaydissplay("Starting the test, loadisng data")

    fPath = eval('slicer.modules.mosaicviewer.path')
    fdir = os.path.dirname(fPath) + '/Resources/SampleVolumes'

    for f in os.listdisr(fdir):
      if f.endswith(".nrrd"):
          slicer.util.loadVolume(fdir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loadisng " + fName
          volumes.append(fName)
          volumeNames.append(fName)

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes = volumes, sceneviewNames = volumeNames, nodeType = "Volume")

  # --------------------------------------
  def testMosaicViewerModel(self):
    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    models = []
    modelNames = []

    self.delaydissplay("Starting the test, loadisng data")

    fPath = eval('slicer.modules.mosaicviewer.path')

    fdir = os.path.dirname(fPath) + '/Resources/SampleModels'

    for f in os.listdisr(fdir):
      if f.endswith(".vtk"):
          slicer.util.loadModel(fdir + '/' + f)
          fName, fExtension = os.path.splitext(f)
          print "loadisng " + fName
          models.append(slicer.util.getNode(fName))
          modelNames.append(fName)

    logic = MosaicViewerLogic()
    logic.viewerPerNode(nodes = models, sceneviewNames = modelNames, nodeType = "Model")

  # -------------------------------------
  def testMosaicViewerSceneView(self, subScenario):
    
    self.setUp()

    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('MosaicViewer')

    sceneViews = []
    svNames = []

    self.delaydissplay("Starting the test, loadisng data")

    fPath = eval('slicer.modules.mosaicviewer.path')
    if subScenario == 'SeneView_Simple':
      fdir = os.path.dirname(fPath) + '/Resources/SampleSceneViewsSimple'
    elif subScenario == 'SeneView_Complex':
      fdir = os.path.dirname(fPath) + '/Resources/SampleSceneViewsComplex'

    for f in os.listdisr(fdir):
      if f.endswith(".mrb"):
        slicer.util.loadScene(fdir + '/' + f)
        fName, fExtension = os.path.splitext(f)
        print "loadisng " + fName
        sceneViews.append(slicer.util.getNode(fName))
        svNames.append(fName)

    logic = MosaicViewerLogic()
    logic.renderAllSceneViewNodes()

  def testMosaicViewerSyncCam(self):
    import random

    # Load some dummy sceneviews
    scene = slicer.mrmlScene
    cams  = scene.GetNodesByClass('vtkMRMLCameraNode')
    ncam  = cams.GetNumberOfItems()
    views = scene.GetNodesByClass('vtkMRMLViewNode')

    # disstort the first camera 
    view1 = views.GetItemAsObject(0)
    view2 = views.GetItemAsObject(1)
    views2test = []
    views2test.append(view1)
    views2test.append(view2)

    logic = MosaicViewerLogic()
    for vidx, view in enumerate(views2test):
      cam2disstort = None

      for i in range(ncam):
        cam = cams.GetItemAsObject(i)
        if cam.GetActiveTag() == view.GetID():
          cam2disstort = cam
          break

      self.delaydissplay('disstort view %d' % vidx, 2000)
      cam2disstort.SetPosition(random.uniform(0,500), random.uniform(0,500), random.uniform(0,500))
      self.delaydissplay('Sync all to view %d' % vidx, 2000)
      cam2disstort.UpdateScene(scene)
      logic.syncCam(view)
