from classes import *
from curses import wrapper

def main(screen):
    MorseDebug().loop()

wrapper(main)