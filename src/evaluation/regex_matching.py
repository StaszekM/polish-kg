import re
from typing import Tuple, Union

# For an unquoted item, we use a lookahead to ensure there is at least one non-whitespace character.
# That alternative is: ((?=(?:.*\S))[^,\[\]]+)
item_pattern = r'''(?:"([^"]+)"|'([^']+)'|((?=(?:.*\S))[^,\[\]]+))'''

# Regex for exactly one pair of brackets: [ ... ]
pattern_single = re.compile(
    r'^\[\s*' +
    item_pattern + r'\s*,\s*' +
    item_pattern + r'\s*,\s*' +
    item_pattern + r'\s*\]$'
)

# Regex for exactly two pairs of brackets: [[ ... ]]
pattern_double = re.compile(
    r'^\[\[\s*' +
    item_pattern + r'\s*,\s*' +
    item_pattern + r'\s*,\s*' +
    item_pattern + r'\s*\]\]$'
)

def parse_string(s: str) -> Union[None, Tuple[str, str, str]]:
    """
    Tries to parse the string s with either the double-bracket or single-bracket regex.
    Returns a tuple of the three items if s is valid, or None otherwise.
    For each item, the function picks the first non-None capture.
    """
    m = pattern_double.match(s)
    if m is None:
        m = pattern_single.match(s)
    if m is None:
        return None
    
    groups = m.groups()
    # Each item is captured in three alternatives:
    # For pattern_single and pattern_double, the groups are:
    # item1: groups[0], groups[1], groups[2]
    # item2: groups[3], groups[4], groups[5]
    # item3: groups[6], groups[7], groups[8]
    def pick_item(grps):
        for g in grps:
            if g is not None:
                # Even though the regex should prevent pure whitespace, we strip to be safe.
                return g.strip()
        return None

    item1 = pick_item(groups[0:3])
    item2 = pick_item(groups[3:6])
    item3 = pick_item(groups[6:9])
    
    # Final check: none of the items may be empty.
    if not item1 or not item2 or not item3:
        return None
    return (item1, item2, item3)

# --- Testing the regex with various example strings ---


def validate():
    test_cases = [
        # Valid cases:
        ("[DJ Feel-X, zawód, DJ]", ("DJ Feel-X", "zawód", "DJ")),
        ("[[DJ Feel-X, zawód, DJ]]", ("DJ Feel-X", "zawód", "DJ")),
        ("[['DJ Feel-X', 'zawód', 'DJ']]", ("DJ Feel-X", "zawód", "DJ")),
        ('[["DJ Feel-X", "zawód", "DJ"]]', ("DJ Feel-X", "zawód", "DJ")),
        ('[ "DJ Feel-X" , \'zawód\' , DJ ]', ("DJ Feel-X", "zawód", "DJ")),
        ("[ABC, DEF, GHI]", ("ABC", "DEF", "GHI")),
        ("[[  one  ,  two  ,  three  ]]", ("one", "two", "three")),
        
        # Invalid cases (should return None):
        ("DJ, zawód, DJ", None),                # Missing brackets.
        ("(DJ, zawód, DJ)", None),               # Wrong type of brackets.
        ("{DJ, zawód, DJ}", None),               # Wrong bracket type.
        ("[DJ, zawód, DJ, extra]", None),        # More than 3 items.
        ("[DJ, zawód]", None),                   # Fewer than 3 items.
        ("[DJ, , DJ]", None),                    # Second item is empty.
        ("[DJ, zawód, ]", None),                 # Third item is empty.
        ("[DJ; zawód; DJ]", None),               # Wrong separators.
        ("[DJ, zawód, DJ]]", None),              # Mismatched brackets: extra closing.
        ("[[DJ, zawód, DJ]", None),              # Mismatched brackets: missing closing.
        ("[[DJ, zawód, DJ]] extra", None),       # Extra text after valid pattern.
        ("[[[DJ, zawód, DJ]]]", None),            # Too many brackets.
    ]

    for s, expected in test_cases:
        result = parse_string(s)
        print(f"Input: {s}")
        print(f"Parsed: {result}")
        print(f"Expected: {expected}")
        assert result == expected
        print("-" * 40)