#!/usr/bin/env python

import os
import sys
import re
import configparser

import constants
import utils

DEBUG = False


def get_default_repo():
    if sys.platform.startswith('linux'):
        default_repo = os.path.expandvars(
            '$HOME/Dropbox/pyqt_learn/DeadlineRepository/')
    else:
        default_repo = r'c:\DeadlineRepository'
    return default_repo


class DeadlineRepo(object):

    def __init__(self, root=get_default_repo()):
        super(DeadlineRepo, self).__init__()
        self.root = root
        self.pluginDir = os.path.join(root, 'plugins')
        self.scriptDir = os.path.join(root, 'scripts', 'Submission')
        self.plugins = {}

        self.supportedPlugins = sorted(constants.SUPPORTED_PLUGINS)

    def is_repo_valid(self):
        if os.path.isdir(self.pluginDir) and os.path.isdir(self.scriptDir):
            return True
        else:
            return False

    def getPlugins(self):
        'should return a list of plugins objects currently in the plugins folder'
        if DEBUG:
            print 'pluginDir', self.pluginDir
        pluginsDirs = os.listdir(self.pluginDir)

        for plugin in pluginsDirs:
            if plugin in self.supportedPlugins:
                if DEBUG:
                    print 'init plugin', plugin
                self.plugins[plugin] = DeadlinePlugins(plugin, self.root)


class DeadlinePlugins(DeadlineRepo):

    def __init__(self, name, root):
        super(DeadlinePlugins, self).__init__(root)
        self.pluginName = name  # re.search('[^/\\]*$',root)
        self.root = root
        self.dlinitFileName = os.path.join(
            self.root, 'plugins', name, '%s.dlinit' % name)
        self.paramFileName = os.path.join(
            self.root, 'plugins', name, '%s.param' % name)

        submissionName = constants.SUBMISSION_FILE_MAP.get(
            self.pluginName, self.pluginName)

        self.submissionFileName = os.path.join(
            self.root, 'scripts', 'Submission', '%sSubmission' % submissionName, '%sSubmission.py' % submissionName)
        self.submissionName = submissionName
        # print 'submisson_file',self.submissionFileName

        self.dlinitFile = DeadlineInitFile(self.dlinitFileName)
        self.paramFile = DeadlineParamFile(self.paramFileName)
        self.submissionFile = DeadlineSubmissionFile(self.submissionFileName)

        # print self.pluginName , ' --- ' ,self.dlinitFile

    def getDlinitFile(self):
        return self.dlinitFile


