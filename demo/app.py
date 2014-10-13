

#? what=that -> Done
def do_things(what):
    print('Doing {}'.format(what))
    if 'a' in what:
        return 'Done something different'
    return 'Done'

#?  -> Everything is alright
def main():
    do_things('this')
    do_things('that')
    return 'Everything is alright'
