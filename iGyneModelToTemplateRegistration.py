from __main__ import vtk, qt, ctk, slicer
import numpy
#
# Endoscopy
#

class iGyneModelToTemplateRegistration:
  def __init__(self, parent):
    import string
    parent.title = "Model To Template Registration"
    parent.categories = ["Gyne IGT"]
    parent.contributors = ["Alireza Mehrtash","Guillaume Pernelle","Xiaojun Chen", "Yi Gao", "Tina Kapur", "Jan Egger", "Carolina Vale"]
    parent.helpText = string.Template("""
    Create a path model as a spline interpolation of a set of fiducial points. See <a href=\"$a/Documentation/$b.$c/Modules/Endoscopy\">$a/Documentation/$b.$c/Modules/Endoscopy</a> for more information.\n\nPick the Camera to be modified by the path and the Fiducial List defining the control points.  Clicking Apply will bring up the flythrough panel.\n\nYou can manually scroll though the path with the Frame slider.\n\nThe Play/Pause button toggles animated flythrough.\n\nThe Frame Skip slider speeds up the animation by skipping points on the path.\n\nThe Frame Delay slider slows down the animation by adding more time between frames.\n\nThe View Angle provides is used to approximate the optics of an endoscopy system.\n\nThe Close button dismisses the flyrhough panel and stops the animation.
    """).substitute({ 'a':parent.slicerWikiUrl, 'b':slicer.app.majorVersion, 'c':slicer.app.minorVersion })
    parent.acknowledgementText = """
    This work is supported by PAR-07-249: R01CA131718 NA-MIC Virtual Colonoscopy (See <a>http://www.na-mic.org/Wiki/index.php/NA-MIC_NCBC_Collaboration:NA-MIC_virtual_colonoscopy</a>) NA-MIC, NAC, BIRN, NCIGT, and the Slicer Community. See http://www.slicer.org for details.  Module implemented by Steve Pieper.
    """
    self.parent = parent

#
# qSlicerPythonModuleWidget
#

