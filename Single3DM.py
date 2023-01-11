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
rs.EnableRedraw(False)
outputFolder = rs.BrowseForFolder(message="Select folder for output.txt file")
docPoint = sc.doc.EarthAnchorPoint
xform = docPoint.GetModelToEarthTransform(Rhino.UnitSystem(9)) # Unit System 9 for feet

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
                newPoint = rs.PointTransform(thisPoint, xform)
                thisX = str(newPoint.X)
                thisY = str(newPoint.Y)
                thisText = '[' + thisX + ',' + thisY + ']' + ','
                curveText += thisText
            curveText = curveText[0:-1]
            curveText += textFooter
# Write Json and Room Number to output text file
            with open(outputFolder + '\PlanProcessing.txt', 'a') as f:
                f.write(curveText)
                f.write('\t')
                f.write(thisNumber)
                f.write('\n')