import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# CompareVolumes
#

class CompareVolumes:
  def __init__(self, parent):
    parent.title = "Compare Volumes"
    parent.categories = ["Wizards"]
    parent.dependencies = []
    parent.contributors = ["Steve Pieper (Isomics)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module helps organize layouts and volume compositing to help compare images
    """
    parent.acknowledgementText = """
    This file was originally developed by Steve Pieper, Isomics, Inc.
    It was partially funded by NIH grant 3P41RR013218-12S1
    and this work is part of the National Alliance for Medical Image
    Computing (NAMIC), funded by the National Institutes of Health
    through the NIH Roadmap for Medical Research, Grant U54 EB005149.
    Information on the National Centers for Biomedical Computing
    can be obtained from http://nihroadmap.nih.gov/bioinformatics.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['CompareVolumes'] = self.runTest

  def runTest(self):
    tester = CompareVolumesTest()
    tester.runTest()

#
# qCompareVolumesWidget
#

class CompareVolumesWidget:
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

    # reload and run specific tests
    scenarios = ("Three Volume", "View Watcher", "LayerReveal",)
    for scenario in scenarios:
      button = qt.QPushButton("Reload and Test %s" % scenario)
      self.reloadAndTestButton.toolTip = "Reload this module and then run the %s self test." % scenario
      reloadFormLayout.addWidget(button)
      button.connect('clicked()', lambda s=scenario: self.onReloadAndTest(scenario=s))

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Target Volume: ", self.inputSelector)

    #
    # Add layer reveal area
    #
    layerRevealCollapsibleButton = ctk.ctkCollapsibleButton()
    layerRevealCollapsibleButton.text = "Layer Reveal Cursor"
    self.layout.addWidget(layerRevealCollapsibleButton)
    layerRevealFormLayout = qt.QFormLayout(layerRevealCollapsibleButton)

    self.layerRevealCheck = qt.QCheckBox()
    layerRevealFormLayout.addRow("Layer Reveal Cursor", self.layerRevealCheck)
    self.layerRevealCheck.connect("toggled(bool)", self.onLayerRevealToggled)

    # Add vertical spacer
    self.layout.addStretch(1)

  def onLayerRevealToggled(self):
    if self.layerRevealCheck.checked:
      self.layerReveal = LayerReveal()
    else:
      self.layerReveal.tearDown()
      self.layerReveal = None

  def onReload(self,moduleName="CompareVolumes"):
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

  def onReloadAndTest(self,moduleName="CompareVolumes",scenario=None):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest(scenario=scenario)
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# CompareVolumesLogic
#

class CompareVolumesLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    self.sliceViewItemPattern = """
      <item><view class="vtkMRMLSliceNode" singletontag="{viewName}">
        <property name="orientation" action="default">{orientation}</property>
        <property name="viewlabel" action="default">{viewName}</property>
        <property name="viewcolor" action="default">{color}</property>
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
    c = 1.5 * math.sqrt(len(volumeNodes))
    columns = math.floor(c)
    if c != columns:
      columns += 1
    if columns > len(volumeNodes):
      columns = len(volumeNodes)
    r = len(volumeNodes)/columns
    rows = math.floor(r)
    if r != rows:
      rows += 1

    #
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
        rgb = [int(round(v*255)) for v in self.lookupTable.GetTableValue(index)[:-1]]
        color = '#%0.2X%0.2X%0.2X' % tuple(rgb)
        layoutDescription += self.sliceViewItemPattern.format(viewName=viewName,orientation=orientation,color=color)
        actualViewNames.append(viewName)
        index += 1
      layoutDescription += '</layout></item>\n'
    layoutDescription += '</layout>'
    self.assignLayoutDescription(layoutDescription)

    # let the widgets all decide how big they should be
    slicer.app.processEvents()

    # if background is specified, move it to the front of the list:
    #  it will show up in first slice view with itself as in foreground
    if background:
      volumeNodes = [background] + [ i for i in volumeNodes if i != background]

    # put one of the volumes into each view, or none if it should be blank
    sliceNodesByViewName = {}
    layoutManager = slicer.app.layoutManager()
    for index in range(len(actualViewNames)):
      viewName = actualViewNames[index]
      try:
        volumeNodeID = volumeNodes[index].GetID()
      except IndexError:
        volumeNodeID = ""

      sliceWidget = layoutManager.sliceWidget(viewName)
      compositeNode = sliceWidget.mrmlSliceCompositeNode()
      if background:
        compositeNode.SetBackgroundVolumeID(background.GetID())
        compositeNode.SetForegroundVolumeID(volumeNodeID)
      else:
        compositeNode.SetBackgroundVolumeID(volumeNodeID)

      if label:
        compositeNode.SetLabelVolumeID(label.GetID())

      sliceNode = sliceWidget.mrmlSliceNode()
      sliceNode.SetOrientation(orientation)
      sliceWidget.fitSliceToBackground()
      sliceNodesByViewName[viewName] = sliceNode
    return sliceNodesByViewName

  def rotateToVolumePlanes(self, referenceVolume):
    sliceNodes = slicer.util.getNodes('vtkMRMLSliceNode*')
    for name, node in sliceNodes.items():
      node.RotateToVolumePlane(referenceVolume)
    # snap to IJK to try and avoid rounding errors
    sliceLogics = slicer.app.layoutManager().mrmlSliceLogics()
    numLogics = sliceLogics.GetNumberOfItems()
    for n in range(numLogics):
      l = sliceLogics.GetItemAsObject(n)
      l.SnapSliceOffsetToIJK()

  def zoom(self,factor,sliceNodes=None):
    """Zoom slice nodes by factor.
    factor: "Fit" or +/- amount to zoom
    sliceNodes: list of slice nodes to change, None means all.
    """
    if not sliceNodes:
      sliceNodes = slicer.util.getNodes('vtkMRMLSliceNode*')
    layoutManager = slicer.app.layoutManager()
    for sliceNode in sliceNodes.values():
      if factor == "Fit":
        sliceWidget = layoutManager.sliceWidget(sliceNode.GetLayoutName())
        if sliceWidget:
          sliceWidget.sliceLogic().FitSliceToAll()
      else:
        newFOVx = sliceNode.GetFieldOfView()[0] * factor
        newFOVy = sliceNode.GetFieldOfView()[1] * factor
        newFOVz = sliceNode.GetFieldOfView()[2]
        sliceNode.SetFieldOfView( newFOVx, newFOVy, newFOVz )
        sliceNode.UpdateMatrices()

  def viewersPerVolume(self,volumeNodes=None,background=None,label=None,include3D=False):
    """ Make an axi/sag/cor(/3D) row of viewers
    for each volume in the scene.
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

    #
    # construct the XML for the layout
    # - one row per volume
    # - viewers for each orientation
    #
    orientations = ('Axial', 'Sagittal', 'Coronal')
    actualViewNames = []
    index = 1
    layoutDescription = ''
    layoutDescription += '<layout type="vertical">\n'
    row = 0
    for volumeNode in volumeNodes:
      layoutDescription += ' <item> <layout type="horizontal">\n'
      column = 0
      for orientation in orientations:
        viewName = volumeNode.GetName() + '-' + orientation
        rgb = [int(round(v*255)) for v in self.lookupTable.GetTableValue(index)[:-1]]
        color = '#%0.2X%0.2X%0.2X' % tuple(rgb)
        layoutDescription += self.sliceViewItemPattern.format(viewName=viewName,orientation=orientation,color=color)
        actualViewNames.append(viewName)
        index += 1
        column += 1
      if include3D:
        print('TODO: add 3D viewer')
      layoutDescription += '</layout></item>\n'
    row += 1
    layoutDescription += '</layout>'
    self.assignLayoutDescription(layoutDescription)

    # let the widgets all decide how big they should be
    slicer.app.processEvents()

    # put one of the volumes into each row and set orientations
    layoutManager = slicer.app.layoutManager()
    sliceNodesByViewName = {}
    for volumeNode in volumeNodes:
      for orientation in orientations:
        viewName = volumeNode.GetName() + '-' + orientation
        sliceWidget = layoutManager.sliceWidget(viewName)
        compositeNode = sliceWidget.mrmlSliceCompositeNode()
        compositeNode.SetBackgroundVolumeID(volumeNode.GetID())
        sliceNode = sliceWidget.mrmlSliceNode()
        sliceNode.SetOrientation(orientation)
        sliceWidget.fitSliceToBackground()
        sliceNodesByViewName[viewName] = sliceNode
    return sliceNodesByViewName

class ViewWatcher(object):
  """A helper class to manage observers on slice views"""

  def __init__(self):
    # the currentLayoutName is tag on the slice node that corresponds
    # view which should currently be shown in the DataProbe window.
    # Keeping track of this allows us to respond to non-interactor updates
    # to the slice (like from an external tracker) but only in the view where
    # the mouse has most recently entered.
    self.currentLayoutName = None

    # Default observer priority is 0.0, and the widgets have a 0.5 priority
    # so we set this to 1 in order to get events that would
    # otherwise be swallowed.  Since we do not abort the event, this is harmless.
    self.priority = 2

    # keep list of pairs: [observee,tag] so they can be removed easily
    self.observerTags = []
    # keep a map of interactor styles to sliceWidgets so we can easily get sliceLogic
    self.sliceWidgetsPerStyle = {}
    self.refreshObservers()

    # saved cursor for restoring custom after overlays
    self.savedCursor = None

    layoutManager = slicer.app.layoutManager()
    layoutManager.connect('layoutChanged(int)', self.refreshObservers)

    # instance variables filled in by processEvent
    self.sliceWidget = None
    self.sliceView = None
    self.sliceLogic = None
    self.sliceNode = None
    self.interactor = None
    self.xy = (0,0)
    self.xyz = (0,0,0)
    self.ras = (0,0,0)
    self.layerLogics = {}
    self.layerVolumeNodes = {}
    self.savedWidget = None

  def __del__(self):
    self.tearDown()

  def removeObservers(self):
    # remove observers and reset
    for observee,tag in self.observerTags:
      observee.RemoveObserver(tag)
    self.observerTags = []
    self.sliceWidgetsPerStyle = {}

  def refreshObservers(self):
    """ When the layout changes, drop the observers from
    all the old widgets and create new observers for the
    newly created widgets"""
    self.removeObservers()
    # get new slice nodes
    layoutManager = slicer.app.layoutManager()
    sliceNodeCount = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
    for nodeIndex in xrange(sliceNodeCount):
      # find the widget for each node in scene
      sliceNode = slicer.mrmlScene.GetNthNodeByClass(nodeIndex, 'vtkMRMLSliceNode')
      sliceWidget = layoutManager.sliceWidget(sliceNode.GetLayoutName())
      if sliceWidget:
        # add obserservers and keep track of tags
        style = sliceWidget.sliceView().interactorStyle().GetInteractor()
        self.sliceWidgetsPerStyle[style] = sliceWidget
        events = ("MouseMoveEvent", "EnterEvent", "LeaveEvent")
        for event in events:
          tag = style.AddObserver(event, self.processEvent, self.priority)
          self.observerTags.append([style,tag])
        tag = sliceNode.AddObserver("ModifiedEvent", self.processEvent, self.priority)
        self.observerTags.append([sliceNode,tag])
        sliceLogic = sliceWidget.sliceLogic()
        compositeNode = sliceLogic.GetSliceCompositeNode()
        tag = compositeNode.AddObserver("ModifiedEvent", self.processEvent, self.priority)
        self.observerTags.append([compositeNode,tag])


  def processEvent(self,observee,event):
    if event == 'LeaveEvent':
      self.currentLayoutName = None
    if event == 'EnterEvent':
      sliceWidget = self.sliceWidgetsPerStyle[observee]
      self.currentLayoutName = None
      sliceLogic = sliceWidget.sliceLogic()
      sliceNode = sliceWidget.mrmlSliceNode()
      self.currentLayoutName = sliceNode.GetLayoutName()
    nodeEvent = (observee.IsA('vtkMRMLSliceNode') or
                observee.IsA('vtkMRMLSliceCompositeNode'))
    if nodeEvent:
      # for a slice node, get the corresponding style and
      # set it as the observee so update is made for that sliceWidget
      # if it is the current layout name
      layoutManager = slicer.app.layoutManager()
      sliceWidget = layoutManager.sliceWidget(observee.GetLayoutName())
      if sliceWidget and observee.GetLayoutName() == self.currentLayoutName:
        observee = sliceWidget.sliceView().interactor()
    if self.sliceWidgetsPerStyle.has_key(observee):
      self.sliceWidget = self.sliceWidgetsPerStyle[observee]
      self.sliceView = self.sliceWidget.sliceView()
      self.sliceLogic = self.sliceWidget.sliceLogic()
      self.sliceNode = self.sliceWidget.mrmlSliceNode()
      self.interactor = observee
      self.xy = self.interactor.GetEventPosition()
      self.xyz = self.sliceWidget.sliceView().convertDeviceToXYZ(self.xy);
      self.ras = self.sliceWidget.sliceView().convertXYZToRAS(self.xyz)

      self.layerLogics = {}
      self.layerVolumeNodes = {}
      layerLogicCalls = (('L', self.sliceLogic.GetLabelLayer),
                         ('F', self.sliceLogic.GetForegroundLayer),
                         ('B', self.sliceLogic.GetBackgroundLayer))
      for layer,logicCall in layerLogicCalls:
        self.layerLogics[layer] = logicCall()
        self.layerVolumeNodes[layer] = self.layerLogics[layer].GetVolumeNode()

      self.onSliceWidgetEvent(event)

  def onSliceWidgetEvent(self,event):
    """ virtual method called when an event occurs
    on a slice widget.  The instance variables of the class
    will have been filled by the processEvent method above
    """
    pass

  def tearDown(self):
    """Virtual method meant to be overridden by the subclass
    Cleans up any observers (or widgets and other instances).
    This is needed because __del__ does not reliably get called.
    """
    layoutManager = slicer.app.layoutManager()
    layoutManager.disconnect('layoutChanged(int)', self.refreshObservers)
    self.removeObservers()

  def cursorOff(self,widget):
    """Turn off and save the current cursor so
    the user can see an overlay that tracks the mouse"""
    self.savedWidget = widget
    self.savedCursor = widget.cursor
    qt_BlankCursor = 10
    widget.setCursor(qt.QCursor(qt_BlankCursor))

  def cursorOn(self):
    """Restore the saved cursor if it exists, otherwise
    just restore the default cursor"""
    if self.savedWidget:
      if self.savedCursor:
        self.savedWidget.setCursor(self.savedCursor)
      else:
        self.savedWidget.unsetCursor()
    self.savedWidget = None

class LayerReveal(ViewWatcher):
  """Track the mouse and show a reveal view"""

  def __init__(self,parent=None,width=400,height=400,showWidget=False,scale=False):
    super(LayerReveal,self).__init__()
    self.width = width
    self.height = height
    self.showWidget = showWidget
    self.scale = scale
    self.renderer = None

    # utility Qt instances for use in methods
    self.gray = qt.QColor()
    self.gray.setRedF(0.5)
    self.gray.setGreenF(0.5)
    self.gray.setBlueF(0.5)
    # a painter to use for various jobs
    self.painter = qt.QPainter()


    # make a qwidget display
    if self.showWidget:
      self.frame = qt.QFrame(parent)
      mw = slicer.util.mainWindow()
      self.frame.setGeometry(mw.x, mw.y, self.width, self.height)
      self.frameLayout = qt.QVBoxLayout(self.frame)
      self.label = qt.QLabel()
      self.frameLayout.addWidget(self.label)
      self.frame.show()

    # make an image actor in the slice view
    self.vtkImage = vtk.vtkImageData()

    self.mrmlUtils = slicer.qMRMLUtils()
    self.imageMapper = vtk.vtkImageMapper()
    self.imageMapper.SetColorLevel(128)
    self.imageMapper.SetColorWindow(255)
    self.imageMapper.SetInput(self.vtkImage)
    self.actor2D = vtk.vtkActor2D()
    self.actor2D.SetMapper(self.imageMapper)

  def tearDown(self):
    # clean up widget
    self.frame = None
    # clean up image actor
    if self.renderer:
      self.renderer.RemoveActor(self.actor2D)
    self.cursorOn()
    if self.sliceView:
      self.sliceView.scheduleRender()
    super(LayerReveal,self).tearDown()

  def onSliceWidgetEvent(self,event):
    """Update reveal displays"""
    revealPixmap = self.revealPixmap(self.xy)

    #widget
    if self.showWidget:
      self.label.setPixmap(revealPixmap)

    # actor
    self.renderWindow = self.sliceView.renderWindow()
    self.renderer = self.renderWindow.GetRenderers().GetItemAsObject(0)

    if event == "LeaveEvent" or not self.layerVolumeNodes['F']:
      self.renderer.RemoveActor(self.actor2D)
      self.cursorOn()
      self.sliceView.forceRender()
    elif event == "EnterEvent":
      self.renderer.AddActor2D(self.actor2D)
      if self.layerVolumeNodes['F'] and (self.layerVolumeNodes['F'] != self.layerVolumeNodes['B']):
        self.cursorOff(self.sliceWidget)
    else:
      self.mrmlUtils.qImageToVtkImageData(revealPixmap.toImage(),self.vtkImage)
      self.imageMapper.SetInput(self.vtkImage)
      x,y = self.xy
      self.actor2D.SetPosition(x-self.width/2,y-self.height/2)
      self.sliceView.forceRender()

  def revealPixmap(self, xy):
    """fill a pixmap with an image that has a reveal pattern
    at xy with the fg drawn over the bg"""

    # Get QImages for the two layers
    bgVTKImage = self.layerLogics['B'].GetImageData()
    fgVTKImage = self.layerLogics['F'].GetImageData()
    bgQImage = qt.QImage()
    fgQImage = qt.QImage()
    slicer.qMRMLUtils().vtkImageDataToQImage(bgVTKImage, bgQImage)
    slicer.qMRMLUtils().vtkImageDataToQImage(fgVTKImage, fgQImage)

    # get the geometry of the focal point (xy) and images
    # noting that vtk has the origin at the bottom left and qt has
    # it at the top left.  yy is the flipped version of y
    imageWidth = bgQImage.width()
    imageHeight = bgQImage.height()
    x,y=xy
    yy = imageHeight-y

    #
    # make a generally transparent image,
    # then fill quadrants with the fg image
    #
    overlayImage = qt.QImage(imageWidth, imageHeight, qt.QImage().Format_ARGB32)
    overlayImage.fill(0)

    halfWidth = imageWidth/2
    halfHeight = imageHeight/2
    topLeft = qt.QRect(0,0, x, yy)
    bottomRight = qt.QRect(x, yy, imageWidth-x-1, imageHeight-yy-1)

    self.painter.begin(overlayImage)
    self.painter.drawImage(topLeft, fgQImage, topLeft)
    self.painter.drawImage(bottomRight, fgQImage, bottomRight)
    self.painter.end()

    # draw the bg and fg on top of gray background
    compositePixmap = qt.QPixmap(self.width,self.height)
    compositePixmap.fill(self.gray)
    self.painter.begin(compositePixmap)
    self.painter.drawImage(
        -1 * (x  -self.width/2),
        -1 * (yy -self.height/2),
        bgQImage)
    self.painter.drawImage(
        -1 * (x  -self.width/2),
        -1 * (yy -self.height/2),
        overlayImage)
    self.painter.end()

    if self.scale:
      compositePixmap = self.scalePixmap(compositePixmap)

    # draw a border around the pixmap
    self.painter.begin(compositePixmap)
    self.pen = qt.QPen()
    self.color = qt.QColor("#FF0")
    self.color.setAlphaF(0.3)
    self.pen.setColor(self.color)
    self.pen.setWidth(5)
    self.pen.setStyle(3) # dotted line (Qt::DotLine)
    self.painter.setPen(self.pen)
    rect = qt.QRect(1, 1, self.width-2, self.height-2)
    self.painter.drawRect(rect)
    self.painter.end()

    return compositePixmap

  def scalePixmap(self,pixmap):
    # extract the center of the pixmap and then zoom
    halfWidth = self.width/2
    halfHeight = self.height/2
    quarterWidth = self.width/4
    quarterHeight = self.height/4
    centerPixmap = qt.QPixmap(halfWidth,halfHeight)
    centerPixmap.fill(self.gray)
    self.painter.begin(centerPixmap)
    fullRect = qt.QRect(0,0,halfWidth,halfHeight)
    centerRect = qt.QRect(quarterWidth, quarterHeight, halfWidth, halfHeight)
    self.painter.drawPixmap(fullRect, pixmap, centerRect)
    self.painter.end()
    scaledPixmap = centerPixmap.scaled(self.width, self.height)

    return scaledPixmap


class CompareVolumesTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
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
    if scenario == "Three Volume":
      self.test_CompareVolumes1()
    elif scenario == "View Watcher":
      self.test_CompareVolumes2()
    elif scenario == "LayerReveal":
      self.test_CompareVolumes3()
    else:
      self.test_CompareVolumes1()
      self.test_CompareVolumes2()

  def test_CompareVolumes1(self):
    """ Test modes with 3 volumes.
    """

    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('CompareVolumes')

    self.delayDisplay("Starting the test")

    # first with two volumes
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    head = sampleDataLogic.downloadMRHead()
    brain = sampleDataLogic.downloadDTIBrain()
    logic = CompareVolumesLogic()
    logic.viewerPerVolume()
    self.delayDisplay('Should be one row with two columns')
    logic.viewerPerVolume(volumeNodes=(brain,head), viewNames=('brain', 'head'))
    self.delayDisplay('Should be two columns, with names')

    # now with three volumes
    otherBrain = sampleDataLogic.downloadMRBrainTumor1()
    logic.viewerPerVolume()
    logic.viewerPerVolume(volumeNodes=(brain,head,otherBrain), viewNames=('brain', 'head','otherBrain'))
    self.delayDisplay('Should be one row with three columns')

    logic.viewerPerVolume(volumeNodes=(brain,head,otherBrain), viewNames=('brain', 'head','otherBrain'), orientation='Sagittal')
    self.delayDisplay('same thing in sagittal')

    logic.viewerPerVolume(volumeNodes=(brain,head,otherBrain), viewNames=('brain', 'head','otherBrain'), orientation='Coronal')
    self.delayDisplay('same thing in coronal')

    anotherHead = sampleDataLogic.downloadMRHead()
    logic.viewerPerVolume(volumeNodes=(brain,head,otherBrain,anotherHead), viewNames=('brain', 'head','otherBrain','anotherHead'), orientation='Coronal')
    self.delayDisplay('now four volumes, with three columns and two rows')


    logic.viewersPerVolume(volumeNodes=(brain,head))
    self.delayDisplay('now axi/sag/cor for two volumes')

    logic.viewersPerVolume(volumeNodes=(brain,head,otherBrain))
    self.delayDisplay('now axi/sag/cor for three volumes')

    self.delayDisplay('Test passed!')

  def test_CompareVolumes2(self):
    """
    Test modes with view watcher class.
    """

    m = slicer.util.mainWindow()
    m.moduleSelector().selectModule('CompareVolumes')

    self.delayDisplay("Starting View Watcher test")

    watcher = ViewWatcher()

    # first with two volumes
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    head = sampleDataLogic.downloadMRHead()
    brain = sampleDataLogic.downloadDTIBrain()
    logic = CompareVolumesLogic()
    logic.viewerPerVolume()
    self.delayDisplay('Should be one row with two columns')
    logic.viewerPerVolume(volumeNodes=(brain,head), viewNames=('brain', 'head'))
    self.delayDisplay('Should be two columns, with names')

    watcher.tearDown()

    self.delayDisplay('Test passed!')

  def test_CompareVolumes3(self):
    """
    Test LayerReveal

    From the python console:
slicer.util.mainWindow().moduleSelector().selectModule("CompareVolumes"); slicer.modules.CompareVolumesWidget.onReloadAndTest(scenario="LayerReveal"); reveal = LayerReveal()
    """

    self.delayDisplay("Starting LayerReveal test")


    # first with two volumes
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    head = sampleDataLogic.downloadMRHead()
    dti = sampleDataLogic.downloadDTIBrain()
    tumor = sampleDataLogic.downloadMRBrainTumor1()
    logic = CompareVolumesLogic()
    logic.viewerPerVolume()
    self.delayDisplay('Should be one row with two columns')
    logic.viewerPerVolume(volumeNodes=(dti,tumor,head),
                            background=dti, viewNames=('dti', 'tumor', 'head'))
    self.delayDisplay('Should be three columns, with dti in foreground')

    # the name of the view was givein the the call to viewerPerVolume above.
    # here we ask the layoutManager to give us the corresponding sliceWidget
    # from which we can get the interactorStyle so we can simulate events
    layoutManager = slicer.app.layoutManager()
    sliceWidget = layoutManager.sliceWidget('head')
    style = sliceWidget.sliceView().interactorStyle().GetInteractor()

    for scale in (False,True):
      for size in (100,400):
        # create a reveal cursor to test
        reveal = LayerReveal(width=size,height=size,scale=scale)
        reveal.processEvent(style, "EnterEvent")
        steps = 300
        for step in range(0,steps):
          t = step/float(steps)
          px = int(t * sliceWidget.width)
          py = int(t * sliceWidget.height)
          style.SetEventPosition(px,py)
          reveal.processEvent(style, "MouseMoveEvent")
        reveal.processEvent(style, "LeaveEvent")
        reveal.tearDown()

    self.delayDisplay('Should have just seen reveal cursor move through head view')

    self.delayDisplay('Test passed!')
