# dictionaries/chord_dict.py

CHORD_DICT = {
    # --- トライアド（3和音）系 ---
    frozenset(['P1', 'M3', 'P5']): "Major",
    frozenset(['P1', 'm3', 'P5']): "Minor",
    frozenset(['P1', 'm3', 'd5']): "Dim",        # ディミニッシュ・トライアド
    frozenset(['P1', 'M3', 'A5']): "Aug",        # オーギュメント
    frozenset(['P1', 'M2', 'P5']): "sus2",       
    frozenset(['P1', 'P4', 'P5']): "sus4",       
    frozenset(['P1', 'P5']): "5",               

    # --- シックス（6th）系 ---
    frozenset(['P1', 'M3', 'P5', 'M6']): "6",
    frozenset(['P1', 'm3', 'P5', 'M6']): "m6",

    # --- セブンス（4和音）系 ---
    frozenset(['P1', 'M3', 'P5', 'M7']): "Maj7",
    frozenset(['P1', 'm3', 'P5', 'm7']): "m7",
    frozenset(['P1', 'M3', 'P5', 'm7']): "7",    # ドミナントセブンス（表記をスッキリ '7' に）
    frozenset(['P1', 'm3', 'P5', 'M7']): "mM7",  # マイナーメジャーセブンス
    frozenset(['P1', 'P4', 'P5', 'm7']): "7sus4",
    frozenset(['P1', 'm3', 'd5', 'd7']): "dim7", # フルディミニッシュ
    frozenset(['P1', 'm3', 'd5', 'm7']): "m7b5", # ハーフディミニッシュ
    frozenset(['P1', 'M3', 'd5', 'm7']): "7b5",
    frozenset(['P1', 'M3', 'A5', 'm7']): "aug7", # または 7#5
    frozenset(['P1', 'M3', 'A5', 'M7']): "augM7",

    # --- 9th テンション系 ---
    frozenset(['P1', 'M3', 'P5', 'M9']): "add9",
    frozenset(['P1', 'm3', 'P5', 'M9']): "m(add9)",
    frozenset(['P1', 'M3', 'P5', 'M7', 'M9']): "Maj9",
    frozenset(['P1', 'm3', 'P5', 'm7', 'M9']): "m9",
    frozenset(['P1', 'M3', 'P5', 'm7', 'M9']): "9",
    frozenset(['P1', 'M3', 'P5', 'm7', 'm9']): "7(b9)",
    frozenset(['P1', 'M3', 'P5', 'm7', 'A9']): "7(#9)",
    frozenset(['P1', 'm3', 'd5', 'm7', 'M9']): "m9b5",

    # --- 11th テンション系 ---
    frozenset(['P1', 'M3', 'P5', 'M7', 'M9', 'P11']): "Maj11",
    frozenset(['P1', 'm3', 'P5', 'm7', 'M9', 'P11']): "m11",
    frozenset(['P1', 'M3', 'P5', 'm7', 'M9', 'P11']): "11",
    frozenset(['P1', 'M3', 'P5', 'M7', 'M9', 'A11']): "Maj7(#11)", # Maj13(#11) の基礎
    frozenset(['P1', 'M3', 'P5', 'm7', 'M9', 'A11']): "7(#11)",

    # --- 13th テンション系 ---
    frozenset(['P1', 'M3', 'P5', 'M7', 'M9', 'P11', 'M13']): "Maj13",
    frozenset(['P1', 'm3', 'P5', 'm7', 'M9', 'P11', 'M13']): "m13",
    frozenset(['P1', 'M3', 'P5', 'm7', 'M9', 'P11', 'M13']): "13",
    frozenset(['P1', 'M3', 'P5', 'm7', 'M9', 'm13']): "7(b13)",

    # --- オミット（省略）系などの特殊ボイシング対応 ---
    # ギターやピアノでよくある「5度抜き（Root, 3rd, 7thのみ）」のコード
    frozenset(['P1', 'M3', 'M7']): "Maj7(omit5)",
    frozenset(['P1', 'm3', 'm7']): "m7(omit5)",
    frozenset(['P1', 'M3', 'm7']): "7(omit5)",

    # --- 4度堆積（Quartal Harmony）系 ---
    # モダンジャズなどで多用される完全4度を積み重ねたボイシング
    # (例) C - F - Bb -> P1, P4, m7
    frozenset(['P1', 'P4', 'm7']): "Quartal(3-note)", # または 7sus4(omit5)
    
    # (例) C - F - Bb - Eb -> P1, P4, m7, m3 (1オクターブ上のEbはm3に正規化される)
    frozenset(['P1', 'P4', 'm7', 'm3']): "Quartal(4-note)", 
    
    # (例) C - F - Bb - Eb - Ab -> P1, P4, m7, m3, m13 (Abは6度ベースでオクターブを超えるのでm13)
    frozenset(['P1', 'P4', 'm7', 'm3', 'm13']): "Quartal(5-note)",

    # --- クラシックの特殊和音（増6の和音） ---
    # ここが「異名同音の区別」の真骨頂です。Dom7(m7)とは異なり、増6度(A6)として解釈します。
    frozenset(['P1', 'M3', 'A6']): "It+6",         # イタリアの増6 (Italian 6th)
    frozenset(['P1', 'M3', 'A4', 'A6']): "Fr+6",   # フランスの増6 (French 6th)
    frozenset(['P1', 'M3', 'P5', 'A6']): "Gr+6",   # ドイツの増6 (German 6th)
    
    # --- クラスター・その他 ---
    frozenset(['P1', 'm2', 'M2']): "Tone Cluster", # 音の塊（長2度と短2度の密集）
    frozenset(['P1', 'P5', 'M9']): "Quintal(3-note)", # 5度堆積 (C - G - D)
}