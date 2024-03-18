#!/usr/bin/python3 -u

## Copyright (C) 2014 troubadour <trobador@riseup.net>
## Copyright (C) 2014 - 2023 ENCRYPTED SUPPORT LP <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

import sys
import signal

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5 import QtCore, QtGui, QtWidgets
from subprocess import call

import os
import yaml
import inspect
import pathlib

from guimessages.translations import _translations
from guimessages.guimessage import gui_message


def declined_legal():
    print('WARNING: legal not accepted.')

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Restricted Access")
    msg.setText("Because the agreements have been declined, you are prohibited from using this software.")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

    sys.exit(1)


class Common:
    '''
    Variables and constants used through all the classes
    '''
    translations_path ='/usr/share/translations/setup-wizard-dist.yaml'
    wizard_steps = []

    if os.path.isfile('/usr/share/anon-gw-base-files/gateway'):
        environment = 'gateway'
    elif os.path.isfile('/usr/share/anon-ws-base-files/workstation'):
        environment = 'workstation'
    else:
        environment = 'machine'

    if not os.path.exists('/var/cache/setup-dist/status-files'):
        pathlib.Path("/var/cache/setup-dist/status-files").mkdir(parents=True, exist_ok=True)

    show_disclaimer = (not os.path.exists('/var/cache/whonix-setup-wizard/status-files/disclaimer.done') and
                       not os.path.exists('/usr/share/whonix-setup-wizard/status-files/disclaimer.skip') and
                       not os.path.exists('/var/cache/setup-dist/status-files/disclaimer.done') and
                       not os.path.exists('/usr/share/setup-dist/status-files/disclaimer.skip')
                      )

    ## Disable disclaimer.
    show_disclaimer = False

    if(show_disclaimer):
        wizard_steps.append('disclaimer_1')
        wizard_steps.append('disclaimer_2')

    show_finish_page = (not os.path.exists('/var/cache/whonix-setup-wizard/status-files/finish_page.done') and
                       not os.path.exists('/usr/share/whonix-setup-wizard/status-files/finish_page.skip') and
                       not os.path.exists('/var/cache/setup-dist/status-files/finish_page.done') and
                       not os.path.exists('/usr/share/setup-dist/status-files/finish_page.skip') and
                       not os.path.exists('/usr/share/setup-dist/status-files/setup-dist.skip') and
                       not os.path.exists('/usr/share/setup-dist/status-files/setup-dist.done')
                       )

    if(show_finish_page):
        wizard_steps.append('finish_page')


class DisclaimerPage1(QtWidgets.QWizardPage):
    def __init__(self):
        super(DisclaimerPage1, self).__init__()

        self.steps = Common.wizard_steps

        self.text = QtWidgets.QTextBrowser(self)
        self.accept_group = QtWidgets.QGroupBox(self)
        self.yes_button = QtWidgets.QRadioButton(self.accept_group)
        self.no_button = QtWidgets.QRadioButton(self.accept_group)

        self.layout = QtWidgets.QVBoxLayout()

        self.setupUi()

    def setupUi(self):
        self.text.setFrameShape(QtWidgets.QFrame.Panel)
        self.text.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        self.accept_group.setMinimumSize(0, 60)
        self.yes_button.setGeometry(QtCore.QRect(30, 10, 300, 21))
        self.no_button.setGeometry(QtCore.QRect(30, 30, 300, 21))
        self.no_button.setChecked(True)

        self.layout.addWidget(self.text)
        self.layout.addWidget(self.accept_group)
        self.setLayout(self.layout)

    def nextId(self):
        if self.yes_button.isChecked():
            return self.steps.index('disclaimer_2')
        # Not understood
        elif self.no_button.isChecked():
            return self.steps.index('finish_page')


