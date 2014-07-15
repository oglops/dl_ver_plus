#!/usr/bin/env python2
# coding: utf8
import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt, QString, pyqtSignal, pyqtSlot
from PyQt4.QtCore import SIGNAL
import base64
import re

import dlp.constants as constants
from dlp.core import DeadlineRepo
import dlp.core

__version__ = '0.1'

DEBUG = False


class VerWidget(QtGui.QWidget):

    def __init__(self, plugin=None, args=None, repo=None, parent=None):
        super(VerWidget, self).__init__(parent)
        self.ui = uic.loadUi(r'verWidget.ui', self)
        self.eachRow = 5
        self.ui.groupBox.setTitle(plugin)
        self.plugin = plugin
        self.repo = repo

    def contextMenuEvent(self, event):
        'actions for the context menus'
        menu = QtGui.QMenu(self)
        apply_versions_action = menu.addAction(
            "Apply Settings for %s" % self.plugin)
        add_version_action = menu.addAction("Add Custom Version")
        menu.addSeparator()
        reload_action = menu.addAction("Reload")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == apply_versions_action:
            versions = self.get_versions()
            print versions
            self.apply_versions(versions)

        # add the version specified in slider to the checkboxes area
        elif action == add_version_action:
            self.add_custom_version()

        # reload itself
        elif action == reload_action:
            import subprocess
            QtGui.qApp.quit()
            subprocess.Popen(['python', __file__, self.repo.root])

    def apply_versions(self, versions):
        self.repo.plugins[self.plugin].dlinitFile.setVersions(versions)
        self.repo.plugins[self.plugin].paramFile.setVersions(versions)
        self.repo.plugins[self.plugiprn].submissionFile.setVersions(versions)

    def get_versions(self):
        versions = dict()
        # a widget is the child of parent widget, not the child of 'parent layout'
        # for checkbox in self.ui.gridLayout.children():
        for i in range(self.ui.gridLayout.count()):
            checkbox = self.ui.gridLayout.itemAt(i).widget()

            ver = str(checkbox.text())
            checked = True if checkbox.checkState() == Qt.Checked else False
            versions[ver] = checked
        return versions

    def add_custom_version(self):
        custom_version = self.get_current_verion()
        if '.' not in self.versions[-1]:
            custom_version = int(custom_version)

        custom_version = str(custom_version)
        if custom_version not in self.versions:
            self.versions.append(custom_version)
            checkbox = QtGui.QCheckBox(custom_version)
            checkbox.setCheckState(Qt.Checked)
            checkbox.setStyleSheet(" background-color: #99CC99 ")
            self.ui.gridLayout.addWidget(checkbox)
            print 'Added a new version', custom_version

    def get_current_verion(self):

        return self.ui.doubleSpinBox.value()

    def add_versions(self, versions):
        'add checkboxes based on versions list'
        self.versions = versions
        c = r = 0
        for ver in versions:
            checkBox = QtGui.QCheckBox(ver)
            if ver in self.versions_need_check:
                checkBox.setCheckState(Qt.Checked)
            self.ui.gridLayout.addWidget(checkBox, r, c)
            c += 1
            if c == self.eachRow:
                c = 0
                r += 1
        self.setup_slider()

    def get_last_ver(self):
        'get last version from new versions defined in constants'
        last_ver = None
        new_versions = constants.NEW_VERSIONS.get(self.plugin)
        if new_versions:
            if not isinstance(new_versions, list):
                new_versions = list(new_versions)
            last_ver = new_versions[-1]

        self.last_ver = last_ver

        return str(last_ver)

    def setup_slider(self):
        'set up slider and spinbox'
        isFloat = False

        lastVer = self.get_last_ver()
        if '.' in lastVer:
            isFloat = True

        if isFloat:
            self.doubleSpinBox.setDecimals(1)
        else:
            self.doubleSpinBox.setDecimals(0)

        # get step value from existing version for spinbox
        self.interval = self.get_interval()
        self.doubleSpinBox.setSingleStep(self.interval)

        self.min_ver = float(lastVer) + self.interval
        self.max_ver = float(lastVer) + 10
        self.doubleSpinBox.setRange(0, 9999)

        self.horizontalSlider.valueChanged.connect(self.handle_slider)

        self.doubleSpinBox.valueChanged.connect(self.handle_spinbox)

        default_value = float(self.versions[-1]) + self.interval
        self.doubleSpinBox.setValue(default_value)

    def get_interval(self):
        'get step value from existing version'
        interval = 1

        for ver in self.versions_need_check:
            ver_str = str(ver)
            if '.' in ver_str:
                interval = 1.0

            if '.1' in ver_str:
                interval = 0.1
                break
            if '.5' in ver_str:
                interval = 0.5
                break

        return interval

    def handle_slider(self, val):

        newVal = self.min_ver + val / 100.0 * (self.max_ver - self.min_ver)
        if self.interval == 1:

            newVal = self.round_to_1(newVal)
        elif self.interval == 0.5:
            newVal = self.round_to_05(newVal)
        elif self.interval == 0.1:
            newVal = self.round_to_01(newVal)

        if DEBUG:
            print "handle_slider: %d -> %0.2f" % (val, newVal)
        self.doubleSpinBox.setValue(newVal)

    def handle_spinbox(self, val):

        newVal = float(val)
        newVal = (val - self.min_ver) / (self.max_ver - self.min_ver) * 100

        newVal = self.round_to_1(newVal)
        if DEBUG:
            print "handle_spinbox: %d -> %0.2f" % (val, newVal)

        # if user is not dragging , then set value , or slider will be
        # jittering
        if not QtGui.qApp.mouseButtons() == Qt.LeftButton:
            self.horizontalSlider.setValue(newVal)

        # if new value is bigger than slider max value, then we need to set it
        # on slider
        if val > self.max_ver:
            if DEBUG:
                print 'val', val, 'max_ver', self.max_ver
            self.max_ver = val

        elif val < self.min_ver:
            self.min_ver = val

    def round_to(self, n, precission):
        correction = 0.5 if n >= 0 else -0.5
        return int(n / precission + correction) * precission

    def round_to_05(self, n):
        return self.round_to(n, 0.5)

    def round_to_01(self, n):
        return self.round_to(n, 0.1)

    def round_to_1(self, n):
        return self.round_to(n, 1)


