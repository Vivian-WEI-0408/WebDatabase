import struct
def snapgene_to_dict(file_obj):

    if(file_obj.read(1) != b"\t"):
        raise ValueError("Error in snapgene file format")
    def unpack(size, mode):
        return struct.unpack(">" + mode, file_obj.read(size))[0]
    length = unpack(4, "I")
    title = file_obj.read(8).decode("ascii")
    if length != 14 or title != "SnapGene":
        raise ValueError("Wrong format for a SnapGene file !")
    data = dict(
        isDNA = unpack(2, "H"),
    )

    while True:
        next_byte = file_obj.read(1)
        if(next_byte == b""):
            break
        block_size = unpack(4, "I")
        
        if(ord(next_byte) == 0):
            props = unpack(1,"b")
            data['seq'] = file_obj.read(block_size - 1).decode("ascii")
        else:
            file_obj.read(block_size)
            pass
    file_obj.close()
    return data

if __name__ == "__main__":
    file_address = r"c:\Users\admin\Desktop\样例数据\level3\CY1802.dna"
    print(snapgene_to_dict(file_address))
    