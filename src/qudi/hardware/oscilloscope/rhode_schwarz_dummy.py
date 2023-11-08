# -*- coding: utf-8 -*-
"""

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
import numpy as np
import pyvisa as visa
from time import sleep

from qtpy import QtCore
from qudi.core.configoption import ConfigOption
from qudi.util.mutex import Mutex
from qudi.interface.oscilloscope_interface import OscilloscopeInterface


class OscilloscopeRS(OscilloscopeInterface):
    _address = ConfigOption('address', missing='error')
    _rto = None
    _visa_timeout = ConfigOption('visa_timeout', default=1000.)
    _opc_timeout = ConfigOption('opc_timeout', default=3000.)
    _measurement_timing = ConfigOption('measurement_timing', default=300.)
    _trace_length = 3000

    sig_handle_timer = QtCore.Signal(bool, int)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        
        self._current_trace = []

    def on_activate(self):
        """ Activate module.
        """
        pass

    def on_deactivate(self):
        """ Deactivate module.
        """
        pass

    def handle_trace(self, trace):
        """ Handle oscilloscope trace.
        """
        self._current_trace = trace

    def getData(self, channel):
        return self._current_trace

    def getData_cont(self, channel):
        """ Generates a dummy trace.

            @return ndarray: _trace_length value ndarray containing random trace
        """
        trace = np.random.standard_cauchy(self._trace_length,)

        self._current_trace = trace
        return self._current_trace

    def RunContinous(self, channel=1, refreshrate=None):
        """ SimpleDataInterface function to get the power from the scope """
        # self._rte.write('RUNContinous')
        # self._rte.query('*OPC?')
        '''
        if refreshrate is not None:
            self._measurement_timing = refreshrate
        if self.module_state() == 'running':
            self.log.error('Scope busy')
            return -1
        self.module_state.run()
        self.sig_handle_timer.emit(True, channel)
        '''
        return 0

    def SetVerticalScale(self, channel=1, scale=10e-3):
        # self._rte.write('CHAN{0}:SCAL {1}'.format(channel, scale))
        pass

    def SetTimeBase(self, timebase=5e-3):
        # self._rte.write('TIMebase:RANGe {}'.format(timebase))
        pass

    def SetRecordLength(self, recordlength=1000):
        # self._rte.write('ACQ:POIN {}'.format(recordlength))
        # sleep(0.1)
        pass

    def RunSingle(self, channel=1):
        """ Generates a dummy trace.

            @return ndarray: _trace_length value ndarray containing random trace
        """
        trace = np.random.standard_cauchy(self._trace_length,)

        return trace    

    def RunSTOP(self):
        if self.module_state() == 'idle':
            self.log.warning('Scope was already stopped, stopping it '
                    'anyway!')
        else:
            self.sig_handle_timer.emit(False, None)
            self.module_state.stop()
        return 0

    def get_xaxis(self):
        # timebase = float(self._rte.query('TIMebase:RANGe?'))
        # self._rte.query('*OPC?')
        # recordlength = int(self._rte.query('ACQ:POIN?'))
        # self._rte.query('*OPC?')
        timebase = 20e-6
        xaxis = np.linspace(-timebase/2, timebase/2, self._trace_length)
        return xaxis
