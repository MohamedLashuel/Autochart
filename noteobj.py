from enum import Enum, IntEnum
from based import *
import copy

class Note():
    def __init__(self, panel, kind, length = -1):
        if length > -1: assert kind in [NoteKind.Hold, NoteKind.Roll]
        else: assert kind not in [NoteKind.Hold, NoteKind.Roll]
        assert length != 0

        self.panel = panel
        self.kind = kind
        self.length = length

    @staticmethod
    def default(): return Note(Panel.N, NoteKind.NA, -1)

    def __hash__(self): return hash(str(self))

class NoteKind(Enum):
    NA = '0'
    Tap = '1'
    Hold = '2'
    Roll = '4'
    Release = '3'
    Mine = 'M'

class Panel(IntEnum):
    N = 0
    L = 1
    D = 2
    U = 3
    R = 4

class Foot(IntEnum):
    L = 0
    R = 1

class LastFoot(IntEnum):
    L = 0
    R = 1
    B = 2
    N = 3

class Facing(IntEnum):
    U = 1
    R = 2
    D = 3
    L = 4

class Beat:
    def __init__(self, notes = []):
        assert len(notes) <= 4
        self.notes = notes

    def __str__(self):
        # Let's make debugging easier
        return self.toText()

    def noteVars(self, var): return [getattr(note, var) for note in self.notes]

    def addNote(self, note):
        assert note.panel not in self.noteVars('panel')
        self.notes += note

    def __add__(self, other):
        new_beat = copy.deepcopy(self)
        for note in other.notes: new_beat.addNote(note)
        return new_beat

    def anyNotes(self): return len(notes) > 0

    def anyHolds(self): return any([timer > 0 for timer in self.noteVars('length')])

    def getPanels(self): return set(self.noteVars('panel'))

    def advanceAndGetReleases(self):
        for note in self.notes: note.length = max(-1, note.length - 1)
        release_notes = [Note(note.panel, NoteKind.Release) for note in self.notes
                            if note.length == 0]
        return Beat(release_notes)

    def getSwappedIndicesBeat(self, p1, p2):
        def changeNotePanel(beat, orig_pan, new_pan):
            panel_notes = [note for note in beat.notes if note.panel == orig_pan]
            if len(panel_notes): panel_notes[0].panel = new_pan

        new_beat = copy.deepcopy(self)
        changeNotePanel(new_beat, p1, p2)
        changeNotePanel(new_beat, p2, p1)
        
        return new_beat

    def Hflipped(self): return self.getSwappedIndicesBeat(0, 3)

    def Vflipped(self): return self.getSwappedIndicesBeat(1, 2)

    def toText(self):
        arrow_notes = [Note.default(), Note.default(), Note.default(), Note.default()]
        for note in self.notes: arrow_notes[note.panel - 1] = note
        
        arrow_strs = [note.kind.value for note in arrow_notes]

        return ''.join(arrow_strs)

class Player:
    def __init__(self):
        self.feet = {Foot.L : Beat(),
                    Foot.R : Beat()}
        self.last_foot = LastFoot.N
        self.direction = Facing.U

    def getPanels(self): return self.feet[Foot.L].getPanels() | self.feet[Foot.R].getPanels()
    def footPanels(self, foot): return self.feet[foot].getPanels()

    def getFoot(self, foot): return self.feet[foot]
    def setFoot(self, foot, beat): self.feet[foot] = beat

    def setLeft(self, beat): self.feet[Foot.L] = beat
    def setRight(self, beat): self.feet[Foot.R] = beat

    def getLastFoot(self): return self.feet[toFoot(self.last_foot)]

class NextNoteArgs:
    def __getattribute__(self, name):
        try:
            result = object.__getattribute__(self, name)

            if callable(result): return result
            else: return True
        except AttributeError:
            return False

    def add(self, option):
        setattr(self, option, True)

def turnPanel(panel, facing):
    # A 90-degree right turn shifts each panel in this list to become the next one (turn 90 degrees and up becomes left)
    directions = [Panel.U, Panel.L, Panel.D, Panel.R]
    
    num_turns = int(facing)-1

    # Move forward num_turns times in directions and wrap around
    turned_panel = directions[(directions.index(panel) + num_turns) % 4]

    return turned_panel

def unturnPanel(panel, facing):
    # A 90-degree right turn shifts each panel in this list to become the next one (turn 90 degrees and up becomes left)
    directions = [Panel.U, Panel.L, Panel.D, Panel.R]

    # Turn the opposite way 4-turns times
    num_turns = 4-(int(facing)-1)

    # Move forward num_turns times in directions and wrap around
    turned_panel = directions[(directions.index(panel) + num_turns) % 4]

    return turned_panel

def toLastFoot(foot):
    if foot == Foot.L:
        result = LastFoot.L
    elif foot == Foot.R:
        result = LastFoot.R
    else:
        assert False

    return result

def toFoot(last_foot):
    return matchVal(last_foot, [LastFoot.L, Foot.L], [LastFoot.R, Foot.R])

def turnRight(direction):
    direction_int = direction + 1

    if direction_int == 5: direction_int = 1

    return Facing(direction_int)

def turnLeft(direction):
    direction_int = direction - 1

    if direction_int == 0: direction_int = 4

    return Facing(direction_int)

def flipLastFoot(last_foot):
    return matchVal(last_foot, [LastFoot.L, LastFoot.R], [LastFoot.R, LastFoot.L], default = last_foot)
