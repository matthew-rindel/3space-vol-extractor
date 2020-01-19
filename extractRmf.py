import sys
import json
import struct
import glob

import os
import processFiles

importFilenames = sys.argv[1:]

for importFilename in importFilenames:

    print("reading " + importFilename)
    try:
        with open(importFilename, "rb") as input_fd:
            rawData = input_fd.read()

        destDir = importFilename.replace(".rmf", "").replace(".RMF", "")
        searchName = destDir.split("/")[-1].split("\\")[-1].upper()
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
            filenameIndex = rawData.find(str.encode(searchNameLower), offset)
            if filenameIndex == -1:
                filenameIndex = rawData.find(str.encode(searchName), offset)
            filenameEndIndex = rawData.find(b".", filenameIndex) + sizeOfExtension
            archiveNames.append(rawData[filenameIndex:filenameEndIndex])
            offset = filenameEndIndex + 1
        for name in archiveNames:
            name = name.decode("utf-8")
            offset = 0
            #TODO searchDir + name used to be here. Why did I write it like that?
            if os.path.isfile(name) is False:
                name = name.upper()

            #TODO same as above
            if os.path.isfile(name) is False:
                continue

            #TODO same again as above
            #name = searchDir + name
            print("reading " + name)
            with open(name, "rb") as input_fd:
                rawData = input_fd.read()
            print("getting file info for " + name)
            files = processFiles.getFileinfo(rawData, offset)
            destDir = name.replace(".", "-")
            if not os.path.exists(destDir):
        	    os.makedirs(destDir)

            for index, file in enumerate(files):
                filename, fileOffset, fileLength = file
                filename = filename.split(b"\0")[0]
                print("writing " + destDir + "/" + filename.decode("utf-8"))
                with open(destDir + "/" + filename.decode("utf-8"),"wb") as newFile:
                        newFileByteArray = bytearray(rawData[fileOffset:fileOffset + fileLength])
                        newFile.write(newFileByteArray)

    except Exception as e:
        print(e)
