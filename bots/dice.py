#!/bin/python
#
# Bot that rolls dices when you send him bang commands.
#

from optparse import OptionParser

import logging
import sys
import threading
import time

import mumble

import random
import exceptions

class DiceBot(mumble.CommandBot):
  def __init__(self):
    mumble.CommandBot.__init__(self)


  def on_bang(self, from_user, *args):
    print "Command: " + str(args)
    success = False
    if (len(args) > 1) and (args[0] == "roll"):
      splitarg = args[1].lower().split("d")
      if len(splitarg) == 2:
        try:
          nDice = int(splitarg[0])
          dDimension = int(splitarg[1])
          if not ((nDice < 1) or (dDimension < 1)):
            results = []
            for i in range(nDice):
              results += [random.randint(1,dDimension)]
            strBuf = "Results: "
            for result in results:
              strBuf = strBuf + str(result) + " "
            print strBuf
            self.send_message(None, strBuf)
            success = True
        except exceptions.ValueError:
          self.send_message(from_user, "Error in command.")
          return
    if not success:
      self.send_message(from_user, "Error in commad.")
