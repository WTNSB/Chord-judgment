import re
# main.py の一番上に追加
from dictionaries.chord_dict import CHORD_DICT
from dataclasses import dataclass
from typing import List, Optional

# --- 1. データ構造 ---
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
        """ Cを0としたときの、五線譜上の基本音名のインデックス """
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

# --- 2. 推論エンジン（ここが大きく進化！） ---
class ChordAnalyzer:
    def __init__(self):
        self.chord_dictionary = CHORD_DICT

        self.INTERVAL_MAP = {
            (0, 0): 'P1',  (0, 1): 'A1',  (0, -1): 'd1',
            (1, 1): 'm2',  (1, 2): 'M2',  (1, 3): 'A2',  (1, 0): 'd2',
            (2, 3): 'm3',  (2, 4): 'M3',  (2, 5): 'A3',  (2, 2): 'd3',
            (3, 5): 'P4',  (3, 6): 'A4',  (3, 4): 'd4',
            (4, 7): 'P5',  (4, 8): 'A5',  (4, 6): 'd5',
            (5, 8): 'm6',  (5, 9): 'M6',  (5, 10): 'A6', (5, 7): 'd6',
            (6, 10): 'm7', (6, 11): 'M7', (6, 12): 'A7', (6, 9): 'd7'
        }

    def _get_interval(self, root: Note, target: Note) -> str:
        # 1. 1オクターブ内に丸めた基本度数を計算
        step_diff = (target.step_index - root.step_index) % 7
        semi_diff = (target.absolute_semitone - root.absolute_semitone) % 12
        
        base_interval = self.INTERVAL_MAP.get((step_diff, semi_diff))
        if not base_interval:
            return f"Unknown({step_diff},{semi_diff})"
            
        # 2. 実際の半音差から、オクターブを超えているか判定
        actual_semi_diff = target.absolute_semitone - root.absolute_semitone
        
        quality = base_interval[0] # 'P', 'M', 'm', 'A', 'd'
        number = int(base_interval[1:]) # 1, 2, 3, 4, 5, 6, 7
        
        # 3. テンションの正規化
        # ルートより1オクターブ以上高く、かつ 2, 4, 6度の場合は 9, 11, 13度に変換
        if actual_semi_diff >= 12 and number in [2, 4, 6]:
            return f"{quality}{number + 7}"
            
        # 1, 3, 5, 7度は何オクターブ離れていても基本度数のまま返す
        return base_interval

    def analyze(self, notes: List[Note]) -> str:
        if not notes: return "No notes"

        # 1. 実際の入力音を高さ順にソートし、ベース音（最低音）を確定
        sorted_notes = sorted(notes, key=lambda n: n.absolute_semitone)
        bass_note = sorted_notes[0]

        # 2. 入力された音から、重複を省いた「仮のルート候補」のリストを作成
        # ※ルートポジション（基本形）を優先して判定するため、ベース音の音名を最初にテストする
        unique_cands = {}
        for n in sorted_notes:
            if n.pitch_class not in unique_cands:
                unique_cands[n.pitch_class] = n
                
        candidates = [unique_cands[bass_note.pitch_class]]
        for pc, n in unique_cands.items():
            if pc != bass_note.pitch_class:
                candidates.append(n)

        # 3. 総当たり推論
        for cand in candidates:
            # 仮想のルート音（ダミールート）をベース音のオクターブに生成
            dummy_root = Note(cand.step, cand.alter, bass_note.octave)
            
            # もしダミールートがベース音より高くなってしまったら、1オクターブ下げる
            # (例: ベースが E4 で、仮ルートが G の場合、G4 だと E4 より高くなるため G3 にする)
            if dummy_root.absolute_semitone > bass_note.absolute_semitone:
                dummy_root.octave -= 1
                
            intervals = set()
            for note in sorted_notes:
                intervals.add(self._get_interval(dummy_root, note))
                
            # 辞書と照合
            quality = self.chord_dictionary.get(frozenset(intervals))
            
            if quality:
                # 4. 推論に成功した場合の出力フォーマット
                cand_alter_str = "#" if cand.alter == 1 else "b" if cand.alter == -1 else ""
                root_name = f"{cand.step}{cand_alter_str}"
                
                bass_alter_str = "#" if bass_note.alter == 1 else "b" if bass_note.alter == -1 else ""
                bass_name = f"{bass_note.step}{bass_alter_str}"
                
                # ルートとベースが同じなら通常コード、違えばオンコード
                if cand.pitch_class == bass_note.pitch_class:
                    chord_name = f"{root_name} {quality}"
                else:
                    chord_name = f"{root_name} {quality} / {bass_name}"
                    
                notes_str = ", ".join(str(n) for n in sorted_notes)
                intervals_str = ", ".join(intervals)
                return f"Input: [{notes_str}] -> Analyzed: {chord_name}"

        # どのルートを仮定しても辞書にない場合
        notes_str = ", ".join(str(n) for n in sorted_notes)
        bass_alter_str = "#" if bass_note.alter == 1 else "b" if bass_note.alter == -1 else ""
        bass_name = f"{bass_note.step}{bass_alter_str}"
        return f"Input: [{notes_str}] -> Analyzed: Unknown (Bass: {bass_name})"

# --- 実行テスト ---
if __name__ == "__main__":
    analyzer = ChordAnalyzer()

    # 以前のテスト
    print("Test 1:", analyzer.analyze(parse_notes("C, E, G")))
    print("Test 2:", analyzer.analyze(parse_notes("C, Fb, G")))
    print("Test 3:", analyzer.analyze(parse_notes("B4, D5, F5, Ab5")))

    # 今回のテンションテスト
    print("Test 4:", analyzer.analyze(parse_notes("C4, E4, G4, D5"))) # Add9
    print("Test 5:", analyzer.analyze(parse_notes("C4, E4, G4, B4, D5"))) # Maj9
    print("Test 6:", analyzer.analyze(parse_notes("G4, B4, D5, F5, Ab5"))) # Dom7(b9)
    print("Test 7:", analyzer.analyze(parse_notes("C4, G4, E5"))) # C Major (E5がM3に正規化されるか)
    # テスト8: Cメジャーの第一転回形 (ミ・ソ・ド)
    print("Test 8:", analyzer.analyze(parse_notes("E4, G4, C5")))
    
    # テスト9: Cメジャーの第二転回形 (ソ・ド・ミ)
    print("Test 9:", analyzer.analyze(parse_notes("G3, C4, E4")))
    
    # テスト10: テンションを含む複雑なオンコード (C Dom9 / E)
    print("Test 10:", analyzer.analyze(parse_notes("E3, Bb3, C4, D4, G4")))

    # テスト11: 入力順がバラバラでも自動でソートしてベース音を判定できるか
    print("Test 11:", analyzer.analyze(parse_notes("C4, G3, E4")))