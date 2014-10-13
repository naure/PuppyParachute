

#? what=that -> Done
def do_things(what):
    print('Doing {}'.format(what))
    return 'Done'

#?  -> Everything is alright
def main():
    do_things('this')
    do_things('that')
    return 'Everything is alright'
