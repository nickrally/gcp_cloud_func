#
# log_squish.py - when copying a log from Google Stackdriver logging page, for any log item
#                 the result will be a line per logging field.
#                 For our purposes with Google Clound Functions, each log item has 4 fields
#                 <timestamp> <function_name> <reference_number> <log_text>
#                 When we copy that in a buffer and paste it into a file, it looks like:
#                 <timestamp>
#                 <function_name>
#                 <reference_number>
#                 <log_text>
#
#                 this script reformats the "pasted content" file to look like what is
#                 displayed on the Google Cloud Stackdriver logging page
#
###################################################################################################
USAGE = """
Usage: log_squish.py <file_name> {--overwrite} 
       where the optional --overwrite flag indicates that the source file should be
        overwritten with the "squished" content 
"""
###################################################################################################

import sys, os
import re

###################################################################################################

TIMESTAMP_PATTERN = "^\d+-\d+-\d+ \d+:\d+:\d+\.\d+ [A-Z]{2,}T$"
EXCLUDED_MESSAGE = "Function execution started"

###################################################################################################

def main(args):
    if not args:
        sys.stderr.write(USAGE)
        sys.exit(1)

    target = args.pop(0)
    if target.startswith('--'):
        sys.stderr.write("Please provide the name of a real file with the 'vertically oriented' content\n")
        sys.stderr.write(USAGE)
        sys.exit(1)
    if not os.path.isfile(target):
        sys.stderr.write("Please provide the name of a real file with the 'vertically oriented' content\n")
        sys.stderr.write(USAGE)
        sys.exit(2)
    overwrite = False
    if args and args.pop(0)  == '--overwrite':
        overwrite = True

    content = []
    with open(target, 'r') as tf:
        content = tf.readlines()
        content = [item[:-1] for item in content]

    result = squishLog(content)
    for log_line in result:
        if log_line.endswith(EXCLUDED_MESSAGE):
            continue
        print(log_line)

###################################################################################################

def group(iterator, count):
    itr = iter(iterator)
    while True:
        yield tuple([itr.next() for i in range(count)])

def squishLog(vertically_oriented_content):
    horiz_content = []
    line = None
    for item in vertically_oriented_content:
        if re.match(TIMESTAMP_PATTERN, item):
            if line:
                horiz_content.append(line)
            line = item
            continue
        line += (" %s" % item)
    if line:
        horiz_content.append(line)
    return horiz_content



###################################################################################################
###################################################################################################

if __name__ == "__main__" :
    main(sys.argv[1:])
