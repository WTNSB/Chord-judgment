# dictionaries/interval_dict.py

# 協和音程・不協和音程の分類と、純正律（Just Intonation）における理想的な周波数比
INTERVAL_INFO_DICT = {
    # --- 完全協和音程 (Perfect Consonance) ---
    'P1': {'type': 'Perfect Consonance', 'ratio': (1, 1), 'name': 'Perfect Unison'},
    'P4': {'type': 'Perfect Consonance', 'ratio': (4, 3), 'name': 'Perfect 4th'},
    'P5': {'type': 'Perfect Consonance', 'ratio': (3, 2), 'name': 'Perfect 5th'},
    'P8': {'type': 'Perfect Consonance', 'ratio': (2, 1), 'name': 'Perfect Octave'},

    # --- 不完全協和音程 (Imperfect Consonance) ---
    'm3': {'type': 'Imperfect Consonance', 'ratio': (6, 5), 'name': 'Minor 3rd'},
    'M3': {'type': 'Imperfect Consonance', 'ratio': (5, 4), 'name': 'Major 3rd'},
    'm6': {'type': 'Imperfect Consonance', 'ratio': (8, 5), 'name': 'Minor 6th'},
    'M6': {'type': 'Imperfect Consonance', 'ratio': (5, 3), 'name': 'Major 6th'},

    # --- 不協和音程 (Dissonance) ---
    'm2': {'type': 'Dissonance', 'ratio': (16, 15), 'name': 'Minor 2nd'},
    'M2': {'type': 'Dissonance', 'ratio': (9, 8),  'name': 'Major 2nd'}, # 大全音の場合(9:8)。小全音(10:9)の解釈もあり
    'A4': {'type': 'Dissonance', 'ratio': (45, 32), 'name': 'Augmented 4th (Tritone)'},
    'd5': {'type': 'Dissonance', 'ratio': (64, 45), 'name': 'Diminished 5th (Tritone)'},
    'm7': {'type': 'Dissonance', 'ratio': (9, 5),  'name': 'Minor 7th'}, # 純正小7度(16:9)や自然7度(7:4)など諸説あり
    'M7': {'type': 'Dissonance', 'ratio': (15, 8), 'name': 'Major 7th'},

    # --- テンション（オクターブ上の不協和音程・協和音程） ---
    'm9': {'type': 'Dissonance', 'ratio': (32, 15), 'name': 'Minor 9th'},
    'M9': {'type': 'Dissonance', 'ratio': (9, 4),  'name': 'Major 9th'},
    'A9': {'type': 'Dissonance', 'ratio': (19, 8), 'name': 'Augmented 9th'}, # 近似値
    'P11': {'type': 'Perfect Consonance', 'ratio': (8, 3), 'name': 'Perfect 11th'},
    'A11': {'type': 'Dissonance', 'ratio': (45, 16), 'name': 'Augmented 11th'},
    'm13': {'type': 'Imperfect Consonance', 'ratio': (16, 5), 'name': 'Minor 13th'},
    'M13': {'type': 'Imperfect Consonance', 'ratio': (10, 3), 'name': 'Major 13th'},
}

def get_dissonance_score(interval_name: str) -> int:
    """
    将来的な機能拡張用：音程の不協和度を数値化して返す（簡易版）
    0: 完全協和, 1: 不完全協和, 3: 不協和（マイルド）, 5: 強い不協和（トライトーン等）
    """
    info = INTERVAL_INFO_DICT.get(interval_name)
    if not info:
        return 0

    itype = info['type']
    if itype == 'Perfect Consonance':
        return 0
    elif itype == 'Imperfect Consonance':
        return 1
    elif itype == 'Dissonance':
        if interval_name in ['m2', 'M7', 'm9', 'A4', 'd5']:
            return 5 # 特にぶつかりの強い音程
        return 3 # M2, m7などのマイルドな不協和
    return 0