class iGyneModelToTemplateRegistrationWidget:
  def __init__(self, parent=None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.cameraNodeSelector.setMRMLScene(slicer.mrmlScene)
      self.inputFiducialsNodeSelector.setMRMLScene(slicer.mrmlScene)
      self.parent.show()
    self.iterationNo = 0
    self.numberOfFiducialPoints = 6
    self.RMS = 0
    self.templateFiducialList = numpy.zeros((self.numberOfFiducialPoints,3)) 
  def setup(self):
    pointCollectionCollapsibleButton = ctk.ctkCollapsibleButton()
    pointCollectionCollapsibleButton.text = "Point Collection"
    self.layout.addWidget(pointCollectionCollapsibleButton)
    
    # Layout within the point collection collapsible button
    pointCollectionFormLayout = qt.QFormLayout(pointCollectionCollapsibleButton)
 
    # Template node selector
    templateLabel = qt.QLabel( 'Template:' )
    self.templateSelector = slicer.qMRMLNodeComboBox()
    self.templateSelector.toolTip = "Choose the template model"
    self.templateSelector.nodeTypes = ['vtkMRMLModelNode']
    self.templateSelector.setMRMLScene(slicer.mrmlScene)
    self.templateSelector.addEnabled = False
    self.templateSelector.noneEnabled= True
    self.templateSelector.removeEnabled= False
    self.templateSelector.connect('currentNodeChanged(bool)', self.enableOrDisablePointCollectionButton)
    pointCollectionFormLayout.addRow( templateLabel, self.templateSelector)

    # Stylus tracker transform node selector
    stylusTrackerLabel = qt.QLabel( 'Stylus:' )
    self.stylusTrackerSelector = slicer.qMRMLNodeComboBox()
    self.stylusTrackerSelector.toolTip = "Choose the followup scan"
    self.stylusTrackerSelector.nodeTypes = ['vtkMRMLTransformNode']
    self.stylusTrackerSelector.setMRMLScene(slicer.mrmlScene)
    self.stylusTrackerSelector.addEnabled = False
    self.stylusTrackerSelector.noneEnabled= True
    self.stylusTrackerSelector.removeEnabled= False
    self.stylusTrackerSelector.connect('currentNodeChanged(bool)', self.enableOrDisablePointCollectionButton)
    pointCollectionFormLayout.addRow( stylusTrackerLabel, self.stylusTrackerSelector )

    # Point Collection button
    pointCollectionButton = qt.QPushButton("Collect Points")
    pointCollectionButton.toolTip = "Collect fiducial points using stylus."
    pointCollectionButton.enabled = False
    pointCollectionFormLayout.addRow(pointCollectionButton)
    pointCollectionButton.connect('clicked()', self.onPointCollectionButtonClicked)

    # Set local var as instance attribute
    self.pointCollectionButton = pointCollectionButton 
    
    # Point Reset button
    self.pointResetButton = qt.QPushButton("Reset")
    self.pointResetButton.toolTip = "Erase all the collected points."
    self.pointResetButton.enabled = False
    pointCollectionFormLayout.addRow(self.pointResetButton)
    self.pointResetButton.connect('clicked()', self.onPointResetButtonClicked)

    #Radio Button 01
    self.pointCollectedButton01= qt.QRadioButton("1: Ec O")
    self.pointCollectedButton01.setAutoExclusive(False)
    self.pointCollectedButton01.setDisabled(True)
    self.pointCollectedButton01.setObjectName("pointCollectedButton01")
    pointCollectionFormLayout.addRow(self.pointCollectedButton01)

    #Radio Button 02
    self.pointCollectedButton02= qt.QRadioButton("2: Ef I")
    self.pointCollectedButton02.setAutoExclusive(False)
    self.pointCollectedButton02.setDisabled(True)
    self.pointCollectedButton02.setObjectName("pointCollectedButton02")
    pointCollectionFormLayout.addRow(self.pointCollectedButton02)

    #Radio Button 03
    self.pointCollectedButton03= qt.QRadioButton("3: Ce I")
    self.pointCollectedButton03.setAutoExclusive(False)
    self.pointCollectedButton03.setDisabled(True)
    self.pointCollectedButton03.setObjectName("pointCollectedButton03")
    pointCollectionFormLayout.addRow(self.pointCollectedButton03)
    
    #Radio Button 04
    self.pointCollectedButton04= qt.QRadioButton("4: Cn O")
    self.pointCollectedButton04.setAutoExclusive(False)
    self.pointCollectedButton04.setDisabled(True)
    self.pointCollectedButton04.setObjectName("pointCollectedButton04")
    pointCollectionFormLayout.addRow(self.pointCollectedButton04)

    #Radio Button 05
    self.pointCollectedButton05= qt.QRadioButton("5: Eb O")
    self.pointCollectedButton05.setAutoExclusive(False)
    self.pointCollectedButton05.setDisabled(True)
    self.pointCollectedButton05.setObjectName("pointCollectedButton05")
    pointCollectionFormLayout.addRow(self.pointCollectedButton05)

    #Radio Button 06
    self.pointCollectedButton06= qt.QRadioButton("6: Eb I")
    self.pointCollectedButton06.setAutoExclusive(False)
    self.pointCollectedButton06.setDisabled(True)
    self.pointCollectedButton06.setObjectName("pointCollectedButton06")
    pointCollectionFormLayout.addRow(self.pointCollectedButton06)


    # Registration collapsible button
    self.registrationCollapsibleButton = ctk.ctkCollapsibleButton()
    self.registrationCollapsibleButton.text = "Registration"
    self.registrationCollapsibleButton.enabled = False
    self.layout.addWidget(self.registrationCollapsibleButton)
    # Layout within the Registration collapsible button
    registrationFormLayout = qt.QFormLayout(self.registrationCollapsibleButton)

    # Model fiducial list heirarachy selector node
    modelFiducialsLabel= qt.QLabel( 'Model Fiducial List:' )
    self.modelFiducialSelector= slicer.qMRMLNodeComboBox()
    self.modelFiducialSelector.toolTip = "Choose the baseline scan"
    self.modelFiducialSelector.nodeTypes = ['vtkMRMLAnnotationHierarchyNode']
    self.modelFiducialSelector.setMRMLScene(slicer.mrmlScene)
    self.modelFiducialSelector.addEnabled = False
    self.modelFiducialSelector.noneEnabled= True
    self.modelFiducialSelector.removeEnabled= False
    self.modelFiducialSelector.connect('currentNodeChanged(bool)', self.enableOrDisableRegistrationButton)
    registrationFormLayout.addRow( modelFiducialsLabel, self.modelFiducialSelector) 

    # Registration button
    registrationButton = qt.QPushButton("Register")
    registrationButton.toolTip = "Performs a Landmark Registration."
    registrationButton.enabled = False
    registrationFormLayout.addRow(registrationButton)
    registrationButton.connect('clicked()', self.onRegistrationButtonClicked)
    # Set local var as instance attribute
    self.registrationButton= registrationButton



    # Reference Attachment collapsible button
    self.referenceAttachmentCollapsibleButton = ctk.ctkCollapsibleButton()
    self.referenceAttachmentCollapsibleButton.text = "Reference Attachment"
    self.referenceAttachmentCollapsibleButton.enabled = False
    self.layout.addWidget(self.referenceAttachmentCollapsibleButton)
    
 
    # Layout within the reference sensor attachment collapsible button
    referenceAttachmentFormLayout = qt.QFormLayout(self.referenceAttachmentCollapsibleButton)

    referenceTrackerLabel= qt.QLabel( 'Reference:' )
    self.referenceTrackerSelector = slicer.qMRMLNodeComboBox()
    self.referenceTrackerSelector.toolTip = "Choose the baseline scan"
    self.referenceTrackerSelector.nodeTypes = ['vtkMRMLTransformNode']
    self.referenceTrackerSelector.setMRMLScene(slicer.mrmlScene)
    self.referenceTrackerSelector.addEnabled = False
    self.referenceTrackerSelector.noneEnabled= True
    self.referenceTrackerSelector.removeEnabled= False
    self.referenceTrackerSelector.connect('currentNodeChanged(bool)', self.enableOrDisableAttachButton)
    referenceAttachmentFormLayout.addRow( referenceTrackerLabel, self.referenceTrackerSelector)

    childNodeLabel= qt.QLabel( 'Nodes to be registered:' )
    self.childNodeSelector= slicer.qMRMLNodeComboBox()
    self.childNodeSelector.toolTip = "Choose the baseline scan"
    self.childNodeSelector.nodeTypes = ['vtkMRMLLinearTransformNode']
    self.childNodeSelector.setMRMLScene(slicer.mrmlScene)
    self.childNodeSelector.addEnabled = False
    self.childNodeSelector.noneEnabled= True
    self.childNodeSelector.removeEnabled= False
    self.childNodeSelector.connect('currentNodeChanged(bool)', self.enableOrDisableAttachButton)
    referenceAttachmentFormLayout.addRow( childNodeLabel, self.childNodeSelector) 

    # Attach button
    attachButton = qt.QPushButton("Attach")
    attachButton.toolTip = "Register model and image to the reference sensor."
    attachButton.enabled = False
    referenceAttachmentFormLayout.addRow(attachButton)
    attachButton.connect('clicked()', self.onAttachButtonClicked)
    # Set local var as instance attribute
    self.attachButton= attachButton 



    self.scene = slicer.mrmlScene
    self.logic = slicer.modules.annotations.logic()
    #self.logic.AddHierarchy
    # a=self.logic.GetActiveHierarchyNode()
    # a.SetName('Template Fiducials')
    
  def enableOrDisablePointCollectionButton(self):
    """Connected to both the fiducial and camera node selector. It allows to 
    enable or disable the 'create path' button."""
    self.pointCollectionButton.enabled = self.stylusTrackerSelector.currentNode() != None and self.templateSelector.currentNode() != None 

  def enableOrDisableRegistrationButton(self):
    """Connected to both the fiducial and camera node selector. It allows to 
    enable or disable the 'create path' button."""
    self.registrationButton.enabled = self.modelFiducialSelector.currentNode() != None 

  def enableOrDisableAttachButton(self):
    """Connected to both the fiducial and camera node selector. It allows to 
    enable or disable the 'create path' button."""
    self.attachButton.enabled = self.referenceTrackerSelector.currentNode() != None and self.childNodeSelector.currentNode() != None



  def onPointCollectionButtonClicked(self):
    """Connected to 'create path' button. It allows to:
      - compute the path
      - create the associated model"""
    listExitence = False
    hierarchyNodes = slicer.util.getNodes('vtkMRMLAnnotationHierarchyNode*')
    for hierarchyNode in hierarchyNodes.keys():
      if hierarchyNode=='Template Fiducials':
        listExitence = True
    if listExitence == False:
      templateFiducialAnnotationList = slicer.vtkMRMLAnnotationHierarchyNode()
      templateFiducialAnnotationList.SetName('Template Fiducials')
      templateFiducialAnnotationList.SetHideFromEditors(0)
      templateFiducialAnnotationList.SetScene(self.scene)
      self.scene.AddNode(templateFiducialAnnotationList)
      self.templateFiducialAnnotationList = templateFiducialAnnotationList

    self.logic.SetActiveHierarchyNodeID(self.templateFiducialAnnotationList.GetID())

    if self.iterationNo < self.numberOfFiducialPoints:
      self.templateFiducialList[self.iterationNo] = self.collect()
      if self.iterationNo == self.numberOfFiducialPoints-1:
        print "Point collection Finished Succesfullly, the Fiducial Coordinates are:"
        print self.templateFiducialList
        self.registrationCollapsibleButton.enabled = True
        self.pointCollectionButton.enabled = False 
        self.pointResetButton.enabled = True
    self.iterationNo += 1


  def onPointResetButtonClicked(self):
    """Connected to 'create path' button. It allows to:"""
    self.iterationNo = 0
    self.pointCollectionButton.enabled = True
    self.pointResetButton.enabled = False
    self.templateFiducialList = numpy.zeros((self.numberOfFiducialPoints,3))    
    self.pointCollectedButton01.setChecked(0)
    self.pointCollectedButton02.setChecked(0)
    self.pointCollectedButton03.setChecked(0)
    self.pointCollectedButton04.setChecked(0)
    self.pointCollectedButton05.setChecked(0)
    self.pointCollectedButton06.setChecked(0)
    self.fiducialAnnotationListNode = slicer.util.getNode('Template Fiducials')
    self.fiducialAnnotationListNode.RemoveAllChildrenNodes()
    #self.scene.RemoveNode(self.templateFiducialAnnotationList)
    
  def collect(self):
    fiducialsNode = self.readStylusTipPosition()
    #print "Getting the point..." 
    fiducial = slicer.vtkMRMLAnnotationFiducialNode()
    fiducialName = "T" + str(self.iterationNo)
    fiducial.SetName(fiducialName)
    fiducial.SetFiducialCoordinates(fiducialsNode)
    fiducial.Initialize(slicer.mrmlScene)
    #fiducial.SetHideFromEditors()
    return fiducialsNode

  def readStylusTipPosition(self):
    tempFiducialsNode = self.stylusTrackerSelector.currentNode()
    xCoordinate = tempFiducialsNode.GetMatrixTransformToParent().GetElement(0,3)
    yCoordinate = tempFiducialsNode.GetMatrixTransformToParent().GetElement(1,3)
    zCoordinate = tempFiducialsNode.GetMatrixTransformToParent().GetElement(2,3)
    self.Coordinate = ([xCoordinate, yCoordinate, zCoordinate])
    transformPositions = self.Coordinate
    self.fiducial = slicer.vtkMRMLAnnotationFiducialNode()
    
      
    if (self.iterationNo==0):  
      self.pointCollectedButton01.setChecked(1)
    elif (self.iterationNo==1):  
      self.pointCollectedButton02.setChecked(1)
    elif (self.iterationNo==2):  
      self.pointCollectedButton03.setChecked(1)
    elif (self.iterationNo==3):  
      self.pointCollectedButton04.setChecked(1)
    elif (self.iterationNo==4):  
      self.pointCollectedButton05.setChecked(1)
    elif (self.iterationNo==5):  
      self.pointCollectedButton06.setChecked(1)

    #print transformPositions
    
    return self.Coordinate

  def onRegistrationButtonClicked(self):
    print "Hello Registration :) "
    self.referenceAttachmentCollapsibleButton.enabled = True
    
    linearTransformExistence = False
    linearTransformNodes = slicer.util.getNodes('vtkMRMLlinearTransformNode*')
    for linearTransformNode in linearTransformNodes.keys():
      if linearTransformNode=='ModelToTemplateTransform':
        linearTransformExistence = True
    if linearTransformExistence == False:
      followupTransform = slicer.vtkMRMLLinearTransformNode()
      followupTransform.SetName('ModelToTemplateTransform')
      followupTransform.SetScene(slicer.mrmlScene)
      slicer.mrmlScene.AddNode(followupTransform)
      self.followupTransform = followupTransform

    self.fiducialListNode = slicer.util.getNode('Template Fiducials')
    movingLandmarksListID = self.fiducialListNode.GetID()
    
    

    modelFiducials = self.modelFiducialSelector.currentNode()
    
    
    
    # extracting the effects of transform parameters
    transformNode1 = self.templateSelector.currentNode().GetParentTransformNode()
    #print transformNode1
    shiftTransform1 = [0 , 0, 0]
    rotationTransform1 = [[1, 0,0],[0,1,0],[0,0,1]]
    #shiftTransform2 = [0, 0, 0]
    #rotationTransform2 = [1, 0,0],[0,1,0],[0,0,1]]
    if transformNode1 != None:
      m = vtk.vtkMatrix4x4()
      transformNode1.GetMatrixTransformToWorld(m)
      shiftTransform1 = [ m.GetElement(0,3), m.GetElement(1,3), m.GetElement(2,3) ]
      rotationTransform1 = [[m.GetElement(0,0), m.GetElement(0,1),m.GetElement(0,2)],[m.GetElement(1,0), m.GetElement(1,1),m.GetElement(1,2)],[m.GetElement(2,0), m.GetElement(2,1),m.GetElement(2,2)]]
      #transformNode2 = transformNode1.GetParentTransformNode()
      #if transformNode2 != None:
        #transformNode2.GetMatrixTransformToWorld(m)
        #shiftTransform2 = [ m.GetElement(0,3), m.GetElement(1,3), m.GetElement(2,3) ]
        #rotationTransform2 = [[m.GetElement(0,0), m.GetElement(0,1),m.GetElement(0,2)],[m.GetElement(1,0), m.GetElement(1,1),m.GetElement(1,2)],[m.GetElement(2,0), m.GetElement(2,1),m.GetElement(2,2)]
    #shiftTransform = numpy.add(shiftTransform1,shiftTransform2)

    
    
    # Changing the fiducial coordinates according to the transform
    
    if modelFiducials.GetClassName() == "vtkMRMLAnnotationHierarchyNode":
    # slicer4 style hierarchy nodes
      collection = vtk.vtkCollection()
      modelFiducials.GetChildrenDisplayableNodes(collection)
      n = collection.GetNumberOfItems()
    
    
    if n != 6: 
        return
      # output an error and ask user to select a fiducial with 6 points
    listExitence = False
    hierarchyNodes = slicer.util.getNodes('vtkMRMLAnnotationHierarchyNode*')
    for hierarchyNode in hierarchyNodes.keys():
      if hierarchyNode=='New Model Fiducials':
        listExitence = True
        self.newModelFiducialAnnotationList.RemoveAllChildrenNodes()
    if listExitence == False:
      newModelFiducialAnnotationList = slicer.vtkMRMLAnnotationHierarchyNode()
      newModelFiducialAnnotationList.SetName('New Model Fiducials')
      # hide the fiducial list from the scene
      newModelFiducialAnnotationList.SetHideFromEditors(1)
      newModelFiducialAnnotationList.SetScene(self.scene)
      self.scene.AddNode(newModelFiducialAnnotationList)
      self.newModelFiducialAnnotationList = newModelFiducialAnnotationList

    self.logic.SetActiveHierarchyNodeID(self.newModelFiducialAnnotationList.GetID())



    #self.logic.AddHierarchy
    #a=self.logic.GetActiveHierarchyNode()
    #a.SetName('New Model Fiducials')
    
    p = numpy.zeros((n,3))
    for i in xrange(n):
      f = collection.GetItemAsObject(i)
      coords = [0,0,0]
      # Need to change to consider the transform that is applied to the points
      f.GetFiducialCoordinates(coords)
      newCoords = numpy.add(numpy.dot(rotationTransform1,coords),shiftTransform1)
      newfid = slicer.vtkMRMLAnnotationFiducialNode()
      newfid.SetFiducialCoordinates(newCoords)
      newfid.SetHideFromEditors(0)
      newfid.SetName(str(i))
      self.scene.AddNode(newfid)

    fixedLandmarksListID = self.newModelFiducialAnnotationList.GetID() 

    self.OutputMessage = ""
    parameters = {}
    parameters["fixedLandmarks"] = fixedLandmarksListID 
    parameters["movingLandmarks"] = movingLandmarksListID
   
    parameters["saveTransform"] = self.followupTransform
    parameters["transformType"] = "Rigid"
    parameters["rms"] = self.RMS
    parameters["outputMessage"] = self.OutputMessage
    
    fidreg = slicer.modules.fiducialregistration
    self.__cliNode = None
    self.__cliNode = slicer.cli.run(fidreg, self.__cliNode, parameters)
    print "RMS is", self.RMS
    #self.__cliObserverTag = self.__cliNode.AddObserver('ModifiedEvent', self.processRegistrationCompletion)
    #self.__registrationStatus.setText('Wait ...')
    #self.firstRegButton.setEnabled(0)

    stylusNode = self.stylusTrackerSelector.currentNode() 
    stylusNode.SetAndObserveTransformNodeID(self.followupTransform.GetID())



  def onAttachButtonClicked(self):
    print "Hello Attachment :) "
    childNode = self.childNodeSelector.currentNode()
    # move the model and the image
    childNode.SetAndObserveTransformNodeID(self.referenceTrackerSelector.currentNode().GetID())
    # move the Stylus
    #stylusNode = self.stylusTrackerSelector.currentNode()
    self.followupTransform.SetAndObserveTransformNodeID(self.referenceTrackerSelector.currentNode().GetID())
