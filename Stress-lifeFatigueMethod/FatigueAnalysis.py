from abaqus import *
from symbolicConstants import *
from abaqusConstants import *
from math import *
import visualization
import odbAccess
from odbAccess import *
from odbMaterial import *
from odbSection import *
from abaqus import getInput


## Open the output database.

ODBNAME1 = getInput('Enter the ODB file name:', 'Job-1')
ODBNAME = '%s.odb' % (ODBNAME1)
print (ODBNAME)

myOdb = visualization.openOdb(path= ODBNAME, readOnly = FALSE)

# Check the flag of odb (When it was opened by means of CAE)
if myOdb.isReadOnly:
    myOdb.close()
    myOdb = visualization.openOdb(path = ODBNAME, readOnly = FALSE)


## Select the part and steps

assembly = myOdb.rootAssembly
instances = assembly.instances

# Printing the names of the instances of the model, This will help in selecting them
for key in instances.keys():
    print key
    
# Making the widndow, in order to input the parts, and steps on which Fatigue Analysis are to be performed
fields = (('PART:', 'PART-1-1'), ('Minimum loading:', 'Step-1'), ('MaximumLoading:', 'Step-2'))
PART, STEP_1, STEP_2 = getInputs(fields = fields, label = 'Specify Part and Steps:', 
    dialogTitle = 'Analysis Requisites', )
p = instances[PART]

## Input Material Properties

# Making a window, where material properties should be input
fields = (('Ultimate Tensile Stress:', '551.6e6'), ('Yield Tensile Stress:', '448.2e6'),
    ('a:', '893.561e6'), ('b:', '-0.0851'))
UTS, YTS, a, b = getInputs(fields = fields, 
    label = 'Specify Material Properties:', dialogTitle = 'Material Properties', )
    
UTS = eval(UTS)
YTS = eval (YTS)
a = eval (a)
b = eval (b)


## Create variables that specify the steps, frames, and stress outputs

step1 = myOdb.steps[STEP_1]
step2 = myOdb.steps[STEP_2]

frame1 = step1.frames[-1]
frame2 = step2.frames[-1]

field1 = frame1.fieldOutputs
field2 = frame2.fieldOutputs

STRESS = 'S'

stressSet1 = field1[STRESS]
stressSet2 = field2[STRESS]


## Getting Elements and Node Number

S = []
for V in stressSet1.values:
    if V.position == ELEMENT_NODAL:
        S.append((V.nodeLabel))
        POSITION = ELEMENT_NODAL
    elif V.position == INTEGRATION_POINT:
        S.append((V.elementLabel))
        POSITION = CENTROID


## Generating Stress midrange and amplitude matrices

Samax = []
Smmax = []

S_aField = frame1.FieldOutput(name = 'Sa',
    description = 'Sa', type = TENSOR_3D_FULL )
S_mField = frame1.FieldOutput(name = 'Sm',
    description = 'Sm', type = TENSOR_3D_FULL )

## Calculating Amplitude ans Midrange Stress
S_aField = abs((stressSet2 - stressSet1)*.5)
S_mField = (stressSet2 + stressSet1)*.5

for V in S_aField.values:
    # Samax.append((V.maxPrincipal))
    Samax.append((V.mises))     
    
for V in S_mField.values:
    # Smmax.append((V.maxPrincipal))
    Smmax.append((V.mises))

## Fatigue Analysis

NF_Souderberg = []
NF_modifiedGoudman = []
NF_Gereber = []

LOGNF_Souderberg = []
LOGNF_modifiedGoudman = []
LOGNF_Gereber = []

# # Souderberg method
# j = 0
# while j <= (len(stressSet1.values)-1):
    # S_f_Souderberg = Samax[j]/(1-Smmax[j]/YTS)
    # N_Souderberg = (S_f_Souderberg/a)**(1/b)
    # NF1 = [N_Souderberg]
    # NF2 = tuple (NF1)
    # NF_Souderberg.append (NF2)
    
    # LN_Souderberg = log10(N_Souderberg)
    # LNf1 = [LN_Souderberg]
    # LNf2 = tuple (LNf1)
    # LOGNF_Souderberg.append (LNf2)
    
    # j += 1 

    
