from optparse import OptionParser
from time import strftime, gmtime
import pysvn, os, sys

def gather(workingCopyDir):
    #debug
    #print "workingCopyDir: " + workingCopyDir

    client = pysvn.Client()
    #print client.info(workingCopyDir).url

    maxdate = 0
    maxrev = 0
    minrev = 9999999
    wcmods = False

    for stat in client.status(workingCopyDir):
        if stat.entry:
            if stat.entry.revision.number > maxrev:
                maxrev = stat.entry.revision.number
            if stat.entry.revision.number < minrev:
                minrev = stat.entry.revision.number
            if stat.entry.commit_time > maxdate:
                maxdate = stat.entry.commit_time
            if stat.text_status == pysvn.wc_status_kind.modified:
                wcmods = True
            if stat.prop_status == pysvn.wc_status_kind.modified:
                wcmods = True

    wcrev = maxrev
    wcdate = strftime("%Y-%m-%d %H:%M:%S", gmtime(maxdate))
    wcnow = strftime("%Y-%m-%d %H:%M:%S")
    wcrange = "%s:%s" % (minrev, maxrev)
    wcmixed = True
    if minrev == maxrev:
        wcrange = "%s" % (wcrev)
        wcmixed = False
    wcurl = client.info(workingCopyDir).url

    #print wcrev
    #print wcdate
    #print wcnow
    #print wcrange
    #print wcmixed
    #print wcmods
    #print wcurl
    
    results = {}
    results['wcrev'] = wcrev
    results['wcdate'] = wcdate
    results['wcnow'] = wcnow
    results['wcrange'] = wcrange
    results['wcmixed'] = wcmixed
    results['wcmods'] = wcmods
    results['wcurl'] = wcurl

    print results
    return results

if __name__ == "__main__":
    usage = """usage: pysubwcrev workingCopyPath [SrcVersionFile DestVersionFile] [-nmdfe]
"""

    if len(sys.argv) not in (2, 3, 4, 5):
        sys.exit(usage)

    workingCopyDir = os.path.abspath(sys.argv[1].strip())
    srcFile = ''
    destFile = ''
    opts = []
    
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
        srcFile = sys.argv[2]
        destFile = sys.argv[3]
    elif len(sys.argv) == 5: # files and args
        srcFile = sys.argv[2]
        destFile = sys.argv[3]
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

    gather(workingCopyDir)
    print opts
