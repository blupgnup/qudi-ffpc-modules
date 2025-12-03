# -*- coding: utf-8 -*-

"""
This file contains the Qudi hardware interface for pulsing devices.

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

from qudi.core.configoption import ConfigOption
from qudi.interface.frequency_generator_interface import FrequencyGeneratorInterface
from qudi.util.mutex import Mutex

from types import SimpleNamespace

class DummySynthHD:
    def __init__(self, **kwargs):
        # Each channel is just an attribute bag
        self.channels = [
            SimpleNamespace(enable = True, power=0, frequency=0, phase=0),
            SimpleNamespace(enable = False, power=0, frequency=0, phase=0)
        ]

    def __getitem__(self, index):
        return self.channels[index]

class WindFreak(FrequencyGeneratorInterface):
    _serial_device = ConfigOption('serial_device', 'COM3', missing='warn')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.lock = Mutex()
        
    def on_activate(self):
        """ Dummy WindFreak, no real activation"""
        self.synth = DummySynthHD()
        for s in self.synth:
            s.enable = False
            s.power = -2
            s.frequency = 500
            s.phase = 0

    def on_deactivate(self):
        self.generator_off(ch=0)
        self.generator_off(ch=1)
        pass

    def generator_on(self, ch=None):
        self.synth[ch].enable = True
        pass

    def generator_off(self, ch=None):
        self.synth[ch].enable = False
        pass

    def set_power_level(self, amplitude=None, ch=None):
        self.synth[ch].power = amplitude
        pass
    
    def get_power_level(self, ch=None):
        return self.synth[ch].power

    def set_frequency(self, freq=None, ch=None):
        self.synth[ch].frequency = freq
        pass

    def get_frequency(self, ch=None):
        return self.synth[ch].frequency

    def set_phase(self, phase=None, ch=None):
        self.synth[ch].phase = phase
        pass
    
    def get_phase(self, ch=None):
        return self.synth[ch].phase

    def get_temp(self, ch=None):
        return 10.62
    
    def get_active_channels(self):
        stat = []
        if self.synth[0].enable is True:
            stat.append(1)
        else:
            stat.append(0)
        if self.synth[1].enable is True:
            stat.append(1)
        else:
            stat.append(0)
        return stat