class ClickableLabel(QtGui.QLabel):

    'Define a clickable QLabel using new style signal/slot'
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(ClickableLabel, self).__init__(parent)
        self.clicked.connect(self.openBrowser)

    def mouseReleaseEvent(self, event):
        'emit clicked signal'
        self.clicked.emit()

    def openBrowser(self):
        'open blog in web browser'
        import webbrowser
        webbrowser.open('https://ilmvfx.wordpress.com/')


class VerPlusUI(QtGui.QDialog):

    'The main ui'

    def __init__(self, args=None, parent=None):
        super(VerPlusUI, self).__init__(parent)
        self.ui = uic.loadUi('dp_ver++.ui', self)
        self.setWindowTitle(
            u'ver++ %s for deadline 5.2.49424 by biubiubiu 大' % __version__)

        # make a clickable QLabel
        self.aboutLayout = QtGui.QVBoxLayout(self.ui.aboutTab)
        aboutLabel = ClickableLabel()
        self.aboutLayout.addWidget(aboutLabel)

        # you can do the following to embed base64 encoded image, but then text is gone
        # pm = QtGui.QPixmap()
        # pm.loadFromData(base64.b64decode(constants.B64_DATA))
        # aboutLabel.setPixmap(pm)

        html = u'''
        <p>lz使用了regex(脑残法)来搜索替换已有的plugin的配置文件们(.dlinit / .param / 和submission目录下的.py文件) 这么做没有任何意义，你手改下不就得了，这纯粹是吃饱了撑的，所以lz只做了6,7个plugin的</p>
        <p>启动时先使用单独做的dlp package去找到所有的plugins们的版本号，然后显示在界面上，此时可以勾选/取消显示的版本们，滑条默认最大到最后一个版本+10，但是spinbox输入框没有限制，可以随便设),右键菜单可以写设置到配置文件里</p>
        <p>点猫头开blog有详细介绍lz的脑抽过程</p><br/>
        <img alt="" src="data:image/jpeg;base64,%s" />

        ''' % constants.B64_DATA

        aboutLabel.setText(html)
        aboutLabel.setAlignment(Qt.AlignTop)

        # enlarge chinese description font
        font = aboutLabel.font()
        font.setPointSize(9)
        aboutLabel.setFont(font)

        # enable word wrap
        aboutLabel.setWordWrap(True)
        self.ui.tabWidget.setCurrentIndex(0)

        if len(sys.argv) >= 2:
            self.root = sys.argv[1]
        else:
            # self.root = dlp.core.get_default_repo()
            self.root = re.search('^.*(?=scripts)',__file__).group()[:-1]
        self.populate_ver_widgets()

        # set repo dir on the repoDirLE lineEdit
        self.ui.browseBtn.clicked.connect(self.browse_repo)
        # self.ui.browseBtn.setAutoDefault(False)
        self.ui.repoDirLE.setEnabled(False)
        self.ui.repoDirLE.setText(self.repo.root)
        self.ui.repoDirLE.returnPressed.connect(self.set_repo)


        if DEBUG:
            self.ui.browseBtn.setContextMenuPolicy(Qt.CustomContextMenu)
            # self.connect(self.ui.browseBtn, SIGNAL('customContextMenuRequested(const QPoint&)'), self._debug_context_menu)
            self.ui.browseBtn.customContextMenuRequested.connect(self._debug_context_menu)
        self.ui.show()

    def browse_repo(self):
        default_repo = dlp.core.get_default_repo()
        root = QtGui.QFileDialog.getExistingDirectory(
            self, 'Select Repo Directory', default_repo)
        if root:
            self.root = str(root)
            self.ui.repoDirLE.setText(self.root)

            # if root is valid
            self._debug_reload_plugins()

    def set_repo(self):
        self.root = str(self.ui.repoDirLE.text())
        # self._debug_reload_plugins()

    def populate_ver_widgets(self):
               # repo = DeadlineRepo(root=r'c:\DeadlineRepository')
        self.repo = DeadlineRepo(self.root)
        if not self.repo.is_repo_valid():
            print 'This Repo is not valid'
            return

        self.repo.getPlugins()

        # create a vertial layout to hold all the verWidget widgets
        # self.ui.verWidgetLayout = QtGui.QVBoxLayout(
        #     self.ui.scrollAreaWidgetContents)

        for plugin in self.repo.supportedPlugins:
            verWidget = VerWidget(plugin, repo=self.repo)

            # get all versions currently available for this plugin
            versions = self.repo.plugins[plugin].dlinitFile.versions

            versions_need_check = versions
            # get new versions defined in constants
            new_ver_range = constants.NEW_VERSIONS.get(plugin)

            if new_ver_range:
                versions = versions + [str(v) for v in new_ver_range]
                versions = list(set(versions))
                versions.sort(key=lambda x: float(x))

            verWidget.versions_need_check = versions_need_check
            # add checkboxes to verWidget
            verWidget.add_versions(versions)
            self.ui.verWidgetLayout.addWidget(verWidget)

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                      tip=None, checkable=False, signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    @pyqtSlot(QtCore.QPoint)
    def _debug_context_menu(self, point):
        self.popMenu = QtGui.QMenu(self)
        self.popMenu.addAction(self.create_action('Delete All Plugins', self._debug_del_plugins))
        self.popMenu.addAction(self.create_action('Reload All Plugins', self._debug_reload_plugins))
        self.popMenu.addSeparator()
        self.popMenu.exec_(self.ui.browseBtn.mapToGlobal(point))

    def _debug_del_plugins(self):
        for child in self.ui.scrollAreaWidgetContents.children():
            if isinstance(child, VerWidget):
                child.deleteLater()

    def _debug_reload_plugins(self):
        self._debug_del_plugins()
        self.populate_ver_widgets()


def run():
    app = QtGui.QApplication(sys.argv)
    app.setStyle('cleanlooks')
    gui = VerPlusUI(sys.argv)
    gui.show()
    app.exec_()

if __name__ == '__main__':
    run()
