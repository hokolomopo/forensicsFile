import sys, traceback
import os
import ntpath

def readMBR(file):
    MBR = []
    b = file.read(512)
    for i in range(4):
        MBR.append(b[446 + i*16:462 + i*16])

    for partition in MBR:
        print(partition)
        type = partition[4]

        if(type == 12):
            addr = partition[8:12]
            addr = bToDec(addr) #in clusters
            addr = addr * 512 #in bytes

            print(bToDec(partition[12:16]) * 512)

    # go to FAT partition
    file.read(addr - 512) # -512 because we already read the first cluster

    return addr

def bToDec(b):
    return (int.from_bytes(b, "little"))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("The number of argument need to be 3.")
        exit(-1)
    ifEqual, diskimg = sys.argv[1].split("=", 1)
    part, primarypart = sys.argv[2].split("=", 1)
    file_abs = sys.argv[3]
    if diskimg != "evidence" or os.path.isabs(file_abs)==False:
        print("Error in the command.")
        exit(-1)

    path = []
    path.append(file_abs.split("/"))
    print(path[1:])
    file = open("evidence.img", "rb")

    fatAddr = readMBR(file)

    print("FAT")
   
    MBR = []
    fatBS = file.read(512)
    for i in range(8):
        print(fatBS[i*16:16 + i*16])

    print()
    BPB_RsvdSecCnt = bToDec(fatBS[14:14+2])
    BPB_NumFATs= bToDec(fatBS[16:16+1])
    BPB_FATSz32 =  bToDec(fatBS[36:36+4])
    BPB_BytsPerSec = bToDec(fatBS[11:11+2])
    BPB_SecPerClus = bToDec(fatBS[13:13+1])
    print("BPB_RsvdSecCnt : ", BPB_RsvdSecCnt)
    print("BPB_FATSz32 : ", BPB_FATSz32)
    print("BPB_NumFATs : ", BPB_NumFATs)

    FirstDataSector = BPB_RsvdSecCnt + (BPB_NumFATs * BPB_FATSz32)

    print(FirstDataSector)
    print(BPB_BytsPerSec)

