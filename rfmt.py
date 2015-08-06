#!/usr/bin/env python

#  Copyright 2015 Google Inc. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Main module for R source code formatter rfmt.

Command line help:

"""

import cStringIO
import os.path
import re
import shutil
import sys
import argparse

from formatter import base
from formatter import google_format
from formatter import r_language


# Command line argument configuration.
ap = argparse.ArgumentParser(description='R source code formatter',
                             formatter_class=argparse
                             .ArgumentDefaultsHelpFormatter)
ap.add_argument('file', help='source file name (will be overwritten); use '
                'stdin/out if omitted.', nargs='?')
ap.add_argument('-b', '--backup', default=True, type=bool, dest='bak',
                help='backup source \'FILE\' to \'FILE.bak\'', metavar='B')
ap.add_argument('-m0', '--margin0', default=0, type=int,
                help='position of the first right margin', dest='m0')
ap.add_argument('-m1', '--margin1', default=80, type=int,
                help='position of the second right margin', dest='m1')
ap.add_argument('-c0', '--cost0', default=.05, type=float,
                help='cost (per character) beyound margin 0', dest='c0')
ap.add_argument('-c1', '--cost1', default=100, type=float,
                help='cost (per character) beyound margin 1', dest='c1')
ap.add_argument('-cb', '--costb', default=2, type=float,
                help='cost per line-break', dest='cb')
ap.add_argument('-i', '--indent', default=2, type=int,
                help='spaces per indent', dest='ind')
ap.add_argument('--adj_comment', default=.25, type=float,
                help='break cost adjustment in comments', metavar='ADJC')
ap.add_argument('--adj_flow', default=.3, type=float,
                help='break cost adjustment in flow constructs', metavar='ADJF')
ap.add_argument('--adj_call', default=.25, type=float,
                help='break cost adjustment in function calls', metavar='ADJCL')
ap.add_argument('--adj_arg', default=40, type=float,
                help='break cost adjustment in arguments', metavar='ADJA')
ap.add_argument('--cpack', default=1e-3, type=float,
                help='cost (per element) for packing justified layouts')


def main():
  """Main command routine."""
  remove_backup = False
  try:
    options = base.Options()
    ap.parse_args(namespace=options)
    options.Check()
    if options.file:  # Input is from a file
      f_path = os.path.abspath(os.path.expanduser(options.file))
      try:
        f_input = open(f_path, 'r')
      except IOError:
        if os.path.isfile(f_path):
          err_msg = 'Cannot open file "%s" for reading'
        else:
          err_msg = 'File "%s" does not exist'
        raise base.Error(err_msg % f_path)
      if options.bak:  # Make a source backup
        try:
          bak_path = f_path + '.bak'
          shutil.copy(f_path, bak_path)
          remove_backup = True
        except Exception:
          f_input.close()
          raise base.Error('Cannot copy file "%s" to "%s"' % (f_path, bak_path))
      print >>sys.stderr, 'Formatting file "%s"' % options.file
    else:
      f_input = sys.stdin
    # Parse source.
    ptree = r_language.ParseTreeFor(f_input)
    if not ptree.exprlist.elements:
      print >>sys.stderr, 'Empty file: "%s"' % options.file
      sys.exit(0)
    # Generate blocks from parse tree.
    blocks = google_format.GoogleFormatPolicy().BlocksFor(ptree)
    # Have generated blocks calculate optimal layout and print on
    # string buffer. (Use of string buffer facilitates trailing space
    # removal below.)
    outp = cStringIO.StringIO()
    blocks.PrintOn(outp)
    format_result = re.sub(r' *$', '', outp.getvalue(), flags=re.MULTILINE)
    # Write to file or stdout, as required.
    if options.file:
      f_input.close()
      try:
        with open(f_path, 'w') as f_output:
          print >>f_output, format_result
          print >>sys.stderr, ('Formatting of file "%s" complete' %
                               options.file)
          remove_backup = False
      except IOError:
        raise base.Error('Cannot write to file "%s"' % f_path)
    else:
      print format_result
  except base.Error as e:  # Format-specific errors.
    print >>sys.stderr, e.msg
    if remove_backup:  # Delete backup if formatting was unsuccessful.
      os.remove(bak_path)
    sys.exit(1)
  except IOError:  # These are usually the result of misuse of the command.
    print FLAGS.MainModuleHelp()


# Conditional script stanza
if __name__ == '__main__':
  main()
