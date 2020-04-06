# PYTHON script
# -*- coding: utf-8 -*-

'''
decomposeInp
============

decomposeInp script collects all model properties and sorts them into separate includes according to the submodel numbering range definitions.

.. note::
	
    Just property entities and their corresponding elements are moved into includes.

Location
--------

BMW>decomposeInp

Usage
-----

* input ABAQUS input file
* push the button

Requirements
------------

.. warning::
    
    No special requirements.
    
* designed for ANSA V.19.1.1

'''

#=========================== to be modified ===================================

BUTTON_NAME = 'decomposeInp'
BUTTON_GROUP_NAME = 'BMW'
DOCUMENTATON_GROUP = 'ANSA tools'
DOCUMENTATON_DESCRIPTION = 'ANSA button for ABAQUS *.inp file decomposition into includes.'

#==============================================================================

DEBUG = 0

#==============================================================================

import os
import sys
from traceback import format_exc

import ansa
from ansa import base, guitk, constants, utils

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ansa.ImportCode(os.path.join(PATH_SELF, 'domain', 'util.py'))

# import common funtionality
ansa.ImportCode(os.path.join(os.environ['ANSA_TOOLS'], 'bmwRenumber', 'default', 'bin' , 'domain', 'base_items.py'))

#==============================================================================

class UnknownPropertyException(Exception): pass

#==============================================================================

class InputFileDecomposer(object):

	APPLICATION_NAME = 'Input file decomposer'

	def __init__(self):
		
		self.decompodeInputFile()
		
	#--------------------------------------------------------------------------

	def decompodeInputFile(self):
		
		props = base.CollectEntities(constants.ABAQUS, None, "__PROPERTIES__")
		
		numberingDefinition = base_items.NumberingConventionIo.getData()
		
		utils.MainProgressBarSetVisible(True)
		
		subModelName = ''
		subModelProps = list()
		currentNumeringIndex = 0
		rangeMin = 0
		rangeMax = 0
		allProps = sorted(props, key=lambda p: p._id)
		for prop in allProps:
						
			if rangeMin <= prop._id <= rangeMax:
				subModelProps.append(prop)
			else:
				if len(subModelProps) > 0:
					
					utils.MainProgressBarSetValue(int(100*allProps.index(prop)/len(allProps)))
					
	#				print(subModelName, len(subModelProps), subModelProps[0].ansa_type(constants.ABAQUS), rangeMin, rangeMax)#, subModelProps)
					
					includeEntity = self._getExistingEntity(subModelName, 'INCLUDE')
					if includeEntity is None:
						includeEntity = base.CreateEntity(constants.ABAQUS, 'INCLUDE', {'Name' : subModelName})
						base.SetEntityId(includeEntity, rangeMin)
					
					base.AddToInclude(includeEntity, subModelProps)
					elems = base.CollectEntities(constants.ABAQUS, subModelProps, "__ELEMENTS__")
					base.AddToInclude(includeEntity, elems)
					
				
				subModelProps = [prop]
				try:
					subModelName, currentNumeringIndex, rangeMin, rangeMax = self._findSubsystemDefinition(
						numberingDefinition[currentNumeringIndex:], prop)				
				except UnknownPropertyException as e:
					subModelProps.remove(prop)
	#				print(str(e))
					continue
		
		utils.MainProgressBarSetValue(100)
		utils.MainProgressBarSetVisible(False)
	
	#--------------------------------------------------------------------------

	def _findSubsystemDefinition(self, numberingDefinition, prop):
		
		for rNo, records in enumerate(numberingDefinition):
			try:
				if int(records[8]) <= prop._id <= int(records[9]):				
					return records[0], rNo, int(records[8]), int(records[9])
			except ValueError as e:
	#			print(str(e), prop.ansa_type(constants.ABAQUS), prop._id, prop._name)
				continue
		
		raise UnknownPropertyException('Property not identified: %s - %i: %s' % (prop.ansa_type(constants.ABAQUS), prop._id, prop._name))
		
	#--------------------------------------------------------------------------

	def _getExistingEntity(self, entityName, entityType):
		
		match = base.NameToEnts(entityName, constants.ABAQUS, constants.ENM_EXACT)
		
		if match is None:
			return None
			
		for entity in match:
			if entity.ansa_type(constants.ABAQUS) == entityType:
				return entity
		
		return None
		
# ==============================================================================

def showCriticalMessage(message):

	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxCritical, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)

# ==============================================================================

def showInfoMessage(message):

	messageWindow = guitk.BCMessageWindowCreate(guitk.constants.BCMessageBoxInformation, message, True)
	guitk.BCMessageWindowSetRejectButtonVisible(messageWindow, False)
	guitk.BCMessageWindowExecute(messageWindow)
	
#==============================================================================
@ansa.session.defbutton(BUTTON_GROUP_NAME, BUTTON_NAME, __doc__)
def main():

	main.__doc__ = __doc__

	try:
		project = InputFileDecomposer()
	except Exception as e:
		print(format_exc())
		showCriticalMessage(str(e))

#==============================================================================

if __name__ == '__main__' and DEBUG:
	main()
