import time
from util.hook import *


@hook(rule=r'.*', event='251', priority='low')
def startup(code, input):
    if code.config('nickserv_password'):
        if code.config('nickserv_username'):
            args = code.config('nickserv_username') + ' ' + \
                code.config('nickserv_password')
        else:
            args = code.config('nickserv_password')
        if code.config('nickserv_is_x'):
            code.write(['PRIVMSG', 'x@channels.undernet.org'], 'login %s' % args, output=False)
        else:
            code.write(['PRIVMSG', 'NickServ'], 'IDENTIFY %s' % args, output=False)
        time.sleep(5)

    # Assume it's for bots, y'know
    code.write(('MODE', code.nick, '+B'))

    for channel in code.channels:
        code.join(channel)
        code.write(('WHO', channel, '%tcuhn,1'))
        time.sleep(0.5)
