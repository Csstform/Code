import time
from util.hook import *
from util import database
from util import tools


maxchars = 400
db = {}
bot = ''


def setup(code):
    """
        Read the database and globalize the variable on module-load.
        Reading/writing is ONLY done when adding data, removing data,
        or the module is being initialized. Less read-write than the
        old tell.py module.
    """
    global bot
    bot = code.default
    read_db()


def read_db():
    """Read from the tell database"""
    global db
    db = database.get(bot, 'tell')
    if not db:
        db = {}


def save_db():
    """Save the local db variable to the database"""
    global db
    database.set(bot, db, 'tell')


@hook(cmds=['tell', 'note'], ex='tell Allen PM me your password!', args=True)
def tell(code, input):
    """tell <user> [#channel] <message> -- Save a note so that when <user> gets on it replays"""
    global db
    if not input.sender.startswith('#'):
        return code.say('{b}You must use this in a channel')

    if len(input.group(2).split()) < 2:
        return code.say('{red}{b}Invalid usage. Use %shelp tell' % code.prefix)
    location, msg = input.group(2).split(' ', 1)
    if msg.split(' ', 1)[0].startswith('#'):
        # Assume they want it in a specific channel..
        channel = msg.split(' ', 1)[0]
        msg = msg.split(' ', 1)[1]
    else:
        channel = False

    if location.startswith('#'):
        return code.say('{red}{b}Invalid usage. Use %shelp tell' % code.prefix)

    if location.lower() in ['code', code.nick.lower()]:
        return code.reply('{b}Thanks for letting me know.')

    if location == input.nick:
        return code.reply('{b}You can tell yourself that.')

    if location.lower() in db:
        for entry in db[location.lower()]:
            if msg == entry['msg'] and input.nick.lower() == entry['sender'].lower():
                return code.reply('{red}That message is already pending!')
    curr = int(time.time())
    entry = {'time': curr, 'msg': msg, 'sender': input.nick, 'channel': channel}
    if not location.lower() in db:
        db[location.lower()] = [entry]
    else:
        db[location.lower()].append(entry)
    save_db()
    code.reply('{b}I\'ll let them know when I see them.')


@hook(rule=r'(.*)', priority='low')
def tell_trigger(code, input):
    """Dispatch notes to users if their name was found in the database"""
    #if not input.sender.startswith('#'):
    #    return

    if input.nick.lower() not in db:
        return

    if not db[input.nick.lower()]:
        return

    count = 0
    lines = 1
    queue = ''
    template = '{b}(%s){b} {b}<%s>{b} %s'
    note_nick = '{blue}{b}%s{b}, you have notes!:{c}' % input.nick
    note_more = '{blue}{b}And more notes..{c}{b}'
    tmp_entries = db[input.nick.lower()]
    for i in range(len(tmp_entries)):
        entry = db[input.nick.lower()][i]
        if 'channel' in entry:
            if entry['channel']:
                if entry['channel'].lower() != input.sender.lower() and input.sender.startswith('#'):
                    continue
        count += 1
        if lines == 1:
            note_msg = note_nick
        else:
            note_msg = note_more
        if (len(queue) + 25 + len(entry['msg'])) > maxchars:
            code.say('%s %s' % (note_msg, queue))
            lines += 1
            queue = template % (time_diff(entry['time']), entry['sender'], entry['msg'])
        else:
            tmp = template % (time_diff(entry['time']), entry['sender'], entry['msg'])
            if queue:
                queue = queue + ' '
            queue = queue + tmp
        del db[input.nick.lower()][i]
    if lines == 1:
        note_msg = note_nick
    else:
        note_msg = note_more
    save_db()
    if len(queue) > 0:
        code.say('%s %s' % (note_msg, queue))


def time_diff(checked):
    """Get the time, in differences between stored and current"""
    curr = int(time.time())
    return tools.relative(seconds=int(curr - int(checked)))[0] + ' ago'
