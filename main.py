from models.note import parse_notes
from engine.analyzer import ChordAnalyzer

# --- 実行テスト ---
if __name__ == "__main__":
    analyzer = ChordAnalyzer()
    
    print("Test 1:", analyzer.analyze(parse_notes("C, E, G")))
    print("Test 2:", analyzer.analyze(parse_notes("C, Fb, G")))
    print("Test 3:", analyzer.analyze(parse_notes("B4, D5, F5, Ab5")))

    # テンションテスト
    print("Test 4:", analyzer.analyze(parse_notes("C4, E4, G4, D5"))) # Add9
    print("Test 5:", analyzer.analyze(parse_notes("C4, E4, G4, B4, D5"))) # Maj9
    print("Test 6:", analyzer.analyze(parse_notes("G4, B4, D5, F5, Ab5"))) # Dom7(b9)
    print("Test 7:", analyzer.analyze(parse_notes("C4, G4, E5"))) # C Major (E5がM3に正規化されるか)
    
    # 転回形・オンコードテスト
    print("Test 8:", analyzer.analyze(parse_notes("E4, G4, C5")))
    print("Test 9:", analyzer.analyze(parse_notes("G3, C4, E4")))
    print("Test 10:", analyzer.analyze(parse_notes("E3, Bb3, C4, D4, G4")))
    print("Test 11:", analyzer.analyze(parse_notes("C4, G3, E4")))

    # エッジケース
    print("Test 12:", analyzer.analyze(parse_notes("C4, E4, G4, A4")))
    print("Test 13:", analyzer.analyze(parse_notes("B3, D4, F4, G4")))
    
    # 4度堆積と特殊系のテスト
    print("Test 14:", analyzer.analyze(parse_notes("C4, F4, Bb4, Eb5")))
    print("Test 15:", analyzer.analyze(parse_notes("C4, G4, D5")))

    # 増6和音 vs ドミナント
    print("Test 16-1:", analyzer.analyze(parse_notes("Ab3, C4, Eb4, Gb4")))
    print("Test 16-2:", analyzer.analyze(parse_notes("Ab3, C4, Eb4, F#4")))

    print("柴又テスト:", analyzer.analyze(parse_notes("G3, B3, D#4, F4, A#4")))

    print("b9th:", analyzer.analyze(parse_notes("C,E,G,Db")))