import os
import logging

BACKEND = os.environ.get('BACKEND', 'Text')

BOT_DATA_DIR = '/errbot/data'
BOT_EXTRA_PLUGIN_DIR = os.environ.get('BOT_EXTRA_PLUGIN_DIR', '/errbot/plugins')

# If you use an external backend as a plugin,
# this is where you tell err where to find it.
# BOT_EXTRA_BACKEND_DIR = '/srv/errbackends'

CORE_PLUGINS = tuple(os.environ['CORE_PLUGINS'].split(',')) \
    if os.environ.get('CORE_PLUGINS') else None

BOT_LOG_FILE = '/errbot/err.log'

BOT_LOG_LEVEL = logging.getLevelName(os.environ.get('BOT_LOG_LEVEL', 'INFO'))

SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
BOT_LOG_SENTRY = bool(SENTRY_DSN)
SENTRY_LOGLEVEL = BOT_LOG_LEVEL

# Execute commands in asynchronous mode. In this mode, Err will spawn 3
# seperate threads to handle commands, instead of blocking on each
# single command.
BOT_ASYNC = True

##########################################################################
# Account and chatroom (MUC) configuration                               #
##########################################################################

BOT_IDENTITY = {}

# username
if 'BOT_USERNAME' in os.environ:
    BOT_IDENTITY['username'] = os.environ['BOT_USERNAME']

# password
if 'BOT_PASSWORD' in os.environ:
    BOT_IDENTITY['password'] = os.environ['BOT_PASSWORD']

# server
if 'BOT_SERVER' in os.environ:
    if ':' in os.environ['BOT_SERVER']:
        server, port = os.environ['BOT_SERVER'].split(':')
        BOT_IDENTITY['server'] = (server, int(port))
    else:
        BOT_IDENTITY['server'] = os.environ['BOT_SERVER']

# token
if 'BOT_TOKEN' in os.environ:
    BOT_IDENTITY['token'] = os.environ['BOT_TOKEN']

# endpoint
if 'BOT_ENDPOINT' in os.environ:
    BOT_IDENTITY['endpoint'] = os.environ['BOT_ENDPOINT']

# nickname
if 'BOT_NICKNAME' in os.environ:
    BOT_IDENTITY['nickname'] = os.environ['BOT_NICKNAME']

# port
if 'BOT_PORT' in os.environ:
    BOT_IDENTITY['port'] = int(os.environ['BOT_PORT'])

# ssl
if 'BOT_SSL' in os.environ:
    BOT_IDENTITY['ssl'] = os.environ['BOT_SSL']

# The identity, or credentials, used to connect to a server
# BOT_IDENTITY = {
# XMPP (Jabber) mode
# 'username': 'err@localhost',  # The JID of the user you have created for the bot
# 'password': 'changeme',       # The corresponding password for this user
# 'server': ('host.domain.tld',5222), # server override

## HipChat mode (Comment the above if using this mode)
# 'username' : '12345_123456@chat.hipchat.com',
# 'password' : 'changeme',
## Group admins can create/view tokens on the settings page after logging
## in on HipChat's website
# 'token'    : 'ed4b74d62833267d98aa99f312ff04',
## If you're using HipChat server (self-hosted HipChat) then you should set
## the endpoint below. If you don't use HipChat server but use the hosted version
## of HipChat then you may leave this commented out.
# 'endpoint' : 'https://api.hipchat.com'

## Slack Mode (comment the others above if using this mode)
# 'token': 'xoxb-4426949411-aEM7...',

## IRC mode (Comment the others above if using this mode)
# 'nickname' : 'err-chatbot',
# 'username' : 'err-chatbot',    # optional, defaults to nickname if omitted
# 'password' : None,             # optional
# 'server' : 'irc.freenode.net',
# 'port': 6667,                  # optional
# 'ssl': False,                  # optional
# }

## TOX Mode
# TOX_BOOTSTRAP_SERVER = ["54.199.139.199", 33445, "7F9C31FE850E97CEFD4C4591DF93FC757C7C12549DDD55F8EEAECC34FE76C029"]

# Set the admins of your bot. Only these users will have access
# to the admin-only commands.
#
# Campfire syntax is the full name:
# BOT_ADMINS = ('Guillaume Binet',)
#
# TOX syntax is a hash.
# BOT_ADMINS = ['F9886B47503FB80E6347CC0907D8000144305796DE54693253AA5E574E5E8106C7D002557189', ]
BOT_ADMINS = tuple(
    os.environ.get('BOT_ADMINS', 'admin@localhost').split(','),
)
# Chatrooms your bot should join on startup. For the IRC backend you
# should include the # sign here. For XMPP rooms that are password
# protected, you can specify another tuple here instead of a string,
# using the format (RoomName, Password).
CHATROOM_PRESENCE = tuple(os.environ['CHATROOM_PRESENCE'].split(',')
                          if os.environ.get('CHATROOM_PRESENCE') else [])

