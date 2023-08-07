from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
import math
import numpy as np

## Initial Data And Calculations

Mdb()

# Curve Geometry
angelOfCurve = 18 #degree
outerRadius = 0.3 #m
thicknessOfCurve = 0.01 #m

angelOfCurveRa = angelOfCurve*math.pi/180
innerRadius = outerRadius - thicknessOfCurve
totalCurveLength = outerRadius*angelOfCurveRa


# Hole
radiusOfHole = 0.002 #m
distanceFromSurface = 0.005 #m

centerOfHole = (outerRadius-distanceFromSurface, 0.0)
pointOfHole = (outerRadius-distanceFromSurface+radiusOfHole, 0.0)


# Piezoelectric Geometry
numberOfPiez = 16
pithOfPiez = 0.0005 #m
thicknessOfPiez = 0.0004 #m

totalPiezCurveLength = (numberOfPiez-1)*pithOfPiez + thicknessOfPiez
totalPiezCurveAngle = totalPiezCurveLength/outerRadius
eachPiezCurveAngle = thicknessOfPiez/outerRadius
emptyAreaOfpiezAngle = (pithOfPiez-thicknessOfPiez)/outerRadius


# Piezoelectric Excition
frequncyOfPiez = 5e6 #Hz
numberOfPeriod = 4

excitionTime = numberOfPeriod/frequncyOfPiez



# Material Properties
mat1Name ='Comp'
mat1E = 20.55e9 #Pa
mat1Nu = 0.25
mat1Density = 2007
sec1Name = 'Section-1'


# Cacluate mesh size, time increment, run time
mat1G = mat1E/(2*(1+mat1Nu))
mat1Lambda = mat1E*mat1Nu/((1+mat1Nu)*(1-2*mat1Nu))

mat1WaveSpeedTra = math.sqrt(mat1G/mat1Density)
mat1WaveSpeedLon = math.sqrt((mat1Lambda+2*mat1G)/mat1Density)

mat1WaveLength = mat1WaveSpeedTra / frequncyOfPiez
mat1maximumMeshSize = mat1WaveLength/10

# round mesh size
formatted_x = "{:.0e}".format(mat1maximumMeshSize)
leadingZero = (float('1'+formatted_x[formatted_x.find('e'):]))
meshSize = math.floor(mat1maximumMeshSize/leadingZero)*leadingZero


stableTimeIncrement = meshSize/mat1WaveSpeedLon
# round stable time
formatted_x = "{:.0e}".format(stableTimeIncrement)
leadingZero = (float('1'+formatted_x[formatted_x.find('e'):]))
stableTimeIncrement = math.floor(stableTimeIncrement/leadingZero)*leadingZero

stepTimeCoef = 1.5
timeForTravelingWave = (thicknessOfCurve*2/mat1WaveSpeedLon + excitionTime)*stepTimeCoef
# round step time
formatted_x = "{:.0e}".format(timeForTravelingWave)
leadingZero = (float('1'+formatted_x[formatted_x.find('e'):]))
stepTime = math.ceil(timeForTravelingWave/leadingZero)*leadingZero



# Model Data
partName = 'Part-1'
modelName = mdb.models.keys()[0]
model = mdb.models[modelName]
loadMagnitude = 10000.0
dispMagnitude = -1e-6


#######################
####  Plot Module  ####
#######################

## Calculate Angel of Each Part of Partitioned Curve 
thetaList = [angelOfCurveRa/2] #First Point of Curve
remainTheta = (angelOfCurveRa-totalPiezCurveAngle)
thetaEnd = angelOfCurveRa/2-remainTheta/2
thetaList.append(thetaEnd) #Start of First Piezoelectric
thetaEnd = thetaEnd - eachPiezCurveAngle
thetaList.append(thetaEnd) #End of First Piezoelectric

piezCenterPoints = [(math.cos(thetaEnd+eachPiezCurveAngle/2)*outerRadius,
                     math.sin(thetaEnd+eachPiezCurveAngle/2)*outerRadius, 0),]
piezCenterTheta = [thetaEnd+eachPiezCurveAngle/2]

for i in range(numberOfPiez - 1):
    thetaEnd = thetaEnd - emptyAreaOfpiezAngle
    thetaList.append(thetaEnd) #End of the Piezoelectric
    thetaEnd = thetaEnd - eachPiezCurveAngle
    thetaList.append(thetaEnd) #End of the Piezoelectric

    piezCenterPoints.append((math.cos(thetaEnd+eachPiezCurveAngle/2)*outerRadius,
                             math.sin(thetaEnd+eachPiezCurveAngle/2)*outerRadius,0))
    piezCenterTheta.append(thetaEnd+eachPiezCurveAngle/2)

thetaList.append(-angelOfCurveRa/2) #End Point of Curve