class DisclaimerPage2(QtWidgets.QWizardPage):
    def __init__(self):
        super(DisclaimerPage2, self).__init__()

        self.steps = Common.wizard_steps
        self.env = Common.environment

        self.text = QtWidgets.QTextBrowser(self)
        self.accept_group = QtWidgets.QGroupBox(self)
        self.yes_button = QtWidgets.QRadioButton(self.accept_group)
        self.no_button = QtWidgets.QRadioButton(self.accept_group)

        self.layout = QtWidgets.QVBoxLayout()

        self.setupUi()

    def setupUi(self):
        self.text.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.text.setFrameShape(QtWidgets.QFrame.Panel)

        self.accept_group.setMinimumSize(0, 60)
        self.yes_button.setGeometry(QtCore.QRect(30, 10, 300, 21))
        self.no_button.setGeometry(QtCore.QRect(30, 30, 300, 21))
        self.no_button.setChecked(True)

        self.layout.addWidget(self.text)
        self.layout.addWidget(self.accept_group)
        self.setLayout(self.layout)

    def nextId(self):
        return self.steps.index('finish_page')


class FinishPage(QtWidgets.QWizardPage):
    def __init__(self):
        super(FinishPage, self).__init__()

        self.icon = QtWidgets.QLabel(self)
        self.text = QtWidgets.QTextBrowser(self)

        self.layout = QtWidgets.QGridLayout()
        self.setupUi()

    def setupUi(self):
        self.icon.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.icon.setMinimumSize(50, 0)

        self.text.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.text.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        self.layout.addWidget(self.icon, 0, 0, 1, 1)
        self.layout.addWidget(self.text, 0, 1, 1, 1)
        self.setLayout(self.layout)


class setup_wizard_dist(QtWidgets.QWizard):
    def __init__(self):
        super(setup_wizard_dist, self).__init__()

        self.finished_normally = False

        translation = _translations(Common.translations_path, 'setup-dist')
        self._ = translation.gettext

        self.steps = Common.wizard_steps
        self.env = Common.environment

        if Common.show_disclaimer:
               self.disclaimer_1 = DisclaimerPage1()
               self.addPage(self.disclaimer_1)

               self.disclaimer_2 = DisclaimerPage2()
               self.addPage(self.disclaimer_2)

        self.finish_page = FinishPage()
        self.addPage(self.finish_page)

        self.setupUi()

    def done(self, result):
        if result == QtWidgets.QWizard.Accepted:
            self.finished_normally = True
        super(setup_wizard_dist, self).done(result)

    def setupUi(self):
      self.setWindowIcon(QtGui.QIcon("/usr/share/icons/icon-pack-dist/whonix.ico"))

      if Common.environment == 'machine':
         self.setWindowTitle('Kicksecure Setup Wizard')
      else:
         self.setWindowTitle('Whonix Setup Wizard')

      screen_resolution = QtWidgets.QDesktopWidget().screenGeometry()
      screen_height = screen_resolution.height()
      screen_width = screen_resolution.width()

      window_width_percentage = 0.8
      window_height_percentage = 0.8

      # Calculate window dimensions
      self.window_width = int(screen_width * window_width_percentage)
      self.window_height = int(screen_height * window_height_percentage)

      # Resize the window
      self.resize(self.window_width, self.window_height)

      # We use QTextBrowser with a white background.
      # Set a default (transparent) background.
      palette = QtGui.QPalette()
      brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
      brush.setStyle(QtCore.Qt.SolidPattern)
      palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
      brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
      brush.setStyle(QtCore.Qt.SolidPattern)
      palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
      brush = QtGui.QBrush(QtGui.QColor(244, 244, 244))
      brush.setStyle(QtCore.Qt.SolidPattern)
      palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
      self.setPalette(palette)

      self.finish_page.icon.setPixmap(QtGui.QPixmap('/usr/share/icons/oxygen/48x48/status/task-complete.png'))
      self.finish_page.text.setText(self._('finish_page'))

      disclaimer_message = ""
      disclaimer_message += self._('disclaimer_1')

      if Common.environment == 'machine':
         disclaimer_message += self._('disclaimer_2_kicksecure')
      else:
         disclaimer_message += self._('disclaimer_2_whonix')

      disclaimer_message += self._('disclaimer_3')

      if Common.environment == 'machine':
         disclaimer_message += self._('disclaimer_4_kicksecure')
      else:
         disclaimer_message += self._('disclaimer_4_whonix')

      if Common.show_disclaimer:
         self.disclaimer_1.text.setText(disclaimer_message)
         self.disclaimer_1.yes_button.setText(self._('accept'))
         self.disclaimer_1.no_button.setText(self._('reject'))

         self.disclaimer_2.text.setText(self._('disclaimer_page_two'))
         self.disclaimer_2.yes_button.setText(self._('accept'))
         self.disclaimer_2.no_button.setText(self._('reject'))

      self.button(QtWidgets.QWizard.CancelButton).setVisible(False)

      self.button(QtWidgets.QWizard.BackButton).clicked.connect(self.back_button_clicked)
      self.button(QtWidgets.QWizard.NextButton).clicked.connect(self.next_button_clicked)

      if not Common.show_disclaimer:
         self.resize(580, 390)

    # called by button toggled signal.
    def set_next_button_state(self, state):
        if state:
            self.button(QtWidgets.QWizard.NextButton).setEnabled(False)
        else:
            self.button(QtWidgets.QWizard.NextButton).setEnabled(True)

    def center(self):
        """
        After the window is resized, its origin point becomes the
        previous window top left corner.
        Re-center the window on the screen.
        """
        frame_gm = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().screenGeometry().center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def next_button_clicked(self):
      """
      Next button slot.
      The commands cannot be implemented in the wizard's nextId() function,
      as it is polled by the event handler on the creation of the page.
      Depending on the checkbox states, the commands would be run when the
      page is loaded.
      Those button_clicked functions are called once, when the user clicks
      the corresponding button.
      Options (like button states, window size changes...) are set here.
      """

      if self.currentId() == self.steps.index('finish_page'):
            if Common.show_disclaimer:
               # Disclaimer page 1 not understood -> leave
               if self.disclaimer_1.no_button.isChecked():
                  self.hide()
                  declined_legal()

               # Disclaimer page 2 not understood -> leave
               if self.disclaimer_2.no_button.isChecked():
                  self.hide()
                  declined_legal()

               file_path = pathlib.Path('/var/cache/setup-dist/status-files/disclaimer.done')
               if not os.path.exists(file_path):
                  file_path.touch(exist_ok=True)

            if self.env == 'workstation':
               self.finish_page.icon.setPixmap(QtGui.QPixmap( \
               '/usr/share/icons/oxygen/48x48/status/task-complete.png'))
               self.finish_page.text.setText(self._('finish_page'))

    def back_button_clicked(self):
        if Common.show_disclaimer:
            if self.currentId() == self.steps.index('disclaimer_2'):
                # Back to disclaimer size.
                self.resize(self.window_width, self.window_height)
                self.center()


