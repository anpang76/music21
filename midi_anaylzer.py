from music21 import roman,stream,chord, note, pitch
import music21
import numpy as np
import os 

class Midi_analyzer():
    def __init__(self, midi_path) -> None:
        self.midi_path = midi_path
        self.midi= music21.converter.parse(self.midi_path)

    @property
    def analyze_key(self):
        return self.midi.analyze("key")

    @property
    def analyze_timesignature(self):
        return self.midi[music21.meter.TimeSignature][0]


    def analyze_chords(self,i=None):
        return self.harmonic_reduction(self.midi)[0:i]
    
    def analyze_result(self):
        print(self.analyze_key)
        print(self.analyze_timesignature)
        print(self.analyze_chords())


    def note_count(self, measure, count_dict):
        bass_note = None
        for chord in measure.recurse().getElementsByClass("Chord"):
            note_length = chord.quarterLength
            for note in chord.pitches:
                note_name = str(note)
                if (bass_note is None or bass_note.ps > note.ps):
                    bass_note = note

                if note_name in count_dict:
                    count_dict[note_name] +=note_length
                else:
                    count_dict[note_name] = note_length
        return bass_note


    def simplify_roman_name(self, roman_numeral):
 
        ret = roman_numeral.romanNumeral
        inversion_name = None
        inversion = roman_numeral.inversion()

            # Checking valid inversions.
        if ((roman_numeral.isTriad() and inversion < 3) or
                (inversion < 4 and
                    (roman_numeral.seventh is not None or roman_numeral.isSeventh()))):
            inversion_name = roman_numeral.inversionName()
            
        if (inversion_name is not None):
            ret = ret + str(inversion_name)
            
        elif (roman_numeral.isDominantSeventh()): ret = ret + "M7"
        elif (roman_numeral.isDiminishedSeventh()): ret = ret + "o7"
        return ret
    

    def harmonic_reduction(self,i):
        ret = []
        temp_midi = stream.Score()
        temp_midi_chords = self.midi.chordify()
        temp_midi.insert(0, temp_midi_chords)    
        music_key = temp_midi.analyze('key')
        max_notes_per_chord = 4   
        for m in temp_midi_chords.measures(0, None): # None = get all measures.
            if (type(m) != stream.Measure):
                continue
        
            count_dict = dict()
            bass_note = self.note_count(m, count_dict)
            if (len(count_dict) < 1):
                ret.append("-") # Empty measure
                continue
            
            sorted_items = sorted(count_dict.items(), key=lambda x:x[1])
            sorted_notes = [item[0] for item in sorted_items[-max_notes_per_chord:]]
            measure_chord = chord.Chord(sorted_notes)
            
            roman_numeral = roman.romanNumeralFromChord(measure_chord, music_key)
            ret.append(self.simplify_roman_name(roman_numeral))
            
        return ret

