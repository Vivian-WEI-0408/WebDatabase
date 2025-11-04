import numpy as np
from collections import defaultdict
import heapq
import sys
sys.path.append(r"C:\Users\admin\Desktop\LabDNASeqSearch")


#由于数据库不同，所以Seq_id存储值为Seq_name

class KmerIndex:
    def __init__(self,k=10):
        self.k = k
        self.index = defaultdict(list)
    
    def add_sequence(self,seq_id,sequence):
        seq_len = len(sequence)

        if seq_len < self.k:
            return
        
        for i in range(seq_len - self.k +1):
            kmer = sequence[i:i+self.k]
            self.index[kmer].append((seq_id,i))

    def query(self,sequence, min_matches=5):
        matches = defaultdict(list)
        query_len = len(sequence)

        for i in range(query_len - self.k+1):
            kmer = sequence[i:i+self.k]
            for seq_id,pos in self.index.get(kmer,[]):
                offset = pos -i
                matches[(seq_id, offset)].append(i)
        
        significant_matches = []
        for (seq_id,offset), positions in matches.items():
            match_count = len(positions)
            if match_count >= min_matches:
                density = match_count/(max(positions) - min(positions)+self.k) if len(positions)>1 else 1
                significant_matches.append({'seq_id':seq_id,
                                            'offset':offset,
                                            'match_count':match_count,
                                            'density':density,
                                            'start':min(positions),
                                            'end':max(positions)+self.k})
        significant_matches.sort(key=lambda x:x['match_count'],reverse=True)
        return significant_matches[:100]

if __name__ == "__main__":
    import pymysql
    from SupportSQL import ManageSql
    kmer = KmerIndex()
    da = pymysql.connect(host = '10.30.76.2',user='root',password="04080117",database="labdnadata")
    c = da.cursor()
    PlasmidValue = ManageSql.GetAllTable("PlasmidNeed","ASC",da,c)
    for each in PlasmidValue:
        kmer.add_sequence(each[1],each[8])
    BackboneValue = ManageSql.GetAllTable("BackboneTable","ASC",da,c)
    for each in BackboneValue:
        kmer.add_sequence(each[1],each[3])
    sequence = "cacatatacctgccgttcactattatttagtgaaatgagatattatgatattttctgaattgtgattaaaaaggcaactttatgcccatgcaacagaaactataaaaaatacagagaaTgAaaagaaacagat"
    # sequence = "GCTCCATAACATCAAACATCGACCCACGGCGTAACGCGCTTGCTGCTTGGATGCCCGAGGCATAGACTGTACCCCAAAAAAACATGTCATAACAAGAAGCCATGAAAACCGCC"
    # sequence = "GATATCCGTCGGCTTGAACGAATTGTTAGACATTATTTGCCGACTACCTTGGTGATCTCGCCTTTCACGTAGTGGACAAATTCTTCCAACTGATCTGCGCGCGAGGCCAAGCGATCTTCTTCTTGTCCAAGATAAGCCTGTCTAGCTTCAAGTATGACGGGCTGATACTGGGCCGGCAGGCGCTCCATTGCCCAGTCGGCAGCGACATCCTTCGGCGCGATTTTGCCGGTTACTGCGCTGTACCAAATGCGGGACAACGTAAGCACTACATTTCGCTCATCGCCAGCCCAGTCGGGCGGCGAGTTCCATAGCGTTAAGGTTTCATTTAGCGCCTCAAATAGATCCTGTTCAGGAACCGGATCAAAGAGTTCCTCCGCCGCTGGACCTACCAAGGCAACGCTATGTTCTCTTGCTTTTGTCAGCAAGATAGCCAGATCAATGTCGATCGTGGCTGGCTCGAAGATACCTGCAAGAATGTCATTGCGCTGCCATTCTCCAAATTGCAGTTCGCGCTTAGCTGGATAACGCCACGGAATGATGTCGTCGTGCACAACAATGGTGACTTCTACAGCGCGGAGAATCTCGCTCTCTCCAGGGGAAGCCGAAGTTTCCAAAAGGTCGTTGATCAAAGCTCGCCGCGTTGTTTCATCAAGCCTTACGGTCACCGTAACCAGCAAATCAATATCACTGTGTGGCTTCAGGCCGCCATCCACTGCGGAGCCGTACAAATGTACGGCCAGCAACGTCGGTTCGAGATGGCGCTCGATGACGCCAACTACCTCTGATAGTTGAGTCGATACTTCGGCGATCACCGCTTCCCTCAT"
    SequenceLength = len(sequence)
    # NewSequence = "GCTCCATAACATCAAACATCGACCCACGGCGTAACGCGCTTGCTGCTTGGATGCCCGAGGCATAGACTGTACCCCAAAAAAACAGTCATAACAAGAAGCCATGAAAACCGCC"
    print(SequenceLength)
    matches = kmer.query(sequence, min_matches=5)
    BackboneList = []
    PlasmidList = []
    print(len(matches))
    for match in matches:
        seq_Name = match['seq_id']
        db_seq = ""
        PartSeq = ManageSql.ReturnPartSeq(seq_Name,c)
        BackboneSeq = ManageSql.ReturnBackboneSeq(seq_Name,c)
        PlasmidSeq = ManageSql.ReturnPlasmidSeq(seq_Name,c)
        # db_seq = ManageSql.ReturnPlasmidSeq(seq_Name,c)
        if(PartSeq != None):
            db_seq = PartSeq
        elif(BackboneSeq != None):
            db_seq = BackboneSeq
        elif(PlasmidSeq != None):
            db_seq = PlasmidSeq
        q_start = match['start']
        q_end = match['end']
        db_start = match['offset'] + match['start']
        db_end = match['offset'] + match['end']
        query_segment = sequence[q_start:q_end]
        db_segment = db_seq[db_start:db_end]

        match_length = len(query_segment)
        print(match_length)
        if(match_length  == SequenceLength):
            if(BackboneSeq != None):
                BackboneList.append({"Name":seq_Name,"Sequence":db_seq,"db_start":db_start,"db_end":db_end,"query_start":q_start,"query_end":q_end})
            elif(PlasmidSeq != None):
                PlasmidList.append({"Name":seq_Name,"Sequence":db_seq,"db_start":db_start,"db_end":db_end,"query_start":q_start,"query_end":q_end})
        # if(BackboneSeq != None):
        #     BackboneList.append({"Name":seq_Name,"Sequence":db_seq,"db_start":db_start,"db_end":db_end,"query_start":q_start,"query_end":q_end})
        # elif(PlasmidSeq != None):
        #     PlasmidList.append({"Name":seq_Name,"Sequence":db_seq,"db_start":db_start,"db_end":db_end,"query_start":q_start,"query_end":q_end})
    print(BackboneList)
    print(PlasmidList)
    # for each in BackboneList:
    #     seq = each['Sequence']
    #     newSeq = seq[:each['db_start']]+sequence+seq[each['db_end']:]
    #     # print(each["Name"])
    #     # print(NewSequence)
    #     ManageSql.UpdateBackbone({"sequence":newSeq},each["Name"],da,c)
    # for each in PlasmidList:
    #     seq = each['Sequence']
    #     newSeq = seq[:each['db_start']]+sequence+seq[each['db_end']:]
    #     ManageSql.UpdatePlasmid({"SequenceConfirm":newSeq},each["Name"],da,c)
    