def signal_handler(sig, frame):
   sys.exit(128 + sig)


def main():
   app = QtWidgets.QApplication(sys.argv)

   signal.signal(signal.SIGINT, signal_handler)
   signal.signal(signal.SIGTERM, signal_handler)

   timer = QtCore.QTimer()
   timer.start(500)
   timer.timeout.connect(lambda: None)

   # when there is no page need showing, we simply do not start GUI to
   # avoid an empty page
   if len(Common.wizard_steps) == 0:
      print('INFO: No page needs showing.')
   else:
      wizard = setup_wizard_dist()
      wizard.exec_()

   if Common.show_disclaimer:
      if os.path.isfile('/usr/share/whonix-setup-wizard/status-files/disclaimer.skip'):
         print('INFO: /usr/share/whonix-setup-wizard/status-files/disclaimer.skip exists.')
      elif os.path.isfile('/var/cache/whonix-setup-wizard/status-files/disclaimer.done'):
         print('INFO: /var/cache/whonix-setup-wizard/status-files/disclaimer.done exists.')
      elif os.path.isfile('/usr/share/setup-dist/status-files/disclaimer.skip'):
         print('INFO: /usr/share/setup-dist/status-files/disclaimer.skip exists.')
      elif os.path.isfile('/var/cache/setup-dist/status-files/disclaimer.done'):
         print('INFO: /var/cache/setup-dist/status-files/disclaimer.done exists.')
      else:
         declined_legal()

   if not wizard.finished_normally:
      print('INFO: Canceled.')
      sys.exit(0)

   if Common.environment == 'gateway':
      '''
      anon-connection-wizard on Whonix-Gateway.
      '''
      command = ['anon-connection-wizard']
      exit_code = call(command)

   command = ['env', 'started_by_setup_wizard_dist=true', '/usr/libexec/setup-dist/ft_m_end']
   exit_code = call(command)

if __name__ == "__main__":
    main()
