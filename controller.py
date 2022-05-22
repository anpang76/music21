from email.policy import default
import math
import pyaudio
import itertools
import numpy as np
import seaborn as sns
from pygame import midi
from scipy.io import wavfile
import matplotlib.pyplot as plt
from IPython.display import Audio
from envelopes import *
from composer import *
from modulator import *
from oscillator import *

sns.set_theme()
SR = 44_100

midi.init()
default_id = midi.get_default_input_id()
midi_input = midi.Input(device_id=default_id)

try:
    while True:
        if midi_input.poll():
            print(midi_input.read(num_events=16))
except KeyboardInterrupt as err:
    print("Stopping...")