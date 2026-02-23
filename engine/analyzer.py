from typing import List, Dict, Any, Set
from models.note import Note
from utils.interval_calc import get_interval
from dictionaries.chord_dict import CHORD_DICT
from engine.fallback_generator import RuleBasedGenerator

class ChordAnalyzer:
    def __init__(self):
        self.chord_dictionary = CHORD_DICT

    def analyze(self, notes: List[Note], threshold: int = 10) -> str:
        if not notes: return "No notes"

        sorted_notes = sorted(notes, key=lambda n: n.absolute_semitone)
        bass_note = sorted_notes[0]
        bass_alter_str = "#" if bass_note.alter == 1 else "b" if bass_note.alter == -1 else ""
        bass_name = f"{bass_note.step}{bass_alter_str}"
        
        spread = sorted_notes[-1].absolute_semitone - sorted_notes[0].absolute_semitone
        voicing_type = "Open" if spread > 12 else "Closed"

        input_pcs = {n.pitch_class for n in sorted_notes}
        unique_cands = {n.pitch_class: n for n in sorted_notes}

        categorized_results = {
            "基本形 (Root Position)": [],
            "転回形 (Inversion)": [],
            "オンコード (On-Chord)": [],
            "ルートレス (Rootless)": [],
            "特殊形 (Special)": []
        }

        # 各探索フェーズの実行（今後フェーズが増えたらここに足す）
        self._search_normal(sorted_notes, unique_cands, bass_note, bass_name, voicing_type, categorized_results)
        self._search_rootless(sorted_notes, input_pcs, bass_note, bass_name, voicing_type, categorized_results)
        
        
        self._search_ust_and_polychord(sorted_notes, unique_cands, input_pcs, bass_note, bass_name, voicing_type, categorized_results)
        self._search_fallback_rulebased(sorted_notes, unique_cands, bass_note, bass_name, voicing_type, categorized_results)

        return self._format_output(sorted_notes, bass_name, categorized_results, threshold)
    
    def _search_fallback_rulebased(self, sorted_notes: List[Note], unique_cands: dict, bass_note: Note, bass_name: str, voicing_type: str, results: dict):
        """辞書にないテンションの組み合わせを動的生成する"""
        for root_pc, cand in unique_cands.items():
            dummy_root = Note(cand.step, cand.alter, bass_note.octave)
            if dummy_root.absolute_semitone > bass_note.absolute_semitone:
                dummy_root.octave -= 1
                
            intervals = {get_interval(dummy_root, note) for note in sorted_notes}
            cand_alter_str = "#" if cand.alter == 1 else "b" if cand.alter == -1 else ""
            root_name = f"{cand.step}{cand_alter_str}"
            is_root_pos = (root_pc == bass_note.pitch_class)

            if self.chord_dictionary.get(frozenset(intervals)):
                continue
            
            intervals_with_p5 = set(intervals)
            intervals_with_p5.add('P5')
            if 'P5' not in intervals and self.chord_dictionary.get(frozenset(intervals_with_p5)):
                continue

            # ★ 変更点：複数の解釈（表記ブレ）をリストで受け取る
            generated_qualities = RuleBasedGenerator.generate_chord_names(intervals)
            
            for generated_quality in generated_qualities:
                # テンションが含まれている、または特殊な表記の場合
                if "(" in generated_quality or "aug" in generated_quality:
                    category = self._get_category(is_root_pos, False, generated_quality, root_pc, bass_note)
                    
                    score = 55 if is_root_pos else 35 
                    tension_count = generated_quality.count(',') + 1 if "(" in generated_quality and "omit5" not in generated_quality else 0
                    score += tension_count * 5

                    name = f"{root_name} {generated_quality}" if is_root_pos else f"{root_name} {generated_quality} / {bass_name}"
                    
                    if not any(r['name'].startswith(name) for r in results[category]):
                        results[category].append({"name": f"{name} ({voicing_type}) [生成]", "score": score})

    def _search_ust_and_polychord(self, sorted_notes: List[Note], unique_cands: Dict[int, Note], input_pcs: Set[int], bass_note: Note, bass_name: str, voicing_type: str, results: Dict):
        """アッパーストラクチャートライアドUSTおよびポリコードの分割探索"""
        # 構成音が4音未満の場合はUSTを構成できないためスキップ
        if len(input_pcs) < 4:
            return

        # トライアドの構成音程（半音差）
        triads = {
            "Major": [0, 4, 7],
            "Minor": [0, 3, 7],
            "Aug": [0, 4, 8],
            "Dim": [0, 3, 6]
        }

        # ボトム（下部構造）のルートはベース音であると仮定
        bottom_root_pc = bass_note.pitch_class
        bottom_cand = unique_cands.get(bottom_root_pc)
        if not bottom_cand:
            return

        bottom_dummy_root = Note(bottom_cand.step, bottom_cand.alter, bass_note.octave)
        if bottom_dummy_root.absolute_semitone > bass_note.absolute_semitone:
            bottom_dummy_root.octave -= 1

        # 入力音の中から「上部構造（トップ）のルート」となる候補をすべて試す
        for top_pc, top_cand in unique_cands.items():
            if top_pc == bottom_root_pc:
                continue # トップとボトムのルートが同じならUSTではない

            for triad_name, intervals_semi in triads.items():
                # 仮定したトップトライアドのピッチクラス集合を生成
                top_triad_pcs = {(top_pc + i) % 12 for i in intervals_semi}
                
                # トップトライアドが入力音に「完全に」含まれているかチェック
                if top_triad_pcs.issubset(input_pcs):
                    
                    # トップの音を除外した残りの音をボトムとする
                    bottom_pcs = input_pcs - top_triad_pcs
                    bottom_pcs.add(bottom_root_pc) # ボトムルートは必ず含むものとする

                    # ボトムの音程（インターバル）を計算
                    bottom_intervals = set()
                    for pc in bottom_pcs:
                        note_for_interval = next((n for n in sorted_notes if n.pitch_class == pc), None)
                        if note_for_interval:
                            interval = get_interval(bottom_dummy_root, note_for_interval)
                            # 骨格判定のため、9, 11, 13度を1オクターブ内(2, 4, 6度)に丸め直す
                            if interval[1:] in ['9', '11', '13']:
                                interval = f"{interval[0]}{int(interval[1:]) - 7}"
                            bottom_intervals.add(interval)

                    # ボトムが特定のコード骨格（特に 7th 系）を形成しているか判定
                    has_M3 = 'M3' in bottom_intervals
                    has_m3 = 'm3' in bottom_intervals
                    has_m7 = 'm7' in bottom_intervals
                    has_M7 = 'M7' in bottom_intervals

                    bottom_quality = None
                    if has_M3 and has_m7: bottom_quality = "7"
                    elif has_m3 and has_m7: bottom_quality = "m7"
                    elif has_M3 and has_M7: bottom_quality = "Maj7"
                    elif has_m3 and 'd5' in bottom_intervals and has_m7: bottom_quality = "m7b5"
                    elif has_M3: bottom_quality = "" # Major
                    elif has_m3: bottom_quality = "m"

                    # ボトムが和音として成立していれば、USTとして出力！
                    if bottom_quality is not None:
                        top_alter_str = "#" if top_cand.alter == 1 else "b" if top_cand.alter == -1 else ""
                        top_name = f"{top_cand.step}{top_alter_str}"
                        # Majorトライアドの場合は "D Major" ではなく単に "D" と表記する
                        top_chord_name = top_name if triad_name == "Major" else f"{top_name} {triad_name}"

                        bottom_alter_str = "#" if bottom_cand.alter == 1 else "b" if bottom_cand.alter == -1 else ""
                        bottom_name = f"{bottom_cand.step}{bottom_alter_str}"

                        ust_name = f"{top_chord_name} / {bottom_name}{bottom_quality}"
                        
                        # USTは意図的な高度なボイシングなので非常に高く評価する
                        score = 80 
                        
                        if not any(r['name'].startswith(ust_name) for r in results["特殊形 (Special)"]):
                            results["特殊形 (Special)"].append({"name": f"{ust_name} (UST) ({voicing_type})", "score": score})

    def _get_category(self, is_root_position: bool, is_rootless: bool, quality: str, dummy_root_pc: int, bass_note: Note) -> str:
        if any(sq in quality for sq in ["Quartal", "Quintal", "+6", "Cluster"]):
            return "特殊形 (Special)"
        if is_rootless:
            return "ルートレス (Rootless)"
        if is_root_position:
            return "基本形 (Root Position)"
            
        bass_interval = (bass_note.pitch_class - dummy_root_pc) % 12
        chord_tone_intervals = {3, 4, 6, 7, 8, 10, 11}
        if bass_interval in chord_tone_intervals:
            return "転回形 (Inversion)"
        else:
            return "オンコード (On-Chord)"

    def _search_normal(self, sorted_notes: List[Note], unique_cands: Dict[int, Note], bass_note: Note, bass_name: str, voicing_type: str, results: Dict):
        for root_pc, cand in unique_cands.items():
            dummy_root = Note(cand.step, cand.alter, bass_note.octave)
            if dummy_root.absolute_semitone > bass_note.absolute_semitone:
                dummy_root.octave -= 1
                
            intervals = {get_interval(dummy_root, note) for note in sorted_notes}
            cand_alter_str = "#" if cand.alter == 1 else "b" if cand.alter == -1 else ""
            root_name = f"{cand.step}{cand_alter_str}"
            is_root_pos = (root_pc == bass_note.pitch_class)
            
            # A. 完全一致
            quality = self.chord_dictionary.get(frozenset(intervals))
            if quality:
                category = self._get_category(is_root_pos, False, quality, root_pc, bass_note)
                score = 80 if is_root_pos else 60
                
                if category == "特殊形 (Special)":
                    name = f"{quality} on {bass_name}"
                    score = 75 
                else:
                    name = f"{root_name} {quality}" if is_root_pos else f"{root_name} {quality} / {bass_name}"
                    
                results[category].append({"name": f"{name} ({voicing_type})", "score": score})
            
            # B. Omit5 補完
            if not quality and 'P5' not in intervals:
                intervals_with_p5 = set(intervals)
                intervals_with_p5.add('P5')
                quality_omit = self.chord_dictionary.get(frozenset(intervals_with_p5))
                
                if quality_omit:
                    category = self._get_category(is_root_pos, False, quality_omit, root_pc, bass_note)
                    score = 65 if is_root_pos else 45 
                    name = f"{root_name} {quality_omit}(omit5)" if is_root_pos else f"{root_name} {quality_omit}(omit5) / {bass_name}"
                    results[category].append({"name": f"{name} ({voicing_type})", "score": score})

    def _search_rootless(self, sorted_notes: List[Note], input_pcs: Set[int], bass_note: Note, bass_name: str, voicing_type: str, results: Dict):
        missing_pcs = [pc for pc in range(12) if pc not in input_pcs]
        phantom_map = {0:('C',0), 1:('C',1), 2:('D',0), 3:('E',-1), 4:('E',0), 5:('F',0), 6:('F',1), 7:('G',0), 8:('A',-1), 9:('A',0), 10:('B',-1), 11:('B',0)}
        
        for phantom_pc in missing_pcs:
            p_step, p_alter = phantom_map[phantom_pc]
            phantom_root = Note(p_step, p_alter, bass_note.octave)
            if phantom_root.absolute_semitone > bass_note.absolute_semitone:
                phantom_root.octave -= 1
                
            intervals = {'P1'}
            for note in sorted_notes:
                intervals.add(get_interval(phantom_root, note))
                
            quality = self.chord_dictionary.get(frozenset(intervals))
            is_omit5 = False
            
            if not quality and 'P5' not in intervals:
                intervals_with_p5 = set(intervals)
                intervals_with_p5.add('P5')
                quality = self.chord_dictionary.get(frozenset(intervals_with_p5))
                if quality: is_omit5 = True

            if quality and any(ext in quality for ext in ['7', '9', '11', '13', 'dim']):
                p_alter_str = "#" if p_alter == 1 else "b" if p_alter == -1 else ""
                root_name = f"{p_step}{p_alter_str}"
                
                tension_bonus = 0
                if '9' in quality: tension_bonus += 10
                if '11' in quality: tension_bonus += 15
                if '13' in quality: tension_bonus += 20
                
                score = 30 + tension_bonus - (10 if is_omit5 else 0)
                omit_str = "(omit5)" if is_omit5 else ""
                name = f"{root_name} {quality}{omit_str}(Rootless) / {bass_name}"
                results["ルートレス (Rootless)"].append({"name": f"{name} ({voicing_type})", "score": score})

    def _format_output(self, sorted_notes: List[Note], bass_name: str, categorized_results: Dict, threshold: int) -> str:
        notes_str = ", ".join(str(n) for n in sorted_notes)
        output_lines = [f"Input: [{notes_str}] (Bass: {bass_name})", "-"*40]
        
        has_results = False
        for category, results in categorized_results.items():
            filtered_results = sorted([r for r in results if r['score'] >= threshold], key=lambda x: x['score'], reverse=True)
            
            if filtered_results:
                has_results = True
                output_lines.append(f"■ {category}")
                seen = set()
                for res in filtered_results:
                    if res['name'] not in seen:
                        seen.add(res['name'])
                        output_lines.append(f"  - {res['name']} [Score: {res['score']}]")

        if not has_results:
            output_lines.append(f"Analyzed: Unknown (No interpretation scored above {threshold})")
            
        output_lines.append("-" * 40)
        return "\n".join(output_lines)