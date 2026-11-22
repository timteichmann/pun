"""
Pixel art for the tray icon: a hungry, box-shaped creature that eats
packages. The sprites are plain data so they can be composed and tested
without Qt; pun.py turns them into icons.

A sprite is a list of strings, one character per pixel:

    .  transparent
    B  body (the colour of the current state)
    D  dark body (outline, added automatically around B)
    W  white (eye, teeth)
    K  black (pupil, feet, digits)
    M  inside of the mouth
    P  parcel
    p  parcel tape and edges
    S  drool and bubbles
"""

SIZE = 16

BODY_COLORS = {
    "checking": (0xFF, 0x66, 0x00),
    "updates": (0xFF, 0x2A, 0x2A),
    "up_to_date": (0x00, 0x99, 0x00),
    "error": (0x88, 0x88, 0x88),
}

FIXED_COLORS = {
    "W": (0xFF, 0xFF, 0xFF),
    "K": (0x1A, 0x1A, 0x1A),
    "M": (0x4A, 0x10, 0x10),
    "P": (0xD9, 0xA0, 0x66),
    "p": (0x8F, 0x56, 0x3B),
    "S": (0x9C, 0xD8, 0xFF),
}

# the creature seen from the side, facing right
MUNCHER_OPEN = [
    ".BBBBBBB...",
    "BBBBBBBBBB.",
    "BBBBBBWWBB.",
    "BBBBBBWKBB.",
    "BBBBBBBBBBB",
    "BBBBBWMWMWM",
    "BBBBMMMMMMM",
    "BBBBMMMMMMM",
    "BBBBMMMMMMM",
    "BBBBBMWMWMW",
    "BBBBBBBBBBB",
    "BBBBBBBBBB.",
    ".BBBBBBBB..",
    ".KK...KK...",
]

MUNCHER_CLOSED = [
    ".BBBBBBB...",
    "BBBBBBBBBB.",
    "BBBBBBWWBB.",
    "BBBBBBWKBB.",
    "BBBBBBBBBBB",
    "BBBBBWBWBWB",
    "BBBBBKKKKKK",
    "BBBBBBBBBBB",
    "BBBBBBBBBB.",
    ".BBBBBBBB..",
    ".KK...KK...",
]

# stuffed and happy: eye closed, round belly
MUNCHER_FULL = [
    ".BBBBBBB....",
    "BBBBBBBBBB..",
    "BBBBBBKKBB..",
    "BBBBBKBBKB..",
    "BBBBBBBBBBB.",
    "BBBBBBBBBBB.",
    "BBBBBBKBBBK.",
    "BBBBBBBKKK..",
    "BBBBBBBBBBB.",
    "BBBBBBBBBBBB",
    "BBBBBBBBBBBB",
    ".BBBBBBBBBB.",
    ".KK....KK...",
]

# choking on a parcel: X eye, parcel stuck in the mouth
MUNCHER_CHOKING = [
    ".BBBBBBB.....",
    "BBBBBBBBBB...",
    "BBBBBKBKBB...",
    "BBBBBBKBBB...",
    "BBBBBKBKBBB..",
    "BBBBBWMWMWM..",
    "BBBBMMMPPPPP.",
    "BBBBMMMPpPpP.",
    "BBBBMMMPPPPP.",
    "BBBBBMWMWMW..",
    "BBBBBBBBBBB..",
    "BBBBBBBBBB...",
    ".BBBBBBBB....",
    ".KK...KK.....",
]

PARCEL = [
    "pPp",
    "PpP",
    "PpP",
]

BIG_PARCEL = [
    "ppppppppp",
    "pPPPpPPPp",
    "pPPPPPPPp",
    "pPPPPPPPp",
    "pPPPPPPPp",
    "pPPPPPPPp",
    "pPPPPPPPp",
    "pPPPPPPPp",
    "ppppppppp",
]

