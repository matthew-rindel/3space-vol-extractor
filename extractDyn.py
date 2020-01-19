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

        destDir = importFilename.replace(".dyn", "").replace(".DYN", "")
        offset = 0
        headerFmt = "<20s"
        filenameFmt = "<13sL"
        header = struct.unpack_from(headerFmt, rawData, offset)
        dynTag = b"Dynamix Volume File\0"
        if header[0] != dynTag:
            raise ValueError("File header is not " + dynTag.decode("utf-8"))
        firstFileIndex = -1
        offset += struct.calcsize(headerFmt)
        firstFileOffset = offset
        validTypes = [b"OVL", b"FMD", b"DAT", b"BMP", b"PAL", b"TBL"]
        firstFile = None
        while firstFileIndex == -1:
            firstFileIndex = rawData.find(b".", firstFileOffset)
            firstFileExt = rawData[firstFileIndex + 1:firstFileIndex + 4]
            if firstFileExt not in validTypes:
                firstFileOffset = firstFileIndex + 4
                firstFileIndex = -1
                continue
            index = firstFileIndex - 1
            #TODO there may be possible problems with this code. Need to fix it.
            while ord(chr(rawData[index - 1])) >= ord("0") and ord(chr(rawData[index - 1])) <= ord("z"):
                index -= 1

            offset = index
            break

        files = processFiles.getFileinfo(rawData, offset)

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
