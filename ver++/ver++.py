# coding=utf-8

from System.Collections.Specialized import *
from System.Drawing import *
from System.IO import *
from System.Diagnostics import *
from Deadline.Scripting import *

import re
import json

########################################################################
## Globals
########################################################################
script_dialog = None
settings = None
mayaVerDict = None

########################################################################
## Main Function Called By Deadline
########################################################################
def __main__():
	global script_dialog
	global settings
	
	

	dialogWidth = 500
	dialogHeight = 654
	# dialogHeight = 600 + 16
	labelWidth = 100
	tabHeight = 600
	
	script_dialog = DeadlineScriptEngine.GetScriptDialog()
	script_dialog.ShowGroupBoxMenu()

	# ClientUtils.LogText(','.join(dir(ProcessUtils)))
	# ProcessUtils.ShellExecute(r'D:\Dropbox\pyqt_learn\boxUI\tree_button.pyw')
	# ClientUtils.ExecuteScript(r'D:\Dropbox\pyqt_learn\boxUI\tree_button.py')
	# ProcessUtils.SpawnProcess(r'D:\Dropbox\pyqt_learn\boxUI\tree_button.pyw',r'',r'c:',ProcessWindowStyle.Hidden,False)
	# ProcessUtils.SpawnProcess(r'D:\Dropbox\pyqt_learn\boxUI\tree_button.pyw',r'')
	# import sys
	# sys.exit()

	script_dialog.SetSize( dialogWidth+24, dialogHeight )
	script_dialog.SetTitle( "ver++ 0.1 by biubiubiu大" )
	script_dialog.SetIcon( Path.Combine( GetRootDirectory(), "scripts/General/ver++/ver++.ico" ) )
	
	script_dialog.AddTabControl("Example Tab Control", dialogWidth+16, tabHeight)
	
	script_dialog.AddTabPage("Fucker")
	script_dialog.AddControl( "Separator1", "SeparatorControl", "Version up your software !", dialogWidth - 16, -1 )

	allMayaBatchVersions= getPluginsVersions()
	script_dialog.AddGroupBox( "GroupBox2", "Maya ver++", True )

	script_dialog.AddRow()
 
	verDict={}
	global mayaVerDict

	import sys
	sys.path.append(r'C:\DeadlineRepository\scripts\General\ver++')
	# sys.path.append(r'C:\Python27\Lib\site-packages')
	# from DLP.core import DeadlineRepo
	# repo = DeadlineRepo(GetRootDirectory())
	# ClientUtils.LogText(','.join(repo.supportedPlugins))

	# import ordereddict

	for i,v  in enumerate([7.0,8.0] + range(2008,2018)):
		# script_dialog.AddSelectionControl( "CheckBox_maya"+str(i), "CheckBoxControl", False, str(i), 50 , -1)
		verStr = str(v).replace('.','_')
		if '_' not in verStr:
			verStr = '%s_0' % verStr

		check = 'True' if verStr in allMayaBatchVersions else 'False'
		verDict[verStr]=eval(check)
		checkBoxName = 'CheckBox_MayaBatch_'+verStr
		cmd='script_dialog.AddSelectionControl("'+checkBoxName+'" , "CheckBoxControl", '+ check+', str(v), 50 , -1)'
		ClientUtils.LogText(cmd)
		checkBoxObj=eval(cmd)

		def updateMayaSettings(checkBoxName,checkBoxObj):
			ClientUtils.LogText(checkBoxName + ' -> '+ str(checkBoxObj))
			key = checkBoxName.replace("CheckBox_MayaBatch_","")
			ClientUtils.LogText(key + ' -> '+ str(script_dialog.GetValue(checkBoxName)))
			mayaVerDict[key]=script_dialog.GetValue(checkBoxName)

		checkBoxObj.ValueModified += lambda _,checkBoxName=checkBoxName,checkBoxObj=checkBoxObj:updateMayaSettings(checkBoxName,checkBoxObj)

		if (i+1) % 8 ==0:
			script_dialog.EndRow()
			script_dialog.AddRow()

	script_dialog.EndRow()

	script_dialog.AddRow()
	script_dialog.AddControl( "mayaVerRangeLabel", "LabelControl", "Add a new Verson", labelWidth, -1 )
	script_dialog.AddRangeControl( "mayaVerSliderBox", "SliderControl", 2018, 2018, 2023, 0, 1, dialogWidth - labelWidth - 24 -100, -1 )
	mayaVerAddBtn = script_dialog.AddControl( "mayaVerAddBtn", "ButtonControl", "Add",40,-1)
	mayaVerRemoveBtn = script_dialog.AddControl( "mayaVerRemoveBtn", "ButtonControl", "Del",40,-1)

	def updateMayaVer(mode,verRangeControl):
		newVer=script_dialog.GetValue(verRangeControl)
		newVer = '%s_0'% str(newVer)
		mode = True if mode else False
		mayaVerDict[newVer]=mode
		
		ClientUtils.LogText(json.dumps(mayaVerDict))

	mayaVerAddBtn.ValueModified += lambda _,verRangeControl='mayaVerSliderBox':updateMayaVer(1,verRangeControl)
	mayaVerRemoveBtn.ValueModified += lambda _,verRangeControl='mayaVerSliderBox':updateMayaVer(0,verRangeControl)

	script_dialog.EndRow()
	mayaVerApplyBtn = script_dialog.AddControl( "mayaVerApplyBtn", "ButtonControl", "Apply",80,-1 )
	mayaVerApplyBtn.ValueModified += setMayaPluginsVersions

	# setattr(mayaVerApplyBtn,'x',"9527")

	# mayaVerApplyBtn.ValueModified += test

	mayaVerDict = verDict

	script_dialog.EndGroupBox( False )

	script_dialog.AddGroupBox( "GroupBox3", "Max ver++", True )
	script_dialog.EndGroupBox( False )
	
	script_dialog.EndTabPage()
	
	script_dialog.AddTabPage("About This Shit")
	script_dialog.AddControl( "Separator3", "SeparatorControl", "Seriously ?!!", dialogWidth - 16, -1 )
	script_dialog.AddRow()
	script_dialog.AddControl( "MultiLineTextLabel", "LabelControl", "Multi Line", labelWidth, -1 )
	script_dialog.AddControl( "MultiLineTextBox", "MultilineTextControl", "环球数码整个就一大傻B\r\n不同意的举手", dialogWidth - labelWidth - 24, 100 )
	script_dialog.EndRow()
	script_dialog.EndTabPage()
	script_dialog.EndTabControl()
	
	script_dialog.AddRow()
	script_dialog.AddControl( "DummyLabel1", "LabelControl", "", dialogWidth - 232, -1 )
	popupButton = script_dialog.AddControl( "PopupButton", "ButtonControl", "Restart", 100, -1 )
	popupButton.ValueModified += PopupButtonPressed
	closeButton = script_dialog.AddControl( "CloseButton", "ButtonControl", "Close", 100, -1 )
	closeButton.ValueModified += CloseButtonPressed
	script_dialog.EndRow()

	script_dialog.ShowDialog( False )

