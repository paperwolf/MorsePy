from classes import *
from curses import wrapper

def main(screen):
    Morse().loop()

wrapper(main)