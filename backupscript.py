#!/bin/python
#define backupfile etc.

import sys
import os
import datetime
import sys
import ctypes
import platform
import collections
import shutil

import unittest

class TestBackup(unittest.TestCase):
    def setUp(self):
        self.dstPath = os.path.abspath("./test/testoutputs/")
        pass

    def testDst(self):
        fileLines = [] 
        
        dstRelPaths, dstAbsPaths, dstHDDs, dstDates, dstSizes = getDstStats(self.dstPath, fileLines)


    def testSets(self):
        pass
        

    def testDeletion(self):
        deleteFiles(['blub'], {'blub': '1'},self.dstPath, sys.stdout )

    def testFreeSpace(self):
        print getFreeSpaceBytes(self.dstPath)

    def testGetFreeSpace(self):
        print getFreeSpaceLog('bla|blub', '5|4')

    def testUpdated(self):
        pass


def createBackupFile(backupFile, srcPath, dstPath):

    freeSpaceDict = {"Dummy": 0}

    with open(backupFile, 'w') as log:
        writeHeader(srcPath, dstPath, freeSpaceDict, log)

        

def getDstStats(dstPath, fileLines):
    dstDates = {}
    dstHDDs = {}
    dstSizes = {}
    for line in fileLines:
        linesplit = line.split("|")
        f = linesplit[1]
        dstHDDs[f] = linesplit[0]
        dstDates[f] = int(linesplit[2])
        dstSizes[f] = int(linesplit[3])


    dstRelPaths = dstDates.keys()
    dstAbsPaths = [os.path.join(dstPath, path) for path in dstRelPaths]

    return dstRelPaths, dstAbsPaths, dstHDDs, dstDates, dstSizes

def getSrcStats(srcPath):
    
    srcAbsPaths = []
    srcSizes = {}
    for root, dirs, files in os.walk(srcPath):
        srcAbsPaths.extend([os.path.join(root, f) for f in files])
    srcRelPaths = [os.path.relpath(path, srcPath) for path in srcAbsPaths]

    return srcRelPaths, srcAbsPaths

def getInventory(path):
    for root, dirs, files in os.walk(srcPath):
        srcAbsPaths.extend([os.path.join(root, f) for f in files])
    

def modifyDisks(delList, dstHDDs, dstPath, 
                addList, srcHDDs, srcPath, 
                freeSpaceDict,
                log, dry_run = True):

    inventory = []

    delFiles = collections.defaultdict(list)
    addFiles = collections.defaultdict(list)
    for f in delList:
        delFiles[dstHDDs[f]].append(f)
    for f in addList:
        addFiles[srcHDDs[f]].append(f)

    for hdd in freeSpaceDict.keys()[1::-1]:
        log.write("HardDisk: " + hdd)
        log.write('\n')
        if not dry_run:
            if len(delFiles[hdd]) > 0 or len(addFiles[hdd]) > 0:
                raw_input("Please insert disk \"" + hdd+ "\" and press Enter.")
        for f in delFiles[hdd]:
            if not dry_run:
                os.path.remove(os.path.join(dstPath, f))
            log.write("delete: ")
            log.write(os.path.join(dstPath, f))
            log.write('\n')

        for f in addFiles[hdd]:
            if not dry_run:
                filepath = os.path.join(dstPath, f)
                dirname = os.path.dirname(filepath)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                shutil.copy2(os.path.join(srcPath, f), os.path.join(dstPath, f))

            log.write("copy to : ")
            log.write(os.path.join(dstPath, f))
            log.write('\n')

    return log


def writeHeader(srcPath, dstPath, freeSpaceDict, log):
    
    srcPath = os.path.abspath(srcPath)
    dstPath = os.path.abspath(dstPath)
    log.write(srcPath)
    log.write('\n')
    log.write(dstPath)
    log.write('\n')
    ids = freeSpaceDict.keys() 
    log.write('|'.join(ids))
    log.write('\n')
    spaces = freeSpaceDict.values()
    log.write('|'.join([str(s) for s in spaces]))
    log.write('\n')

    return log


def writeEntries(fileList, fileHDDs, fileDates, fileSizes, log):
    for f in fileList:
        data = [ fileHDDs[f], f, str(fileDates[f]), str(fileSizes[f])]
        log.write('|'.join(data))
        log.write('\n')

    return log

def writeLog(srcPath, dstPath, freeSpaceDict,
            filesNotUpdated, dstHDDs, dstDates, dstSizes,
            addList, srcHDDs, srcDates, srcSizes,
            log):

    writeHeader(srcPath, dstPath, freeSpaceDict, log)    
    #Format
    #HDD|RelPath|Timestamp|Size
    #write down unchanged part
    #pairing up:
    #filesNotUpdated, dstHDDs, dstDates, dstSizes
    #addList, srcHDDs, srcDates, srcSizes
    writeEntries(filesNotUpdated, dstHDDs, dstDates, dstSizes, log)
    writeEntries(addList, srcHDDs, srcDates, srcSizes, log)

    return log




