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
            strBuf = strBuf + "on %d D%d" %(nDice, dDimension)
            print strBuf
            self.send_message_channel(from_user, strBuf)
            success = True
        except exceptions.ValueError:
          self.send_message(from_user, "Error in command.")
          return
    if (len(args) > 2) and (args[0] == "roll_sr"):
      try:
        targetNumber = int(args[1])
        nDice = int(args[2])
        if not ((nDice < 1) or (targetNumber < 2)):
          results = []
          strBuf = ""
          fails = 0
          successes = 0
          for i in range(nDice):
            result = random.randint(1,6)
            resultSum = result
            # Rule of 6
            while (result == 6):
              result = random.randint(1,6)
              resultSum += result
            if resultSum == 1:
              fails += 1
            if resultSum >= targetNumber:
              successes += 1
            strBuf = strBuf + str(resultSum)+ " "
            results += [resultSum]
          success = True
          if successes > fails:
            self.send_message_channel(from_user, ("You made it with %d net succeses. Results: " % (successes-fails,)) + strBuf)
          if fails >= successes:
            if fails == len(results):
              self.send_message_channel(from_user, "CATASTROPHIC FAILURE. It was nice knowing you, Chummer. Results: " + strBuf)
            else:
              self.send_message_channel(from_user, "You failed. Results: " + strBuf)
      except exceptions.ValueError:
          self.send_message(from_user, "Error in command.")
    if not success:
      self.send_message(from_user, "Error in commad.")
