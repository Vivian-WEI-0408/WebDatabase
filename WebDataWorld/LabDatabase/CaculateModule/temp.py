from Bio.Seq import Seq
import re
import pymysql
import sys
sys.path.append(r'C:\Users\admin\Desktop\WebDatabaseBeta\WebDatabase\WebDataWorld\LabDatabase')
from ControllerModule import FittingLabels

conn = pymysql.connect(user="root",password="04080117",host="localhost",database="labdnadata")
cur = conn.cursor()

sql = "begin;"
sql = "select plasmidid from plasmidneed;"
cur.execute(sql)
result = cur.fetchall()
for each in result:
    sql2 = f"select function_content from plasmid_culture_functions where plasmid_id = {each[0]} and function_type = 'ori';"
    cur.execute(sql2)
    result2 = cur.fetchall()
    if(len(result2) > 1):
        sql3 = f"update plasmidneed set tag = 'abnormal' where plasmidid = {each[0]};"
        cur.execute(sql3)
    else:
        sql4 = f"select function_content from plasmid_culture_functions where plasmid_id = {each[0]} and function_type = 'marker';"
        cur.execute(sql4)
        result4 = cur.fetchall()
        if(len(result4) > 1):
            sql5 = f"update plasmidneed set tag = 'abnormal' where plasmidid = {each[0]};"
            cur.execute(sql5)
        else:
            sql5 = f"update plasmidneed set tag = 'normal' where plasmidid = {each[0]};"
            cur.execute(sql5)
#     sql2 = f"update parttable set tag = 'normal' where partid = {each[0]};"
#     cur.execute(sql2)
# sql = "begin;"
# sql = "select plasmidid from plasmidneed;"
# cur.execute(sql)
# result = cur.fetchall()
# for each_id in result:
#     sql_t = f"select pcfid,function_content from plasmid_culture_functions where plasmid_id = {each_id[0]} and function_type = \"marker\";"
#     print(sql_t)
#     cur.execute(sql_t)
#     result_t = cur.fetchall()
#     result_list = set()
#     for each in result_t:
#         if(result_list.__contains__(each[1]) == False):
#             sql_2 = f"delete from plasmid_culture_functions where pcfid = {each[0]};"
#             cur.execute(sql_2)
#         else:
#             result_list.add(each[1])
# cur.execute("rollback;")
conn.commit()
# from FeatureIdentify import featureIdentify
# # from LabDatabase.CaculateModule.FileGenerator import SequenceAnnotator
# from FileGenerator import SequenceAnnotator
# seq_obj = Seq("ttaagcaaggattttcttaacttcttcggcgacagcatcaccgacttcggtggtactgttggaaccacctaaatcaccagttctgatacctgcatccaaaacctttttaactgcatcttcaatggccttaccttcttcaggcaagttcaatgacaatttcaacatcattgcagcagacaagatagtggcgatagggttgaccttattctttggcaaatctggagcagaaccgtggcatggttcgtacaaaccaaatgcggtgttcttgtctggcaaagaggccaaggacgcagatggcaacaaacccaaggaacctgggataacggaggcttcatcggagatgatatcaccaaacatgttgctggtgattataataccatttaggtgggttgggttcttaactaggatcatggcggcagaatcaatcaattgatgttgaaccttcaatgtaggaaattcgttcttgatggtttcctccacagtttttctccataatcttgaagaggccaaaacattagctttatccaaggaccaaataggcaatggtggctcatgttgtagggccatgaaagcggccattcttgtgattctttgcacttctggaacggtgtattgttcactatcccaagcgacaccatcaccatcgtcttcctttctcttaccaaagtaaatacctcccactaattctctgacaacaacgaagtcagtacctttagcaaattgtggcttgattggagataagtctaaaagagagtcggatgcaaagttacatggtcttaagttggcgtacaattgaagttctttacggatttttagtaaaccttgttcaggtctaacactacctgtaccccatttaggaccacccacagcacctaacaaaacggcatcagccttcttggaggcttccagcgcctcatctggaagtggaacacctgtagcatcgatagcagcaccaccaattaaatgattttcgaaatcgaacttgacattggaacgaacatcagaaatagctttaagaaccttaatggcttcggctgtgatttcttgaccaacgtggtcacctggcaaaacgacgatcttcttaggggcagacat")
# print(str(seq_obj.reverse_complement()))
# from ScarIdentify import ScarIdentify, scarFunction, scarPosition

