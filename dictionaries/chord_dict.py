CHORD_DICT = {
    # --- 基本和音 ---
    frozenset(['P1', 'M3', 'P5']): "Major",
    frozenset(['P1', 'm3', 'P5']): "Minor",
    frozenset(['P1', 'M3', 'P5', 'M7']): "Maj7",
    frozenset(['P1', 'm3', 'P5', 'm7']): "Min7",
    frozenset(['P1', 'M3', 'P5', 'm7']): "Dom7",
    frozenset(['P1', 'm3', 'd5', 'd7']): "Dim7",
    frozenset(['P1', 'm3', 'd5', 'm7']): "Min7b5",
    frozenset(['P1', 'M3', 'A5']): "Aug",
    

    frozenset(['P1', 'M3', 'P5', 'M6']): "6",
    frozenset(['P1', 'm3', 'P5', 'M6']): "m6",
    # --- テンションコード (9th) ---
    frozenset(['P1', 'M3', 'P5', 'M9']): "Add9",
    frozenset(['P1', 'M3', 'P5', 'M7', 'M9']): "Maj9",
    frozenset(['P1', 'm3', 'P5', 'm7', 'M9']): "Min9",
    frozenset(['P1', 'M3', 'P5', 'm7', 'M9']): "Dom9",
    frozenset(['P1', 'M3', 'P5', 'm7', 'm9']): "Dom7(b9)",
    frozenset(['P1', 'M3', 'P5', 'm7', 'A9']): "Dom7(#9)",
    
    # --- テンションコード (11th, 13th の例) ---
    frozenset(['P1', 'M3', 'P5', 'M7', 'M9', 'A11']): "Maj13(#11)", 
    # 必要に応じてどんどん追加可能
}