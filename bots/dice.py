#!/usr/bin/env python


import logging
import time
import mumble

import random
import exceptions

import socket

class DiceBot(mumble.CommandBot):
  """Implements a bot that makes fair dice rolls for role-playing games.
  
  If the bot sees a "!roll" or "!roll_sr" command it makes an appropriate
  dice roll and announces the result to the channel containing the user
  who sent the command.
  
  DiceBot does not care how it received the command. Users can message it
  directly or send the command to the channel the DiceBot is in (normally
  the root channel).
  
  Additionally, DiceBot listens for "!help" commands that on which it
  explains command usage to the user via direct messages. 
  
  """
  
  def __init__(self):
    """Init method. Only calls CommandBot's __init__ method."""
    mumble.CommandBot.__init__(self)

  def on_socket_closed(self):
    """Callback method for socket_closed event.
    
    This callback method will be called when the used socket has been
    closed. DiceBot will retry to connect to the server unless the
    socket was closed due to a call of Bot.stop(). 
    
    """
    if self.stop_ordered:
      return
    connected = False
    while not connected: 
      try:
        print "Reconnecting"
        self.start(self.server, self.nickname)
        connected = True
        print "Connection re-established"
      except socket.error:
        connected = False
        time.sleep(5)

  def _evalNumber(self,toEval):
    """Private method that evaluates a term including "+" and "-".
    
    This method evaluates a numeric term containing the operations
    plus and minus.
    
    The term may only consist of integers and "+" and "-" characters and
    must start with an integer. No whitespace allowed.
    
    Examples:
    
    * _evalNumber(2+3-1) returns 4
    * _evalNumber(2) return 2
    
    """
    result = 0
    for term in toEval.split("+"):
      subTerms = term.split("-")
      termResult = int(subTerms[0])
      for subTerm in subTerms[1:]:
        termResult = termResult-int(subTerm)
      result = result+termResult
    return result

  def on_bang(self, from_user, *args):
    """Callback method for bang messages.
    
    'Bang messages' are messages that start
    with a '!' character and are treated
    as commands.
    
    Currently interpreted commands are:
    * !roll for general purpose dice rolls
    * !roll_sr for Shadowrun 3 success tests
    
    """
    print "Command: " + str(args)
    success = False
    if (len(args) > 1) and (args[0] == "roll"):
      splitarg = args[1].lower().split("d")
      if len(splitarg) == 2:
        try:
          nDice = self._evalNumber(splitarg[0])
          dDimension = self._evalNumber(splitarg[1])
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
        targetNumber = self._evalNumber(args[1])
        nDice = self._evalNumber(args[2])
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
          if (successes > 0) and (not (fails == len(results))):
            self.send_message_channel(from_user, ("You made it with %d successes on %d against %d. Results: " % (successes, nDice, targetNumber)) + strBuf)
          else:
            if fails == len(results):
              self.send_message_channel(from_user, "CATASTROPHIC FAILURE. It was nice knowing you, Chummer. Results: " + strBuf)
            else:
              self.send_message_channel(from_user, ("You failed on %d against %d. Results: " % (nDice, targetNumber)) + strBuf)
      except exceptions.ValueError:
          self.send_message(from_user, "Error in command.")
    if not success:
      self.send_message(from_user, "Error in commad.")