def getFreeSpaceLog(ids, spaces):
    freeSpaceDict = collections.OrderedDict()
    ids = ids.split("|")
    spaces = spaces.split("|")
    for ident, space in zip(ids, spaces):
        freeSpaceDict[ident] = int(space)

    return freeSpaceDict


def backup(backupFile):
    lines = [line.rstrip() for line in open(backupFile, 'r')]
    srcPath = lines[0]
    dstPath = lines[1]
    freeSpaceDict = getFreeSpaceLog(lines[2], lines[3])
    firstFile = 4


    srcRelPaths, srcAbsPaths = getSrcStats(srcPath)

    dstRelPaths, dstAbsPaths, dstHDDs, dstDates, dstSizes = getDstStats(dstPath, lines[firstFile:])


    #it is sufficient to just compare the entries in the relative paths to each other 

    filesInBoth = list(set(srcRelPaths).intersection(dstRelPaths))
    filesInSrc = list(set(srcRelPaths).difference(dstRelPaths))
    filesInDst = list(set(dstRelPaths).difference(srcRelPaths))

    print filesInBoth, filesInSrc, filesInDst

    #filesInDst can be removed freely
    #We have to check for filesInBoth which can be removed

    srcDates = {f : int(os.path.getmtime(os.path.join(srcPath, f))) for f in filesInSrc + filesInBoth}
    filesUpdated = [f for f in filesInBoth if srcDates[f] > dstDates[f]]
    filesNotUpdated = [f for f in filesInBoth if srcDates[f] <= dstDates[f]]


    delList = filesInDst + filesUpdated
    addList = filesInSrc + filesUpdated

    srcSizes = getNewFileSizes(addList, srcPath)

    freeSpaceDict = freeAfterDeletion(delList, dstHDDs, dstSizes, freeSpaceDict)
    
    freeSpaceDict, srcHDDs = allocateFiles(addList, srcSizes, freeSpaceDict, dstPath, buff = 1024 ** 3)

    #Delete files
    simulate = raw_input("Only simulate file transfers? Y/n\n")
    dry_run = True
    if simulate.lower() == "n":
        dry_run = False


    with open('transaction.log', 'w') as log:
        modifyDisks(delList, dstHDDs, dstPath, 
                addList, srcHDDs, srcPath, 
                freeSpaceDict,
                log, dry_run)
    
    #backup old logfile
    if not dry_run:
        os.rename(backupFile, backupFile + '.bak')

        with open(backupFile, 'w') as log:
            writeLog(srcPath, dstPath, freeSpaceDict,
                    filesNotUpdated, dstHDDs, dstDates, dstSizes,
                    addList, srcHDDs, srcDates, srcSizes,
                    log)
    
            

def getFreeSpaceBytes(folder):
    """ Return folder/drive free space (in Megabytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize

def freeAfterDeletion(delList, dstHDDs, dstSizes, freeSpaceDict):

    for f in delList:
        freeSpaceDict[dstHDDs[f]] += dstSizes[f]

    return freeSpaceDict

def getNewFileSizes(addList, srcPath):

    srcSizes = {}

    for f in addList:
        srcSizes[f] = os.path.getsize(os.path.join(srcPath, f))
    
    
    return srcSizes



def allocateFiles(addList, srcSizes, freeSpaceDict, dstPath, buff = 1024 ** 3):

    assert len(freeSpaceDict.keys()) > 0
    srcHDDs = {}
    currentIndex = 0
    currentHardDisk = freeSpaceDict.keys()[currentIndex]


    for f in addList:

        if freeSpaceDict[currentHardDisk]  - srcSizes[f] < buff:
            currentIndex += 1
            #need another harddisk
            if currentIndex >= len(freeSpaceDict.keys()):
                while True:
                    newID = raw_input("Please insert a fresh HDD and input an unique identifier:\n")
                    if len(newID) > 0:
                        break

                freeSpaceDict[newID] = getFreeSpaceBytes(dstPath)
            currentHardDisk = freeSpaceDict.keys()[currentIndex]

        srcHDDs[f] = currentHardDisk
        freeSpaceDict[currentHardDisk] -= srcSizes[f]

    return freeSpaceDict, srcHDDs




         

if __name__ == "__main__":
    #unittest.main()
    #sys.exit()
    if len(sys.argv) < 2:
        print "Please enter the name for the backup logfile: "
        backupFile = raw_input()
        print "Please enter the source path: "
        srcPath = raw_input()
        print "Please enter the destination path: "
        dstPath = raw_input()
        createBackupFile(backupFile, srcPath, dstPath)
    else:
        print "The selected logfile is: ", sys.argv[1]
        input_var = raw_input("Backup using this file: Y/n\n")
        if input_var.lower() == "n":
            print "Self-destructing..."

            sys.exit()
        else:
            backupFile = sys.argv[1]

    print "Starting backup"
    backup(backupFile)

