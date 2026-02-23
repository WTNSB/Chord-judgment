import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Note:
    step: str
    alter: int
    octave: int

    def __post_init__(self):
        self.step = self.step.upper()

    STEP_TO_SEMITONE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    STEP_TO_INDEX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}

    @property
    def pitch_class(self) -> int:
        return (self.STEP_TO_SEMITONE[self.step] + self.alter) % 12

    @property
    def absolute_semitone(self) -> int:
        base = self.STEP_TO_SEMITONE[self.step]
        return base + self.alter + (self.octave * 12)

    @property
    def step_index(self) -> int:
        return self.STEP_TO_INDEX[self.step]

    def __str__(self):
        alter_str = ""
        if self.alter == 1: alter_str = "#"
        elif self.alter == -1: alter_str = "b"
        elif self.alter == 2: alter_str = "x"
        elif self.alter == -2: alter_str = "bb"
        return f"{self.step}{alter_str}{self.octave}"

    @classmethod
    def from_string(cls, note_str: str, default_octave: Optional[int] = None) -> 'Note':
        match = re.match(r"^([a-gA-G])([#bx]*)(-?\d+)?$", note_str.strip())
        if not match: raise ValueError(f"Invalid format: '{note_str}'")
        step_str, alter_str, octave_str = match.groups()
        alter = {'': 0, '#': 1, 'b': -1, 'bb': -2, 'x': 2}.get(alter_str.lower(), 0)
        octave = int(octave_str) if octave_str is not None else default_octave
        if octave is None: octave = 4 
        return cls(step=step_str, alter=alter, octave=octave)

def parse_notes(notes_csv: str, start_octave: int = 4) -> List[Note]:
    note_strs = [s.strip() for s in notes_csv.split(",")]
    notes = []
    current_octave = start_octave
    last_pc = -1
    for n_str in note_strs:
        temp_note = Note.from_string(n_str, default_octave=None)
        if re.search(r"-?\d+$", n_str) is None:
            if temp_note.pitch_class < last_pc:
                current_octave += 1
            temp_note.octave = current_octave
            last_pc = temp_note.pitch_class
        else:
            current_octave = temp_note.octave
            last_pc = temp_note.pitch_class
        notes.append(temp_note)
    return notes