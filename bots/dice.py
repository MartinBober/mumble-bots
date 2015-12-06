#!/usr/bin/env python


import time
import mumble
import random
import exceptions
import socket
import re
import urllib2


class ParsedArguments:

    def __init__(self, args):
        self._normal_args = []
        self._special_args = {}
        for arg in args:
            if arg[:2] == "--":
                value = True
                equals_pos = arg.find("=")
                key = args[2:]
                if equals_pos > 0:
                    value = arg[equals_pos + 1:]
                    key = arg[2:equals_pos]
                self._special_args[key] = value
            else:
                self._normal_args += [arg]

    def __getitem__(self, item):
        if type(item) is int:
            return self._normal_args[item]
        else:
            if item in self._special_args:
                return self._special_args[item]
            else:
                return False

    def __len__(self):
        return len(self._normal_args)

    def __contains__(self, item):
        return item in self._special_args


class CommandException:

    def __init__(self, error_msg):
        self._error_msg = error_msg

    def __str__(self):
        return self._error_msg

    
def get_user_name(from_user, args):
    if "name" in args:
        return args["name"]
    return from_user.name


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
        self._implemented_commands = {
            "roll": self._on_roll,
            "roll_sr": self._on_roll_sr,
            "sr5": self._on_roll_sr5,
            "sr_open": self._on_sr_open,
            "sr_ini": self._on_sr_ini,
            "vamp": self._on_vamp
        }

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

    def _eval_number(self, from_user, args, to_eval):
        """Private method that evaluates a term including "+" and "-".
    
    This method evaluates a numeric term containing the operations
    plus and minus.
    
    The term may only consist of integers and "+" and "-" characters and
    must start with an integer. No whitespace allowed.
    
    Examples:
    
    * _evalNumber(2+3-1) returns 4
    * _evalNumber(2) return 2
    
    """
        char_url = None
        try:
            char_url = self._get_char_url(args, from_user.comment)
        except AttributeError:
            pass
        if char_url:
            for attribute in re.findall(r"[a-z_]+", to_eval):
                attribute_value = self._get_attribute(char_url, attribute)
                if attribute_value:
                    to_eval = to_eval.replace(attribute, attribute_value)
                else:
                    self.send_message(from_user, "Attribute \"%s\" not found in char at \"%s\"" % (attribute, char_url))

        result = 0
        for term in to_eval.split("+"):
            sub_terms = term.split("-")
            term_result = int(sub_terms[0])
            for subTerm in sub_terms[1:]:
                term_result -= int(subTerm)
            result += term_result
        return result

    @staticmethod
    def _get_char_url(args, comment):
        if "char-url" in args:
            return args["char-url"]
        results = re.findall(r"https://charxchange.com/chars/[0-9]+", comment)
        if len(results) > 0:
            return results[0]
        else:
            return None

    @staticmethod
    def _get_attribute(char_url, attribute):
        try:
            return urllib2.urlopen(char_url + "/attrs/" + attribute).read()
        except urllib2.HTTPError:
            return None

    def _on_roll(self, from_user, args):
        """Private method for making general purpose dice rolls."""
        if len(args) == 0:
            raise CommandException("Error in command. Say \"!help roll\" for help.")

        split_arg = args[0].lower().split("d")
        if len(split_arg) != 2:
            raise CommandException("Error in command. Say \"!help roll\" for help.")

        try:
            n_dice = self._eval_number(from_user, args, split_arg[0])
            d_dimension = self._eval_number(from_user, args, split_arg[1])
            if not ((n_dice < 1) or (d_dimension < 1)):
                results = []
                for i in range(n_dice):
                    results += [random.randint(1, d_dimension)]
                str_buf = "Results (" + get_user_name(from_user, args) + "): "
                for result in results:
                    str_buf = str_buf + str(result) + " "
                str_buf += "on %d D%d" % (n_dice, d_dimension)
                print str_buf
                self.send_message_channel(from_user, str_buf)
        except exceptions.ValueError:
            raise CommandException("Error in command. Say \"!help roll\" for help.")

    def _on_roll_sr(self, from_user, args):
        """Private method for making Shadowrun 3 success tests."""
        if len(args) == 0:
            raise CommandException("Error in command. Say \"!help roll_sr\" for help.")

        try:
            target_number = self._eval_number(from_user, args, args[0])
            n_dice = self._eval_number(from_user, args, args[1])
            if not ((n_dice < 1) or (target_number < 2)):
                results = []
                str_buf = ""
                fails = 0
                successes = 0
                for i in range(n_dice):
                    result = random.randint(1, 6)
                    result_sum = result
                    # Rule of 6
                    while result == 6:
                        result = random.randint(1, 6)
                        result_sum += result
                    if result_sum == 1:
                        fails += 1
                    if result_sum >= target_number:
                        successes += 1
                    str_buf = str_buf + str(result_sum) + " "
                    results += [result_sum]
                if (successes > 0) and (not (fails == len(results))):
                    self.send_message_channel(from_user, get_user_name(from_user, args) + (
                        " made it with %d successes on %d against %d. Results: " % (
                            successes, n_dice, target_number)) + str_buf)
                else:
                    if fails == len(results):
                        self.send_message_channel(from_user,
                                                  "CATASTROPHIC FAILURE. It was nice knowing you, " +
                                                  get_user_name(from_user, args) + ". Results: " + str_buf)
                    else:
                        self.send_message_channel(from_user, get_user_name(from_user, args) + (
                            " failed on %d against %d. Results: " % (n_dice, target_number)) + str_buf)
        except exceptions.ValueError:
            raise CommandException("Error in command. Say \"!help roll_sr\" for help.")

    def _on_roll_sr5(self, from_user, args):
        """Private method for making Shadowrun 5 success tests."""
        if len(args) == 0:
            raise CommandException("Error in command. Say \"!help sr5\" for help.")

        explode = "explode" in args
        try:
            n_dice = self._eval_number(from_user, args, args[0])
            char_url = None
            try:
                char_url = self._get_char_url(args, from_user.comment)
            except AttributeError:
                pass
            if char_url and "no-dmg" not in args:
                physical_dmg = self._get_attribute(char_url, "physical_damage_current")
                if physical_dmg:
                    n_dice -= int(physical_dmg) / 3
                stun_dmg = self._get_attribute(char_url, "stun_damage_current")
                if stun_dmg:
                    n_dice -= int(stun_dmg) / 3
            if n_dice < 1:
                raise CommandException(get_user_name(from_user, args) + " cannot roll with a pool of %d." % (n_dice,))

            results = []
            str_buf = ""
            fails = 0
            successes = 0
            for i in range(n_dice):
                result = 6
                while result == 6:
                    result = random.randint(1, 6)
                    if result == 1:
                        fails += 1
                    if result >= 5:
                        successes += 1
                    str_buf = str_buf + str(result) + " "
                    results += [result]
                    if not explode:
                        break
            glitched = 2 * fails > n_dice
            if not glitched:
                msg = " has %d hits on %d dice. Results: "
                if explode:
                    msg = " has %d hits on %d dice with exploding sixes. Results: "
                self.send_message_channel(from_user, get_user_name(from_user, args) + (msg % (successes, n_dice)) + str_buf)
            else:
                if successes == 0:
                    self.send_message_channel(from_user,
                                              "CRITICAL GLITCH. It was nice knowing you, " +
                                              get_user_name(from_user, args) + ". Results: " + str_buf)
                else:
                    msg = " glitched but has %d hits on %d dice. Results: "
                    if explode:
                        msg = " glitched but has %d hits on %d dice with exploding sixes. Results: "
                    self.send_message_channel(from_user, get_user_name(from_user, args) + (msg % (successes, n_dice)) + str_buf)

        except exceptions.ValueError:
            raise CommandException("Error in command. Say \"!help sr5\" for help.")

    def _on_sr_open(self, from_user, args):
        if len(args) == 0:
            raise CommandException("Error in command. Say \"!help sr_open\" for help.")

        try:
            n_dice = self._eval_number(from_user, args, args[0])
            max_result = 0
            str_buf = ""
            for i in range(n_dice):
                result = random.randint(1, 6)
                result_sum = result
                while result == 6:
                    result = random.randint(1, 6)
                    result_sum += result
                if result_sum > max_result:
                    max_result = result_sum
                str_buf += str(result_sum) + " "
            self.send_message_channel(from_user,
                                      get_user_name(from_user, args) + " scored %d in an open test on %d D6. Results:" % (
                                          max_result, n_dice) + str_buf)
        except exceptions.ValueError:
            raise CommandException("Error in command. Say \"!help sr_open\" for help.")

    def _on_sr_ini(self, from_user, args):
        if len(args) > 1:
            try:
                ini_base = self._eval_number(from_user, args, args[0])
                n_dice = self._eval_number(from_user, args, args[1])
                result = 0
                for i in range(n_dice):
                    result += random.randint(1, 6)
                self.send_message_channel(from_user, get_user_name(from_user, args) + " has initiative %d (base %d)" % (
                    result + ini_base, ini_base))
            except exceptions.ValueError:
                raise CommandException("Error in command. Say \"!help sr_ini\" for help.")
        else:
            char_url = None
            try:
                char_url = self._get_char_url(args, from_user.comment)
            except AttributeError:
                pass
            if not char_url:
                raise CommandException("Error in command. Say \"!help sr_ini\" for help.")
            mode = ""
            if len(args) > 0:
                mode = args[0] + "_"
            try:
                base = self._get_attribute(char_url, "initiative_" + mode + "base")
                dice = self._get_attribute(char_url, "initiative_" + mode + "dice")
                if not base or not dice:
                    raise CommandException("Error. %s has no attributes %s and %s." % (
                        char_url, "initiative_" + mode + "base", "initiative_" + mode + "dice"))
                base = int(base)
                dice = int(dice)
                result = base
                for i in range(dice):
                    result += random.randint(1, 6)
                physical_dmg = self._get_attribute(char_url, "physical_damage_current")
                if physical_dmg:
                    result -= int(physical_dmg) / 3
                stun_dmg = self._get_attribute(char_url, "stun_damage_current")
                if stun_dmg:
                    result -= int(stun_dmg) / 3
                self.send_message_channel(from_user, "%s has initiative %d (on %d + %d D6)" % (
                    get_user_name(from_user, args), result, base, dice))
            except ValueError:
                raise CommandException("Error in command. Say \"!help sr_ini\" for help.")

    def _on_vamp(self, from_user, args):
        """Private method for making Vampire success tests."""
        if len(args) <= 1:
            raise CommandException("Error in command. Say \"!help vamp\" for help.")
        try:
            target_number = self._eval_number(from_user, args, args[0])
            n_dice = self._eval_number(from_user, args, args[1])
            if (n_dice < 1) or (target_number < 2):
                raise CommandException("Error in command. Invalid target number or amount of dice")

            str_buf = ""
            fails = 0
            successes = 0
            for i in range(n_dice):
                result = random.randint(1, 10)
                if result == 1:
                    fails += 1
                if result >= target_number:
                    successes += 1
                str_buf = str_buf + str(result) + " "
            if (successes > 0) and (fails < successes):
                self.send_message_channel(from_user, get_user_name(from_user, args) + (
                    " made it with %d successes on %d against %d. Results: " % (
                        successes - fails, n_dice, target_number)) + str_buf)
            else:
                if (fails > 0) and (successes == 0):
                    self.send_message_channel(from_user,
                                              "CATASTROPHIC FAILURE. It was nice knowing you, " +
                                              get_user_name(from_user, args) + ". Results: " + str_buf)
                else:
                    self.send_message_channel(from_user, get_user_name(from_user, args) + (
                        " failed on %d against %d. Results: " % (n_dice, target_number)) + str_buf)
        except exceptions.ValueError:
            self.send_message(from_user, "Error in command. Say \"!help vamp\" for help.")

    def _on_help(self, from_user, args):
        if len(args) < 2:
            self.send_message(from_user,
                              "Available commands are \"!roll\" for general purpose dice rolls and \"!roll_sr\", \"!sr\", \"!sr_open\" or \"!sr_ini\" for Shadowrun 3 related rolls and !sr5 for Shadowrun 5 rolls. Use !vamp for Vampire rolls.")
        else:
            if args[1] == "roll":
                self.send_message(from_user, "Usage: \"!roll nDd\". Example: \"!roll 2+1D6\" rolls 3 D6.")
            if args[1] == "roll_sr":
                self.send_message(from_user,
                                  "Usage: \"!roll_sr target_number dice_pool\". Example: \"!roll_sr 2+1 6-1\" makes a test against target number 3 with 5 dice.")
            if args[1] == "sr":
                self.send_message(from_user,
                                  "Usage: \"!sr target_number dice_pool\". Example: \"!sr 2+1 6-1\" makes a test against target number 3 with 5 dice.")
            if args[1] == "sr_open":
                self.send_message(from_user,
                                  "Usage: \"!sr_open dice_pool\". Example: \"!sr_open 6-1\" makes an open test with 5 dice.")
            if args[1] == "sr_ini":
                self.send_message(from_user,
                                  "Usage: \"!sr_ini ini_base nDice\". Example: \"!sr_ini 5-1 2\" makes an initiative roll with base 4 plus two D6.")
            if args[1] == "vamp":
                self.send_message(from_user,
                                  "Usage: \"!vamp target_number dice_pool\". Example: \"!vamp 2+1 6-1\" makes a test against target number 3 with 5 dice.")
            if args[1] == "sr5":
                self.send_message(from_user,
                                  "Usage: \"!sr5 dice_pool\". Example: \"!sr5 4+5-1\" makes a roll against 8 dice.")

    def on_bang(self, from_user, *args):
        """Callback method for bang messages.
    
    'Bang messages' are messages that start
    with a '!' character and are treated
    as commands.
    
    Currently interpreted commands are:
    * !roll for general purpose dice rolls
    * !roll_sr or !sr for Shadowrun 3 success tests
    * !sr_ini for Shadowrun initiative rolls
    * !sr_open for Shadowrun open rolls
    * !sr5 for Shadowrun 5 success tests
    * !vamp for Vampire rolls
    * !help explains the command syntax to users
        :param args:
        :param from_user:

    """
        print "Command: " + str(args)
        if args[0] in self._implemented_commands:
            try:
                self._implemented_commands[args[0]](from_user, ParsedArguments(args[1:]))
            except CommandException as err:
                self.send_message(from_user, err.__str__())

        elif args[0] == "help":
            self._on_help(from_user, args)
        else:
            self.send_message(from_user, "Error in command. Say \"!help\" for help.")
