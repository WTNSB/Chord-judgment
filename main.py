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

    @property
    def pitch_class(self) -> int:
        """ 0(C) から 11(B) までのピッチクラス（オクターブを無視した音の高さ） """
        return (self.STEP_TO_SEMITONE[self.step] + self.alter) % 12

    @property
    def absolute_semitone(self) -> int:
        base = self.STEP_TO_SEMITONE[self.step]
        return base + self.alter + (self.octave * 12)

    def __str__(self):
        alter_str = ""
        if self.alter == 1: alter_str = "#"
        elif self.alter == -1: alter_str = "b"
        elif self.alter == 2: alter_str = "x"
        elif self.alter == -2: alter_str = "bb"
        return f"{self.step}{alter_str}{self.octave}"

    @classmethod
    def from_string(cls, note_str: str, default_octave: Optional[int] = None) -> 'Note':
        # 正規表現: 数字部分 (-?\d+) に ? をつけて「省略可能」にする
        match = re.match(r"^([a-gA-G])([#bx]*)(-?\d+)?$", note_str.strip())
        if not match:
            raise ValueError(f"Invalid note format: '{note_str}'")

        step_str, alter_str, octave_str = match.groups()

        alter_map = {'': 0, '#': 1, 'b': -1, 'bb': -2, 'x': 2}
        alter = alter_map.get(alter_str.lower(), 0)

        # オクターブ指定があればそれを、なければ引数のデフォルト値を使う
        octave = int(octave_str) if octave_str is not None else default_octave
        
        # 単体パース時など、どうしても決まらない場合は一旦4にする
        if octave is None:
            octave = 4 

        return cls(step=step_str, alter=alter, octave=octave)

def parse_notes(notes_csv: str, start_octave: int = 4) -> List[Note]:
    """ 
    カンマ区切り文字列をNoteリストに変換する。
    オクターブが省略されている場合は、下から順に積み上がるクローズドボイシングを生成する。
    """
    note_strs = [s.strip() for s in notes_csv.split(",")]
    notes = []
    
    current_octave = start_octave
    last_pitch_class = -1

    for n_str in note_strs:
        # 一旦オクターブ未定のまま仮パース
        temp_note = Note.from_string(n_str, default_octave=None)
        
        # もし入力文字列にオクターブが含まれていなかった場合の自動補完ロジック
        if re.search(r"-?\d+$", n_str) is None:
            current_pc = temp_note.pitch_class
            # 前の音よりピッチクラスが下がったら（例: A -> C）、オクターブを繰り上げる
            if current_pc < last_pitch_class:
                current_octave += 1
            
            temp_note.octave = current_octave
            last_pitch_class = current_pc
        else:
            # 入力文字列にオクターブが明記されていた場合はそれを基準に更新
            current_octave = temp_note.octave
            last_pitch_class = temp_note.pitch_class

        notes.append(temp_note)

    return notes