# seq = "TTATGACAACTTGACGGCTACATCATTCACTTTTTCTTCACAACCGGCACGGAACTCGCTCGGGCTGGCCCCGGTGCATTTTTTAAATACCCGCGAGAAATAGAGTTGATCGTCAAAACCAACATTGCGACCGACGGTGGCGATAGGCATCCGGGTGGTGCTCAAAAGCAGCTTCGCCTGGCTGATACGTTGGTCCTCGCGCCAGCTTAAGACGCTAATCCCTAACTGCTGGCGGAAAAGATGTGACAGACGCGACGGCGACAAGCAAACATGCTGTGCGACGCTGGCGATATCAAAATTGCTGTCTGCCAGGTGATCGCTGATGTACTGACAAGCCTCGCGTACCCGATTATCCATCGGTGGATGGAGCGACTCGTTAATCGCTTCCATGCGCCGCAGTAACAATTGCTCAAGCAGATTTATCGCCAGCAGCTCCGAATAGCGCCCTTCCCCTTGCCCGGCGTTAATGATTTGCCCAAACAGGTCGCTGAAATGCGGCTGGTGCGCTTCATCCGGGCGAAAGAACCCCGTATTGGCAAATATTGACGGCCAGTTAAGCCATTCATGCCAGTAGGCGCGCGGACGAAAGTAAACCCACTGGTGATACCATTCGCGAGCCTCCGGATGACGACCGTAGTGATGAATCTCTCCTGGCGGGAACAGCAAAATATCACCCGGTCGGCAAACAAATTCTCGTCCCTGATTTTTCACCACCCCCTGACCGCGAATGGTGAGATTGAGAATATAACCTTTCATTCCCAGCGGTCGGTCGATAAAAAAATCGAGATAACCGTTGGCCTCAATCGGCGTTAAACCCGCCACCAGATGGGCATTAAACGAGTATCCCGGCAGCAGGGGATCATTTTGCGCTTCAGCCAT"
# print(seq.upper())
# seq = "GAAGACCTCTGACAATCACCTATGAACTGTCGGTGCGGAGACCGGCTTACTAAAAGCCAGATAACAGTATGCATATTTGCGCGCTGATTTTTGCGGTATAAGAATATATACTGATATGTATACCCGAAGTATGTCAAAAAGAGGTATGCTATGAAGCAGCGTATTACAGTGACAGTTGACAGCGACAGCTATCAGTTGCTCAAGGCATATATGATGTCAATATCTCCGGTCTGGTAAGCACAACCATGCAGAATGAAGCCCGTCGTCTGCGTGCCGAACGCTGGAAAGCGGAAAATCAGGAAGGGATGGCTGAGGTCGCCCGGTTTATTGAAATGAACGGCTCTTTTGCTGACGAGAACAGGGGCTGGTGAAATGCAGTTTAAGGTTTACACCTATAAAAGAGAGAGCCGTTATCGTCTGTTTGTGGATGTACAGAGTGATATTATTGACACGCCCGGGCGACGGATGGTGATCCCCCTGGCCAGTGCACGTCTGCTGTCAGATAAAGTCTCCCGTGAACTTTACCCGGTGGTGCATATCGGGGATGAAAGCTGGCGCATGATGACCACCGATATGGCCAGTGTGCCGGTTTCCGTTATCGGGGAAGAAGTGGCTGATCTCAGCCACCGCGAAAATGACATCAAAAACGCCATTAACCTGATGTTCTGGGGAATATAAGGTCTCCCCTCTACGGAGTCTTCGAGCGGTATCAGCTCACTCAAAGGCGGTAATACGGTTATCCACAGAATCAGGGGATAACGCAGGAAAGAACATGTGAGCAAAAGGCCAGCAAAAGGCCAGGAACCGTAAAAAGGCCGCGTTGCTGGCGTTTTTCCATAGGCTCCGCCCCCCTGACGAGCATCACAAAAATCGACGCTCAAGTCAGAGGTGGCGAAACCCGACAGGACTATAAAGATACCAGGCGTTTCCCCCTGGAAGCTCCCTCGTGCGCTCTCCTGTTCCGACCCTGCCGCTTACCGGATACCTGTCCGCCTTTCTCCCTTCGGGAAGCGTGGCGCTTTCTCATAGCTCACGCTGTAGGTATCTCAGTTCGGTGTAGGTCGTTCGCTCCAAGCTGGGCTGTGTGCACGAACCCCCCGTTCAGCCCGACCGCTGCGCCTTATCCGGTAACTATCGTCTTGAGCCCAACCCGGTAAGACACGACTTATCGCCACTGGCAGCAGCCACTGGTAACAGGATTAGCAGAGCGAGGTATGTAGGCGGTGCTACAGAGTTCTTGAAGTGGTGGCCTAACTACGGCTACACTAGAAGAACAGTATTTGGTATCTGCGCTCTGCTGAAGCCAGTTACCTTCGGAAAAAGAGTTGGTAGCTCTTGATCCGGCAAACAAACCACCGCTGGTAGCGGTGGTTTTTTTGTTTGCAAGCAGCAGATTACGCGCAGAAAAAAAGGATCTCAAGAAGATCCTTTGATCTTTTCTACGGGGTCTGACGCTCAGTGGAACGAAAACTCACGTTAAGGGATTTTGGTCATGAGATTATCAAAAAGGATCTTCACCTAGATCCTTTTAAATTAAAAATGAAGTTTTAAATCAATCTAAAGTATATATGAGTAAACTTGGTCTGACAGAGTTCTGAGGTCATTACTGGATCTATCAACAGCAGTCCAAGCGAGCTCGATATCAAATTACGCCCCGCCCTGCCACTCATCGCAGTACTGTTGTAATTCATTAAGCATTCTGCCGACATGGAAGCCATCACAAACGGCATGATGAACCTGAATCGCCAGCGGCATCAGCACCTTGTCGCCTTGCGTATAATATTTGCCCATGGTGAAAACGGGGGCGAAGAAGTTGTCCATATTGGCCACGTTTAAATCAAAACTGGTGAAACTCACCCAGGGATTGGCTGAGACGAAAAACATATTCTCAATAAACCCTTTAGGGAAATAGGCCAGGTTTTCACCGTAACACGCCACATCTTGCGAATATATGTGTAGAAACTGCCGGAAATCGTCGTGGTATTCACTCCAGAGCGATGAAAACGTTTCAGTTTGCTCATGGAAAACGGTGTAACAAGGGTGAACACTATCCCATATCACCAGCTCACCGTCTTTCATTGCCATACGAAATTCCGGATGAGCATTCATCAGGCGGGCAAGAATGTGAATAAAGGCCGGATAAAACTTGTGCTTATTTTTCTTTACGGTCTTTAAAAAGGCCGTAATATCCAGCTGAACGGTCTGGTTATAGGTACATTGAGCAACTGACTGAAATGCCTCAAAATGTTCTTTACGATGCCATTGGGATATATCAACGGTGGTATATCCAGTGATTTTTTTCTCCATTTTAGCTTCCTTAGCTCCTGAAAATCTCGATAACTCAAAAAATACGCCCGGTAGTGATCTTATTTCATTATGGTGAAAGTTGGAACCTCTTACGTGCCCGATCAACTCGCGCGTTTGCCACCTGACGTCTAAGAAAAGGAATATTCAGCAATTTGCCCGTGCCGAAGAAAGGCCCACCCGTGAAGGTGAGC"
# seq_obj = Seq(seq)
# seq_reverse = str(seq_obj.reverse_complement())
# fi = featureIdentify()
# feature_list = fi.featureMatch(seq)
# reverse_feature_list = fi.featureMatch(seq_reverse)
# scar_list = scarPosition(seq)
# sa = SequenceAnnotator(seq,feature_list,reverse_feature_list,scar_list)
# sa.GenerateGBKFile()



# print(scar_list)
# for eachfeature in scar_list:
#     EnzymeName = next(iter(eachfeature.keys()))
#     EnzymeInfo = eachfeature[EnzymeName]
#     # 通过scar位置判断酶切位点位置
#     for each_index in EnzymeInfo['index']:
#         print(seq[each_index-8:each_index-2].upper())
#         print(seq[each_index+4:each_index+10].upper())
        # if(seq[each_index-7:each_index-1].upper() == "CGTCTC"):
                




# for each_feature in feature_list.keys():
#     seq_id = 
#     start = each_feature
# print(feature_list)
# print(reverse_feature_list)

# text = "AAAAAAAAPart(Ptet)Part( BCD2)Part(fluc)Part(DT100)Backbone(CQM007)Plasmid(XJL38)Plasmid(XJL39)Plasmid(XJL40)Plasmid(GFW60)"
# pattern = r'(\w+)\(([ a-zA-z0-9]+)\)'
# matches = re.findall(pattern, text)
# result = {
#     "parts":[],
#     "backbones":[],
#     "plasmid":[],
# }
# for component_type, letter in matches:
#     if(component_type == 'Part'):
#         result
# print(matches)
