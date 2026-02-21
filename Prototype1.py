from dataclasses import dataclass
from typing import List

# 1. データ構造の定義：音（Note）
@dataclass
class Note:
    step: str      # 基本音名: 'C', 'D', 'E', 'F', 'G', 'A', 'B'
    alter: int     # 変化記号: -2(bb), -1(b), 0(♮), 1(#), 2(x)
    octave: int    # オクターブ: 4が中央ド(C4)

    def __post_init__(self):
        self.step = self.step.upper()

    # Cを基準としたときの基本音名の半音数（計算用）
    STEP_TO_SEMITONE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    @property
    def absolute_semitone(self) -> int:
        """
        高さの比較用に、C0を基準とした絶対的な半音数を計算します。
        ※これをそのまま異名同音の判定に使うとC#とDbが同じになりますが、
        ここでは「どの音が一番低いか(ベース音)」を判別するために使います。
        """
        base = self.STEP_TO_SEMITONE[self.step]
        return base + self.alter + (self.octave * 12)

    def __str__(self):
        alter_str = ""
        if self.alter == 1: alter_str = "#"
        elif self.alter == -1: alter_str = "b"
        elif self.alter == 2: alter_str = "x"
        elif self.alter == -2: alter_str = "bb"
        return f"{self.step}{alter_str}{self.octave}"

# 2. 推論エンジン：コードアナライザー
class ChordAnalyzer:
    def __init__(self):
        # 拡張性を考慮した辞書
        # プロトタイプとして、ルート音からの「半音数」の集合で品質(Quality)を定義します。
        # ※今後の拡張で、これを「度数(Interval)」の判定に切り替えます。
        self.chord_dictionary = {
            frozenset([0, 4, 7]): "Major",
            frozenset([0, 3, 7]): "Minor",
            frozenset([0, 4, 7, 11]): "Maj7",
            frozenset([0, 3, 7, 10]): "Min7",
            frozenset([0, 4, 7, 10]): "Dom7",
            frozenset([0, 3, 6, 9]): "Dim7",
            frozenset([0, 4, 8]): "Aug",
        }

    def analyze(self, notes: List[Note]) -> str:
        if not notes:
            return "No notes provided"

        # 1. ボイシングの解析: 一番低い音(ベース音)を特定する
        sorted_notes = sorted(notes, key=lambda n: n.absolute_semitone)
        bass_note = sorted_notes[0]
        
        # プロトタイプなので、とりあえず「一番下の音＝ルート音」として仮定します。
        # （転回形の対応は今後の拡張ポイントです）
        root_note = bass_note 

        # 2. ルートからの相対的な半音程を計算（1オクターブ内に丸める）
        intervals = set()
        for note in sorted_notes:
            diff = (note.absolute_semitone - root_note.absolute_semitone) % 12
            intervals.add(diff)

        # 3. 辞書とパターンマッチング
        quality = self.chord_dictionary.get(frozenset(intervals), "Unknown")
        
        # 4. ルート音のフォーマット
        alter_str = "#" if root_note.alter == 1 else "b" if root_note.alter == -1 else ""
        root_name = f"{root_note.step}{alter_str}"

        # 構成音を文字列化して返す
        notes_str = ", ".join(str(n) for n in sorted_notes)
        return f"Input: [{notes_str}] -> Analyzed: {root_name} {quality}"

# 3. 実行テスト
if __name__ == "__main__":
    analyzer = ChordAnalyzer()

    # テストケース1: Cメジャー (C4, E4, G4)
    c_maj = [Note('C', 0, 4), Note('E', 0, 4), Note('G', 0, 4)]
    print(analyzer.analyze(c_maj))

    # テストケース2: Dマイナーセブンス (D3, F3, A3, C4)
    # オクターブをまたいでも判定できるかテスト
    d_min7 = [Note('D', 0, 3), Note('A', 0, 3), Note('C', 0, 4), Note('F', 0, 3)]
    print(analyzer.analyze(d_min7))

    # テストケース3: Ebメジャーセブンス (Eb4, G4, Bb4, D5)
    eb_maj7 = [Note('E', -1, 4), Note('G', 0, 4), Note('B', -1, 4), Note('D', 0, 5)]
    print(analyzer.analyze(eb_maj7))

#a