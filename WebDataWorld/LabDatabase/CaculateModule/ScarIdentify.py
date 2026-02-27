from Bio import Restriction
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


'''
Scar  标识
GTGC   A
ATCA   A2
AATG   B
TAAA   C
CCTC   D
GCTT   E
CTGA   F
TACG   G
TTCC   H
AGGT   I
CACC   J
TGTC   K
CGCT   L
CCGT   M
TTTT   T
'''

type2s_enzymes = ["BsmBI","BsaI","BbsI","AarI","SapI"]
class ScarIdentify:
    def __init__(self, Sequence):
        self.Sequence = Sequence
        self.Part = SeqRecord(Seq(self.Sequence),id="test",name="test",description="test")
    
    def number_of_site(self,enzyme):
        linear = False
        return enzyme.search(self.Part.seq,linear=linear)

    def enzyme_fit_score(self,enzyme_name):
        enzyme = Restriction.__dict__[enzyme_name]
        Site = self.number_of_site(enzyme)
        if(len(Site) == 2):
            scar = {"start":self.Part.seq[Site[0]-1:Site[0]+3],"end":self.Part.seq[Site[1]-1:Site[1]+3]}
        else:
            scar = {"start":"","end":""}
        return {"enzyme_name":enzyme, "site_number":len(Site),"Scar":scar}
        # return self.number_of_site(enzyme)
    def enzyme_position_fit(self,enzyme_name):
        enzyme = Restriction.__dict__[enzyme_name]
        Site = self.number_of_site(enzyme)
        if(len(Site) % 2 == 0):
            return Site
        else:
            return []

def scarPosition(seq):
    SI = ScarIdentify(seq)
    scar_list = []
    for enzyme in type2s_enzymes:
        scar = SI.enzyme_position_fit(enzyme)
        
        scar_name_list = []
        for each_position in scar:
            each_str = scarName(seq[each_position-1:each_position+3])
            scar_name_list.append(each_str)
        scar_list.append({enzyme:{"index":scar,"name":scar_name_list}})
    print(scar_list)
    return scar_list

def scarIdentSitePosition(seq):
    
    SI = ScarIdentify(seq)
    scar_list = []
    for enzyme in type2s_enzymes:
        scar = SI.enzyme_position_fit(enzyme)
        scar_position_list = []
        scar_name_list = []
        for each_position in scar:
            each_str = scarName(seq[each_position-1:each_position+3])
            before_index = 0
            print(enzyme)
            if(str(enzyme) == "BsaI"):
                
                if(seq[each_position-8:each_position-2].upper() == "GGTCTC"):
                    before_index = each_position - 8
                if(seq[each_position+4:each_position+10].upper() == "GAGACC"):
                    before_index = each_position +4
            elif(enzyme == "BbsI"):
                print(seq[each_position-9:each_position-3].upper() )
                if(seq[each_position-9:each_position-3].upper() == "GAAGAC"):
                    before_index = each_position -9
                if(seq[each_position+5:each_position+11].upper() == "GTCTTC"):
                    before_index = each_position + 4
            elif(enzyme == "BsmBI"):
                if(seq[each_position-8:each_position-2].upper() == "CGTCTC"):
                    before_index = each_position -8
                if(seq[each_position+4:each_position+10].upper() == "GAGACG"):
                    before_index = each_position + 4
            elif(enzyme == "AarI"):
                if(seq[each_position-12:each_position-5].upper() == "CACCTGC"):
                    before_index = each_position -8
                if(seq[each_position+7:each_position+14].upper() == "GCAGGTG"):
                    before_index = each_position + 4
            elif(enzyme == "SapI"):
                if(seq[each_position-9:each_position-2].upper() == "GCTCTTC"):
                    before_index = each_position -8
                if(seq[each_position+3:each_position+10].upper() == "GAAGAGC"):
                    before_index = each_position + 4
            if(before_index != 0):
                scar_name_list.append(each_str)
                scar_position_list.append(before_index)
        scar_list.append({enzyme:{"index":scar_position_list,"name":scar_name_list}})
    return scar_list

    
    

