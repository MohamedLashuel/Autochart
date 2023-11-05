from .noteobj import *
from .based import *
from collections import OrderedDict
from random import choice

ALL_PANELS = {Panel.L, Panel.D, Panel.U, Panel.R}

ALL_JUMPS = [
	(Panel.L, Panel.R),
	(Panel.L, Panel.U),
	(Panel.L, Panel.D),
	(Panel.D, Panel.U),
	(Panel.D, Panel.R),
	(Panel.U, Panel.D),
	(Panel.U, Panel.R),
]

ALL_CORNERS = [
	(Panel.L, Panel.U),
	(Panel.L, Panel.D),
	(Panel.D, Panel.R),
	(Panel.U, Panel.R),
]

player = Player()


def unpackPhrases(phrases):
	return [measure for phrase in phrases for measure in phrase]


def isBeatCode(char):
	return char.isalpha() or char == "."


class Command:
	def __init__(self, line, phrase):
		self.line = line
		self.phrase = phrase


def processLines(lines):
	commands = OrderedDict()

	for line in lines:
		dictAddKeyVal(commands, lineToCommand(line, commands))

	phrases = [cmd.phrase for cmd in commands.values()]
	return phrases


def lineToCommand(line, commands):
	phrase = []

	slash_inds = find_all(line, "/")

	name = line[0 : (slash_inds[0] - 1)]  # Exclude colon
	segments = [(slash_inds[x], slash_inds[x + 1]) for x in range(len(slash_inds) - 1)]

	for segment in segments:
		segment_string = line[(segment[0] + 1) : segment[1]]

		if not isBeatCode(segment_string[0]):
			ref_string = segment_string[1:]
			ref_cmd = commands[ref_string]

		match segment_string[0]:
			case "#":
				measures = ref_cmd.phrase
			case "^":
				measures = flippedPhrase(ref_cmd.phrase, "vertical")
			case "-":
				measures = flippedPhrase(ref_cmd.phrase, "horizontal")
			case "@":
				name_command = lineToCommand(ref_cmd.line, commands)
				return (name, name_command[1])
			case "$":
				pdb.set_trace()
			case _:
				measures = [segToMeasure(segment_string)]

		phrase.extend(measures)

	return (name, Command(line, phrase))

def flippedPhrase(phrase, direction):
	assert direction in ("vertical", "horizontal")

	measures = []
	flip_function = Beat.Hflipped if direction == "horizontal" else Beat.Vflipped

	for measure in phrase:
		measures.append([flip_function(beat) for beat in measure])

	return measures

def segToMeasure(line):
	measure = []
	# Mines don't work properly between measures
	mines_and_indices = []

	length = -1
	note_kind = NoteType.Tap
	ii = 0

	last_beat = Beat([])

	while ii < len(line):
		skip_beat = False
		char = line[ii]
		# Reset options each time
		options = NextNoteArgs()

		match char:
			case "n":
				pass

			case ".":
				next_beat = Beat([])
				skip_beat = True

			case "j":
				next_beat = nextJump(length, note_kind)
				skip_beat = True

			case "l" | "o":
				note_kind = matchVal(char, ["d", NoteType.Hold], ["o", NoteType.Roll])
				ii += 1
				length = numberGrab(line, ii)
				ii += len(str(length))
				continue

			case "v":
				options.add("vertical")

			case "h":
				options.add("horizontal")

			case "x":
				options.add("crossover")

			case "d":
				options.add("doublestep")
				mines_and_indices.append((lastNoteMine(), ii))

			case "f":
				options.add("switch")
				mines_and_indices.append((outOfWayMine(), ii))

			case "s":
				options.add("side_switch")
				mines_and_indices.append((outOfWayMine(), ii))

			case "r":
				options.add("repeat")

			case "m":
				options.add("move_off")

			case "C":
				next_beat = nextJump(length, note_kind, corner=True)
				skip_beat = True

			case "O":
				next_beat = nextJump(length, note_kind, opposite=True)
				skip_beat = True

			case "w":
				options.add("weak_uncross")

			case "u":
				options.add("strong_uncross")

			case "b":
				options.add("bracket")

			case "k":
				next_beat = last_beat

			case "(":
				ii += 1
				continue

			case ")":
				ii += 1
				length = -1
				note_kind = NoteType.Tap
				continue

			case _:
				print(f"{char} is not a note indicator!")
				return

		if not skip_beat:
			next_beat = nextRegNote(options, length, note_kind)
			last_beat = next_beat

		for foot in Foot:
			next_beat += player.getFoot(foot).advanceAndGetReleases()

		measure.append(next_beat)

		ii += 1

	if len(mines_and_indices) > 0:
		measure = padMeasureWithMines(measure, mines_and_indices)

	return measure

