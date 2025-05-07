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
from time import sleep

import socket
import struct 
import sys
import re
import array
import io

from qtpy import QtCore
from qudi.core.configoption import ConfigOption
from qudi.util.mutex import Mutex
from qudi.interface.oscilloscope_interface import OscilloscopeInterface

headerformat = '>BBBBL'

# data types in lecroy binary blocks, where:
# length  -- byte length of type
# string  -- string representation of type
# packfmt -- format string for struct.unpack()
class String:
    length = 16
    string = 'string'
class Byte:
    length = 1
    string = 'byte'
    packfmt = 'b'
class Word:
    length = 2
    string = 'word'
    packfmt = 'h'
class Long:
    length = 4
    string = 'long'
    packfmt = 'l'
class Enum:
    length = 2
    string = 'enum'
    packfmt = 'h'
class Float:
    length = 4
    string = 'float'
    packfmt = 'f'
class Double:
    length = 8
    string = 'double'
    packfmt = 'd'
class TimeStamp:
    length = 16
    string = 'time_stamp'
    packfmt = 'dbbbbhh'
class UnitDefinition:
    length = 48
    string = 'unit_definition'

# byte length of wavedesc block
wavedesclength = 346

# template of wavedesc block, where each entry in tuple is:
# (variable name, byte position from beginning of block, datatype)
wavedesc = ( ('descriptor_name'    , 0   , String),
             ('template_name'      , 16  , String),
             ('comm_type'          , 32  , Enum),
             ('comm_order'         , 34  , Enum),
             ('wave_descriptor'    , 36  , Long),
             ('user_text'          , 40  , Long),
             ('res_desc1'          , 44  , Long),
             ('trigtime_array'     , 48  , Long),
             ('ris_time_array'     , 52  , Long),
             ('res_array1'         , 56  , Long),
             ('wave_array_1'       , 60  , Long),
             ('wave_array_2'       , 64  , Long),
             ('res_array_2'        , 68  , Long),
             ('res_array_3'        , 72  , Long),
             ('instrument_name'    , 76  , String),
             ('instrument_number'  , 92  , Long),
             ('trace_label'        , 96  , String),
             ('reserved1'          , 112 , Word),
             ('reserved2'          , 114 , Word),
             ('wave_array_count'   , 116 , Long),
             ('pnts_per_screen'    , 120 , Long),
             ('first_valid_pnt'    , 124 , Long),
             ('last_valid_pnt'     , 128 , Long),
             ('first_point'        , 132 , Long),
             ('sparsing_factor'    , 136 , Long),
             ('segment_index'      , 140 , Long),
             ('subarray_count'     , 144 , Long),
             ('sweeps_per_acq'     , 148 , Long),
             ('points_per_pair'    , 152 , Word),
             ('pair_offset'        , 154 , Word),
             ('vertical_gain'      , 156 , Float),
             ('vertical_offset'    , 160 , Float),
             ('max_value'          , 164 , Float),
             ('min_value'          , 168 , Float),
             ('nominal_bits'       , 172 , Word),
             ('nom_subarray_count' , 174 , Word),
             ('horiz_interval'     , 176 , Float),
             ('horiz_offset'       , 180 , Double),
             ('pixel_offset'       , 188 , Double),
             ('vertunit'           , 196 , UnitDefinition),
             ('horunit'            , 244 , UnitDefinition),
             ('horiz_uncertainty'  , 292 , Float),
             ('trigger_time'       , 296 , TimeStamp),
             ('acq_duration'       , 312 , Float),
             ('record_type'        , 316 , Enum),
             ('processing_done'    , 318 , Enum),
             ('reserved5'          , 320 , Word),
             ('ris_sweeps'         , 322 , Word),
             ('timebase'           , 324 , Enum),
             ('vert_coupling'      , 326 , Enum),
             ('probe_att'          , 328 , Float),
             ('fixed_vert_gain'    , 332 , Enum),
             ('bandwidth_limit'    , 334 , Enum),
             ('vertical_vernier'   , 336 , Float),
             ('acq_vert_offset'    , 340 , Float),
             ('wave_source'        , 344 , Enum) )


class HardwarePull(QtCore.QObject):
    """ Helper class for running the hardware communication in a separate thread. """

    # signal to deliver the wavelength to the parent class
    sig_trace = QtCore.Signal(list)

    def __init__(self, parentclass):
        super().__init__()

        # remember the reference to the parent class to access functions ad settings
        self._parentclass = parentclass

    def handle_timer(self, state_change, channel):
        """ Threaded method that can be called by a signal from outside to start the timer.
        @param bool state: (True) starts timer, (False) stops it.
        """
        self.channel = channel
        if state_change:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self._measure_thread)
            self.timer.start(self._parentclass._measurement_timing)
        else:
            if hasattr(self, 'timer'):
                self.timer.stop()

    def _measure_thread(self):
        """ The threaded method querying the data from the scope.
        """
        # update as long as the state is busy
        if self._parentclass.module_state() == 'running':
            trace = self.RunSingle(self.channel)
            # send the data to the parent via a signal
            self.sig_trace.emit(trace)


