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
  
  def _on_roll(self, from_user, args):
    """Private method for making general purpose dice rolls."""
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
            strBuf = "Results (" + self.state.users_by_id[from_user.id].name + "): "
            for result in results:
              strBuf = strBuf + str(result) + " "
            strBuf = strBuf + "on %d D%d" %(nDice, dDimension)
            print strBuf
            self.send_message_channel(from_user, strBuf)
        except exceptions.ValueError:
          self.send_message(from_user, "Error in command. Say \"!help roll\" for help.")
          return
    else:
      self.send_message(from_user, "Error in command. Say \"!help roll\" for help.")
  
  def _on_roll_sr(self, from_user, args):
    """Private method for making Shadowrun 3 success tests."""
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
          if (successes > 0) and (not (fails == len(results))):
            self.send_message_channel(from_user, self.state.users_by_id[from_user.id].name + (" made it with %d successes on %d against %d. Results: " % (successes, nDice, targetNumber)) + strBuf)
          else:
            if fails == len(results):
              self.send_message_channel(from_user, "CATASTROPHIC FAILURE. It was nice knowing you, " + self.state.users_by_id[from_user.id].name + ". Results: " + strBuf)
            else:
              self.send_message_channel(from_user, self.state.users_by_id[from_user.id].name + (" failed on %d against %d. Results: " % (nDice, targetNumber)) + strBuf)
      except exceptions.ValueError:
          self.send_message(from_user, "Error in command. Say \"!help roll_sr\" for help.")
    else:
      self.send_message(from_user, "Error in command. Say \"!help roll_sr\" for help.")
  
  def _on_help(self, from_user, args):
    if len(args) < 2:
      self.send_message(from_user, "Available commands are \"!roll\" for general purpose dice rolls and \"!roll_sr\" for Shadowrun 3 success tests.")
    else:
      if args[1] == "roll":
        self.send_message(from_user, "Usage: \"!roll nDd\". Example: \"!roll 2+1D6\" rolls 3 D6.")
      if args[1] == "roll_sr":
        self.send_message(from_user, "Usage: \"!roll_sr target_number dice_pool\". Example: \"!roll_sr 2+1 6-1\" makes a test against target number 3 with 5 dices.")


  def on_bang(self, from_user, *args):
    """Callback method for bang messages.
    
    'Bang messages' are messages that start
    with a '!' character and are treated
    as commands.
    
    Currently interpreted commands are:
    * !roll for general purpose dice rolls
    * !roll_sr for Shadowrun 3 success tests
    * !help explains the command syntax to users
    
    """
    print "Command: " + str(args)
    success = False
    if args[0] == "roll":
      self._on_roll(from_user, args)
      success = True
    if args[0] == "roll_sr":
      self._on_roll_sr(from_user, args)
      success = True
    if args[0] == "help":
      self._on_help(from_user, args)
      success = True
    if not success:
      self.send_message(from_user, "Error in command. Say \"!help\" for help.")
