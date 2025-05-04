# -*- coding: utf-8 -*-

"""
Interface file for simple data acquisition.

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

from abc import abstractmethod
from qudi.core.module import Base


class OscilloscopeInterface(Base):
    """
    """

    abstractmethod
    def get_xaxis(self, channel):
        """ Return the x-axis of the oscilloscope trace """
        pass

    @abstractmethod
    def RunSingle(self, channel):
        """ Run single measurment and return specific channel """
        pass

    @abstractmethod
    def RunContinous(self, channel):
        """ Run continuous measurment and return specific channel """
        pass
    
    @abstractmethod
    def getData(self, channel):
        """ Return the last measured value """
        pass

    @abstractmethod
    def getData_cont(self, channel):
        """ Return the last measured value while scope is in continuous mode """
        pass

    @abstractmethod
    def SetVerticalScale(self, channel, vertical_scale):
        """ Sets the vertical scale for the given channel """
        pass   

    @abstractmethod
    def RunSTOP(self):
        """ Stops the oscilloscope and close the connection if necessary """
        pass

    @property
    @abstractmethod
    def time_base(self) -> float:
        """ Timebase of the oscilloscope (in milliseconds)
        Equivalent to the total time of the trace divided by the number of points.
        """
        pass
    
    @time_base.setter
    def time_base(self, value: int) -> None:
        """ Setter for property "time_base" 
        """
        pass

    @property
    @abstractmethod
    def record_length(self) -> int:
        """ Number of points in the oscilloscope trace 
        """
        pass
    
    @record_length.setter
    def record_length(self, value: int) -> None:
        """ Setter for property "record_length" 
        """
        pass
