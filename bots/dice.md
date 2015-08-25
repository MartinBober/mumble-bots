# DiceBot Reference

## Command structure

Every command for DiceBot starts with an exclamation mark ("!") followed immediately by the command verb. Additional parameters are provided after the verb separated by white spaces. Example:

> `!verb param1 param2`

All parameters expect integer values. Simple mathematical terms consisting of addition ("+") and subtraction ("-") will be evaluated before being used as parameters. For example, `2+3-1` will be evaluated to `4`.

## charXchange integration

If you set the URL to your character at [charXchange](https://charxchange.com) as your Mumble user comment, DiceBot will try to replace given attribute's API names with their values. For example `intuition+reaction` will be evaluated to `10` if your character has an attribute `intuition` with value `4` and an attribute `reaction` with value `6`.

## Command reference

### General purpose dice roll

> `!roll <n>d<type>`

Example:

> `!roll 3d12`

This will roll `<n>` dice resulting in with values between 1 and `<type>`.

### Shadowrun

#### Shadowrun 3 common roll

> `!sr <target> <pool>`

Example:

> `!sr 4 10`

This will perform a normal 3rd Edition dice roll with target number `<target>` and a pool of `<pool>` dice.

#### Shadowrun 3 open roll

> `!sr_open <pool>`

Example:

> `!sr_open 8`

This will perform an open 3rd edition roll with a pool of `<pool>` dice and yield the highest result.

#### Initiative roll

> `!sr_ini <base> <dice>`

> `!sr_ini`

> `!sr ini <mode>`

Examples:

> `!sr_ini 8 2`

> `!sr_ini`

> `!sr_ini matrix_cold`

In the first form, this does an initiative role with a base initiative `<base>` plus `<dice>` D6.

In the second form, the same roll is done as in the first form but DiceBot will use the character's `initiative_base` and `initiative_dice` attributes.

In the third form, the character's `initiative_<mode>_base` and `initiative_<mode>_dice` attributes will be used.

In the late two cases, the character's `stun_damage_current` and `physical_damage_current` attributes will be used to apply damage modifiers automatically.

#### Shadowrun 5 roll

> `!sr5 <dice> [--explode] [--no-dmg]`

Examples:

> `!sr5 10`

> `!sr5 6 --explode`

> `!sr5 8 --no-dmg`

> `!sr5 13 --explode --no-dmg`

This command will perform a Shadowrun dice roll (5th edition) with `<dice>` dice. The "exploding sixes" rule will be applied if you provide the `--explode` option. Notice that your `edge` attribute will **not** be added automatically to your dice pool.

Your character's `stun_damage_current` and `physical_damage_current` attributes will be used to apply damage modifiers to the dice pool automatically *unless* you provide the `--no-dmg` option.

### Vampire (old World of Darkness)

> `!vamp <target> <pool>`

This will perform a Vampire (old World of Darkness) roll with a target number of `<target>` and a dice pool of `<pool>`.

### Help

> `!help [<verb>]`

Examples:

> `!help`

> `!help sr_ini`

Calling the `help` verb without any parameter will give you a list of all available verbs. Calling `!help` with a verb will give you information about the verb's expected parameters.