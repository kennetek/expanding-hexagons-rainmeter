import locale
import struct

# Source:
# https://gist.github.com/Winand/997ed38269e899eb561991a0c663fa49
# http://stackoverflow.com/a/28952464/1119602


def __readLink(path):
    try:
        return __readLNK(path)
    except:
        return __readURL(path)


def __readURL(path):
    with open(path, "r") as infile:
        for line in infile:
            if line.startswith('URL'):
                url = line[4:]
                break
    return url


def __readLNK(path):
    with open(path, 'rb') as stream:
        content = stream.read()
        # skip first 20 bytes (HeaderSize and LinkCLSID)
        # read the LinkFlags structure (4 bytes)
        lflags = struct.unpack('I', content[0x14:0x18])[0]
        position = 0x18
        # if the HasLinkTargetIDList bit is set then skip the stored IDList
        # structure and header
        if (lflags & 0x01) == 1:
            position = struct.unpack('H', content[0x4C:0x4E])[0] + 0x4E
        last_pos = position
        position += 0x04
        # get how long the file information is (LinkInfoSize)
        length = struct.unpack('I', content[last_pos:position])[0]
        # skip 12 bytes (LinkInfoHeaderSize, LinkInfoFlags and VolumeIDOffset)
        position += 0x0C
        # go to the LocalBasePath position
        lbpos = struct.unpack('I', content[position:position+0x04])[0]
        position = last_pos + lbpos
        # read the string at the given position of the determined length
        size = (length + last_pos) - position - 0x02
        content = content[position:position+size].split(b'\x00', 1)
        return content[-1].decode('utf-16' if len(content) > 1
                                  else locale.getlocale()[1])

