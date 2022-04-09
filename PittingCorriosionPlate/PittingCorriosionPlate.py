from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import random
executeOnCaeStartup()


## import data

randomNumber = getWarningReply('Random Number of Pits?', (YES,NO))
shapeOfPits = getWarningReply('Cylindrical Pits (Yes) Or Conical Pits (No)?', (YES,NO))

if randomNumber == SymbolicConstant('NO'):

    field=( ('Tickness of Part (y-direction): ' , '0.005'), ('Width of Part (z-direction): ' , '0.1'),
        ('Length of Part (x-direction): ' , '0.1'), ('Maximum Radius Of Pits: ' , '0.005'), 
        ('Maximum Height Of Pits: ' , '0.001'), ('Number of Pits: ','10'),
        ('Part Name: ' , 'Part-1'), ('Model Name: ' , 'Model-1') )
        
    tickness, width, length, maximumPitsRadius, maximumPitsHeight, pitsNumber, partName, modelName = getInputs(fields = field)

    pitsNumber = eval(pitsNumber) 

else:

    field=( ('Tickness of Part (y-direction): ' , '0.005'), ('Width of Part (z-direction): ' , '0.1'),
        ('Length of Part (x-direction): ' , '0.1'), ('Maximum Radius Of Pits: ' , '0.005'), 
        ('Maximum Height Of Pits: ' , '0.001'), ('Maximum Number of Pits: ','100'),
        ('Part Name: ' , 'Part-1'), ('Model Name: ' , 'Model-1') )
        
    tickness, width, length, maximumPitsRadius, maximumPitsHeight, maximumPitsNumber, partName, modelName = getInputs(fields = field)

    maximumPitsNumber = eval(maximumPitsNumber) 
    pitsNumber = random.randint(1,maximumPitsNumber)

tickness = eval(tickness)
width = eval(width)
length = eval(length)

maximumPitsRadius = eval(maximumPitsRadius)
maximumPitsHeight = eval(maximumPitsHeight)

model = mdb.models[modelName]

## Model the Pits

for ii in range(pitsNumber):

    # Sketch
    s = model.ConstrainedSketch(name = '__profile__', sheetSize = 0.1)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.sketchOptions.setValues(decimalPlaces = 3)
    s.setPrimaryObject(option = STANDALONE)
    
    pitRadius = random.uniform(maximumPitsRadius/10,maximumPitsRadius)
    pitHeight = random.uniform(maximumPitsHeight/10,maximumPitsHeight)

    if shapeOfPits == SymbolicConstant('NO'):
        s.ConstructionLine(point1 = (0.0, -0.05), point2 = (0.0, 0.05))
        s.Line(point1 = (0.0, 0.0), point2 = (pitRadius, 0.0))
        s.Line(point1 = (pitRadius, 0.0), point2 = (0.0, -pitHeight))
        s.Line(point1 = (0.0, -pitHeight), point2 = (0.0, 0.0))
    else:
        s.ConstructionLine(point1 = (0.0, -0.05), point2=(0.0, 0.05))
        s.Line(point1 = (0.0, 0.0), point2 = (pitRadius, 0.0))
        s.Line(point1 = (pitRadius, 0.0), point2 = (pitRadius, -pitHeight))
        s.Line(point1 = (pitRadius, -pitHeight), point2 = (0.0, -pitHeight))
        s.Line(point1 = (0.0, -pitHeight), point2 = (0.0, 0.0))

    # Part
    p = model.Part(name = 'Pit-'+str(ii), dimensionality = THREE_D, 
        type = DEFORMABLE_BODY)    
    p = model.parts['Pit-'+str(ii)]
    p.BaseSolidRevolve(sketch = s, angle = 360.0, flipRevolveDirection = OFF)
    s.unsetPrimaryObject()
    p = model.parts['Pit-'+str(ii)]
    del model.sketches['__profile__']


## Import the base part to assembly    
model.rootAssembly.deleteAllFeatures()
p = model.parts[partName]
model.rootAssembly.Instance(name = 'cuted-'+str(0)+'-1', part = p, dependent = ON)

## Cut the pits from base part
count = 0
for ii in range(pitsNumber):
    
    # Import a pit
    a = model.rootAssembly
    p = model.parts['Pit-'+str(ii)]
    a.Instance(name = 'Pit-'+str(ii)+'-1', part = p, dependent = ON)
    
    # Change and translate the position of pit randomly
    XcordOfPit = random.uniform(0,length)
    ZcordOfPit = random.uniform(0,width)  
    a.translate(instanceList = ('Pit-'+str(ii)+'-1', ), vector = (XcordOfPit, tickness, ZcordOfPit))
    
    # Cut the pit and make a new part
    try:	
        ## cut the pit and make a new part
        a.InstanceFromBooleanCut(name = 'cuted-'+str(ii+1-count), 
            instanceToBeCut = model.rootAssembly.instances['cuted-'+str(ii-count)+'-1'], 
            cuttingInstances = (a.instances['Pit-'+str(ii)+'-1'], ), originalInstances = SUPPRESS)
        ## delet last instances to reduce file size
        del a.features['Pit-'+str(ii)+'-1']
        del a.features['cuted-'+str(ii-count)+'-1']
        del model.parts['Pit-'+str(ii)]    
    except:
        count += 1
        print('%s pit dont cut' % (count))
        ## delet last instances to reduce file size
        del a.features['Pit-'+str(ii)+'-1']
        del model.parts['Pit-'+str(ii)]