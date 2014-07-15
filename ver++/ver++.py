# coding=utf-8

from System.Collections.Specialized import *
from System.Drawing import *
from System.IO import *
from System.Diagnostics import *
from Deadline.Scripting import *

import sys
import os
import platform
########################################################################
## Globals
########################################################################
script_dialog = None
settings = None

########################################################################
## Main Function Called By Deadline
########################################################################
def __main__():
	global script_dialog
	global settings
	
	ClientUtils.LogText(GetRootDirectory())
	ClientUtils.LogText(Path.Combine( GetRootDirectory(), r"scripts\General\ver++\dp_ver++.pyw"))
	
	script_path = r"scripts/General/ver++/dp_ver++.pyw"
	if platform.system()=='Windows':
		script_path = os.path.normpath(script_path)

	script_path = os.path.join(os.path.normpath(GetRootDirectory()),script_path)
	ClientUtils.LogText(script_path)
	script_path_root = os.path.dirname(script_path)
	os.chdir(script_path_root)
	ProcessUtils.ShellExecute(script_path)