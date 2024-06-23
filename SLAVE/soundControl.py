from machine import Pin, PWM
import time

class Buzzer:
    # Note frequencies dictionary including all notes from C1 to C7
    NOTE_FREQS = {
        'C1': 33, 'C#1': 35, 'Db1': 35, 'D1': 37, 'D#1': 39, 'Eb1': 39, 'E1': 41, 'F1': 44, 'F#1': 46, 'Gb1': 46, 'G1': 49, 'G#1': 52, 'Ab1': 52, 'A1': 55, 'A#1': 58, 'Bb1': 58, 'B1': 62,
        'C2': 65, 'C#2': 69, 'Db2': 69, 'D2': 73, 'D#2': 78, 'Eb2': 78, 'E2': 82, 'F2': 87, 'F#2': 93, 'Gb2': 93, 'G2': 98, 'G#2': 104, 'Ab2': 104, 'A2': 110, 'A#2': 117, 'Bb2': 117, 'B2': 123,
        'C3': 130, 'C#3': 139, 'Db3': 139, 'D3': 147, 'D#3': 156, 'Eb3': 156, 'E3': 165, 'F3': 175, 'F#3': 185, 'Gb3': 185, 'G3': 196, 'G#3': 208, 'Ab3': 208, 'A3': 220, 'A#3': 233, 'Bb3': 233, 'B3': 247,
        'C4': 261, 'C#4': 277, 'Db4': 277, 'D4': 294, 'D#4': 311, 'Eb4': 311, 'E4': 330, 'F4': 349, 'F#4': 370, 'Gb4': 370, 'G4': 392, 'G#4': 415, 'Ab4': 415, 'A4': 440, 'A#4': 466, 'Bb4': 466, 'B4': 494,
        'C5': 523, 'C#5': 554, 'Db5': 554, 'D5': 587, 'D#5': 622, 'Eb5': 622, 'E5': 659, 'F5': 698, 'F#5': 740, 'Gb5': 740, 'G5': 784, 'G#5': 831, 'Ab5': 831, 'A5': 880, 'A#5': 932, 'Bb5': 932, 'B5': 988,
        'C6': 1047, 'C#6': 1109, 'Db6': 1109, 'D6': 1175, 'D#6': 1245, 'Eb6': 1245, 'E6': 1319, 'F6': 1397, 'F#6': 1480, 'Gb6': 1480, 'G6': 1568, 'G#6': 1661, 'Ab6': 1661, 'A6': 1760, 'A#6': 1865, 'Bb6': 1865, 'B6': 1976,
        'C7': 2093, 'C#7': 2217, 'Db7': 2217, 'D7': 2349, 'D#7': 2489, 'Eb7': 2489, 'E7': 2637, 'F7': 2794, 'F#7': 2960, 'Gb7': 2960, 'G7': 3136, 'G#7': 3322, 'Ab7': 3322, 'A7': 3520, 'A#7': 3729, 'Bb7': 3729, 'B7': 3951,
        'P': 0  # Pause
    }

    def __init__(self, pin, frequency=2700, duty=32768):
        # Initialize the PWM pin for the buzzer
        self.buzzer = PWM(Pin(pin), freq=frequency, duty_u16=duty)
        self.buzzer.duty(0)  # Set duty cycle to 0 (buzzer off)
        self.songs = {}  # Dictionary to store songs

    def add_song(self, name, notes):
        # Add a song to the dictionary
        self.songs[name] = notes

    def play_song(self, name):
        # Play a song by name if it exists in the dictionary
        if name not in self.songs:
            return False  # Return False if the song is not found
        
        notes = self.songs[name]  # Get the list of notes for the song
        for note, duration in notes:
            freq = self.NOTE_FREQS.get(note, 0)  # Get the frequency for the note
            if freq == 0:
                self.buzzer.duty(0)  # Turn off the buzzer for a pause
            else:
                self.buzzer.freq(freq)  # Set the buzzer frequency
                self.buzzer.duty(512)  # Set the duty cycle to play the note
            time.sleep(duration)  # Wait for the duration of the note
        self.buzzer.duty(0)  # Turn off the buzzer after the song is finished

    def stop(self):
        # Stop the buzzer
        self.buzzer.duty(0)

    def is_song_available(self, name):
        # Check if a song is available in the dictionary
        return name in self.songs