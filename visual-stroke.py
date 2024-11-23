# A visual stroke dictionary.
import re
from enum import Enum

LONGEST_KEY = 2

SHOW_STROKE_TRIGGER = 'STR*Z'

PARTS_MATCHER = re.compile(
    r'(#?)(S?)(T?)(K?)(P?)(W?)(H?)(R?)(A?)(O?)([-*]?)(E?)(U?)(F?)(R?)(P?)(B?)(L?)(G?)(T?)(S?)(D?)(Z?)'
)

space = " "
gap = " " + space
indent = f'{gap * 3}'
newline = "\n"
always_full_form = False

class Form(Enum):
    full = 1
    left_full = 2
    right_full = 3
    left_consonants = 4
    right_consonants = 5

def define_form(hands):
    (left, right) = (hands.left.to_clusters(), hands.right.to_clusters())
    any_vowels = left.vowels or right.vowels
    if left.consonants and not (right.consonants or any_vowels):
        return Form.left_consonants
    elif right.consonants and not (left.consonants or any_vowels):
        return Form.right_consonants
    left_full = left.consonants and left.vowels
    left_any = left.consonants or left.vowels
    right_full = right.consonants and right.vowels
    right_any = right.consonants or right.vowels
    if left_full and not right_any:
        return Form.left_full
    elif right_full and not left_any:
        return Form.right_full
    return Form.full

class Hand:
    def __init__(self, top: list[str], middle: list[str], base: list[str]):
        self.top = top
        self.middle = middle
        self.base = base

    def join(self) -> Hand:
        rows = self.__dict__
        for name, row in rows.items():
            for i in range(len(row)):
                if row[i] == '' :
                    row[i] = '-'
            rows[name] = space.join(row).lower()
        return Hand(rows['top'], rows['middle'], rows['base']) 

    def to_clusters(self):
        consonants = self.check(self.top) and self.check(self.middle)
        vowels = self.check(self.base)
        return Clusters(consonants, vowels)

    @staticmethod
    def check(row) -> bool:
        if ''.join(row) == "":
            return False
        else:
            return True

class Hands:
    def __init__(self, left: Hand, right: Hand):
        self.left = left
        self.right = right

class Clusters():
    def __init__(self, consonants: bool, vowels: bool):
        self.consonants = consonants
        self.vowels = vowels

def add_newlines_to_rows(*rows):
    result = map(lambda row: f"{newline}{row}", rows)
    return ''.join(result) + newline

def construct_full(left, right, star):
    star_gap = space + star + gap + star + space
    top =    left.top           + star_gap + right.top
    middle = left.middle        + star_gap + right.middle 
    base =   indent + left.base + gap      + right.base
    return add_newlines_to_rows(top, middle, base)

def construct_left_full(left, star):
    star_gap = space + star
    top =    left.top           + star_gap
    middle = left.middle        + star_gap
    base =   indent + left.base
    return add_newlines_to_rows(top, middle, base)

def construct_right_full(right, star):
    star_gap = star + space
    top =    star_gap + right.top
    middle = star_gap + right.middle 
    base =   right.base
    return add_newlines_to_rows(top, middle, base)

def construct_left_consonants(left):
    top =    left.top
    middle = left.middle
    return add_newlines_to_rows(top, middle)

def construct_right_consonants(right):
    top =    right.top
    middle = right.middle 
    return add_newlines_to_rows(top, middle)

def construction(hands, star, form):
    left = hands.left.join() 
    right = hands.right.join()
    if star == '':
        star = '-'
    if form == Form.full:
       return construct_full(left, right, star)
    elif form == Form.left_full:
       return construct_left_full(left, star)
    elif form == Form.right_full:
       return construct_right_full(right, star)
    elif form == Form.left_consonants:
       return construct_left_consonants(left)
    elif form == Form.right_consonants:
       return construct_right_consonants(right)


def lookup(key):
    assert len(key) <= LONGEST_KEY, '%d/%d' % (len(key), LONGEST_KEY)
    if SHOW_STROKE_TRIGGER != key[0]:
        raise KeyError
    if len(key) == 1:
        return ' '

    stroke = key[1]
    match = PARTS_MATCHER.fullmatch(stroke)
    if not match:
        raise KeyError
    (ht, s1, t1, k, p1, w, h, r1, a, o, star, e, u, f,
     r2, p2, b, l, g, t2, s2, d, z) = match.groups()

    left = Hand( [ht, t1, p1, h], [s1, k, w, r1], [a, o] )
    right = Hand( [f, p2, l, t2, d], [r2, b, g, s2, z], [e, u] )
    hands = Hands(left, right)
    form = Form.full if always_full_form else define_form(hands)
    return construction(hands, star, form)
