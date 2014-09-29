from util.hook import *
from util import web

@hook(cmds=['wa'], ex='wa 1 mile in feet', args=True)
def wa(code, input):
    """Wolphram Alpha search"""
    query = input.group(2)
    uri = 'http://tumbolia.appspot.com/wa/'
    try:
        answer = web.get(uri + web.quote(query), timeout=10).read()
    except timeout:
        return code.say('It seems WolphramAlpha took too long to respond!')

    if answer and 'json stringified precioussss' not in answer:
        answer = answer.split(';')
        if len(answer) > 3:
            answer = answer[1]
        answer = '{purple}{b}WolphramAlpha: {c}{b}' + answer
        while '  ' in answer:
            answer = answer.replace('  ', ' ')
        return code.say(web.htmlescape(answer))
    else:
        return code.reply('{red}Sorry, no result.')