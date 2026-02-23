from typing import Set, List

class RuleBasedGenerator:
    """辞書にない未知のテンション和音を、骨格とテンションに分解して動的生成するクラス"""

    @staticmethod
    def generate_chord_names(intervals: Set[str]) -> List[str]:
        # 1. 骨格の判定（3度、5度、7度の組み合わせ）
        has_M3 = 'M3' in intervals
        has_m3 = 'm3' in intervals
        has_M7 = 'M7' in intervals
        has_m7 = 'm7' in intervals
        has_P5 = 'P5' in intervals
        has_d5 = 'd5' in intervals
        has_A5 = 'A5' in intervals
        has_d7 = 'd7' in intervals

        base_options = []
        
        # 4和音の骨格判定（特殊な5度を含むものを優先して判定）
        if has_M3 and has_A5 and has_m7: 
            base_options.extend(["aug7", "7(#5)"])  # ★両方の表記を登録
        elif has_M3 and has_A5 and has_M7: 
            base_options.extend(["augM7", "Maj7(#5)"])
        elif has_m3 and has_d5 and has_m7: base_options.append("m7b5")
        elif has_m3 and has_d5 and has_d7: base_options.append("dim7")
        elif has_M3 and has_M7: base_options.append("Maj7")
        elif has_m3 and has_m7: base_options.append("m7")
        elif has_M3 and has_m7: base_options.append("7")  
        elif has_m3 and has_M7: base_options.append("mM7")
        
        # 3和音の骨格判定
        elif has_M3 and has_A5: base_options.append("aug")
        elif has_m3 and has_d5: base_options.append("dim")
        elif has_M3: base_options.append("Major")
        elif has_m3: base_options.append("Minor")

        if not base_options:
            return []

        # 2. テンションの抽出
        tensions = []
        if 'm9' in intervals: tensions.append("b9")
        if 'M9' in intervals: tensions.append("9")
        if 'A9' in intervals: tensions.append("#9")
        if 'P11' in intervals: tensions.append("11")
        if 'A11' in intervals: tensions.append("#11")
        if 'm13' in intervals: tensions.append("b13")
        if 'M13' in intervals: tensions.append("13")

        # 3. Omit5判定 (5度の音がどれも含まれていない場合)
        omit_str = ""
        rep_base = base_options[0]
        if not (has_P5 or has_d5 or has_A5) and rep_base not in ["dim7", "dim", "aug7", "augM7", "m7b5", "aug"]:
            omit_str = "(omit5)"

        # 4. 文字列の結合処理（カッコの中身を綺麗にまとめる）
        results = []
        for base in base_options:
            if "(" in base and tensions:
                # "7(#5)" のような表記に "#9" を足す場合 -> "7(#5, #9)" に整形
                base_stripped = base.rstrip(")")
                tension_joined = ", ".join(tensions)
                chord_name = f"{base_stripped}, {tension_joined}){omit_str}"
            else:
                tension_str = f"({', '.join(tensions)})" if tensions else ""
                chord_name = f"{base}{tension_str}{omit_str}"
            
            results.append(chord_name)

        return results