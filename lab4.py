
partNumber = 0

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

    partition = MBR[partNumber]
    type = partition[4]

    if(type == 12):
        addr = partition[8:12]
        addr = bToDec(addr) #in clusters
        addr = addr * 512 #in bytes
    else:
        raise Exception('Wrong partition type, type is : {}'.format(type))


    # go to FAT partition
    file.read(addr - 512) # -512 because we already read the first cluster

    return addr

def bToDec(b):
    return (int.from_bytes(b, "little"))

def readSecNumber(num, number=1):
    file = open("evidence.img", "rb")
    file.read(num * 512)
    return file.read(512 * number)

def firstSec(N, BPB_SecPerClus, FirstDataSector):
    a = ((N - 2) * BPB_SecPerClus) + FirstDataSector
    return a

def parseDir(dir, toFind="", type="dir"):
    for i in range(100):
        offset = i*32
        name = dir[0 + offset:11 + offset]
        addrLO = dir[26 + offset:28 + offset]
        addrHI = dir[20 + offset:22 + offset]
        attr = dir[11 + offset:12 + offset]
        addr = addrLO + addrHI
        size = bToDec(dir[28 + offset:32 + offset])
        if(bToDec(name) == 0):
            break

        print("Name : ",name," ,Adr  :", bToDec(addr), " ,Attr : ", bToDec(attr))

        if(type == "dir"):
            att = 16
        if(type == "file"):
            att = 32

        name = str(name)[2:]
        attr = bToDec(attr)
        if(att == attr and name.startswith(toFind)):
            return bToDec(addr), size
    
    return -1, -1

if __name__ == "__main__":
    file = open("evidence.img", "rb")

    fatAddr = readMBR(file)
    fatsec = int(fatAddr / 512)

    print("FAT")
   
    MBR = []
    fatBS = file.read(512)
    # for i in range(8):
    #     print(fatBS[i*16:16 + i*16])

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

    rsvdEnd = BPB_RsvdSecCnt * 512

    print(FirstDataSector)
    print(BPB_BytsPerSec)

    file.read(rsvdEnd - 512) # - 512 because we already read 1 sector
    fatTable = file.read(BPB_FATSz32 * 512)

    # for i in range(4):
    #     print(fatTable[i*16:16 + i*16])

    table = []
    for i in range(32):
        b = fatTable[i*4:4 + i*4]
        table.append(bToDec(b))
        
    print(table)

    path = ["1", "BD"]

    #Find the file
    i = 0
    nextAddr = 2 #Root dir
    type = "dir"
    while(nextAddr != -1):
        if(i == len(path) - 1):
            type = "file"

        dirSec = firstSec(nextAddr, BPB_SecPerClus, FirstDataSector)
        dir = readSecNumber(dirSec + fatsec, number=BPB_SecPerClus)
        nextAddr, size = parseDir(dir, type=type, toFind=path[i])
        print("NextAddr", nextAddr, " Size : ", size)

        if(i == len(path) - 1):
            break

        i +=1

    if(size == -1):
        print("File not found")
        exit(-1)

    # Get the slack
    leftToRead = size
    clustSize = BPB_SecPerClus * 512
    print(clustSize)

    file = bytes()
    while(True):

        fileSec = firstSec(nextAddr, BPB_SecPerClus, FirstDataSector)
        file += readSecNumber(fileSec + fatsec, number=BPB_SecPerClus)
        
        leftToRead -= clustSize
        if(leftToRead < 0):#EOF
            break
        nextAddr = table[nextAddr]


    slack = file[size:]

    slackHex = []
    for b in slack:
        slackHex.append(format(b, 'x'))
    print(slackHex)


