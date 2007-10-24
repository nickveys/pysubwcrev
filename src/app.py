from optparse import OptionParser
from time import strftime, gmtime
import os, pysvn, re, sys

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
    results['wcdate']  = wcdate
    results['wcnow']   = wcnow
    results['wcrange'] = wcrange
    results['wcrev']   = wcrev
    results['wcmixed'] = wcmixed
    results['wcmods']  = wcmods
    results['wcurl']   = wcurl

    #print results
    return results

def process(inFile, outFile, info):
    
    fin = open(inFile, 'r')
    fout = open(outFile, 'w')
    for line in fin:
        tmp = re.sub(r'\$WCDATE\$', str(info['wcdate']), line)
        tmp = re.sub(r'\$WCNOW\$', str(info['wcnow']), tmp)
        tmp = re.sub(r'\$WCRANGE\$', str(info['wcrange']), tmp)
        tmp = re.sub(r'\$WCREV\$', str(info['wcrev']), tmp)
        tmp = re.sub(r'\$WCMODS.*\$', str(info['wcmods']), tmp)
        tmp = re.sub(r'\$WCMIXED.*\$', str(info['wcmixed']), tmp)
        tmp = re.sub(r'\$WCURL\$', str(info['wcurl']), tmp)
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

    repoInfo = gather(workingCopyDir)

    if shouldProcess:
        process(srcFile, destFile, repoInfo)
