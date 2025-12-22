import datetime
import os
from Bio.Seq import Seq



DATE_FORMAT = "%Y-%m-%d"
class SequenceAnnotator:
    def __init__(self,sequence,feature_list,reverse_feature_list,EnzymeList,name = "Unknow",species = "synthetic DNA construct",Reference = ""):
        self.length = len(sequence)
        self.sequence = sequence
        # self.seq_obj = Seq(sequence)
        # self.complementSeq = str(self.seq_obj.reverse_complement())
        self.name = name
        self.EnzymeList = EnzymeList

        self.feature_list = feature_list
        self.reverse_feature_list = reverse_feature_list
        self.species = species
        self.reference = Reference
        self.colors = {
            'promoter':'#FFD700',
            'CDS':'#FF6B6B',
            'terminator':'#95E1D3',
            'rbs':'#45B7D1',
            'ori':'#6A0572',
            'marker':'#FF8C42',
            'restriction_site':'#CCCCCC',
        }

    def GenerateGBKFile(self, file_address):
        definition = "synthetic circular DNA"
        accession = "."
        version = "1.0"
        Keywords = "."
        print(self.EnzymeList)
        with open(os.path.join(f'{file_address}',f'{self.name}.gbk'),'w') as file:
            file.write(("LOCUS       Exported              {0:>6} bp    DNA     {1:>8} CST \
            {2}\n").format(len(self.sequence),"circular",datetime.datetime.now().strftime(DATE_FORMAT)))
            file.write("DEFINITION  {}\n".format(definition))
            file.write("ACCESSION   {}\n".format(accession))
            file.write("VERSION     {}\n".format(version))
            file.write("KEYWODS     {}\n".format(Keywords))
            file.write("SOURCE      {}\n".format(self.reference))
            file.write("FEATURES             Location/Qualifiers\n")
            for each_feature in self.feature_list.keys():
                print(self.feature_list[each_feature])
                if(self.feature_list[each_feature][2] == "Origin"):
                    if(self.feature_list[each_feature][0] > self.feature_list[each_feature][1]):
                        file.write(f"     rep_origin      join({self.feature_list[each_feature][0]}..{self.length},1..{self.feature_list[each_feature][1]})\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     rep_origin      {self.feature_list[each_feature][0]}..{self.feature_list[each_feature][1]}\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.feature_list[each_feature][2] == "CDS"):
                    if(self.feature_list[each_feature][0] > self.feature_list[each_feature][1]):
                        file.write(f"     CDS             join({self.feature_list[each_feature][0]}..{self.length},1..{self.feature_list[each_feature][1]})\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     CDS             {self.feature_list[each_feature][0]}..{self.feature_list[each_feature][1]}\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.feature_list[each_feature][2] == "Promoter"):
                    if(self.feature_list[each_feature][0] > self.feature_list[each_feature][1]):
                        file.write(f"     promoter        join({self.feature_list[each_feature][0]}..{self.length},1..{self.feature_list[each_feature][1]})\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     promoter        {self.feature_list[each_feature][0]}..{self.feature_list[each_feature][1]}\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.feature_list[each_feature][2] == "Terminator"):
                    if(self.feature_list[each_feature][0] > self.feature_list[each_feature][1]):
                        file.write(f"     terminator      join({self.feature_list[each_feature][0]}..{self.length},1..{self.feature_list[each_feature][1]})\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     terminator      {self.feature_list[each_feature][0]}..{self.feature_list[each_feature][1]}\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.feature_list[each_feature][2] == "misc_feature"):
                    if(self.feature_list[each_feature][0] > self.feature_list[each_feature][1]):
                        file.write(f"     misc_feature    join({self.feature_list[each_feature][0]}..{self.length},1..{self.feature_list[each_feature][1]})\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     misc_feature    {self.feature_list[each_feature][0]}..{self.feature_list[each_feature][1]}\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.feature_list[each_feature][2] == "primer_bind"):
                    if(self.feature_list[each_feature][0] > self.feature_list[each_feature][1]):
                        file.write(f"     primer_bind     join({self.feature_list[each_feature][0]}..{self.length},1..{self.feature_list[each_feature][1]})\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     primer_bind     {self.feature_list[each_feature][0]}..{self.feature_list[each_feature][1]}\n")
                        file.write(f"                     /label={each_feature}\n")
            for each_feature in self.reverse_feature_list.keys():
                print(self.reverse_feature_list[each_feature])
                if(self.reverse_feature_list[each_feature][2] == "Origin"):
                    if(self.reverse_feature_list[each_feature][0] > self.reverse_feature_list[each_feature][1]):
                        file.write(f"     rep_origin      complement(join({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length},1..{self.length - self.reverse_feature_list[each_feature][0]+1}))\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     rep_origin      complement({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length - self.reverse_feature_list[each_feature][0]+1})\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.reverse_feature_list[each_feature][2] == "CDS"):
                    if(self.reverse_feature_list[each_feature][0] > self.reverse_feature_list[each_feature][1]):
                        file.write(f"     CDS             complement(join({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length},1..{self.length - self.reverse_feature_list[each_feature][0]+1}))\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     CDS             complement({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length - self.reverse_feature_list[each_feature][0] + 1})\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.reverse_feature_list[each_feature][2] == "Promoter"):
                    if(self.reverse_feature_list[each_feature][0] > self.reverse_feature_list[each_feature][1]):
                        file.write(f"     promoter        complement(join({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length},1..{self.length - self.reverse_feature_list[each_feature][0]+1}))\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     promoter        complement({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length - self.reverse_feature_list[each_feature][0] + 1})\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.reverse_feature_list[each_feature][2] == "Terminator"):
                    if(self.reverse_feature_list[each_feature][0] > self.reverse_feature_list[each_feature][1]):
                        file.write(f"     terminator      complement(join({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length},1..{self.length - self.reverse_feature_list[each_feature][0]+1}))\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     terminator      complement({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length - self.reverse_feature_list[each_feature][0] + 1})\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.reverse_feature_list[each_feature][2] == "misc_feature"):
                    if(self.reverse_feature_list[each_feature][0] > self.reverse_feature_list[each_feature][1]):
                        file.write(f"     misc_feature    complement(join({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length},1..{self.length - self.reverse_feature_list[each_feature][0]+1}))\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     misc_feature    complement({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length - self.reverse_feature_list[each_feature][0] + 1})\n")
                        file.write(f"                     /label={each_feature}\n")
                elif(self.reverse_feature_list[each_feature][2] == "primer_bind"):
                    if(self.reverse_feature_list[each_feature][0] > self.reverse_feature_list[each_feature][1]):
                        file.write(f"     primer_bind     complement(join({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length},1..{self.length - self.reverse_feature_list[each_feature][0]+1}))\n")
                        file.write(f"                     /label={each_feature}\n")
                    else:
                        file.write(f"     primer_bind     complement({self.length - self.reverse_feature_list[each_feature][1] + 1}..{self.length - self.reverse_feature_list[each_feature][0] + 1})\n")
                        file.write(f"                     /label={each_feature}\n")
            for each_feature in self.EnzymeList:
                EnzymeName = next(iter(each_feature.keys()))
                EnzymeInfo = each_feature[EnzymeName]
                EnzymeScarName = EnzymeInfo['name']
                NameIndex = 0
                # 通过scar位置判断酶切位点位置
                for each_index in EnzymeInfo['index']:
                    if(EnzymeName == "BsmBI"):
                        print(self.sequence[each_index-8:each_index-2].upper())
                        print(self.sequence[each_index+4:each_index+10].upper())
                    #BsmBI forward
                    if(self.sequence[each_index-8:each_index-2].upper() == "CGTCTC"):
                        file.write(f"     misc_feature    {each_index-7}..{each_index-2}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")
                    #BsmBI reverse
                    elif(self.sequence[each_index+4:each_index+10].upper() == "GAGACG"):
                        file.write(f"     misc_feature    {each_index+5}..{each_index+10}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")
                    
                    #BsaI forward
                    elif(self.sequence[each_index-8:each_index-2].upper() == "GGTCTC"):
                        file.write(f"     misc_feature    {each_index-7}..{each_index-2}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")
                    #BsaI reverse
                    elif(self.sequence[each_index+4:each_index+10].upper() == "GAGACC"):
                        file.write(f"     misc_feature    {each_index+5}..{each_index+10}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")
                    
                    #BbsI forward
                    elif(self.sequence[each_index-9:each_index-3].upper() == "GAAGAC"):
                        file.write(f"     misc_feature    {each_index-8}..{each_index-3}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")
                    #BbsI reverse
                    elif(self.sequence[each_index+5:each_index+11].upper() == "GTCTTC"):
                        file.write(f"     misc_feature    {each_index+6}..{each_index+11}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")
                    
                    #AarI forward
                    elif(self.sequence[each_index-12:each_index-5].upper() == "CACCTGC"):
                        file.write(f"     misc_feature    {each_index-13}..{each_index-5}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")

                    #AarI reverse
                    elif(self.sequence[each_index+7:each_index+14].upper() == "GCAGGTG"):
                        file.write(f"     misc_feature    {each_index+8}..{each_index+14}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+3}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")
                    
                    #SapI forward
                    elif(self.sequence[each_index-9:each_index-2].upper() == "GCTCTTC"):
                        file.write(f"     misc_feature    {each_index-8}..{each_index-2}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+2}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")

                    #SapI reverse
                    elif(self.sequence[each_index+3:each_index+10].upper() == "GAAGAGC"):
                        file.write(f"     misc_feature    {each_index+4}..{each_index+10}\n")
                        file.write(f"                     /label={EnzymeName} Site\n")
                        file.write(f"     misc_feature    {each_index}..{each_index+2}\n")
                        file.write(f"                     /label={EnzymeScarName[NameIndex]} Scar\n")

            file.write("ORIGIN\n")
            numOfline = (self.length // 60) + 1
            offset = 0
            for each_line in range(0,numOfline):
                file.write(f" "*(9-len(str(1+(60*each_line))))+f"{1+(60*each_line)} ")
                if each_line != numOfline - 1:
                    for i in range(0,6):
                        if(i != 5):
                            file.write(f"{self.sequence[offset:offset+10]} ")
                            offset = offset + 10
                        else:
                            file.write(f"{self.sequence[offset:offset+10]}")
                            offset = offset + 10
                else:
                    col_number = (len(self.sequence[offset:]) // 10) + 1
                    for i in range(0,col_number):
                        if(i != col_number -1):
                            file.write(f"{self.sequence[offset:offset+10]} ")
                            offset = offset + 10
                        else:
                            file.write(f"{self.sequence[offset:offset+10]} ")
                            offset = offset + 10
                file.write("\n")
            file.write('//')
            file.flush()
            file.close()
    def GenerateAPEFile(self,name, sequence):
        pass