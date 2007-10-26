#!/usr/bin/env python
#
# This file is part of pysubwcrev.
#
# pysubwcrev is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pysubwcrev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pysubwcrev.  If not, see <http://www.gnu.org/licenses/>.

from optparse import OptionParser
from time import strftime, gmtime
import os, pysvn, re, sys

def gather(workingCopyDir, opts):
    #debug
    #print "workingCopyDir: " + workingCopyDir

    client = pysvn.Client()
    #print client.info(workingCopyDir).url

    maxdate = 0
    maxrev = 0
    minrev = sys.maxint
    hasMods = False

    # ignore externals if e isn't a given option
    ignoreExt = 'e' not in opts

    for stat in client.status(workingCopyDir, ignore_externals=ignoreExt):
        # skip externals if desired
        if stat.text_status == pysvn.wc_status_kind.external and ignoreExt:
            continue;

        if stat.entry:
            # skip directories if not specified
            if stat.entry.kind == pysvn.node_kind.dir and 'f' not in opts:
                continue;
            if stat.entry.revision.number > maxrev:
                maxrev = stat.entry.revision.number
            if stat.entry.revision.number < minrev:
                minrev = stat.entry.revision.number
            if stat.entry.commit_time > maxdate:
                maxdate = stat.entry.commit_time
            if stat.text_status == pysvn.wc_status_kind.modified:
                hasMods = True
            if stat.prop_status == pysvn.wc_status_kind.modified:
                hasMods = True

    wcrange = "%s:%s" % (minrev, maxrev)
    isMixed = True
    if minrev == maxrev:
        wcrange = "%s" % (maxrev)
        isMixed = False

    results = {
        'wcrange' : wcrange,
        'wcmixed' : isMixed,
        'wcmods'  : hasMods,
        'wcrev'   : maxrev,
        'wcurl'   : client.info(workingCopyDir).url,
        'wcdate'  : strftime("%Y-%m-%d %H:%M:%S", gmtime(maxdate)),
        'wcnow'   : strftime("%Y-%m-%d %H:%M:%S", gmtime())
    }

    #print results
    return results

def process(inFile, outFile, info, opts):

    # if wanted, exit if the out file exists
    if 'd' in opts and os.path.exists(outFile):
        sys.exit(9)

    fin = open(inFile, 'r')
    fout = open(outFile, 'w')
    for line in fin:
        tmp = re.sub(r'\$WCDATE\$', str(info['wcdate']), line)
        tmp = re.sub(r'\$WCNOW\$', str(info['wcnow']), tmp)
        tmp = re.sub(r'\$WCRANGE\$', str(info['wcrange']), tmp)
        tmp = re.sub(r'\$WCREV\$', str(info['wcrev']), tmp)
        tmp = re.sub(r'\$WCURL\$', str(info['wcurl']), tmp)

        match = re.search(r'\$WCMODS\?(.*):(.*)\$', tmp)
        if match:
            idx = 1
            if not info['wcmods']:
                idx = 2
            tmp = re.sub(r'\$WCMODS.*\$', match.group(idx), tmp)

        match = re.search(r'\$WCMIXED\?(.*):(.*)\$', tmp)
        if match:
            idx = 1
            if not info['wcmixed']:
                idx = 2
            tmp = re.sub(r'\$WCMIXED.*\$', match.group(idx), tmp)

        fout.write(tmp)

    fin.close()
    fout.close()

if __name__ == "__main__":
    usage = """usage: pysubwcrev workingCopyPath [SrcVersionFile DestVersionFile] [-nmdfe]
"""

    if len(sys.argv) not in (2, 3, 4, 5):
        sys.exit(usage)

    workingCopyDir = os.path.abspath(sys.argv[1].strip())
    srcFile = ''
    destFile = ''
    opts = []
    
    shouldProcess = False
    
    if len(sys.argv) == 3: # just path and args
        if sys.argv[2].find('n') > 0:
            opts += 'n'
        if sys.argv[2].find('m') > 0:
            opts += 'm'
        if sys.argv[2].find('d') > 0:
            opts += 'd'
        if sys.argv[2].find('f') > 0:
            opts += 'f'
        if sys.argv[2].find('e') > 0:
            opts += 'e'
    elif len(sys.argv) == 4: # just files
        srcFile = os.path.abspath(sys.argv[2].strip())
        if not os.path.exists(srcFile):
            sys.exit(usage)
        destFile = os.path.abspath(sys.argv[3].strip())
        shouldProcess = True
    elif len(sys.argv) == 5: # files and args
        srcFile = os.path.abspath(sys.argv[2].strip())
        if not os.path.exists(srcFile):
            sys.exit(usage)
        destFile = os.path.abspath(sys.argv[3].strip())
        shouldProcess = True
        if sys.argv[4].find('n') > 0:
            opts += 'n'
        if sys.argv[4].find('m') > 0:
            opts += 'm'
        if sys.argv[4].find('d') > 0:
            opts += 'd'
        if sys.argv[4].find('f') > 0:
            opts += 'f'
        if sys.argv[4].find('e') > 0:
            opts += 'e'

    repoInfo = gather(workingCopyDir, opts)
    print repoInfo

    if 'n' in opts and repoInfo['wcmods']:
        sys.exit(7)
    elif 'm' in opts and repoInfo['wcmixed']:
        sys.exit(8)

    if shouldProcess:
        process(srcFile, destFile, repoInfo, opts)
