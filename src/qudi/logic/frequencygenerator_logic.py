#-*- coding: utf-8 -*-
"""
Windfreak modulator management.

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

import time
import numpy as np
from qtpy import QtCore

from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption
from qudi.core.statusvariable import StatusVar
from qudi.core.module import LogicBase

class FrequencyGeneratorLogic(LogicBase):
    """ Logic module to drive the WindFreak frequency generator.
    """

    # declare connectors
    generator = Connector(interface='FrequencyGeneratorInterface')

    # declare status variable
    ch1_freq = StatusVar('ch1_frequency', 53000000)
    ch2_freq = StatusVar('ch2_frequency', 53000000)
    ch1_pwr = StatusVar('ch1_power', -5)
    ch2_pwr = StatusVar('ch2_power', -5)
    ch1_phase = StatusVar('ch1_phase', 0)
    ch2_phase = StatusVar('ch2_phase', 0)

    # waiting time between queries in milliseconds
    queryInterval = ConfigOption('query_interval', 1000)

    # External signals eg for GUI module
    sigUpdate = QtCore.Signal()

    def __init__(self, **kwargs):
        """ Create FrequencyGeneratorLogic object with connectors.

          @param dict kwargs: optional parameters
        """
        super().__init__(**kwargs)
        self.tempch1 = 0
        self.tempch2 = 0

    def on_activate(self):
        """ Prepare logic module for work.
        """
        self._generator = self.generator()

        self.set_frequency(0, self.ch1_freq)
        self.set_frequency(1, self.ch2_freq)
        self.set_power(0, self.ch1_pwr)
        self.set_power(1, self.ch2_pwr)
        self.set_phase(0, self.ch1_phase)
        self.set_phase(1, self.ch2_phase)

        self.stopRequest = False

        self.queryTimer = QtCore.QTimer()
        self.queryTimer.setInterval(self.queryInterval)
        self.queryTimer.setSingleShot(False)
        self.queryTimer.timeout.connect(self.check_temp_loop, QtCore.Qt.QueuedConnection)

        self.check_rf_state()
        self.start_query_loop()

    def on_deactivate(self):
        """ Deactivate module.
        """
        self.stop_query_loop()

    def check_temp_loop(self):
        """ Get power, current, shutter state and temperatures from laser. """
        if self.stopRequest:
            self.stopRequest = False
            return
        qi = self.queryInterval
        try:
            # print('frequencygen_temp_loop', QtCore.QThread.currentThread()) # Unnecessary and log consuming...
            self.tempch1 = self._generator.get_temp(0)
            self.tempch2 = self._generator.get_temp(1)
        except:
            qi = 3000
            self.log.exception("Exception in temp status loop, throttling refresh rate.")

        self.sigUpdate.emit()
        self.queryTimer.start(qi)

    def start_query_loop(self):
        """ Start the readout loop. """
        # self.module_state.run() # Module run/stop state does not exist anymore        
        self.queryTimer.start(self.queryInterval)

    def stop_query_loop(self):
        """ Stop the readout loop. """
        self.stopRequest = True
        # self.module_state.stop() # Module run/stop state does not exist anymore
        self.queryTimer.stop()

        time.sleep(self.queryInterval / 1000)
        QtCore.QCoreApplication.processEvents() # Ensure that the GUI does not freeze.

        # Time consuming... Necessary ?
        # for i in range(10):
        #     if not self.stopRequest:
        #         return
        #     QtCore.QCoreApplication.processEvents()
        #     time.sleep(self.queryInterval/1000)

    def check_rf_state(self):
        """ Turn laser on or off. """
        self._generator.get_active_channels()
        self.sigUpdate.emit()

    def set_frequency(self, ch, freq):
        self._generator.set_frequency(freq, ch)
        self.sigUpdate.emit()
        if ch == 0:
            self.ch1_freq = freq
        else:
            self.ch2_freq = freq

    def read_frequency(self, ch):
        return self._generator.get_frequency(ch)

    def set_power(self, ch, amplitude):
        self._generator.set_power_level(amplitude, ch)
        self.sigUpdate.emit()
        if ch == 0:
            self.ch1_pwr = amplitude
        else:
            self.ch2_pwr = amplitude

    def read_power(self, ch):
        return self._generator.get_power_level(ch)

    def set_phase(self, ch, phase):
        self._generator.set_phase(phase, ch)
        self.sigUpdate.emit()
        if ch == 0:
            self.ch1_phase = phase
        else:
            self.ch2_phase = phase

    def read_phase(self, ch):
        return self._generator.get_phase(ch)

    def switch_on(self, ch):
        return self._generator.generator_on(ch)

    def switch_off(self, ch):
        return self._generator.generator_off(ch)