# The FullName, or nickname, your bot should use. What you set here will
# be the nickname that Err shows in chatrooms. Note that some XMPP
# implementations, notably HipChat, are very picky about what name you
# use. In the case of HipChat, make sure this matches exactly with the
# name you gave the user.
CHATROOM_FN = os.environ.get('CHATROOM_FN', 'Err')

##########################################################################
# Prefix configuration                                                   #
##########################################################################

# Command prefix, the prefix that is expected in front of commands directed
# at the bot.
#
# Note: When writing plugins,you should always use the default '!'.
# If the prefix is changed from the default, the help strings will be
# automatically adjusted for you.
#
BOT_PREFIX = os.environ.get('BOT_PREFIX', '!')

# Uncomment the following and set it to True if you want the prefix to be
# optional for normal chat.
# (Meaning messages sent directly to the bot as opposed to within a MUC)
# BOT_PREFIX_OPTIONAL_ON_CHAT = False
BOT_PREFIX_OPTIONAL_ON_CHAT = bool(
    os.environ.get('BOT_PREFIX_OPTIONAL_ON_CHAT', False)
)

# You might wish to have your bot respond by being called with certain
# names, rather than the BOT_PREFIX above. This option allows you to
# specify alternative prefixes the bot will respond to in addition to
# the prefix above.
# BOT_ALT_PREFIXES = ('Err',)
BOT_ALT_PREFIXES = tuple(
    os.environ.get('BOT_ALT_PREFIXES', 'Err').split(','),
)

# If you use alternative prefixes, you might want to allow users to insert
# separators like , and ; between the prefix and the command itself. This
# allows users to refer to your bot like this (Assuming 'Err' is in your
# BOT_ALT_PREFIXES):
# "Err, status" or "Err: status"
#
# Note: There's no need to add spaces to the separators here
#
# BOT_ALT_PREFIX_SEPARATORS = (':', ',', ';')
BOT_ALT_PREFIX_SEPARATORS = tuple(
    os.environ.get('BOT_ALT_PREFIX_SEPARATORS', ': , ;').split(' '),
)

# Continuing on this theme, you might want to permit your users to be
# lazy and not require correct capitalization, so they can do 'Err',
# 'err' or even 'ERR'.
# BOT_ALT_PREFIX_CASEINSENSITIVE = True
BOT_ALT_PREFIX_CASEINSENSITIVE = bool(
    os.environ.get('BOT_ALT_PREFIX_CASEINSENSITIVE', False)
)

##########################################################################
# Access controls and message diversion                                  #
##########################################################################

# Access controls, allowing commands to be restricted to specific users/rooms.
# Available filters (you can omit a filter or set it to None to disable it):
#   allowusers: Allow command from these users only
#   denyusers: Deny command from these users
#   allowrooms: Allow command only in these rooms (and direct messages)
#   denyrooms: Deny command in these rooms
#   allowprivate: Allow command from direct messages to the bot
#   allowmuc: Allow command inside rooms
# Rules listed in ACCESS_CONTROLS_DEFAULT are applied when a command cannot
# be found inside ACCESS_CONTROLS
#
# Example:
# ACCESS_CONTROLS_DEFAULT = {} # Allow everyone access by default
# ACCESS_CONTROLS = {'status': {'allowrooms': ('someroom@conference.localhost',)},
#                   'about': {'denyusers': ('baduser@localhost',), 'allowrooms': ('room1@conference.localhost', 'room2@conference.localhost')},
#                   'uptime': {'allowusers': BOT_ADMINS},
#                   'help': {'allowmuc': False},
#                  }

CRITICAL_COMMANDS = os.environ.get('CRITICAL_COMMANDS', "")
OPERATORS = os.environ.get('OPERATORS', "")
PRIVATE_COMMANDS = os.environ.get('PRIVATE_COMMANDS', "")

critical_commands = CRITICAL_COMMANDS.split(",")
operators = tuple(OPERATORS.split(","))
private_commands = PRIVATE_COMMANDS.split(",")

ACCESS_CONTROLS = {}
cmd_list = []
for cmd in set(critical_commands) | set(private_commands):
    cmd_policy = {}
    if cmd in private_commands:
        cmd_policy["allowmuc"] = False
    if cmd in critical_commands:
        cmd_policy["allowusers"] = operators
    ACCESS_CONTROLS[cmd] = cmd_policy



# Uncomment and set this to True to hide the restricted commands from
# the help output.
# HIDE_RESTRICTED_COMMANDS = False
HIDE_RESTRICTED_COMMANDS = bool(
    os.environ.get('HIDE_RESTRICTED_COMMANDS', False)
)

# Uncomment and set this to True to ignore commands from users that have no
# access for these instead of replying with error message.
# HIDE_RESTRICTED_ACCESS = False
HIDE_RESTRICTED_ACCESS = bool(
    os.environ.get('HIDE_RESTRICTED_ACCESS', False)
)

DIVERT_TO_PRIVATE = tuple(
    os.environ.get('DIVERT_TO_PRIVATE', '').split(','),
)
