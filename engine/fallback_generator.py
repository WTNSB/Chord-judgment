from typing import Set, Optional

class RuleBasedGenerator:
    """辞書にない未知のテンション和音を、骨格とテンションに分解して動的生成するクラス"""

    @staticmethod
    def generate_chord_name(intervals: Set[str]) -> Optional[str]:
        # 1. 骨格の判定（3度、5度、7度の組み合わせ）
        has_M3 = 'M3' in intervals
        has_m3 = 'm3' in intervals
        has_M7 = 'M7' in intervals
        has_m7 = 'm7' in intervals
        has_P5 = 'P5' in intervals
        has_d5 = 'd5' in intervals
        has_A5 = 'A5' in intervals
        has_d7 = 'd7' in intervals

        base = "Unknown"
        
        # 4和音の骨格判定（特殊な5度を含むものを優先して判定）
        if has_M3 and has_A5 and has_m7: base = "aug7"
        elif has_M3 and has_A5 and has_M7: base = "augM7"
        elif has_m3 and has_d5 and has_m7: base = "m7b5"
        elif has_m3 and has_d5 and has_d7: base = "dim7"
        elif has_M3 and has_M7: base = "Maj7"
        elif has_m3 and has_m7: base = "m7"
        elif has_M3 and has_m7: base = "7"  # ドミナントセブンス
        elif has_m3 and has_M7: base = "mM7"
        # 3和音の骨格判定
        elif has_M3 and has_A5: base = "aug"
        elif has_m3 and has_d5: base = "dim"
        elif has_M3: base = "Major"
        elif has_m3: base = "Minor"

        # 3度がなく、sus系やパワーコードの骨格の場合は辞書引きに任せるためここでは弾く
        if base == "Unknown":
            return None

        # 2. テンションの抽出
        tensions = []
        if 'm9' in intervals: tensions.append("b9")
        if 'M9' in intervals: tensions.append("9")
        if 'A9' in intervals: tensions.append("#9")
        if 'P11' in intervals: tensions.append("11")
        if 'A11' in intervals: tensions.append("#11")
        if 'm13' in intervals: tensions.append("b13")
        if 'M13' in intervals: tensions.append("13")

        tension_str = ""
        if tensions:
            tension_str = f"({', '.join(tensions)})"

        # 3. Omit5判定 (5度の音がどれも含まれていない場合)
        omit_str = ""
        if not (has_P5 or has_d5 or has_A5) and base not in ["dim7", "dim", "aug", "aug7", "augM7", "m7b5"]:
            omit_str = "(omit5)"

        # 例: 骨格が "aug7" で、テンションが "#9" の場合 -> "aug7(#9)"
        return f"{base}{tension_str}{omit_str}"