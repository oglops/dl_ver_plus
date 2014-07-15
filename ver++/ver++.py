# coding=utf-8

from System.Collections.Specialized import *
from System.Drawing import *
from System.IO import *
from System.Diagnostics import *
from Deadline.Scripting import *


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
	
	ClientUtils.LogText(','.join(dir(ProcessUtils)))
	# ProcessUtils.ShellExecute(r'D:\Dropbox\pyqt_learn\boxUI\tree_button_1.pyw')
	# ClientUtils.ExecuteScript(r'D:\Dropbox\pyqt_learn\boxUI\tree_button.py')
	# ProcessUtils.SpawnProcess(r'D:\Dropbox\pyqt_learn\boxUI\tree_button.pyw',r'',r'c:',ProcessWindowStyle.Hidden,False)
	# ProcessUtils.SpawnProcess(r'D:\Dropbox\pyqt_learn\boxUI\tree_button.pyw',r'')

	ClientUtils.LogText('yeah === ')
	ClientUtils.LogText(GetRootDirectory())
	ClientUtils.LogText(Path.Combine( GetRootDirectory(), r"scripts\General\ver++\dp_ver++.pyw"))
	# ProcessUtils.SpawnProcess(Path.Combine( GetRootDirectory(), r"scripts\General\ver++\dp_ver++.pyw" ),r'')
	# ProcessUtils.ShellExecute(Path.Combine( GetRootDirectory(), r"scripts\General\ver++\dp_ver++.pyw" ))
	
	import sys
	sys.path.insert(0,r'\\oglop-fujitsu\DeadlineRepository\scripts\General\ver++')
	import os
	# os.chdir(r'c:\DeadlineRepository\scripts\General\ver++')
	os.chdir(r'\\oglop-fujitsu\DeadlineRepository\scripts\General\ver++')
	# import subprocess
	ClientUtils.LogText('yeah ===  after')
	# ProcessUtils.ShellExecute(r'\\oglop-fujitsu\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw')
	# ProcessUtils.SpawnProcess(r'\\oglop-fujitsu\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw',r'\\oglop-fujitsu\DeadlineRepository')
	
	# ProcessUtils.ShellExecute(r'c:\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw')
	# ProcessUtils.ShellExecute(r'D:\Dropbox\pyqt_learn\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw')

	# ProcessUtils.SpawnProcess(r'D:\Dropbox\pyqt_learn\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw',r'',r'c:',ProcessWindowStyle.Normal,False)

	# ProcessUtils.SpawnProcess(r'D:\Dropbox\pyqt_learn\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw')

	# ProcessUtils.ShellExecute(r'python \\oglop-fujitsu\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw')
	# ProcessUtils.ShellExecute(r'\\oglop-fujitsu\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw',r'\\oglop-fujitsu\DeadlineRepository')
	# try:
	# 	ProcessUtils.SpawnProcess(r'\\oglop-fujitsu\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw',r'xxx')

	# except Exception as e:
	# 	ClientUtils.LogText('error')
	# 	ClientUtils.LogText(str(e))

	ProcessUtils.ShellExecute(r'\\oglop-fujitsu\DeadlineRepository\scripts\General\ver++\dp_ver++.pyw')