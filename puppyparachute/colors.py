import sys
import re

# Optional colored output
if sys.stdout.isatty():
    ENDCOLOR = '\033[0m'

    def color(s, code):
        ' Make `s` a colored text. Can be nested. '
        return '{}{}{}'.format(
            code,
            s.replace(ENDCOLOR, code),
            ENDCOLOR,
        )

    def gray(s):
        return color(s, '\033[97m')

    def blue(s):
        return color(s, '\033[94m')

    def green(s):
        return color(s, '\033[92m')

    def orange(s):
        return color(s, '\033[93m')

    def red(s):
        return color(s, '\033[91m')

    re_restore = re.compile(r'\\+e(\\\s*)?\[')

    def restore_colors(s):
        ' Unescape terminal control codes in yaml to display colors '
        return re_restore.sub('\033[', s)

else:
    # No colored output
    color = lambda s, c: s
    gray = blue = green = orange = red = restore_colors = lambda s: s
