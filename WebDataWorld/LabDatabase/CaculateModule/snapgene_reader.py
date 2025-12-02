import struct
try:
    # Biopython <1.78
    from Bio.Alphabet import DNAAlphabet

    has_dna_alphabet = True
except ImportError:
    # Biopython >=1.78
    has_dna_alphabet = False
def snapgene_to_dict(file_obj):
    
    if file_obj.read(1) != b"\t":
        raise ValueError("Wrong format for a SnapGene file!")

    def unpack(size, mode):
        """Unpack the fileobject."""
        return struct.unpack(">" + mode, file_obj.read(size))[0]

    # READ THE DOCUMENT PROPERTIES
    length = unpack(4, "I")
    title = file_obj.read(8).decode("ascii")
    if length != 14 or title != "SnapGene":
        raise ValueError("Wrong format for a SnapGene file !")

    data = dict(
        isDNA=unpack(2, "H"),
        exportVersion=unpack(2, "H"),
        importVersion=unpack(2, "H"),
        features=[],
    )

    while True:
        next_byte = file_obj.read(1)
        if next_byte == b"":
            break
        block_size = unpack(4, "I")

        if ord(next_byte) == 0:
            # READ THE SEQUENCE AND ITS PROPERTIES
            props = unpack(1, "b")
            data["dna"] = dict(
                topology="circular" if props & 0x01 else "linear",
                strandedness="double" if props & 0x02 > 0 else "single",
                damMethylated=props & 0x04 > 0,
                dcmMethylated=props & 0x08 > 0,
                ecoKIMethylated=props & 0x10 > 0,
                length=block_size - 1,
            )
            data["seq"] = file_obj.read(block_size - 1).decode("ascii")
            break
        else:
            # WE IGNORE THE WHOLE BLOCK
            file_obj.read(block_size)
            pass

    file_obj.close()
    print(data)
    return data

if __name__ == "__main__":
    file_address = r"c:\Users\admin\Desktop\样例数据\level3\CY1802.dna"
    print(snapgene_to_dict())
    