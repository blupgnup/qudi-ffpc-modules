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
    _trace_length = 6000
    _timebase = 20e-6

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

            @return ndarray: _trace_length value ndarray containing sample trace
        """
        if channel == 1:
            # Lorentzian peak without sidebands
            trace = self.gen_trace(self.get_xaxis)
        else:
            # Lorentzian peak with sidebands
            trace = self.gen_trace(self.get_xaxis, sidebands=True)

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
        xaxis = np.linspace(-self._timebase/2, self._timebase/2, self._trace_length)
        return xaxis

    def gen_trace(self, x, sidebands = False):
        # Parameters for the generated Lorentzian trace
        amplitude = 0.2e-6
        center = 0.0
        gamma = 0.2e-6
        noise_level = 2e-3
    
        # Retrieving x_values that fit with the timescale
        x_values = np.linspace(-self._timebase/2, self._timebase/2, self._trace_length)
        
        #lorentzian_values = amplitude / np.pi * (gamma / ((x_values - center)**2 + gamma**2))  
        # It is better to use the physical definition of the Lorentzian as it is the one used for the fit...
        I = amplitude / (np.pi * gamma)
        lorentzian_values = I * (gamma**2 / ((x_values - center)**2 + gamma**2))

        # Add random noise
        noise = np.random.normal(loc=0, scale=noise_level, size=self._trace_length)
        trace = lorentzian_values + noise

        # If sidebands, adding 20% amplitude sidebands at 15 gammas distance
        if sidebands:
            offset = 10 * gamma
            sideband_1 = 0.1 * I * (gamma**2 / ((x_values - (center + offset))**2 + gamma**2))
            sideband_2 = 0.1 * I * (gamma**2 / ((x_values - (center - offset))**2 + gamma**2))

            trace = trace + sideband_1 + sideband_2

        return trace
