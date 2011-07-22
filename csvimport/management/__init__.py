from django.core.management import _commands, get_commands 

if _commands is None:
    _commands = get_commands()

_commands['csvimport'] = 'djangocsvimport'

        


