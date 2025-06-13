# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__
import os

#def Macro1():
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

from odbAccess import openOdb

myLocation = os.getcwd()

fname = "IXI013-HH-1212-T1_run1"
# open the odb file
save_path = "simulation_results/" + fname + "/"
odb_path = "simulation_results/" + fname + "/" + fname + ".odb"

# From ANU: name=os.path.join(myLocation, 'All_Hex_Dec_ogden.odb')
# o1 = session.openOdb(path)
o1 = openOdb(path=odb_path)
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='LE', outputPosition=INTEGRATION_POINT, refinement=(
    INVARIANT, 'Max. Principal'), )
session.viewports['Viewport: 1'].odbDisplay.display.setValues(
    plotState=CONTOURS_ON_DEF)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_UNDEF, ))
session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
# adjust the model display in the window or automatically fit 
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.430951, 
    farPlane=0.682514, width=0.467434, height=0.217851, 
    viewOffsetX=0.0245512, viewOffsetY=-0.018731)
session.viewports['Viewport: 1'].view.fitView()    
# show axial cross-section    
session.viewports['Viewport: 1'].odbDisplay.setValues(viewCutNames=('Z-Plane', 
    ), viewCut=ON)
session.viewports['Viewport: 1'].odbDisplay.viewCuts['Z-Plane'].setValues(
    showModelBelowCut=False)
# select the cross-section plane
session.viewports['Viewport: 1'].odbDisplay.viewCuts['Z-Plane'].setValues(
    position=-0.015)    
# remove all the other materials from display    
session.linkedViewportCommands.setValues(_highlightLinkedViewports=True)
# FROM ANU: leaf = dgo.LeafFromOdbElementMaterials(elementMaterials=("CSF_MATL", 
#     "DURA_MATL", "SKULL_MATL", ))
leaf = dgo.LeafFromOdbElementMaterials(elementMaterials=("CSF", "SKULL"))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)
# set legends limits
# FROM ANU: session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
#     maxAutoCompute=OFF, maxValue=0.3, minAutoCompute=OFF, minValue=0.00)

session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    maxAutoCompute=OFF, maxValue=0.5, minAutoCompute=OFF, minValue=0.00,
    outsideLimitsAboveColor='#800000')

# remove elements edges from display    
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    visibleEdges=NONE)

# only save the model figure, without any annotations
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    triad=OFF, legend=OFF, title=OFF, state=OFF, annotations=OFF, compass=OFF)

## if we want to include legends in the figure
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    legendFont='-*-verdana-medium-r-normal-*-*-80-*-*-p-*-*-*',
    legend=ON, legendBox=OFF, legendDecimalPlaces=4, legendNumberFormat=FIXED)

# # select the frame 
# session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=9)

# output_filename = save_path + "fig1"
# session.printToFile(fileName=output_filename, format=PNG, canvasObjects=(
#     session.viewports['Viewport: 1'], ))

# Define output folder
slice_folder = os.path.join(save_path, "slice_viz")
if not os.path.exists(slice_folder):
    os.makedirs(slice_folder)

# Get step name and frame count
step_name = session.odbs[odb_path].steps.keys()[0]
num_frames = len(session.odbs[odb_path].steps[step_name].frames)

# Loop through all frames
for i in range(num_frames):
    # select the frame
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=i)

    # create output filename inside slice_viz folder
    output_filename = os.path.join(slice_folder, "frame_{:03d}".format(i))

    # save PNG
    session.printToFile(fileName=output_filename, format=PNG, canvasObjects=(
        session.viewports['Viewport: 1'], ))
