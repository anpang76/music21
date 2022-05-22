import math
import itertools
from re import I
from more_itertools import sample
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import pandas as pd

class Oscillator(ABC):
    def __init__(self, freq=440, phase=0, amp=1, \
                 sample_rate=44_100, wave_range=(-1, 1)):
        self._freq = freq
        self._amp = amp
        self._phase = phase
        self._sample_rate = sample_rate
        self._wave_range = wave_range
        
        # Properties that will be changed
        self._f = freq
        self._a = amp
        self._p = phase
        
    @property
    def init_freq(self):
        return self._freq
    
    @property
    def init_amp(self):
        return self._amp
    
    @property
    def init_phase(self):
        return self._phase
    
    @property
    def freq(self):
        return self._f
    
    @freq.setter
    def freq(self, value):
        self._f = value
        self._post_freq_set()
        
    @property
    def amp(self):
        return self._a
    
    @amp.setter
    def amp(self, value):
        self._a = value
        self._post_amp_set()
        
    @property
    def phase(self):
        return self._p
    
    @phase.setter
    def phase(self, value):
        self._p = value
        self._post_phase_set()
    
    def _post_freq_set(self):
        pass
    
    def _post_amp_set(self):
        pass
    
    def _post_phase_set(self):
        pass
    
    @abstractmethod
    def _initialize_osc(self):
        pass
    
    @staticmethod
    def squish_val(val, min_val=0, max_val=1):
        '''
        to bring the oscillator output into a given range
        '''
        return (((val + 1) / 2 ) * (max_val - min_val)) + min_val

    @abstractmethod
    def __next__(self):
        return None
    
    def __iter__(self):
        '''
        when press the key __iter__() called and the __next is called as long as the key is held.

        '''
        self.freq = self._freq
        self.phase = self._phase
        self.amp = self._amp
        self._initialize_osc()
        return self


class SineOscillator(Oscillator):
    def __post_freq_set(self):
        self._step = (2 * math.pi * self._f) /  self._sample_rate
        return self._step
        
    def _post_phase_set(self):
        self._p = (self._p / 360) * 2 * math.pi
        
    def _initialize_osc(self):
        self._i = 0
        
    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self.__post_freq_set()
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a
    

    
   
class SquareOscillator(SineOscillator):
    def __init__(self, freq=440, phase=0, amp=1, \
                sample_rate=44_100, wave_range=(-1, 1), threshold=0):
        super().__init__(freq, phase, amp, sample_rate, wave_range)
        self.threshold = threshold

    def __post_freq_set(self):
        self._step = (2 * math.pi * self._f) /  self._sample_rate
        return self._step

    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self.__post_freq_set()
        if val < self.threshold:
            val = self._wave_range[0]
        else:
            val = self._wave_range[1]
        return val * self._a


class SawtoothOscillator(Oscillator):
    def _post_freq_set(self):
        self._period = self._sample_rate / self._f
        self._post_phase_set
        
    def _post_phase_set(self):
        self._p = ((self._p + 90)/ 360) * self._period
    
    def _initialize_osc(self):
        self._i = 0
    
    def __next__(self):
        div = (self._i + self._p )/self._period
        val = 2 * (div - math.floor(0.5 + div))
        self._i = self._i + 1
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a


class TriangleOscillator(SawtoothOscillator):
    def __next__(self):
        div = (self._i + self._p)/self._period
        val = 2 * (div - math.floor(0.5 + div))
        val = (abs(val) - 0.5) * 2
        self._i = self._i + 1
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a
