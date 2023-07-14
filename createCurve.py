from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
import math




#Curve
angelOfCurve = 18 #degree
angelOfCurveRa = angelOfCurve*math.pi/180
outerRadius = 0.3 #m
thicknessOfCurve = 0.01 #m

innerRadius = outerRadius - thicknessOfCurve
totalCurveLength = outerRadius*angelOfCurveRa


# Hole
radiusOfHole = 0.002 #m
distanceFromSurface = 0.004 #m

centerOfHole = (outerRadius-distanceFromSurface, 0.0)
pointOfHole = (outerRadius-distanceFromSurface+radiusOfHole, 0.0)


#Piezoelectric
numberOfPiez = 4
pithOfPiez = 0.004 #m
thicknessOfPiez = 0.002 #m

totalPiezCurveLength = (numberOfPiez-1)*pithOfPiez + thicknessOfPiez
totalPiezCurveAngle = totalPiezCurveLength/outerRadius
eachPiezCurveAngle = thicknessOfPiez/outerRadius
emptyAreaOfpiezAngle = (pithOfPiez-thicknessOfPiez)/outerRadius






#Model
partName = 'Part-1'
modelName = mdb.models.keys()[0]
model = mdb.models[modelName]
sheetSize = outerRadius*4



# Calculate Angel of Each Part of Partitioned Curve 
thetaList = [angelOfCurveRa/2] #First Point of Curve
remainTheta = (angelOfCurveRa-totalPiezCurveAngle)
thetaEnd = angelOfCurveRa/2-remainTheta/2
thetaList.append(thetaEnd) #Start of First Piezoelectric
thetaEnd = thetaEnd - eachPiezCurveAngle
thetaList.append(thetaEnd) #End of First Piezoelectric

piezCenterPoints = [(math.cos(thetaEnd+eachPiezCurveAngle/2)*outerRadius,
                     math.sin(thetaEnd+eachPiezCurveAngle/2)*outerRadius, 0),]

for i in range(numberOfPiez - 1):
    thetaEnd = thetaEnd - emptyAreaOfpiezAngle
    thetaList.append(thetaEnd) #End of the Piezoelectric
    thetaEnd = thetaEnd - eachPiezCurveAngle
    thetaList.append(thetaEnd) #End of the Piezoelectric

    piezCenterPoints.append((math.cos(thetaEnd+eachPiezCurveAngle/2)*outerRadius,
                             math.sin(thetaEnd+eachPiezCurveAngle/2)*outerRadius,0))


thetaList.append(-angelOfCurveRa/2) #End Point of Curve



# Plot Base Curve
s = model.ConstrainedSketch(name='__profile__', sheetSize=sheetSize)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
for i in range(len(thetaList)-1): 
    point1 = (math.cos(thetaList[i])*outerRadius,math.sin(thetaList[i])*outerRadius)
    point2 = (math.cos(thetaList[i+1])*outerRadius,math.sin(thetaList[i+1])*outerRadius)  
    s.ArcByCenterEnds(center=(0.0, 0.0), point1=point1, point2=point2, direction=CLOCKWISE)

   
pointOuterCurve = [(math.cos(angelOfCurveRa/2)*outerRadius,math.sin(angelOfCurveRa/2)*outerRadius),
          (math.cos(angelOfCurveRa/2)*outerRadius,-math.sin(angelOfCurveRa/2)*outerRadius)]
pointInnerCurve = [(math.cos(angelOfCurveRa/2)*innerRadius,math.sin(angelOfCurveRa/2)*innerRadius),
          (math.cos(angelOfCurveRa/2)*innerRadius,-math.sin(angelOfCurveRa/2)*innerRadius)]

s.ArcByCenterEnds(center=(0.0, 0.0), point1=pointInnerCurve[0], point2=pointInnerCurve[1], direction=CLOCKWISE)
s.Line(point1=pointOuterCurve[0], point2=pointInnerCurve[0])
s.Line(point1=pointOuterCurve[1], point2=pointInnerCurve[1])
p = model.Part(name=partName, dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = model.parts[partName]
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
del model.sketches['__profile__']


# Define Surfaces and Sets of Piezoelectric in Part Module
p = model.parts[partName]
for i, point in enumerate(piezCenterPoints):
    side1Edges = p.edges.findAt((point,))
    p.Surface(side1Edges=side1Edges, name='Surf-'+str(i+1))
    p.Set(edges=side1Edges, name='Set-'+str(i+1))




# #Plot Hole
# s1 = model.ConstrainedSketch(name='__profile__', 
#     sheetSize=sheetSize, gridSpacing=0.01)
# g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
# s1.setPrimaryObject(option=SUPERIMPOSE)
# p = model.parts[partName]
# p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
# s1.CircleByCenterPerimeter(center=centerOfHole, point1=pointOfHole)
# p = model.parts[partName]
# p.Cut(sketch=s1)
# s1.unsetPrimaryObject()
# del model.sketches['__profile__']




# p = model.parts[partName]
# pickedFaces = p.faces.findAt((((innerRadius+outerRadius)/2,0,0),))
# v2, e1, d2 = p.vertices, p.edges, p.datums
# p.PartitionFaceByShortestPath(faces=pickedFaces, point1=((innerRadius),0,0), point2=((outerRadius),0,0))
# s = model.ConstrainedSketch(name='__profile__', sheetSize=0.62, 
#     gridSpacing=0.01)
# g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
# s.setPrimaryObject(option=SUPERIMPOSE)
# p = model.parts['Part-1']
# p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
# session.viewports['Viewport: 1'].view.setValues(nearPlane=0.185077, 
#     farPlane=0.194269, width=0.0688967, height=0.030416, cameraPosition=(
#     0.294685, -0.000442039, 0.189673), cameraTarget=(0.294685, -0.000442039, 
#     0))
# s.CircleByCenterPerimeter(center=(0.292395085096359, 0.0), point1=(
#     0.297365009784698, 0.0))
# s.CoincidentConstraint(entity1=v[16], entity2=g[2], addUndoState=False)
# s.CoincidentConstraint(entity1=v[15], entity2=g[2], addUndoState=False)
# s.RadialDimension(curve=g[18], textPoint=(0.294051736593246, 
#     0.00716196419671178), radius=0.002)
# s.HorizontalDimension(vertex1=v[15], vertex2=v[1], textPoint=(
#     0.296585410833359, -0.00457625510171056), value=0.005)
# p = model.parts['Part-1']
# p.Cut(sketch=s)
# s.unsetPrimaryObject()
# del model.sketches['__profile__']








# Define Set in the Midle of Piezoelctrics in Assemmbley Module
a = model.rootAssembly
#a.DatumCsysByDefault(CARTESIAN)
p = model.parts[partName]
a.Instance(name='Part-1-1', part=p, dependent=OFF)

for i, point in enumerate(piezCenterPoints):
    pickedEdge = a.instances['Part-1-1'].edges.findAt((point,))
    a.PartitionEdgeByParam(edges=pickedEdge, parameter=0.5)

    pickedVertice = a.instances['Part-1-1'].vertices.findAt((point,))
    a.Set(vertices=pickedVertice, name='CenterPoint-'+str(i+1))
    

# Define a Set for all Midle Points
for i, point in enumerate(piezCenterPoints):
    pickedVertice = a.instances['Part-1-1'].vertices.findAt((point,))
    if i < 1 :
        allVertices = pickedVertice
    else:
        allVertices = allVertices + pickedVertice
a.Set(vertices=allVertices, name='AllCenterPoint')



# session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].view.fitView()