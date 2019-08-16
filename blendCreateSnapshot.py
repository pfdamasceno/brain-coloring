#!BPY


#import Blender
# import scipy.io
import bpy
import numpy as np
# import colorsys
import os
import sys
import pandas as pd


# filename = 'blendCreateSnapshot.py'
# exec(compile(open('blendCreateSnapshot.py').read(), 'blendCreateSnapshot.py', 'exec'))

blendFullPath = os.path.abspath('.')
os.chdir(blendFullPath)
sys.path.append(blendFullPath)
from blendHelper import *

# if environment variable configFile is set, read the path from there. Otherwise, load ./config.py
configFile = os.getenv('configFile', './config2.py')
import importlib.util
spec = importlib.util.spec_from_file_location("module.name", configFile)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


INPUT_FILE = config.INPUT_FILE
print(INPUT_FILE)


OUT_FOLDER = config.OUTPUT_FOLDER

COLOR_POINTS = [np.array(x) for x in config.COLORS_RGB]
NR_SIGN_LEVELS = len(COLOR_POINTS)-1

IMG_TYPE = config.IMG_TYPE

BRAIN_TYPE = config.BRAIN_TYPE

ATLAS = config.ATLAS

if ATLAS == 'DK':
  cortAreasIndexMap = config.cortAreasIndexMapDK
  subcortAreasIndexMap = config.subcortAreasIndexMap
elif ATLAS == 'Destrieux':
  cortAreasIndexMap = config.cortAreasIndexMapDestrieux
  subcortAreasIndexMap = config.subcortAreasIndexMap
elif ATLAS == 'Tourville':
  cortAreasIndexMap = config.cortAreasIndexMapTourville
  subcortAreasIndexMap = config.subcortAreasIndexMap
  ATLAS = 'DKT' # actually 3D models are labelled as DKT
elif ATLAS == 'Custom':
  cortAreasIndexMap = config.cortAreasIndexMapCustom
  subcortAreasIndexMap = config.subcortAreasIndexMapCustom
else:
  raise ValueError('ATLAS has to be either \'DK\', \'Destrieux\', \'Tourville\' or \'Custom\' ')

cortAreas = cortAreasIndexMap.keys()
subcortAreasShort = subcortAreasIndexMap.keys()

cortRegionsThatShouldBeInTemplate = cortAreasIndexMap.values()
subcortRegionsThatShouldBeInTemplate = subcortAreasIndexMap.values()


cortFilesRight = ['models/%s_atlas_%s/rh.%s.%s.%s.ply' % (ATLAS, BRAIN_TYPE, BRAIN_TYPE, ATLAS, x) for x in cortAreas]
cortFilesLeft =  ['models/%s_atlas_%s/lh.%s.%s.%s.ply' % (ATLAS, BRAIN_TYPE, BRAIN_TYPE, ATLAS, x) for x in cortAreas]
cortFilesAll = cortFilesLeft + cortFilesRight
cortAreasNamesFull = [x.split("/")[-1][:-4] for x in cortFilesAll]
cortAreasIndexMap = dict(zip(cortAreasNamesFull, 2*list(cortAreasIndexMap.values())))




subcortRightAreas = ['Right' + x[4:] for x in subcortAreasIndexMap.keys()]
subcortRightAreasIndexMap = dict(zip(subcortRightAreas, subcortAreasIndexMap.values()))
subcortAreasIndexMap.update(subcortRightAreasIndexMap)
subcortAreas = [x for x in subcortAreasIndexMap.keys() if subcortAreasIndexMap[x] != -1]
subcortFiles = ['./models/subcortical_ply/%s.ply' % x for x in subcortAreas]



nrSubcortRegions = len(subcortAreas)
nrCortRegions = len(cortFilesAll)

if IMG_TYPE == 'subcortical':
  #loadSubcortical(cortFilesRight,subcortFiles)
  painter = SubcorticalPainter(cortFilesRight,subcortFiles)
  indexMap = subcortAreasIndexMap
  areasShort = subcortAreasShort
  regionsThatShouldBeInTemplate = subcortRegionsThatShouldBeInTemplate
elif IMG_TYPE == 'cortical-outer':
  #loadCortical(cortFilesAll)
  painter = CorticalPainter(cortFilesRight)
  indexMap = cortAreasIndexMap
  areasShort = cortAreas
  regionsThatShouldBeInTemplate = cortRegionsThatShouldBeInTemplate
elif IMG_TYPE == 'cortical-inner':
  painter = CorticalPainterInner(cortFilesRight)
  indexMap = cortAreasIndexMap
  areasShort = cortAreas
  regionsThatShouldBeInTemplate = cortRegionsThatShouldBeInTemplate
else:
  raise ValueError('mode has to be either cortical-outer, cortical-inner or subcortical')

fov = 50.0
if BRAIN_TYPE == 'inflated':
  ortho_scale = 280
else:
  ortho_scale = 180

painter.prepareScene(resolution=config.RESOLUTION, bckColor = config.BACKGROUND_COLOR, fov=fov, ortho_scale=ortho_scale, BRAIN_TYPE=BRAIN_TYPE)
painter.loadMeshes()


matDf = pd.read_csv(INPUT_FILE)
labels = matDf.columns.to_list()


regionsThatShouldBeInTemplate = set(regionsThatShouldBeInTemplate) - set([-1])
print(regionsThatShouldBeInTemplate)
print(labels)
missingRegions = list(set(regionsThatShouldBeInTemplate) - set(matDf.columns.to_list()[1:]))
print(missingRegions)
if len(missingRegions) > 0:
  raise ValueError('Regions missing: %s\n\n Make sure the correct atlas is used, see variable ATLAS in config.py. Otherwise add the above missing regions to the input .csv file' % str(missingRegions))


print('-------------%s---------', INPUT_FILE)
colorRegionsAndRender(indexMap, matDf, COLOR_POINTS, OUT_FOLDER, IMG_TYPE)

