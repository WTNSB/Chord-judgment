from models.note import Note

INTERVAL_MAP = {
    (0, 0): 'P1',  (0, 1): 'A1',  (0, -1): 'd1',
    (1, 1): 'm2',  (1, 2): 'M2',  (1, 3): 'A2',  (1, 0): 'd2',
    (2, 3): 'm3',  (2, 4): 'M3',  (2, 5): 'A3',  (2, 2): 'd3',
    (3, 5): 'P4',  (3, 6): 'A4',  (3, 4): 'd4',
    (4, 7): 'P5',  (4, 8): 'A5',  (4, 6): 'd5',
    (5, 8): 'm6',  (5, 9): 'M6',  (5, 10): 'A6', (5, 7): 'd6',
    (6, 10): 'm7', (6, 11): 'M7', (6, 12): 'A7', (6, 9): 'd7'
}

def get_interval(root: Note, target: Note) -> str:
    step_diff = (target.step_index - root.step_index) % 7
    semi_diff = (target.absolute_semitone - root.absolute_semitone) % 12
    
    base_interval = INTERVAL_MAP.get((step_diff, semi_diff))
    if not base_interval:
        return f"Unknown({step_diff},{semi_diff})"
        
    actual_semi_diff = target.absolute_semitone - root.absolute_semitone
    quality = base_interval[0] 
    number = int(base_interval[1:]) 
    
    if actual_semi_diff >= 12 and number in [2, 4, 6]:
        return f"{quality}{number + 7}"
        
    return base_interval