def nextRegNote(options, length=-1, note_kind=NoteType.Tap):
	# Regular note with alternating feet
	banned_panels = set()

	left_stuck, right_stuck = feetStuck(options.doublestep)
	step_foot = nextFoot(left_stuck, right_stuck)

	if not left_stuck and not right_stuck and not options.bracket:
		banned_panels |= set(ambiguousPanels())
	if not (options.switch | options.side_switch):
		banned_panels |= set(stuckPanels(left_stuck, right_stuck))
	if options.horizontal:
		banned_panels |= {Panel.U, Panel.D}
	if options.vertical:
		banned_panels |= {Panel.L, Panel.R}

	if options.crossover:
		banned_panels |= set(allPanelsBut([crossoverPanel(step_foot)]))
		crossDirection(step_foot)
	elif not options.side_switch:
		banned_panels.add(crossoverPanel(step_foot))

	if options.weak_uncross:
		banned_panels |= set(allPanelsBut([weakUncrossPanel(step_foot)]))
	if options.strong_uncross:
		banned_panels |= set(allPanelsBut([strongUncrossPanel(step_foot)]))
	if options.weak_uncross or options.strong_uncross:
		player.direction = Facing.U
	if options.move_off:
		banned_panels |= set(beforeLastFootBeat().getPanels())
	if options.repeat:
		banned_panels |= set(allPanelsBut(beforeLastFootBeat().getPanels()))
	if options.switch:
		banned_panels |= {Panel.L, Panel.R}
	if options.side_switch:
		banned_panels |= {Panel.D, Panel.U}
		switchDirection(step_foot)
	if options.switch or options.side_switch:
		banned_panels |= set(allPanelsBut(player.footPanels(Foot(not step_foot))))

	valid_choices = [panel for panel in ALL_PANELS if panel not in banned_panels]
	step_foot_panel = unset(player.footPanels(step_foot))

	if options.bracket:
		choices = chooseBracket(valid_choices)
	else:
		choices = [weightedChoice(valid_choices, [step_foot_panel, 0.5])]

	chosen_beat = Beat([Note(choice, note_kind, length) for choice in choices])
	player.setFoot(step_foot, chosen_beat)
	player.last_foot = toLastFoot(step_foot)
	return chosen_beat

def nextJump(length, note_kind, corner=False, opposite=False):
	# Basic jump note
	jump = randomJump(corner)
 
	occupied_panels = occupiedPanels()

	# Decide which equivalent panels, then unturn at the end
	# Don't do a jump we're already on, those are lame
	if opposite:
		while jump[0] in occupied_panels or jump[1] in occupied_panels:
			jump = randomJump(corner)
	else:
		while jump[0] in occupied_panels and jump[1] in occupied_panels:
			jump = randomJump(corner)

	left_note, right_note = jumpToNotes(jump, note_kind, length)
	setFeetBeat(Beat([left_note]), Beat([right_note]))
	chosen_beat = jumpToBeat(jump)
	player.last_foot = LastFoot.B
	return chosen_beat

def chooseBracket(panels):
	# Lists are mutable, avoid side effects
	vert_panels = set(panels) & {Panel.U, Panel.D}
	hori_panels = set(panels) & {Panel.L, Panel.R}
	return (choice(vert_panels), choice(hori_panels))

def padMeasureWithMines(measure, mines_and_indices):
	# Places mines at the indices given by mine_indices
	empty_beat = Beat([])
	new_measure = [[beat, empty_beat] for beat in measure]
	unpacked_measure = [beat for beats in new_measure for beat in beats]
	for mine_beat, ii in mines_and_indices:
		unpacked_measure[ii * 2 - 1] = mine_beat
	return unpacked_measure

def outOfWayMine():
	invalid_panels = player.getPanels()
	valid_choices = list(ALL_PANELS - invalid_panels)
	chosen_panel = choice(valid_choices)
	mine_beat = Beat([Note(chosen_panel, NoteType.Mine)])
	return mine_beat