class OscilloscopeLecroy(OscilloscopeInterface):
    _host = ConfigOption('host', missing='error')
    _port = ConfigOption('port', default=1861)
    _timeout = ConfigOption('timeout', default=2.0)
    _measurement_timing = ConfigOption('measurement_timing', default=300.)
    _trace_length = 6000
    _timebase = 20e-6

    sig_handle_timer = QtCore.Signal(bool, int)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

        #locking for thread safety
        self.threadlock = Mutex()

        self._current_xaxis = []
        self._current_trace = []

    def on_activate(self):
        """ Startup the module """
        self.log.info('Starting dummy hardware: LeCroy scope')
        
        self.hardware_thread = QtCore.QThread()
        self._hardware_pull = HardwarePull(self)
        self._hardware_pull.moveToThread(self.hardware_thread)
        self.sig_handle_timer.connect(self._hardware_pull.handle_timer)
        self._hardware_pull.sig_trace.connect(self.handle_trace)
        self.hardware_thread.start()

    def on_deactivate(self):
        """ Stops the module """
        self.log.info('Closing dummy hardware: LeCroy scope')
        self.hardware_thread.quit()
        self.sig_handle_timer.disconnect()
        self._hardware_pull.sig_trace.disconnect()

    def send(self, command):
        pass  # Dummy function to simulate sending a command to the oscilloscope

    def getheader(self):
        """
        Unpacks a header string from the oscilloscope into the tuple
        (operation, header version, sequence number, spare, total bytes).
        """
        return struct.unpack(headerformat, self.sock.recv(8))

    def recv(self):
        pass # Dummy function to simulate receiving a message from the oscilloscope
    
    def clear(self):
        pass # Dummy function to simulate clearing the oscilloscope

    def handle_trace(self, trace):
        """ Function to set a specific trace, when it comes in with a signal.
        """
        self._current_trace = trace

    def getData(self, channel):
        return self._current_trace

    def getData_cont(self, channel):
        trace = self.RunSingle(channel)
        return trace

    def RunContinous(self, channel=1, refreshrate=None):
        self.channel = channel
        self.log.info('Starting continuous measurment')
        return 0

    def SetVerticalScale(self, channel=1, scale=10e-3):
        self.log.info('Method is not implemented yet for LeCroy scope')

    @property
    def time_base(self):
        """ Timebase of the oscilloscope (in milliseconds ???)
        Equivalent to the total time of the trace divided by
        the number of points.
        """
        timebase = self._current_xaxis[-1] - self._current_xaxis[0] / len(self._current_xaxis)
        return timebase
    
    @time_base.setter
    def time_base(self, value: float) -> None:
        """ Setter for property "time_base" 
        """
        self.log.info('Method is not implemented yet for LeCroy scope')

    @property
    def record_length(self):
        """ Number of points in the trace.
        """
        recordlength = len(self._current_xaxis)
        return recordlength
    
    @record_length.setter
    def record_length(self, value: int) -> None:
        """ Setter for property "record_length" 
        """
        self.log.info('Method is not implemented yet for LeCroy scope')

    def RunSingle(self, channel=1):
        """ Generates a dummy trace.

            @return ndarray: _trace_length value ndarray containing sample trace
        """
        self.log.info("Generating dummy trace for channel {} ...".format(channel))
        if channel == 1:
            # Lorentzian peak without sidebands
            trace = self.gen_trace()
        else:
            # Lorentzian peak with sidebands
            trace = self.gen_trace(sidebands=True)

        self._current_trace = trace

        self.log.info("Successfully generated dummy trace for channel {}".format(channel))
        return self._current_trace

    def RunSTOP(self):
        if self.module_state() == 'idle':
            self.log.warning('Scope was already stopped, stopping it '
                    'anyway!')
        else:
            self.sig_handle_timer.emit(False, None)
            self.module_state.stop()
        return 0

    def get_xaxis(self, channel=1):
        xaxis = self._current_xaxis
        return xaxis
    
    def gen_trace(self, sidebands = False):
        # Parameters for the generated Lorentzian trace
        amplitude = 0.2e-6
        center = 0.0
        gamma = 0.2e-6
        noise_level = 2e-3
    
        # Retrieving x_values that fit with the timescale
        x_values = np.linspace(-self._timebase/2, self._timebase/2, self._trace_length)
        self._current_xaxis = x_values
        
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
