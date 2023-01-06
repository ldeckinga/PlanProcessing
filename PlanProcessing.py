import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import Rhino

def addOutlines(layerName, roomOutlines):
    thisLayer = rs.ObjectsByLayer(layerName, select=False)
    for thisOutline in thisLayer:
        if rs.ObjectType(thisOutline) == 4:
            roomOutlines.append(thisOutline)
    return roomOutlines

sc.doc = Rhino.RhinoDoc.ActiveDoc
rs.EnableRedraw(True)

files = rs.OpenFileNames(title="Select DWG files to process", extension=".dwg")
outputFolder = rs.BrowseForFolder(message="Select folder for output.txt file")

for filepath in files:
# Import the dwg file
    rs.Command("!_-Import \"" + filepath + "\" -Enter -Enter")
#    docPoint = sc.doc.EarthAnchorPoint
#    xform = docPoint.GetModelToEarthTransform(Rhino.UnitSystem(9)) # Unit System 9 for feet
#    rs.UnselectAllObjects()

# Process Room Outline Layers
    roomOutlines = []
    roomOutlines = addOutlines("I-AREA-NASF", roomOutlines)
    roomOutlines = addOutlines("I-AREA-NONF", roomOutlines)

# Get Room Number Tags
    roomTagLocations = []
    roomTagNumbers = []
    blockTagLayer = rs.ObjectsByLayer("I-IDEN-RMNO", select=False)
    for blockTag in blockTagLayer:
       if rs.ObjectType(blockTag) == 4096:
           roomTagLocations.append(rs.BlockInstanceInsertPoint(blockTag))
           roomTagNumbers.append(rs.GetUserText(blockTag, key="ROOMNUMBER"))

# Match Room Outline to Room Number
    for thisOutline in roomOutlines:
        for thisLocation, thisNumber in zip(roomTagLocations, roomTagNumbers):
            result = rs.PointInPlanarClosedCurve(thisLocation, thisOutline, plane=rs.WorldXYPlane())
            if result == 1:
# Translate curve points into Json
                pointList = rs.CurvePoints(thisOutline)
                textHeader = '{"type":"Polygon","coordinate":[['
                curveText = textHeader
                textFooter = ']]}'
                for thisPoint in pointList:
#                    newPoint = rs.PointTransform(thisPoint, xform)
                    thisX = str(thisPoint.X)
                    thisY = str(thisPoint.Y)
                    thisText = '[' + thisX + ',' + thisY + ']' + ','
                    curveText += thisText
                curveText = curveText[0:-1]
                curveText += textFooter
# Write Json and Room Number to output text file
                with open(outputFolder + '\output2.txt', 'a') as f:
                    f.write(curveText)
                    f.write('\t')
                    f.write(thisNumber)
                    f.write('\t')
                    f.write(filepath)
                    f.write('\n')

# Clear all geometry and layers before importing next file 
    allLayers = rs.LayerNames()
    for thisLayer in allLayers: rs.LayerVisible(thisLayer, visible=True)
    rs.AllObjects(select=True, include_references=True)
    rs.Command("_Delete")
    rs.Command("_Purge BlockDefinitions=Yes Layers=Yes -Enter")
