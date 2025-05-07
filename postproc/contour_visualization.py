# -*- coding: mbcs -*-
# Abaqus postprocessing macro to open an ODB, apply settings, and export a PNG.
# Run using: abaqus cae noGUI=contour_visualization.py -- myfile.odb

print "Importing Abaqus modules..."

from abaqus import *
from abaqusConstants import *
import section, regionToolset, displayGroupMdbToolset as dgm
import part, material, assembly, step, interaction, load
import mesh, optimization, job, sketch, visualization, xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from odbAccess import openOdb

odb_path = "simulation_results/example1/example1.odb"
print "Opening ODB file:", odb_path

# ===> Open the ODB and assign to the viewport
my_odb = openOdb(path=odb_path)
session.viewports['Viewport: 1'].setValues(displayedObject=my_odb)
print "ODB opened and assigned to viewport."

# ===> Set primary variable for display: LE, Max Principal strain
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='LE', outputPosition=INTEGRATION_POINT,
    refinement=(INVARIANT, 'Max. Principal'))

# ===> Adjust contour display state
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_UNDEF,))

# ===> Set camera view
session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
session.viewports['Viewport: 1'].view.setValues(
    nearPlane=0.430951, farPlane=0.682514,
    width=0.467434, height=0.217851,
    viewOffsetX=0.0245512, viewOffsetY=-0.018731)

# ===> Apply view cut on Z-Plane
session.viewports['Viewport: 1'].odbDisplay.setValues(viewCutNames=('Z-Plane',), viewCut=ON)
session.viewports['Viewport: 1'].odbDisplay.viewCuts['Z-Plane'].setValues(showModelBelowCut=False)

# ===> Hide specific materials
leaf = dgo.LeafFromOdbElementMaterials(
    elementMaterials=("CSF", "SKULL"))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)

# ===> Set contour limits and out-of-bounds color
session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    maxAutoCompute=OFF, maxValue=0.3, minAutoCompute=OFF, minValue=0.00)
session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    outsideLimitsAboveColor='#800000')

# ===> Hide mesh edges
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(visibleEdges=NONE)

# ===> Set Z-plane cut position
session.viewports['Viewport: 1'].odbDisplay.viewCuts['Z-Plane'].setValues(position=-0.015)

# ===> Select specific output frame
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=9)

# ===> Define output filename based on ODB name
odb_basename = odb_path.split('/')[-1].replace('.odb', '')
output_filename = odb_basename + '_contour'

# ===> Export PNG
print "Saving PNG to: %s.png" % output_filename
session.printToFile(fileName=output_filename, format=PNG,
    canvasObjects=(session.viewports['Viewport: 1'],))

print "Script completed successfully."