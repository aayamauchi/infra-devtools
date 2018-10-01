#!/usr/bin/env python

# This is a personally developed stuff that I (Alex Yamauchi) created, circa
# 2014, prior to my employment at Hotschedules.  I am adding it here since I
# use it constantly and think others may find it useful.  I plan to publish
# this, along with some other shell utility content, at some point -- under
# and unopensource license and reserve all rights to do so.

import sys
import os

from utils import data_diff
from yaml import load,dump
import simplejson as json

obj = []
for fh in [ open(x,'r') for x in sys.argv[1:] ]:
    obj.append(load(fh))
    fh.close()

if 'OUTPUT_FORMAT' in os.environ and os.environ['OUTPUT_FORMAT'] == 'yaml':
    sys.stdout.write('%s\n' % (dump(data_diff(obj[0],obj[1]))))
else:
    sys.stdout.write('%s\n' % (json.dumps(data_diff(obj[0],obj[1]),sort_keys=True,indent=2)))
