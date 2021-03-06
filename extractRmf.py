import sys
import json
import struct
import glob

import os
import processFiles

importFilenames = sys.argv[1:]

for importFilename in importFilenames:

    print "reading " + importFilename
    try:
        with open(importFilename, "rb") as input_fd:
            rawData = input_fd.read()

        destDir = importFilename.replace(".rmf", "").replace(".RMF", "")
        searchName = destDir.split("/")[-1].split("\\")[-1]
        searchNameLower = searchName.lower()
        searchDir = destDir.replace(searchName, "")

        sizeOfExtension = 4
        offset = 0
        headerFmt = "<3H"
        filenameFmt = "<13s"
        header = struct.unpack_from(headerFmt, rawData, offset)
        rmfTag = 256
        versionTagMin = 1700
        if header[0] != 256 and header[1] < 1700:
            raise ValueError("RMF file header not correct")
        archiveNames = []
        for i in range(header[2]):
            filenameIndex = rawData.find(searchNameLower, offset)
            if filenameIndex == -1:
                filenameIndex = rawData.find(searchName, offset)
            filenameEndIndex = rawData.find(".", filenameIndex) + sizeOfExtension
            archiveNames.append(rawData[filenameIndex:filenameEndIndex])
            offset = filenameEndIndex + 1
        for name in archiveNames:
            offset = 0

            if os.path.isfile(searchDir + name) is False:
                name = name.upper()

            if os.path.isfile(searchDir + name) is False:
                continue
            name = searchDir + name
            print "reading " + name
            with open(name, "rb") as input_fd:
                rawData = input_fd.read()
            print "getting file info for " + name
            files = processFiles.getFileinfo(rawData, offset)
            destDir = name.replace(".", "-")
            if not os.path.exists(destDir):
        	    os.makedirs(destDir)

            for index, file in enumerate(files):
                filename, fileOffset, fileLength = file
                filename = filename.split("\0")[0]
                print "writing " + destDir + "/" + filename
                with open(destDir + "/" + filename,"w") as newFile:
                        newFileByteArray = bytearray(rawData[fileOffset:fileOffset + fileLength])
                        newFile.write(newFileByteArray)

    except Exception as e:
        print e