DIGITS = {
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", ".##", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    "!": ["#", "#", "#", ".", "#"],
}

# row of the floor the creature's feet stand on
FLOOR = SIZE - 1


def blank():
    return [["."] * SIZE for _ in range(SIZE)]


def paste(canvas, sprite, x, y):
    """Draws sprite onto canvas with its top left corner at (x, y)."""
    for dy, row in enumerate(sprite):
        for dx, char in enumerate(row):
            cx, cy = x + dx, y + dy
            if char != "." and 0 <= cx < SIZE and 0 <= cy < SIZE:
                canvas[cy][cx] = char


def paste_creature(canvas, sprite, x=0):
    """Draws a creature sprite standing on the floor, with an outline."""
    outlined = outline(sprite)
    paste(canvas, outlined, x, FLOOR - len(outlined) + 1)


def outline(sprite):
    """Darkens the body pixels at the edge of the body."""
    height = len(sprite)
    width = max(len(row) for row in sprite)
    rows = [row.ljust(width, ".") for row in sprite]

    def is_body(x, y):
        return 0 <= x < width and 0 <= y < height and rows[y][x] != "."

    result = []
    for y, row in enumerate(rows):
        line = ""
        for x, char in enumerate(row):
            if char == "B" and not all(is_body(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                char = "D"
            line += char
        result.append(line)
    return result


def text(value):
    """Renders a string with the digit font, one blank column between glyphs."""
    glyphs = [DIGITS[char] for char in value]
    return ["." .join(glyph[row] for glyph in glyphs) for row in range(5)]


def checking_frames():
    """The creature eating a row of parcels that move into its mouth."""
    frames = []
    for frame in range(4):
        canvas = blank()
        for k in range(3):
            paste(canvas, PARCEL, 11 + 4 * k - frame, 8)
        if frame in (0, 3):
            paste_creature(canvas, MUNCHER_OPEN)
        else:
            paste_creature(canvas, MUNCHER_CLOSED)
        frames.append(canvas)
    return frames


def updates_frames(count):
    """The creature drooling at a parcel labelled with the number of updates."""
    label = str(count) if count < 100 else "!!"
    frames = []
    for drop in (10, 11, 12):
        canvas = blank()
        paste_creature(canvas, MUNCHER_OPEN, x=-4)
        paste(canvas, BIG_PARCEL, 7, 6)
        digits = text(label)
        width = len(digits[0])
        paste(canvas, [row.replace("#", "K") for row in digits], 7 + (9 - width + 1) // 2, 8)
        canvas[drop][4] = "S"
        frames.append(canvas)
    return frames


def up_to_date_frames():
    """The creature resting with a full belly; now and then it burps."""
    resting = blank()
    paste_creature(resting, MUNCHER_FULL)
    burp = blank()
    paste_creature(burp, MUNCHER_FULL)
    paste(burp, ["..S", "...", "S.."], 12, 4)
    burp2 = blank()
    paste_creature(burp2, MUNCHER_FULL)
    paste(burp2, ["..S.", ".S.S", "..S."], 12, 1)
    return [resting, burp, burp2]


def error_frames():
    canvas = blank()
    paste_creature(canvas, MUNCHER_CHOKING)
    return [canvas]


# (frames, milliseconds each frame is shown); a single frame is not animated
def animation(state, count=0):
    if state == "checking":
        return checking_frames(), [150] * 4
    if state == "updates":
        return updates_frames(count), [1200, 250, 250]
    if state == "up_to_date":
        return up_to_date_frames(), [6000, 300, 300]
    return error_frames(), [0]


def to_rgba(canvas, state):
    """Converts a canvas to rows of (r, g, b, a) tuples."""
    body = BODY_COLORS[state]
    dark = tuple(c * 3 // 5 for c in body)
    colors = dict(FIXED_COLORS, B=body, D=dark)
    return [[colors[char] + (255,) if char != "." else (0, 0, 0, 0) for char in row] for row in canvas]
