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


class WindFreak(FrequencyGeneratorInterface):
    _serial_device = ConfigOption('serial_device', 'COM3', missing='warn')

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)


    def on_activate(self):
        """ Dummy WindFreak, no activation"""
        pass

    def on_deactivate(self):
        pass

    def generator_on(self, ch=None):
        pass

    def generator_off(self, ch=None):
        pass

    def set_power_level(self, amplitude=None, ch=None):
        pass
    
    def get_power_level(self, ch=None):
        return 0

    def set_frequency(self, freq=None, ch=None):
        pass

    def get_frequency(self, ch=None):
        return 666

    def set_phase(self, phase=None, ch=None):
        pass
    
    def get_phase(self, ch=None):
        return 0

    def get_temp(self, ch=None):
        return 1062
    
    def get_active_channels(self):
        stat = []
        return stat