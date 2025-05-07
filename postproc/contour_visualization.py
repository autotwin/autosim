# -*- coding: mbcs -*-
# Abaqus postprocessing macro to open an ODB, apply settings, and export a PNG at t=0.02 s

print "Importing Abaqus modules..."

from abaqus import *
from abaqusConstants import *
import section, regionToolset, displayGroupMdbToolset as dgm
import part, material, assembly, step, interaction, load
import mesh, optimization, job, sketch, visualization, xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from odbAccess import openOdb

# === Set input path ===
odb_path = "simulation_results/example1/example1.odb"
print "Opening ODB file:", odb_path

# === Open ODB and assign to viewport
my_odb = openOdb(path=odb_path)
session.viewports['Viewport: 1'].setValues(displayedObject=my_odb)
print "ODB opened and assigned to viewport."

# === Find frame closest to t = 0.02
target_time = 0.02
step = list(my_odb.steps.values())[-1]
frame_times = [f.frameValue for f in step.frames]
closest_index = min(range(len(frame_times)), key=lambda i: abs(frame_times[i] - target_time))
closest_time = frame_times[closest_index]
print "Using frame %d at time %.6f s" % (closest_index, closest_time)

# === Set primary variable for display
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='LE', outputPosition=INTEGRATION_POINT,
    refinement=(INVARIANT, 'Max. Principal'))

# === Adjust contour display state
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_UNDEF,))

# === Set camera view
session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
session.viewports['Viewport: 1'].view.setValues(
    nearPlane=0.430951, farPlane=0.682514,
    width=0.467434, height=0.217851,
    viewOffsetX=0.0245512, viewOffsetY=-0.018731)

# === Apply view cut on Z-Plane
session.viewports['Viewport: 1'].odbDisplay.setValues(viewCutNames=('Z-Plane',), viewCut=ON)
session.viewports['Viewport: 1'].odbDisplay.viewCuts['Z-Plane'].setValues(showModelBelowCut=False)

# === Hide specific materials
leaf = dgo.LeafFromOdbElementMaterials(elementMaterials=("CSF", "SKULL"))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)

# === Set contour limits and out-of-bounds color
session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    maxAutoCompute=OFF, maxValue=0.3, minAutoCompute=OFF, minValue=0.00)
session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    outsideLimitsAboveColor='#800000')

# === Hide mesh edges
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(visibleEdges=NONE)

# === Set Z-plane cut position
session.viewports['Viewport: 1'].odbDisplay.viewCuts['Z-Plane'].setValues(position=-0.015)

# === Set frame based on time
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=closest_index)

# === Define and save output
odb_basename = odb_path.split('/')[-1].replace('.odb', '')
output_filename = "%s_contour_%.0fms" % (odb_basename, closest_time * 1000)
print "Saving PNG to: %s.png" % output_filename

session.printToFile(fileName=output_filename, format=PNG,
    canvasObjects=(session.viewports['Viewport: 1'],))

print "Script completed successfully."
