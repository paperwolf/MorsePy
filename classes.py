from pynput import keyboard
from strings import *
import time
import curses

#=========#
# CLASSES #
#=========#

class Morse():
	def __init__(self):
		# TIME
		self.start_time 		= 0
		self.press_time 		= 0
		self.release_time 		= 0
		self.last_event_time	= 0

		self.press_duration 	= 0
		self.space_duration 	= 0

		# KEY EVENTS
		self.current_key		= None
		self.last_key 			= None
		self.last_key_event 	= None
		self.key_is_pressed 	= False

		# STRINGS
		self.morse_char			= ''
		self.morse_string 		= ''
		self.alpha_string 		= ''

		# FLAGS
		self.flag_show_time		= True

		# DEFINES
		self.dot_duration				= 0.05
		self.dash_duration				= 3 * self.dot_duration
		self.letter_space_duration		= 3 * self.dot_duration
		self.word_space_duration		= 12 * self.dot_duration
		self.morse_dict = {
			'.-'	:	'A',
			'-...'	:	'B',
			'-.-.'	:	'C',
			'-..'	:	'D',
			'.'		:	'E',
			'..-.'	:	'F',
			'--.'	:	'G',
			'....'	:	'H',
			'..'	:	'I',
			'.---'	:	'J',
			'-.-'	:	'K',
			'.-..'	:	'L',
			'--'	:	'M',
			'-.'	:	'N',
			'---'	:	'O',
			'.--.'	:	'P',
			'--.-'	:	'Q',
			'.-.'	:	'R',
			'...'	:	'S',
			'-'		:	'T',
			'..-'	:	'U',
			'...-'	:	'V',
			'.--'	:	'W',
			'-..-'	:	'X',
			'-.--'	:	'Y',
			'--..'	:	'Z',
			'.----'	:	'1',
			'..---'	:	'2',
			'...--'	:	'3',
			'....-'	:	'4',
			'.....'	:	'5',
			'-....'	:	'6',
			'--...'	:	'7',
			'---..'	:	'8',
			'----.'	:	'9',
			'-----'	:	'0',

			'...---...':'SOS'
		}

		# UI
		self.curses_pos_current_time	= 2
		self.curses_pos_space_duration	= self.curses_pos_current_time + 1
		self.curses_pos_press_duration	= self.curses_pos_current_time + 2

		self.curses_pos_current_key		= self.curses_pos_press_duration + 2
		self.curses_pos_last_morse		= self.curses_pos_current_key + 1

		self.curses_pos_morse_string	= self.curses_pos_last_morse + 2
		self.curses_pos_alpha_string	= self.curses_pos_morse_string + 1

		self.attr_dict = {
			CURRENT_TIME 	: {'pos':self.curses_pos_current_time, 		'str':STR_CURRENT_TIME, 	'calc':self.get_current_time},
			SPACE_DURATION 	: {'pos':self.curses_pos_space_duration, 	'str':STR_SPACE_DURATION,	'calc':self.get_space_duration},
			PRESS_DURATION 	: {'pos':self.curses_pos_press_duration, 	'str':STR_PRESS_DURATION, 	'calc':self.get_press_duration},
			CURRENT_KEY 	: {'pos':self.curses_pos_current_key, 		'str':STR_CURRENT_KEY, 		'calc':self.get_current_key},
			LAST_MORSE 		: {'pos':self.curses_pos_last_morse, 		'str':STR_LAST_MORSE, 		'calc':self.get_last_morse},
			MORSE_STRING 	: {'pos':self.curses_pos_morse_string, 		'str':STR_MORSE_STR, 		'calc':self.get_morse_string},
			ALPHA_STRING 	: {'pos':self.curses_pos_alpha_string, 		'str':STR_ALPHA_STR, 		'calc':self.get_alpha_string}
		}

		self.stdscr = curses.initscr()
		self.stdscr.keypad(True)
		curses.noecho()
		curses.cbreak()
		curses.endwin()

	#=====================#
	# STRING CALCULATIONS #
	#=====================#

	def get_current_time(self):
		return str(time.time() - self.start_time)[0:7]

	def get_space_duration(self):
		return str(time.time() - self.release_time)[0:7]

	def get_press_duration(self):
		return str(time.time() - self.press_time)[0:7]

	def get_current_key(self):
		return (' ' if self.current_key == None else str(self.current_key))

	def get_last_morse(self):
		return self.morse_char

	def get_morse_string(self):
		return self.morse_string

	def get_alpha_string(self):
		return self.alpha_string

	#====================#
	# UI PRINT FUNCTIONS #
	#====================#

	def curses_print(self, y, x, string):
		self.stdscr.addstr(y, x, string)
		self.stdscr.refresh()

	def attr_print(self, attr_str, override=None):
		attr 	= self.attr_dict[attr_str]
		pos 	= attr['pos']
		string 	= attr['str']
		value 	= (override if type(override) == str else attr['calc']())

		self.curses_print(pos,0,string.format(value))

	def attr_erase(self, attr_str):
		if attr_str == MORSE_STRING:
			self.attr_print(attr_str, len(self.morse_string)*' ')
		elif attr_str == ALPHA_STRING:
			self.attr_print(attr_str, len(self.alpha_string)*' ')
		else:
			self.attr_print(attr_str, ' '*80)

	def clear_print_strings(self):
		self.attr_erase(CURRENT_TIME)
		self.attr_erase(PRESS_DURATION)
		self.attr_erase(SPACE_DURATION)
		self.attr_erase(LAST_MORSE)
		self.attr_erase(MORSE_STRING)
		self.attr_erase(ALPHA_STRING)

	#============================#
	# MORSE CONVERSION FUNCTIONS #
	#============================#

	def duration_to_morse(self, duration):
		if duration < self.dash_duration:
			return '.'
		return '-'

	def single_morse_to_alpha(self, morse_char):
		try:
			return self.morse_dict[morse_char]
		except KeyError:
			return '?'

	def multi_morse_to_alpha(self, morse_string):
		morse_list = morse_string.split(' ')
		for i, morse in enumerate(morse_list):
			morse_list[i] = (self.single_morse_to_alpha(morse) if morse != '' else ' ')
		return ''.join(morse_list)

	#================#
	# EVENT HANDLERS #
	#================#

	def handle_key_event(self, event):
		self.last_key_event = event
		self.last_key = event.key

	def handle_backspace(self):
		self.clear_print_strings()
		self.morse_string = ''
		self.alpha_string = ''
		self.morse_char = ''
		
		self.press_time = self.start_time
		self.release_time = self.start_time
		self.last_key_event	= None

	def handle_press(self):
		self.press_time 		= time.time()
		self.current_key		= self.last_key
		self.key_is_pressed 	= True
		self.last_event_time 	= self.press_time
		self.space_duration 	= self.press_time - self.release_time

	def handle_release(self):
		self.release_time 		= time.time()
		self.current_key		= None
		self.key_is_pressed 	= False
		self.last_event_time 	= self.release_time
		self.press_duration 	= self.release_time - self.press_time

		self.morse_char = self.duration_to_morse(self.press_duration)
		self.morse_string += self.morse_char
		self.alpha_string = self.multi_morse_to_alpha(self.morse_string)

	def handle_space(self):
		if self.morse_string and not self.key_is_pressed:
			exceeded_new_letter_duration = time.time() - self.release_time > self.letter_space_duration
			exceeded_new_word_duration = time.time() - self.release_time > self.word_space_duration

			if not self.morse_string.endswith(' ') and exceeded_new_letter_duration:
				self.morse_string += ' '
			elif self.morse_string.endswith(' ') and not self.morse_string.endswith('  ') and exceeded_new_word_duration:
				self.morse_string += ' '

	#============#
	# MORSE LOOP #
	#============#

	def esc_key_pressed(self):
		return self.last_key == keyboard.Key.esc

	def update_UI(self):
		self.attr_print(CURRENT_TIME)
		self.attr_print(LAST_MORSE)
		self.attr_print(MORSE_STRING)
		self.attr_print(ALPHA_STRING)

		if type(self.last_key_event) == keyboard.Events.Press:
			self.attr_print(PRESS_DURATION)
			self.attr_print(CURRENT_KEY)
		elif type(self.last_key_event) == keyboard.Events.Release:
			self.attr_print(SPACE_DURATION)
			self.attr_erase(CURRENT_KEY)

	def init_loop(self):
		self.stdscr.clear()
		self.stdscr = curses.initscr()
		curses.curs_set(False)

		# Prevents initial ENTER release from being returned by event getter.
		self.curses_print(0,0,'Initializing...')
		time.sleep(0.1)
		self.curses_print(0,0,'[Press BACKSPACE to clear. Press ESC to exit.]')
		for attr_str in self.attr_dict.keys():
			self.attr_print(attr_str, '')

		self.start_time = time.time()

	def loop(self):
		self.init_loop()

		with keyboard.Events() as events:
			while not self.esc_key_pressed():
				try:
					event = events.get(0.00001)
					# Only call event handlers when press changes to release or vice versa.
					if type(event) != type(self.last_key_event):
						self.handle_key_event(event)
						if event.key == keyboard.Key.backspace:
							self.handle_backspace()
						else:
							# PRESS OR RELEASE
							if type(event) == keyboard.Events.Press:
								self.handle_press()
							elif type(event) == keyboard.Events.Release:
								self.handle_release()
				except:
					# NO KEY PRESSED
					self.handle_space()
				finally:
					self.update_UI()

		self.stdscr.clear()
		curses.endwin()