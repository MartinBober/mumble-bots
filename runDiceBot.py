#!/usr/bin/env python

import bots
import sys
import mumble
import time
import signal

def handler(signum, frame):
  print "Signal handler called with signal", signum
  global stopRequested
  stopRequested = True


stopRequested = False
signal.signal(signal.SIGINT, handler)
bot = bots.DiceBot()
server = mumble.Server(sys.argv[1])
bot.start(server, "DiceBot")
while not stopRequested:
  time.sleep(1)
bot.stop()
exit(0)