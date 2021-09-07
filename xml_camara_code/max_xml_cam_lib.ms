/*
Los_CamXML
by Carlos Anguiano
XML Camera Format
*/
struct Los_Cam
(
	headerName = "camera_export",
	camHeader = "camera",
	frameHeader = "frame",
	
	fn dicFromXmlAttributes xml =
	(
		masterDic = dotNetObject "System.Collections.Hashtable" 
		for i=1 to xml.attributes.count do
		(
			keyP = xml.attributes.item[i-1].name
			valP = xml.attributes.item[i-1].value
			masterDic.add keyP valP
		)
		masterDic
	),
	fn getKeys hash =
	(
		--spit the posible keys out  
		DNArray = dotNetObject "System.string[]" hash.keys.count  
		hash.keys.copyTo DNArray 0  
		out =for i = 1 to hash.keys.count collect (DNArray.get (i-1))  
		sort out
		out
	),
	fn isKey dic pkey =
	(
		if finditem (getKeys dic) pkey == 0 then return false
		true
	),
	fn setProp dic pkey val =
	(
		--dicRemoveKey dic pKey
		if (isKey dic pkey) then dic.remove pkey
		dic.add pkey Val
		true
	),
	fn timeToInt t =
	(
		if classof t != time then return t
		out = t as integer/ticksPerFrame
		out
	),
	fn convertMax2MayaUnits val =
	(
		out = case val of
		(
			#inches:"inch"
			#feet:"foot"
			#miles:"mile"
			#millimeters: "millimeter"
			#centimeters:"centimeter"
			#meters: "meter"
			#kilometers: "" -- no maya equivalent
		)
		out
	),
	fn convertMaya2maxUnits val =
	(
		out = case val of
		(
			"inch":#inches
			"foot":#feet
			"mile":#miles
			"millimeter":#millimeters 
			"centimeter":#centimeters
			"meter":#meters
			 -- no maya equivalent
		)
		out
	),
	fn fnConverttoMaya4x4 mat3Row iW = 
	(
		([mat3Row.x, mat3Row.z, mat3Row.y*-1, iW ] as Point4)
	),
	fn matrixAsString mat3Matrix =
	(
		pt4MayaRow1 = fnConverttoMaya4x4 mat3Matrix.row1 0
		pt4MayaRow2 = fnConverttoMaya4x4 mat3Matrix.row2 0
		pt4MayaRow3 = fnConverttoMaya4x4 mat3Matrix.row3 0
		pt4MayaRow4 = fnConverttoMaya4x4 mat3Matrix.row4 1
		arrMayaMatrix = #(pt4MayaRow1, pt4MayaRow2, pt4MayaRow3, pt4MayaRow4)
		arrStrMatrix = #()
		for i = 1 to 4 do
		(
			for j = 1 to 4 do 
			(
				append arrStrMatrix (formattedPrint arrMayaMatrix[i][j] format: "0.12g")
			)
		)
		sStream = stringStream ""
		format "%" arrStrMatrix to:sStream
		sMatrix = sStream as String
		sMatrix = substituteString sMatrix "\"" ""
		sMatrix = substituteString sMatrix "#(" ""
		sMatrix = substituteString sMatrix ")" ""
		sMatrix = substituteString sMatrix "," ""
		close sStream
		flush  sStream
		return sMatrix
	),
	fn stringMatrixToMaxMatrix sMatrix = 
	( 
		camMatrix = (matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0])
		arrStrMatrix = filterString sMatrix " "
		for strIdx = 0 to (arrStrMatrix.Count/4) - 1  do 
		(
			idx = strIdx * 4
			camMatrix[strIdx+1] = [arrStrMatrix[idx + 1] as float, ((arrStrMatrix[idx + 3] as float) * -1), arrStrMatrix[idx + 2] as float ] as Point3
		)
		return camMatrix
	),
	fn getCamAttr cam attr =
	(
		if isproperty cam attr then return getproperty cam attr
		0
	),
	fn genFrameCamDic cam pFrame =
	(
		extraAttrs = #(#panx,#pany,#distortion)
		
		hash = dotNetObject "System.Collections.Hashtable"  
		at time pFrame 
		(
			wrldTrans = matrixAsString ( cam.transform)
			aperturex =(getRendApertureWidth())/25.4
			fov = cam.fov
			lens = aperturex/(2*tan(fov/2))
			aperturey = aperturex/(renderWidth as float/renderHeight as float)
			
			hash.add "frame" (timeToInt pFrame)
			hash.add "matrix" wrldTrans
			hash.add "lens"  lens
			hash.add "fov" fov 
			hash.add "aperturex" aperturex
			hash.add "aperturey" aperturey
			for x in extraAttrs do hash.add (tolower (x as string)) (getCamAttr cam x)
		)
		hash
	),
	fn genCamDic cam startF endF =
	(
		camDic = dotNetObject "System.Collections.Hashtable" 
		camDic.add "name" cam.name
		camDic.add "type" ""
		camDic.add "position" ""
		camDic.add "centrecam" ""
		camDic.add "parent" ""
		frameDicAr = #()
		
		for t=startF to endF do
		(
			at time t
			(
				append frameDicAr (genFrameCamDic cam t)
			)
		)
		camDic.add frameHeader frameDicAr
		
		camDic
	),
	fn genHeaderDic startframe endframe =
	(
		hash = dotNetObject "System.Collections.Hashtable"  
		hash.add "software" "max"
		hash.add "version" (maxVersion())[1]
		hash.add "exportdate"  localtime
		hash.add "unitLinear" (convertMax2MayaUnits units.systemtype)
		hash.add "frame_rate"  framerate
		hash.add "sourcefilename"  (maxFilePath+maxFileName)
		hash.add "exportfilename" maxFilePath
		hash.add "firstframe" (timeToInt startframe)
		hash.add "lastframe" (timeToInt endframe)
		hash.add "reswidth" renderWidth
		hash.add "resheight" renderHeight
		hash.add "pixelaspectratio"  renderPixelAspect 
		hash
	),
	fn recursiveDicToXMLFile  xmlSec dicSec xmlDom =
	(
		for k in (getKeys dicSec) do
		(
			val =  dicSec.item[k]
			if classof val == array then
			(
				for a in val do 
				(
					element = xmlDom.CreateElement k
					xmlSec.AppendChild element
					recursiveDicToXMLFile element a xmlDom
				)
				continue
			)
			if classof val != string then val = val as string
			xmlSec.SetAttribute k val
		)
	),	
	fn dicToXml dic xmlFile =
	(
		DotNet.LoadAssembly "System.Xml"
		xmlDoc = dotNetObject "System.Xml.XmlDocument"
		body=xmlDoc.CreateElement headerName
		xmlDoc.AppendChild body
		
		recursiveDicToXMLFile body dic xmlDoc

		
		--wrap the shit up..
		writer = dotNetClass "System.Xml.XmlTextWriter"
		wSettings = dotNetObject "System.Xml.XmlWriterSettings"
		wSettings.indent = True
		wSettings.NewLineOnAttributes = True

		w = writer.create xmlFile wSettings
		try
		(
			xmlDoc.writeContentTo w
		)
		catch
		(
			("IO Error on file " + xmlFile + ".")
			w.close()
			return False
		)
		m_statusMsg = ("PXMcam file " + xmlFile + " created successfully.")
		w.close()
		true
	),
	fn xmlHeaderToDic xmlsec parDic  =
	(
		dic = dotNetObject "System.Collections.Hashtable" 
		--for i=1 to xmlSec.Attributes.count do dic.add xmlSec.attributes.item[i-1].name xmlSec.attributes.item[i-1].value
		
		dicAr = case (iskey parDic xmlsec.name) of
		(
			(true):for o in parDic.item[xmlsec.name] collect o
			default:#()
		)
		
		for i=1 to xmlsec.childNodes.count do
		(
			el  =xmlsec.ChildNodes.item[i-1]
			if (el as string) != "dotNetObject:System.Xml.XmlElement" then continue
			
			xmlHeaderToDic el dic 
		)
		append dicAr dic
		print ("this is dic ar for section "+xmlsec.name)
		print dicAr
		setProp parDic xmlsec.name dicAr
		dic
	),
	fn xmlToDic xml  =
	(
		masterDic = dotNetObject "System.Collections.Hashtable" 
		xmlHeaderToDic xml.item[headerName] masterDic 
		masterDic
	),
	fn getCamXHorizontalApertureFromXML xml =
	(
		cams = this.getCamElementsFromXML xml
		elmList = cams[1].GetElementsByTagName frameHeader
		props = dicFromXmlAttributes  elmList.item[0]
		out = ((props.item["aperturex"] as float) * 25.4)
		out
	
	),
	fn applySceneSettingsFromXML xml =
	(
		renderSceneDialog.close()
		print "applying camera max render settings.."
		props = dicFromXmlAttributes xml.item["camera_export"]
		framerate =  props.item["frame_rate"] as integer
		startF  = (props.item["firstframe"]+"f") as time
		endF = (props.item["lastframe"]+"f") as time
		animationRange = interval startF endF
		--removing this part is it could be potential destructive...
		/*
		if props.item["unitLinear"] != "" then 
			units.systemtype = convertMaya2maxUnits props.item["unitLinear"]
		*/

		setRendApertureWidth (getCamXHorizontalApertureFromXML xml)
		
		renderWidth = props.item["reswidth"] as integer
		renderHeight = props.item["resheight"] as integer
	),
	fn findAttrByName nd attrName =
	(
		out = undefined
		if custAttributes.count nd == 0 then return out
		for i=1 to custAttributes.count nd do
		(
			ca = custAttributes.get nd i
			if ca.name == attrName then return out
		)
		out
	),
	fn genCamAttrOtherData cam =
	(
		attrName = "camOtherData"
		if (findAttrByName cam  attrName) != undefined then return false
		camOtherCA = attributes attrName
		(
			parameters main rollout:params
			(
				aperturex  type: #float ui:aperturexUi default:0.0
				aperturey type: #float ui:apertureyUi default:0.0
				panx type: #float ui: panxUi default:0.0
				pany type: #float ui: panyUi default:0.0
				distortion type:#float ui:distortionUi default:0.0
				qdistortion type:#float ui:qdistortionUi default:0.0
			)
			rollout params "Other Parameters"
			(
				spinner aperturexUi  "aperturex" type:#float Range:[-100000.0,100000.0,0]
				spinner apertureyUi  "aperturey" type:#float Range:[-100000.0,100000.0,0]
				spinner panxUi  "panx" type:#float Range:[-100000.0,100000.0,0]
				spinner panyUi  "pany" type:#float Range:[-100000.0,100000.0,0]
				spinner distortionUi  "distortion" type:#float Range:[-100000.0,100000.0,0]
				spinner qdistortionUi  "qdistortion" type:#float Range:[-100000.0,100000.0,0]
			)
		)
		custAttributes.add cam camOtherCA
		true
	),
	fn camSetupAnimControllers cam =
	(
		deleteKeys  cam #allkeys
		
		cam.position.controller = position_xyz()
		
		for i = 1 to 3 do
		(
			lF =  linear_float()
			cam.position.controller[i].controller = lF
			setBeforeORT lF #linear
			setAfterORT lF #linear

		)
		
		cam.rotation.controller = bezier_rotation()
		return true
	),
	fn getCamFrameElementsFromXML xml =
	(
		elmList = xml.GetElementsByTagName frameHeader
		if elmList.count == 0 then return #()
		out = for i=1 to elmList.count collect elmList.item[i-1]
		out
	),
	fn createCameraFromXML xml cam:undefined useVrayCam:False =
	(
		camProps = dicFromXmlAttributes xml
		camName = camProps.item["name"]
		camMath = python.import "mango.UTILs.camMath"
		physicalClass = VRayPhysicalCamera
		if findItem camera.classes Physical != 0 then physicalClass = Physical
		--in case a phisical camera can not be found...
		if useVrayCam then if findItem camera.classes physicalClass == 0 then useVrayCam = False
		if cam == undefined then 
		(
			try(delete (getNodeByName camName))catch()
			cam = case useVrayCam of
			(
				(True):physicalClass()
				default:freeCamera()
			)
		)
		camSetupAnimControllers cam
		genCamAttrOtherData cam
		
		if classof cam == physicalClass then cam.specify_fov = true 

		firstFrame = undefined
		for f in (getCamFrameElementsFromXML xml) do
		(
			--generate all the varialbes we need to set at this frames
			fProps =  dicFromXmlAttributes f
			kTime = fProps.item["frame"] as integer
			
			if firstFrame == undefined then firstFrame = kTime
				
			kTrans = stringMatrixToMaxMatrix fProps.item["matrix"]
			kFov = fProps.item["fov"] as float
			
			kApX = (fProps.item["aperturex"] as float) * 25.4
			kApY = (fProps.item["aperturey"] as float) * 25.4
			
			kPanX = fProps.item["panx"] as float
			kPanY = fProps.item["pany"] as float
			
			kDist = fProps.item["distortion"] as float
			kLens = fProps.item["lens"] as float

			--let's make some motha fucking key frames baby!!!!!!
			
			at time kTime
			(
				animate on
				(
					cam.transform = kTrans
					
					
					cam.aperturex = kApX
					cam.aperturey = kApY
					
					cam.panx = kPanX
					cam.pany = kPanY
					cam.distortion = kDist
					if classof cam == VRayPhysicalCamera then
					(
						cam.film_width = kApX
						--cam.focal_length = camMath.focalLengthFromFilmWithAndFov kApX kfov --kApX/(2.*(tan (kfov/2.0)))
						--continue
					)
					cam.fov = kfov
				)
			)
			
		)
		--if the camera animation starts after frame zero let's make sure to delte the zero key....
		if firstFrame > 0 then
		(
			camCons = #(cam.transform.controller,
								cam.fov.controller,
								cam.aperturex.controller,
								cam.aperturey.controller,
								cam.panx.controller,
								cam.pany.controller,
								cam.distortion.controller)
			if classof cam == VRayPhysicalCamera then append camCons cam.film_width.controller
				
			for con in camCons do
			(
				selectKeys con (interval 0f 0f)
				deleteKeys con #selection
			)
			--selectKeys cam.fov.controller (interval 0f 0f)
		)
		cam
	),
	fn getCamElementsFromXML xml =
	(
		elmList = xml.item[headerName].GetElementsByTagName camHeader
		if elmList.count == 0 then return #()
		out = for i=1 to elmList.count collect elmList.item[i-1]
		out
	),
	fn genCamerasFromXML xml applySceneSettings:true useVrayCam:false =
	(
		camAr = getCamElementsFromXML xml
		if camAr.count == 0 then throw "ERROR Los_CameraXML:There is no camera info in the suplied XML"
		if applySceneSettings then applySceneSettingsFromXML xml
		out = #()
		for c in camAr do 
		(
			camProps = c.Attributes.GetNamedItem
			format "Importing CAM %\n" camProps["name"].value
			cam = createCameraFromXML c useVrayCam:useVrayCam
			cam.name = camProps["name"].value
			append out cam
		)
		gc light:true
		out
	),
	fn ExportCamera camList outPath startF:animationRange.start endF:animationRange.end =
	(
		xml = genHeaderDic startF endF
		camDicAr = for c in camList collect genCamDic c startF endF
		xml.add camHeader camDicAr
		dicToXml xml outPath
	),
	fn  importCamera xmlFile useVrayCam:false =
	(
		dotnet.LoadAssembly "system.xml.dll"
		xmlDoc = dotNetObject "System.Xml.XmlDocument"
		doc = xmlDoc.Load xmlFile
		xmldoc
		cams = genCamerasFromXML xmldoc useVrayCam:useVrayCam
		cams
	)
)
global camLib = Los_cam()