## Plot Base Curve
sheetSize = outerRadius*4
s = model.ConstrainedSketch(name='__profile__', sheetSize=sheetSize)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.ConstructionLine(point1=(0.0, -1.0), point2=(0.0, 1.0))
s.FixedConstraint(entity=g[g.keys()[0]])
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
# p = model.Part(name=partName, dimensionality=TWO_D_PLANAR, 
#     type=DEFORMABLE_BODY)
p = model.Part(name=partName, dimensionality=AXISYMMETRIC, 
    type=DEFORMABLE_BODY)
p = model.parts[partName]
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
del model.sketches['__profile__']



## Define Surfaces and Sets of Piezoelectric in Part Module
p = model.parts[partName]
for i, point in enumerate(piezCenterPoints):
    side1Edges = p.edges.findAt((point,))
    p.Surface(side1Edges=side1Edges, name='Surf-'+str(i+1))
    p.Set(edges=side1Edges, name='Set-'+str(i+1))


## Partition the base surface from midle
pickedFaces = p.faces.findAt((((innerRadius+outerRadius)/2,0,0),))
p.PartitionFaceByShortestPath(faces=pickedFaces, point1=(innerRadius,0,0), point2=(outerRadius,0,0))

## Plot Hole
s1 = model.ConstrainedSketch(name='__profile__', 
    sheetSize=sheetSize, gridSpacing=0.01)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.CircleByCenterPerimeter(center=centerOfHole, point1=pointOfHole)
# Put Dimensions
# # Default Dimensions
# s1.RadialDimension(curve=g[21], textPoint=(0.26, 0.017), radius=radiusOfHole)
# s1.HorizontalDimension(vertex1=v[17], vertex2=v[1], textPoint=(0.28, 0.016), value=distanceFromSurface)
# s1.DistanceDimension(entity1=v[17], entity2=g[2], textPoint=(0.3, 0.01), value=0.0)
# Try to Find Geometries ands Vertices (More Rubust Method)
for i in g.keys():
    if str(g[i].curveType) =='CIRCLE':
        circleGeo = g[i]
# circleGeo = g[g.keys()[-1]]
for i in v.keys():
    if sum([abs(m-n) for m,n in zip(v[i].coords,centerOfHole)]) < 1e-10:
        circleCenterVert = v[i]
    if sum([abs(m-n) for m,n in zip(v[i].coords,(outerRadius,0))]) < 1e-10:
        curveSurfaceVert = v[i]
s1.RadialDimension(curve=circleGeo, textPoint=(0.26, 0.017), radius=radiusOfHole)
s1.HorizontalDimension(vertex1=circleCenterVert, vertex2=curveSurfaceVert, 
                       textPoint=(outerRadius*0.95, 0.016), value=distanceFromSurface)
s1.VerticalDimension(vertex1=circleCenterVert, vertex2=curveSurfaceVert, 
                     textPoint=(outerRadius*1.05, 0.1), value=0.0)

p.Cut(sketch=s1)
s1.unsetPrimaryObject()
del model.sketches['__profile__']





###########################
#### Properties Module ####
###########################

model.Material(name=mat1Name)
model.materials[mat1Name].Elastic(table=((mat1E, mat1Nu), ))
model.materials[mat1Name].Density(table=((mat1Density, ), ))
model.HomogeneousSolidSection(name=sec1Name, material=mat1Name, thickness=None)

pointOnFace1Up = (math.cos(angelOfCurveRa/4)*(outerRadius+innerRadius)/2,
                math.sin(angelOfCurveRa/4)*(outerRadius+innerRadius)/2, 0)
pointOnFace1Down = (math.cos(angelOfCurveRa/4)*(outerRadius+innerRadius)/2,
                    -math.sin(angelOfCurveRa/4)*(outerRadius+innerRadius)/2, 0)
faces1 = p.faces.findAt((pointOnFace1Up,))+p.faces.findAt((pointOnFace1Down,))
region = regionToolset.Region(faces=faces1)

p.SectionAssignment(region=region, sectionName=sec1Name, offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)






##########################
#### Assembley Module ####
##########################


## Define Set in the Midle of Piezoelctrics in Assemmbley Module
a = model.rootAssembly
a.DatumCsysByDefault(CARTESIAN)
a.DatumCsysByThreePoints(name='Datum csys-R', coordSysType=CYLINDRICAL, 
    origin=(0.0, 0.0, 0.0), line1=(1.0, 0.0, 0.0), line2=(0.0, 1.0, 0.0))
p = model.parts[partName]
a.Instance(name='Part-1-1', part=p, dependent=OFF)