def lastNoteMine():
	chosen_panel = choice(list(player.getLastFoot().getPanels()))
	mine_beat = Beat([Note(chosen_panel, NoteType.Mine)])
	return mine_beat

def crossoverPanel(step_foot):
	orig_crossover_panel = Panel.R if step_foot == Foot.L else Panel.L
	return unturnPanel(orig_crossover_panel, player.direction)

def weakUncrossPanel(step_foot):
	failure = False
	unturn_left = unturnPanel(Panel.L, player.direction)
	unturn_right = unturnPanel(Panel.R, player.direction)
	if step_foot == Foot.L:
		if player.footPanels(Foot.R) == [unturn_right]:
			uncross_panel = unturn_left
		else:
			failure = True
	else:
		if player.footPanels(Foot.L) == [unturn_left]:
			uncross_panel = unturn_right
		else:
			failure = True
	if failure:
		blowup("There's no weak crossover panel available.")
	return uncross_panel

def strongUncrossPanel(step_foot):
	current_beat = footBeat(step_foot)
	current_panels = current_beat.getPanels()
	unturn_up = unturnPanel(Panel.U, player.direction)
	unturn_down = unturnPanel(Panel.D, player.direction)
	if unturn_up in current_panels:
		return unturn_down
	elif unturn_down in current_panels:
		return unturn_up
	else:
		blowup("Strong uncrossover is impossible here")

def randomJump(corner=False):
	# Output: A random jump, correcting for there being two up-downs. Can specify to use corners only
	return choice(ALL_CORNERS) if corner else choices(ALL_JUMPS, weights=[1, 1, 1, 0.5, 1, 0.5, 1])[0]

def jumpToBeat(jump):
	left_note = Note(jump[0], NoteType.Tap)
	right_note = Note(jump[1], NoteType.Tap)
	result = Beat([left_note, right_note])
	return result

def occupiedPanels():
	return set(player.footPanels(Foot.L)) | set(player.footPanels(Foot.R))

def feetStuck(doublestep=False):
	if doublestep:
		def footStuck(foot):
			return player.last_foot is not toLastFoot(foot)
	else:
		def footStuck(foot):
			return player.getFoot(foot).anyHolds() \
				or player.last_foot == toLastFoot(foot) \
				and not player.getFoot(not foot).anyHolds()
	return footStuck(Foot.L), footStuck(Foot.R)

def beforeLastFootBeat():
	return player.getFoot(not toFoot(player.last_foot))

def ambiguousPanels():
	# TODO: Allow for jumps into up/down if a foot is on there
	return [
		unturnPanel(Panel.U, player.direction),
		unturnPanel(Panel.D, player.direction),
	]

def nextFoot(left_stuck, right_stuck):
	return twoBoolEvaluate(
		left_stuck,
		right_stuck,
		(choice([Foot.L, Foot.R]), Foot.R, Foot.L, "DIE"),
	)

def stuckPanels(left_stuck, right_stuck):
	assert not (left_stuck and right_stuck)
	result = []
	stuck_foot_beat = match(
		(left_stuck, player.getFoot(Foot.L)),
		(right_stuck, player.getFoot(Foot.R)),
		default=Beat([]),
	)
	result = stuck_foot_beat.getPanels()
	return result

def setFeetBeat(*beats):
	for foot, beat in zip(Foot, beats):
		player.setFoot(foot, beat)

def allPanelsBut(exclude_panels):
	return [panel for panel in ALL_PANELS if (panel not in exclude_panels)]

def crossDirection(step_foot):
	other_foot = player.getFoot(not step_foot)
	assert player.direction == Facing.U
	up_pivot = Panel.U in other_foot.getPanels()
	assert up_pivot ^ Panel.D in other_foot.getPanels()
	if (step_foot == Foot.L and up_pivot) or (step_foot == Foot.R and not up_pivot):
		player.direction = turnLeft(player.direction)
	else:
		player.direction = turnRight(player.direction)

def switchDirection(step_foot):
	if player.direction != Facing.U:
		player.direction = Facing.U
		return
	if step_foot == Foot.L:
		player.direction = turnRight(player.direction)
	else:
		player.direction = turnLeft(player.direction)

def jumpToNotes(jump, note_kind, length):
	return Note(unturnPanel(jump[0], player.direction), note_kind, length), Note(
		unturnPanel(jump[1], player.direction), note_kind, length
	)