def scarName(seq):
    scar_str = ""
    if(seq.upper() == "GCTT"):
        scar_str = "E"
    elif(seq.upper() == "CTGA"):
        scar_str += "F"
    elif(seq.upper() == "TACG"):
        scar_str = "G"
    elif(seq.upper() == "TTCC"):
        scar_str += "H"
    elif(seq.upper() == "GTGC"):
        scar_str += "A"
    elif(seq.upper() == "ATCA"):
        scar_str += "A2"
    elif(seq.upper() == "AATG"):
        scar_str += "B"
    elif(seq.upper() == "TAAA"):
        scar_str += "C"
    elif(seq.upper() == "CCTC"):
        scar_str += "D"
    elif(seq.upper() == "AGGT"):
        scar_str += "I"
    elif(seq.upper() == "CACC"):
        scar_str += "J"
    elif(seq.upper() == "TGTC"):
        scar_str += "K"
    elif(seq.upper() == "CGCT"):
        scar_str += "L"
    elif(seq.upper() == "CCGT"):
        scar_str += "M"
    elif(seq.upper() == "TTTT"):
        scar_str += "T"
    else:
        scar_str = "undefine"
    return scar_str

def scarFunction(seq):

    SI = ScarIdentify(seq)
    scar_list = []
    for enzyme in type2s_enzymes:
        NoSite = SI.enzyme_fit_score(enzyme)
        scar_str = ""
        if(NoSite['site_number'] == 2):
            if(NoSite["Scar"]["start"].upper() == "GCTT"):
                scar_str += "E"
            elif(NoSite["Scar"]["start"].upper() == "CTGA"):
                scar_str += "F"
            elif(NoSite["Scar"]["start"].upper() == "TACG"):
                scar_str += "G"
            elif(NoSite["Scar"]["start"].upper() == "TTCC"):
                scar_str += "H"
            elif(NoSite["Scar"]["start"].upper() == "GTGC"):
                scar_str += "A"
            elif(NoSite["Scar"]["start"].upper() == "ATCA"):
                scar_str += "A2"
            elif(NoSite["Scar"]["start"].upper() == "AATG"):
                scar_str += "B"
            elif(NoSite["Scar"]["start"].upper() == "TAAA"):
                scar_str += "C"
            elif(NoSite["Scar"]["start"].upper() == "CCTC"):
                scar_str += "D"
            elif(NoSite["Scar"]["start"].upper() == "AGGT"):
                scar_str += "I"
            elif(NoSite['Scar']["start"].upper() == "CACC"):
                scar_str += "J"
            elif(NoSite['Scar']["start"].upper() == "TGTC"):
                scar_str += "K"
            elif(NoSite['Scar']["start"].upper() == "CGCT"):
                scar_str += "L"
            elif(NoSite['Scar']["start"].upper() == "CCGT"):
                scar_str += "M"
            elif(NoSite['Scar']["start"].upper() == "TTTT"):
                scar_str += "T"
            if(NoSite["Scar"]["end"].upper() == "CTGA"):
                scar_str += "F"
            elif(NoSite["Scar"]["end"].upper() == "TACG"):
                scar_str += "G"
            elif(NoSite["Scar"]["end"].upper() == "TTCC"):
                scar_str += "H"
            elif(NoSite["Scar"]["end"].upper() == "AGGT"):
                scar_str += "I"
            elif(NoSite["Scar"]["end"].upper() == "TGTC"):
                scar_str += "K"
            elif(NoSite["Scar"]["end"].upper() == "CCTC"):
                scar_str += "D"
            elif(NoSite["Scar"]["end"].upper() == "GTGC"):
                scar_str += "A"
            elif(NoSite["Scar"]["end"].upper() == "ATCA"):
                scar_str += "A2"
            elif(NoSite["Scar"]["end"].upper() == "AATG"):
                scar_str += "B"
            elif(NoSite["Scar"]["end"].upper() == "TAAA"):
                scar_str += "C"
            elif(NoSite["Scar"]["end"].upper() == "CCTC"):
                scar_str += "D"
            elif(NoSite["Scar"]["end"].upper() == "GCTT"):
                scar_str += "E"
            elif(NoSite["Scar"]["end"].upper() == "AGGT"):
                scar_str += "I"
            elif(NoSite['Scar']["end"].upper() == "CACC"):
                scar_str += "J"
            elif(NoSite['Scar']["end"].upper() == "TGTC"):
                scar_str += "K"
            elif(NoSite['Scar']["end"].upper() == "CGCT"):
                scar_str += "L"
            elif(NoSite['Scar']["end"].upper() == "CCGT"):
                scar_str += "M"
            elif(NoSite['Scar']['end'].upper() == "TTTT"):
                scar_str += "T"
        if(scar_str == ""):
            scar_list.append("-")
        else:
            scar_list.append(scar_str)
    return scar_list