class DeadlineParamFile(DeadlinePlugins):

    'class representing .param file'

    def __init__(self, name):
        self.name = name
        self.content = None
        try:
            self.content = open(name).read()
        except:
            self.content = None
            if DEBUG:
                print 'param file read failed'
        self.pluginName = re.search(r'[^\\/]*(?=\.param)', name).group()
        self.versions = self.getVersions()

    def getVersions(self):
        'return all currently added versions'
        cp = configparser.ConfigParser(allow_no_value=True)

        regex = constants.PARAM_GETVERSIONS_REGEX.get(self.pluginName)
        versions = None
        if regex:
            if self.content:
                cp.read_string(unicode(self.content))
                versions = [x for x in cp.keys()[1:] if re.search(regex, x)]
                versions = [
                    re.search(regex, x).group().replace('_', '.') for x in versions]
                versions = [str(x) for x in versions]

        return versions

    def getVersionConfig(self, ver):
        'given a version such as 2008, get the config lines for this version'
        regex = constants.PARAM_GETVERSIONCONFIG_REGEX.get(self.pluginName)
        config = None
        if regex:
            regex = regex.format(
                verStr=str(ver).replace('.', '_'), ver=str(ver))
            try:
                config = re.search(regex, self.content).group()
            except:
                pass

        return config

    def setVersions(self, verDict):
        '''verDict is a dict like {'7.0':False ...}'''
        for v, enabled in verDict.items():
            exists = v in self.versions

            if enabled:
                if not exists:
                    verStr = v.replace('.', '_')
                    verPath = v.replace('.', '')
                    verDescription = re.search('^\d*[^\.0]', v).group()
                    vendor = 'Alias' if float(v) <= 8.0 else 'Autodesk'
                    vendorLower = vendor.lower()
                    verMajor = v
                    verMinor = '1'
                    if '.' in v:
                        verMajor, xxx = v.split('.')[:2]

                    newConfig = constants.PARAM_RENDERERPATH[self.pluginName].format(
                        verStr=verStr, ver=v, verDescription=verDescription, verPath=verPath, verMinor=verMinor, verMajor=verMajor, vendor=vendor, index=-1, vendorLower=vendorLower)

                    self.insertConfig(v, newConfig)
            else:
                if exists:

                    delContent = self.getVersionConfig(v)
                    newContent = self.content.replace(delContent + '\n\n', '')

                    with open(self.name, 'w') as f:
                        f.write(newContent)
                        self.content = newContent

            self.updateIndex()
            self.__init__(self.name)

    def insertConfig(self, ver, insertStr):
        'ver is a string "7.0", insert version 2008 into config file, it needs to be inserted between 2007 and 2009 '
        # first find where the new ver should be inserted in the
        # self.versions list
        versionArray = [float(v) for v in self.versions]
        print 'checking', versionArray, 'ver', ver
        index, s = 0, None
        for index, s in enumerate(versionArray):
            if DEBUG:
                print 'checking index,', index, s
            if s > float(ver):
                # index += 1
                break
        else:
            index += 1
        if DEBUG:
            print 'index,s', index, s

        index = max(0, index - 1)
        insertAfterVer = versionArray[index]
        if DEBUG:
            print 'insert after ver:', insertAfterVer

        with open(self.name, 'r') as f:
            lines = f.read()

        if '.' not in ver:
            insertAfterVer = re.search(
                '^\d*[^\.]', str(insertAfterVer)).group()
        if DEBUG:
            print 'insertAfterVer', insertAfterVer

        insertAfterLine = self.getVersionConfig(insertAfterVer)

        # cp = configparser.ConfigParser(allow_no_value=True)
        # cp.optionxform = str
        # cp.read_string(unicode(insertAfterLine))
        if DEBUG:
            print '=' * 50
            print 'insertAfterLine', insertAfterLine, insertAfterVer

        indexAttr = self.getIndexAttr(insertAfterLine)

        # indexVal = re.search('(?<=Index\=).*', insertAfterLine).group()
        indexVal = re.search(
            '(?<=%s\=).*' % indexAttr, insertAfterLine).group()
        indexVal = str(int(indexVal) + 1)
        insertStr = re.sub('(?<=%s\=).*' % indexAttr, indexVal, insertStr)

        newContent = lines.replace(
            insertAfterLine, insertAfterLine + '\n\n' + insertStr)

        with open(self.name, 'w') as f:
            f.write(newContent)

    def getIndexAttr(self, section):

        if DEBUG:
            print 'section', section
        indexAttr = None
        if section:
            if isinstance(section, configparser.SectionProxy):
                allKeys = section.keys()
            else:
                cp = configparser.ConfigParser(allow_no_value=True)
                cp.optionxform = str
                cp.read_string(unicode(section))
                allKeys = cp[cp.keys()[-1]].keys()

            if 'Index' in allKeys:
                indexAttr = 'Index'
            elif 'CategoryIndex' in allKeys:
                indexAttr = 'CategoryIndex'

        return indexAttr

    def updateIndex(self):
        'update index after inserting'
        cp = configparser.ConfigParser(allow_no_value=True)
        cp.optionxform = str

        # reload self.content
        self.__init__(self.name)

        if self.content:
            cp.read_string(unicode(self.content))
            regex = constants.PARAM_GETVERSIONS_REGEX.get(self.pluginName)
            print 'in updateIndex', regex
            if regex:
                checkKeys = [x for x in cp.keys() if re.search(regex, x)]
                if DEBUG:
                    print '-' * 50
                    print 'checkKeys', checkKeys

                indexKey = self.getIndexAttr(cp[checkKeys[-1]])
                for i, k in enumerate(checkKeys):
                    if str(i) != cp[k][indexKey]:
                        cp[k][indexKey] = str(i)

                with open(self.name, 'w') as f:
                    cp.write(f, space_around_delimiters=False)

            else:
                return False