# Modified Goudman method
j = 0
while j <= (len(stressSet1.values)-1):
    S_f_modifiedGoudman = Samax[j]/(1-Smmax[j]/UTS)
    N_modifiedGoudman = (S_f_modifiedGoudman/a)**(1/b)
    NF1 = [N_modifiedGoudman]
    NF2 = tuple (NF1)
    NF_modifiedGoudman.append (NF2)
    
    LN_modifiedGoudman = log10(N_modifiedGoudman)
    LNf1 = [LN_modifiedGoudman]
    LNf2 = tuple (LNf1)
    LOGNF_modifiedGoudman.append (LNf2)
    
    j += 1    
    
# Gereber method
j = 0
while j <= (len(stressSet1.values)-1):
    S_f_Gereber = Samax[j]/(1-((Smmax[j]/UTS)**2))
    N_Gereber = (S_f_Gereber/a)**(1/b)
    NF1 = [N_Gereber]
    NF2 = tuple (NF1)
    NF_Gereber.append (NF2)
    
    LN_Gereber = log10(N_Gereber)
    LNf1 = [LN_Gereber]
    LNf2 = tuple (LNf1)
    LOGNF_Gereber.append (LNf2)
    
    j += 1 


## Create Output fields
outputData = field2.keys()

elementLabelData = S

# Number of Life Cycles

# if 'Number Souderberg' not in outputData:
    # nField_Souderberg = frame2.FieldOutput(name = 'Number Souderberg',
        # description='Calculated Number of Life Cycles of Each Element', type = SCALAR)
    # nField_Souderberg.addData(position = POSITION, instance = p, labels = elementLabelData,
        # data=NF_Souderberg)

if 'Number modified Goudman' not in outputData:
    nField_modifiedGoudman = frame2.FieldOutput(name = 'Number modified Goudman',
        description = 'Calculated Number of Life Cycles of Each Element', type = SCALAR)
    nField_modifiedGoudman.addData(position = POSITION, instance = p, labels = elementLabelData,
        data = NF_modifiedGoudman)

if 'Number Gereber' not in outputData:
    nField_Gereber = frame2.FieldOutput(name = 'Number Gereber',
        description = 'Calculated Number of Life Cycles of Each Element', type = SCALAR)
    nField_Gereber.addData(position = POSITION, instance = p, labels = elementLabelData,
        data = NF_Gereber)


# LOG Number of Life Cycles

# if 'Log Number Souderberg' not in outputData:
    # lnField_Souderberg = frame2.FieldOutput(name = 'Log Number Souderberg',
        # description = 'Calculated LOG Number of Life Cycles of Each Element', type = SCALAR)
    # lnField_Souderberg.addData(position = POSITION, instance = p, labels = elementLabelData,
        # data = LOGNF_Souderberg)

if 'Log Number modified Goudman' not in outputData:
    lnField_modifiedGoudman = frame2.FieldOutput(name = 'Log Number modified Goudman',
        description = 'Calculated LOG Number of Life Cycles of Each Element', type = SCALAR)
    lnField_modifiedGoudman.addData(position = POSITION, instance = p, labels = elementLabelData,
        data = LOGNF_modifiedGoudman)

if 'Log Number Gereber' not in outputData:
    lnField_Gereber = frame2.FieldOutput(name = 'Log Number Gereber',
        description = 'Calculated LOG Number of Life Cycles of Each Element', type = SCALAR)
    lnField_Gereber.addData(position = POSITION, instance = p, labels = elementLabelData,
        data = LOGNF_Gereber)

myOdb.save()
print (ODBNAME + ' Updated')
myOdb.close()
myOdb = visualization.openOdb(path = ODBNAME, readOnly = FALSE)