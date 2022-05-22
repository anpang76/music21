import librosa
import numpy as np
import seaborn as sns
from scipy.io import wavfile
import IPython.display as ipd
import matplotlib.pyplot as plt
import math
import itertools
from oscillator import * 
from collections.abc import Iterable


class ModulatedOscillator:
    def __init__(self, oscillator, *modulators, amp_mod=None, freq_mod=None, phase_mod=None):
        self.oscillator = oscillator
        self.modulators = modulators # list
        self.amp_mod = amp_mod
        self.freq_mod = freq_mod
        self.phase_mod = phase_mod
        self._modulators_count = len(modulators)
    
    def __iter__(self):
        iter(self.oscillator)
        [iter(modulator) for modulator in self.modulators]
        return self
    
    def _modulate(self, mod_vals):
        if self.amp_mod is not None:
            new_amp = self.amp_mod(self.oscillator.init_amp, mod_vals[0])
            self.oscillator.amp = new_amp
            
        if self.freq_mod is not None:
            if self._modulators_count == 2:
                mod_val = mod_vals[1]
            else:
                mod_val = mod_vals[0]
            new_freq = self.freq_mod(self.oscillator.init_freq, mod_val)
            self.oscillator.freq = new_freq
            
        if self.phase_mod is not None:
            if self._modulators_count == 3:
                mod_val = mod_vals[2]
            else:
                mod_val = mod_vals[-1]
            new_phase = self.phase_mod(self.oscillator.init_phase, mod_val)
            self.oscillator.phase = new_phase
    
    def trigger_release(self):
        tr = "trigger_release"
        for modulator in self.modulators:
            if hasattr(modulator, tr):
                modulator.trigger_release()
        if hasattr(self.oscillator, tr):
            self.oscillator.trigger_release()
            
    @property
    def ended(self):
        e = "ended"
        ended = []
        for modulator in self.modulators:
            if hasattr(modulator, e):
                ended.append(modulator.ended)
        if hasattr(self.oscillator, e):
            ended.append(self.oscillator.ended)
        return all(ended)

    def __next__(self):
        mod_vals = [next(modulator) for modulator in self.modulators]
        self._modulate(mod_vals)
        return next(self.oscillator)

    def amp_mod(self, init_amp, env):
        return env * init_amp
    
    def freq_mod(self, init_freq, env, mod_amt=0.01, sustain_level=0.7):
        return init_freq + ((env - sustain_level) * init_freq * mod_amt)


class Volume:
    def __init__(self, amp=1.):
        self.amp = amp
    
    def __call__(self, val):
        _val = None
        if isinstance(val, Iterable):
            _val = tuple(v * self.amp for v in val)
        elif isinstance(val, (int, float)):
            _val = val * self.amp
        return _val


class ModulatedVolume(Volume):
    def __init__(self, modulator):
        super().__init__(0.)
        self.modulator = modulator 
    
    def __iter__(self):
        iter(self.modulator)
        return self

    def __next__(self):
        self.amp = next(self.modulator)
        return self.amp
    
    def trigger_release(self):
        if hasattr(self.modulator, "trigger_release"):
            self.modulator.trigger_release()
    
    @property
    def ended(self):
        ended = False 
        if hasattr(self.modulator, "ended"):
            ended = self.modulator.ended
        return ended
    

class Panner :
    '''
    split mono inputs to stereo outputs, this component is a wave modifier

    '''
    def __init__(self, r=0.5) -> None:
        self.r = r

    def __call__(self,val)->float :
        r = self.r * 2
        l = 2 - r
        return (l * val, r * val)

    
class ModulatedPanner(Panner):
    def __init__(self, modulator):
        super().__init__(r=0)
        self.modulator = modulator

    def __iter__(self):
        iter(self.modulator)
        return self
    
    def __next__(self):
        self.r = (next(self.modulator)+1)/2
        return self.r