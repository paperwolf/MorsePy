#===============#
# KEY FUNCTIONS #
#===============#

def keydown_base(key):
	global last_key
	last_key = key
	return False

def keyup_base(key):
	return False

def keydown_test(key):
	keydown_base(key)

	if key != keyboard.Key.esc:
		print('PRESS')

	return False

def keyup_test(key):
	keyup_base(key)

	if key != keyboard.Key.esc:
		press_time = str(time.time() - release_time)[0:5]
		print('RELEASE')
		print('key = {0}, time = {1}s'.format(key, press_time))
	return False

def keyup_morse(key):
	keyup_base(key)

	press_time = time.time() - release_time
	morse = key_to_morse(press_time)
	print(morse)
	global morse_string
	morse_string += morse

	return False

def keydown_morse_loop(key):
	keydown_base(key)
	global press_time, release_time
	press_time = time.time()
	space_duration = press_time - release_time

#==================#
# LISTEN FUNCTIONS #
#==================#

def listen_press(func=keydown_base):
	with keyboard.Listener(on_press = func) as listener:
		listener.join()

def listen_release(func=keyup_base):
	with keyboard.Listener(on_release = func) as listener:
		listener.join()

#=================#
# MORSE FUNCTIONS #
#=================#

def key_test():
	listen_press(keydown_test)

	global release_time
	release_time = time.time()

	listen_release(keyup_test)

def constant_keytest():
	global last_key
	last_key = None
	while last_key != keyboard.Key.esc:
		key_test()

def morse_test():
	listen_press()
	global release_time
	release_time = time.time()
	listen_release(keyup_morse)

def constant_morse_test():
	global last_key, morse_string
	last_key = None
	morse_string = ''
	printed = False
	while last_key != keyboard.Key.esc:
		if (abs(time.time() - release_time > 1)) and printed == False:
			print(morse_string)
			printed = True
		else:
			morse_test()
			printed = False
	print()