class DeadlineInitFile(DeadlinePlugins):

    'class representing .dlinit file'

    def __init__(self, name):
        # super(DeadlineInitFile, self).__init__()
        self.name = name
        try:
            self.content = open(name).read()
        except:
            if DEBUG:
                print 'init file read failed'

        self.pluginName = re.search(r'[^\\/]*(?=\.dlinit)', name).group()

        self.versions = self.getVersions()

    def getVersions(self):
        'return all currently added versions'
        regex = constants.DLINIT_GETVERSIONS_REGEX.get(self.pluginName)
        if regex:
            allVersions = re.findall(regex, self.content)
            versions = [x.replace('_', '.') for x in allVersions]
        else:
            versions = None

        return versions

    def setVersions(self, verDict):
        '''verDict is a dict like {'7.0':False ...}'''
        for v, enabled in verDict.items():

            if DEBUG:
                print 'check exists', v, self.versions
            exists = v in self.versions

            if enabled:
                if not exists:
                    if '.' in v:
                        verStr = v.replace('.', '_')
                    else:
                        verStr = v

                    verMinor = '1'
                    verPath = v.replace('.', '')
                    newConfig = constants.DLINIT_RENDERERPATH[self.pluginName].format(
                        verStr=verStr, ver=v, verMinor=verMinor, verPath=verPath) + '\n'

                    print newConfig
                    # instead of appedning the new line to the end of the file, i want to insert it to the
                    # appropirate location of the file
                    # newContent += newConfig
                    self.insertConfig(v, newConfig)
            else:
                if exists:
                    delRegex = constants.DLINIT_GETVERSIONCONFIG_REGEX[
                        self.pluginName] % v
                    newContent = re.sub(delRegex, '', self.content)
                    print 'del ver:', delRegex

                    with open(self.name, 'w') as f:
                        f.write(newContent)
                        self.content = newContent

    def getVersionConfig(self, ver):
        'given a version such as 2008, get the config lines for this version'
        regex = constants.DLINIT_GETVERSIONCONFIG_REGEX.get(self.pluginName)
        config = None
        if regex:
            regex = regex % str(ver).replace('.', '_')
            try:
                config = re.search(regex, self.content).group()
            except:
                pass

        return config

    def insertConfig(self, ver, insertStr):
        'ver is a string "7.0", insert version 2008 into config file, it needs to be inserted between 2007 and 2009 '
        # first find where the new ver should be inserted in the self.versions
        # list
        versionArray = [float(v) for v in self.versions]
        print self.versions, versionArray
        index, s = 0, None
        for index, s in enumerate(versionArray):
            print 'checking index,', index
            if s > float(ver):
                # index += 1
                break
        else:
            index += 1

        print 'index,s', index, s

        index = max(0, index - 1)
        # we should insert after this
        insertAfterVer = versionArray[index]

        # for vue, ver should be  int
        if '.' not in ver:
            insertAfterVer = re.search(
                '^\d*[^\.]', str(insertAfterVer)).group()

        if DEBUG:
            print 'insert after ver:', insertAfterVer

        # not sure if this is bad to duplicate the self.content string
        with open(self.name, 'r') as f:
            lines = f.readlines()

        insertAfterLine = self.getVersionConfig(insertAfterVer)

        if DEBUG:
            print 'insertAfterLine', insertAfterVer, insertAfterLine

        with open(self.name, 'w') as f:
            for i, line in enumerate(lines):
                f.write(line)
                if line == insertAfterLine:
                    f.write(insertStr)


class DeadlineSubmissionFile(DeadlinePlugins):

    'class representing submission file'

    def __init__(self, name):
        self.name = name
        try:
            # print 'reading submission file', self.name
            self.content = open(name).read()
        except:
            self.content = None
            if DEBUG:
                print 'submission file read failed'

        self.pluginName = re.search(r'[^\\/]*(?=\.py)', name).group()

        self.versions = self.getVersions()

    def getVersions(self):
        #scriptDialog.AddComboControl( "VersionBox", "ComboControl", "2012", ("7.0","8.0","8.5","2008","2009","2010","2011","2012","2013"), 120, -1 )
        # regex = constants.SUBMISSION_GETVERSIONS_REGEX.get(self.pluginName)
        # regex='scriptDialog.AddComboControl\( "VersionBox", "ComboControl", "[\d\.]*", \(("[\d\.]*"|,)*\)'
        # houdini
        # regex='scriptDialog.AddComboControl\("VersionBox","ComboControl","([\d\.]*)",\((("([\d\.]*)"|,)*)\)'

        regex_line = '\t*scriptDialog.AddComboControl\(\s*"VersionBox",\s*"ComboControl",\s*"([\d\.]*)",\s*\(("[\d\.]*"|,\s*)*\),\s*.*'
        versions = None
        if regex_line:

            if self.content:
                try:
                    versions_line = re.search(regex_line, self.content).group()
                    # print self.pluginName,'--->',versions_line
                    self.submission_versions_line = versions_line
                    # versions = re.search('"([\d\.]*)"',versions_line).groups()
                    versions = re.findall('"([\d\.]*)"', versions_line)
                    self.versions = versions
                except:
                    pass

        return versions

    def setVersions(self, versions):

        self.versions = self.getVersions()

        new_versions = '"%s", (%s)' % (
            versions[-1], ', '.join(['"%s"' % v for v in versions]))
        print new_versions
        new_submission_versions_line = re.sub(
            '(?<="ComboControl",)\s*.*.*\)(?=,)', new_versions, self.submission_versions_line)

        if DEBUG:
            print 'newline', new_submission_versions_line

        with open(self.name, 'w') as f:
            newContent = self.content.replace(
                self.submission_versions_line, new_submission_versions_line)
            f.write(newContent)