for i, point in enumerate(piezCenterPoints):
    if len(piezCenterPoints)%2 > 0:
        if abs(math.floor(len(piezCenterPoints)/2) - i) > 1e-6:
            pickedEdge = a.instances['Part-1-1'].edges.findAt((point,))
            a.PartitionEdgeByParam(edges=pickedEdge, parameter=0.5)
    else:
        pickedEdge = a.instances['Part-1-1'].edges.findAt((point,))
        a.PartitionEdgeByParam(edges=pickedEdge, parameter=0.5)        
    pickedVertice = a.instances['Part-1-1'].vertices.findAt((point,))
    a.Set(vertices=pickedVertice, name='CenterPoint-'+str(i+1))
    

## Define a Set for all Midle Points
for i, point in enumerate(piezCenterPoints):
    pickedVertice = a.instances['Part-1-1'].vertices.findAt((point,))
    if i < 1 :
        allVertices = pickedVertice
    else:
        allVertices = allVertices + pickedVertice
a.Set(vertices=allVertices, name='AllCenterPoint')



## Define Set For Boundry Conditions

pointOnEdge1Up = (math.cos(angelOfCurveRa/2)*(outerRadius+innerRadius)/2,
                math.sin(angelOfCurveRa/2)*(outerRadius+innerRadius)/2, 0)
pointOnEdge1Down = (math.cos(angelOfCurveRa/2)*(outerRadius+innerRadius)/2,
                    -math.sin(angelOfCurveRa/2)*(outerRadius+innerRadius)/2, 0)
edges1 = a.instances['Part-1-1'].edges.findAt((pointOnEdge1Up,)) +  \
         a.instances['Part-1-1'].edges.findAt((pointOnEdge1Down,))
a.Set(edges=edges1, name='Set-BC')





#######################
####  Step Module  ####
#######################

model.ExplicitDynamicsStep(name='Step-1', previous='Initial', 
    timePeriod=stepTime, timeIncrementationMethod=FIXED_USER_DEFINED_INC, 
    userDefinedInc=stableTimeIncrement, improvedDtMethod=ON)

model.fieldOutputRequests['F-Output-1'].setValues(variables=(
    'S', 'U'), numIntervals=20)
    # 'S', 'U', 'V', 'A', 'COORD'), numIntervals=100)

regionDef=a.sets['AllCenterPoint']
model.historyOutputRequests['H-Output-1'].setValues(variables=(
    'U1', 'U2'), frequency=1, region=regionDef, 
    sectionPoints=DEFAULT, rebar=EXCLUDE)






#######################
####  Load Module  ####
#######################

# BC
region = a.sets['Set-BC']
datum = a.datums[a.features['Datum csys-R'].id]
model.DisplacementBC(name='BC-Sides', createStepName='Initial', 
    region=region, u1=UNSET, u2=SET, ur3=UNSET, amplitude=UNSET, 
    distributionType=UNIFORM, fieldName='', localCsys=datum)


# amplitude

ampTable = ((0,0),)

for time in np.arange (stableTimeIncrement,excitionTime+stableTimeIncrement,stableTimeIncrement):
    omega = 2*math.pi*frequncyOfPiez
    g = math.sin(omega*time)
    h = 0.5*(1 - math.cos(omega*time/numberOfPeriod))
    amp = g*h
    ampTable = ampTable + ((time,amp),)

ampTable = ampTable + ((excitionTime + stableTimeIncrement,0),) + \
                      ((stepTime,0),)
 

model.TabularAmplitude(name='Amp-1', timeSpan=STEP, 
    smooth=SOLVER_DEFAULT, data=ampTable)


### Displacement
## for i in range(1,numberOfPiez+1):
##     region = a.instances['Part-1-1'].sets['Set-'+str(i)]
##     datum = a.datums[a.features['Datum csys-R'].id]
##     model.DisplacementBC(name='BC-Exc-'+str(i), createStepName='Step-1', 
##        region=region, u1=dispMagnitude, u2=UNSET, ur3=UNSET, amplitude='Amp-1', fixed=OFF, 
##        distributionType=UNIFORM, fieldName='', localCsys=datum)


# Pressure
for i in range(1,numberOfPiez+1):
   region = a.instances['Part-1-1'].surfaces['Surf-'+str(i)]
   model.Pressure(name='Pressure-'+str(i), createStepName='Step-1', 
       region=region, distributionType=UNIFORM, field='', magnitude=loadMagnitude, 
       amplitude='Amp-1')
   #mdb.models['Model-1'].loads['Pressure-'+str(i)].suppress()

# # Traction
## for i in range(1,numberOfPiez+1):
##     region = a.instances['Part-1-1'].surfaces['Surf-'+str(i)]
##     model.SurfaceTraction(name='Traction-'+str(i), createStepName='Step-1', 
##         region=region, magnitude=loadMagnitude, amplitude='Amp-1', 
##         directionVector=(piezCenterPoints[i-1], (0.0, 0.0, 0.0)), 
##         distributionType=UNIFORM, field='', localCsys=None, traction=GENERAL)





#######################
####  Mesh Module  ####
#######################