#         seq = ManageSql.ReturnBackboneSeq(BackboneList[21],c)
# newSeq = seq[:285]+"ATGTTACGCAGCAGCAACGATGTTACGCAGCAGGGCAGTCGCCCTAAAACAAAGTTAGGTGGCTCAAGTATGGGCATCATTCGCACATGTAGGCTCGGCCCTGACCAAGTCAAATCCATGCGGGCTGCTCTTGATCTTTTCGGTCGTGAGTTCGGAGACGTAGCCACCTACTCCCAACATCAGCCGGACTCCGATTACCTCGGGAACTTGCTCCGTAGTAAGACATTCATCGCGCTTGCTGCCTTCGACCAAGAAGCGGTTGTTGGCGCTCTCGCGGCTTACGTTCTGCCCAaGTTTGAGCAGCCGCGTAGTGAGATCTATATCTATGATCTCGCAGTCTCCGGaGAGCACCGGAGGCAGGGCATTGCCACCGCGCTCATCAATCTCCTCAAGCATGAGGCCAACGCGCTTGGTGCTTATGTGATCTACGTGCAAGCAGATTACGGTGACGATCCCGCAGTGGCTCTCTATACAAAGTTGGGCATACGGGAAGAAGTGATGCACTTTGATATCGACCCAAGTACCGCCACCTAA"+seq[819:]
# ManageSql.UpdateBackbone({"sequence":newSeq},BackboneList[21],conn,c)
# seq = ManageSql.ReturnPlasmidSeq(PlasmidNeed[102],c)
# newSeq = seq[:285]+"ATGTTACGCAGCAGCAACGATGTTACGCAGCAGGGCAGTCGCCCTAAAACAAAGTTAGGTGGCTCAAGTATGGGCATCATTCGCACATGTAGGCTCGGCCCTGACCAAGTCAAATCCATGCGGGCTGCTCTTGATCTTTTCGGTCGTGAGTTCGGAGACGTAGCCACCTACTCCCAACATCAGCCGGACTCCGATTACCTCGGGAACTTGCTCCGTAGTAAGACATTCATCGCGCTTGCTGCCTTCGACCAAGAAGCGGTTGTTGGCGCTCTCGCGGCTTACGTTCTGCCCAaGTTTGAGCAGCCGCGTAGTGAGATCTATATCTATGATCTCGCAGTCTCCGGaGAGCACCGGAGGCAGGGCATTGCCACCGCGCTCATCAATCTCCTCAAGCATGAGGCCAACGCGCTTGGTGCTTATGTGATCTACGTGCAAGCAGATTACGGTGACGATCCCGCAGTGGCTCTCTATACAAAGTTGGGCATACGGGAAGAAGTGATGCACTTTGATATCGACCCAAGTACCGCCACCTAA"+seq[819:]
# # ManageSql.UpdateBackbone({"sequence":newSeq},BackboneList[3],conn,c)
# ManageSql.UpdatePlasmid({"SequenceConfirm":newSeq},PlasmidNeed[102],conn,c)
    
    