########################################################################
## Helper Functions
########################################################################
def ProgressButtonPressed( *args ):
	global script_dialog
	
	currentProgress = script_dialog.GetValue( "ProgressBox" )
	currentProgress = currentProgress + 5
	if currentProgress > 100:
		currentProgress = 1
	script_dialog.SetValue( "ProgressBox", currentProgress )

def CloseButtonPressed( *args ):
	global script_dialog
	script_dialog.CloseDialog()

def PopupButtonPressed( *args ):
	global script_dialog
	# script_dialog.ShowMessageBox( "This is a popup!", "Popup" )
	# script_dialog.CloseDialog()
	# ExecuteScript(__file__,'')
	ExecuteScript(Path.Combine( GetRootDirectory(), "scripts/General/ver++/ver++.py" ),'')
	script_dialog.CloseDialog()
	
def mayaPlusButtonPressed (*args):
	global script_dialog
	
	currentProgress = script_dialog.GetValue( "ProgressBox" )

def getPluginsVersions(*args):
	global script_dialog

	pluginsDir = GetPluginsDirectory()
	mayaBatchPluginsDir = Path.Combine(pluginsDir,'MayaBatch')
	ClientUtils.LogText('CRAP!!! ' +mayaBatchPluginsDir)

	initFile = Path.Combine(mayaBatchPluginsDir,'MayaBatch.dlinit')
	import os
	if os.path.isfile(initFile):
		ClientUtils.LogText(initFile+' exists')
	else:
		ClientUtils.LogText(initFile+' not exists')

	allVersions=[]
	with open(initFile) as f:
		# for line in f:
			# ClientUtils.LogText(line)
		initFileContent = f.read()
		ClientUtils.LogText(initFileContent)
		allVersions = re.findall('(?<=\nRenderExecutable)(\d+_\d)',initFileContent)
		ClientUtils.LogText(','.join(allVersions))

	return allVersions

def setMayaPluginsVersions(*args):
	global script_dialog
	pluginsDir = GetPluginsDirectory()
	mayaBatchPluginsDir = Path.Combine(pluginsDir,'MayaBatch')
	initFile = Path.Combine(mayaBatchPluginsDir,'MayaBatch.dlinit')

	ClientUtils.LogText(str(len(args)))

	global mayaVerDict
	import json
	ClientUtils.LogText(json.dumps(mayaVerDict))

	initFileContent= ''
	with open(initFile) as f:
		initFileContent = f.read()
		for v,enabled in mayaVerDict.items():
			exists = re.search('\nRenderExecutable'+v,initFileContent)
			if enabled:
				if exists:
					pass
				else:
					# Add
					verInt=v.replace('_','.')
					newConfig = r'RenderExecutable%s=C:\Program Files\Alias\Maya%s\bin\Render.exe;C:\Program Files (x86)\Alias\Maya%s\bin\Render.exe' % (v,verInt,verInt) +'\n'
					initFileContent+=newConfig
					
					pass

			else:
				if exists:
					ClientUtils.LogText('RenderExecutable'+v+'.*\n')
					initFileContent = re.sub('RenderExecutable'+v+'.*','',initFileContent)
					# delete
				else:
					pass

	# with open(r'E:\DeadlineRepository\plugins\MayaBatch\MayaBatch_test.dlinit','w') as f:
	with open(initFile,'w') as f:
		f.write(initFileContent)

def test(*args):
	ClientUtils.LogText(str(len(args)))
	ClientUtils.LogText(str(args[0]))
	ClientUtils.LogText(','.join(dir(args[0])))