pointOnFace1Up = (math.cos(angelOfCurveRa/4)*(outerRadius+innerRadius)/2,
                math.sin(angelOfCurveRa/4)*(outerRadius+innerRadius)/2, 0)
pointOnFace1Down = (math.cos(angelOfCurveRa/4)*(outerRadius+innerRadius)/2,
                    -math.sin(angelOfCurveRa/4)*(outerRadius+innerRadius)/2, 0)
pickedFaces = a.instances['Part-1-1'].faces.findAt((pointOnFace1Up,)) +\
              a.instances['Part-1-1'].faces.findAt((pointOnFace1Down,))

a.setMeshControls(regions=pickedFaces, elemShape=QUAD, algorithm=MEDIAL_AXIS)
partInstances =(a.instances['Part-1-1'], )
a.seedPartInstance(regions=partInstances, size=meshSize, deviationFactor=0.1, 
    minSizeFactor=0.1)
a.generateMesh(regions=partInstances)


#Edit stable Time Incerement
findedStableTime = a.verifyMeshQuality(criterion=STABLE_TIME_INCREMENT)['worst']
formatted_x = "{:.0e}".format(findedStableTime)
leadingZero = (float('1'+formatted_x[formatted_x.find('e'):]))
findedStableTime = math.floor(findedStableTime/leadingZero)*leadingZero

model.steps['Step-1'].setValues(userDefinedInc=min(findedStableTime,stableTimeIncrement), 
    improvedDtMethod=ON)






######################
####  Job Module  ####
######################

runOrNot = getWarningReply('Do you want to run', (YES,NO))

if runOrNot == SymbolicConstant('YES'):
   
   for i in range(1,numberOfPiez+1):
        
        for j in range(1,numberOfPiez+1):
            if abs(j - i)>1e-6:
                # model.boundaryConditions['BC-Exc-'+str(i)].suppress()
                model.loads['Pressure-'+str(j)].suppress()
                # model.loads['Traction-'+str(j)].suppress()
            else:
                # model.boundaryConditions['BC-Exc-'+str(i)].resume()
                model.loads['Pressure-'+str(j)].resume()
                # model.loads['Traction-'+str(j)].resume()
                

        jobName = 'JobPhaseArray-'+str(i)
        mdb.Job(name=jobName, model=modelName, description='',
            type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None,
            memory=90, memoryUnits=PERCENTAGE, explicitPrecision=DOUBLE, 
            nodalOutputPrecision=FULL, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, 
            historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, 
            parallelizationMethodExplicit=DOMAIN, numDomains=3, 
            activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=3)
        mdb.jobs[jobName].submit(consistencyChecking=OFF)
        mdb.jobs[jobName].waitForCompletion()

        print(' ')
        print('Run' + str(i) + 'Done')
        print(' ')



##############################
#### visualization Module ####
##############################

readOrNot = getWarningReply('Do you want to save data', (YES,NO))

if readOrNot == SymbolicConstant('YES'):
    for i in range(1,numberOfPiez+1):
        try:
            odbName = 'JobPhaseArray-'+str(i) + '.odb'
            odb = visualization.openOdb(path= odbName)
            step = odb.steps['Step-1']
            for hisReg in step.historyRegions.keys():
                nodeLabel = int(hisReg[hisReg.find('.')+1:])
                nodeCoord = a.instances['Part-1-1'].nodes[nodeLabel-1].coordinates
                for number , piezCoord in enumerate(piezCenterPoints):
                    if abs(piezCoord[0] - nodeCoord[0]) < 1e-6 and \
                        abs(piezCoord[1] - nodeCoord[1]) < 1e-6 and \
                        abs(piezCoord[2] - nodeCoord[2]) < 1e-6:
                        peizoNumber = number
                        data1 = np.array(step.historyRegions[hisReg].historyOutputs['U1'].data)
                        data2 = np.array(step.historyRegions[hisReg].historyOutputs['U2'].data)
                        time = data1[:,0]
                        U1 = data1[:,1]
                        U2 = data2[:,1]
                        theta = piezCenterTheta[peizoNumber]
                        Ur = np.sqrt(U1*U1 + U2*U2)
                        Un = U1*np.cos(theta)+U2*np.sin(theta)
                        time = np.atleast_2d(time).T
                        Ur = np.atleast_2d(Ur).T
                        Un = np.atleast_2d(Un).T
                        
                        df = np.concatenate((time, Un), axis=1)
                        
                        fileName = 'Exe_' + str(i) + '_Sig_' + str(peizoNumber+1) + ".csv"
                        np.savetxt(fileName , df, delimiter=",") 
            odb.close()     
        except Exception as e:
            #print(e)
            print('File ' + odbName + ' Dont exsist')
            



# session.viewports['Viewport: 1'].setValues(displayedObject=p)
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].view.fitView()
