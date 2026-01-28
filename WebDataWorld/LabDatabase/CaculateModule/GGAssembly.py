import json
import logging
import requests
from django.forms import ValidationError
import os
from Bio.Seq import Seq
from GGModule import SupportGG
from .FeatureIdentify import featureIdentify
from .FileGenerator import SequenceAnnotator
from .ScarIdentify import scarPosition, scarFunction
from Bio.SeqIO import parse
from ControllerModule import FittingLabels



logger = logging.getLogger(__name__)



def createSession(django_request):
    session = requests.Session()
    # token = django_request.COOKIES.get('csrftoken')
            # session.headers.update({
            #     'User-Agent':'Django-App/1.0',
            #     'Content-Type':'application/json',
            #     'X-CSRFToken':token,
            # })
    token = django_request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    return session



class GGFileProcessor:
    """Excel 文件处理工具类"""
    
    # 预期的列映射（Excel列名 -> 模型字段）
    ASSEMBLY_REQUIRED_COLUMNS = ['AssemblyName']
    @classmethod
    def validate_excel_structure(cls, df):
        """验证 Excel 文件结构"""
        missing_columns = []
        for col in cls.ASSEMBLY_REQUIRED_COLUMNS:
            if col not in df.columns:
                missing_columns.append(col)
        if missing_columns:
            raise ValidationError(f"Excel 文件缺少必要的列: {', '.join(missing_columns)}")
        if len(df) == 0:
            raise ValidationError("Excel 文件没有数据")
    
    @classmethod
    def clean_dataframe(cls, df):
        """清理 DataFrame 数据"""
        # 删除完全为空的行
        df = df.dropna(how='all')
        # 填充空值
        df = df.fillna('')
        # 去除字符串字段的空白
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        return df
    
    @classmethod
    def validate_row_data(cls, row_data, row_index):
        """验证单行数据"""
        errors = []
        # 检查必填字段
        for col in cls.ASSEMBLY_REQUIRED_COLUMNS:
            if not row_data.get(col):
                errors.append(f'第 {row_index} 行：{col}为必填项\n')
        return errors
    
    @classmethod
    def createTemporaryRepo(cls,django_request,upload_record, BASE_URL, File_Address, Assembly_File_Address):
        """处理 Excel 文件"""
        logger.info('处理上传文件请求：%s',django_request.path)
        try:
            # 读取 Excel 文件
            df = upload_record
            
            # 验证文件结构
            cls.validate_excel_structure(df)

            # 清理数据
            df = cls.clean_dataframe(df)

            error_rows = []
            empty_seq_rows = []
            session = createSession(django_request)
            # session = requests.Session()
            # token = django_request.COOKIES.get('csrftoken')
            # session.headers.update({
            #     'User-Agent':'Django-App/1.0',
            #     'Content-Type':'application/json',
            #     'X-CSRFToken':token,
            # })
            # GenerateLabels()
            # 处理每一行数据
            for index, row in df.iterrows():
                row_data = row.to_dict()
                row_errors = cls.validate_row_data(row_data, index+2)
                if row_errors:
                    error_rows.extend(row_errors)
                    continue
                else:
                    try:
                        Assembly_Plan_Name = row["AssemblyName"]
                        request_body = {"Name":Assembly_Plan_Name, "Note":row["Note"]}
                        # print(request_body)
                        tempRepo_response = session.post(f"{BASE_URL}createRepo",json=request_body,cookies=django_request.COOKIES)
                        # print(tempRepo_response.json())
                        if(tempRepo_response.status_code != 200):
                            # print("false")
                            error_rows.append(f"第{index}行，创建仓库失败")
                        else:
                            # print(tempRepo_response.json()["repository_id"])
                            # print(tempRepo_response.json()["repository_name"])
                            # print(tempRepo_response.json()["expires_at"])
                            Assembly_Part_List = row["Part"].split(",")
                            Assembly_Backbone_List = row["Backbone"].split(",")
                            Assembly_Plasmid_List = row["Plasmid"].split(",")
                            if(len(Assembly_Part_List) == 1 and Assembly_Part_List[0] == ''):
                                Assembly_Part_List = []
                            if(len(Assembly_Backbone_List) == 1 and Assembly_Backbone_List[0] == ''):
                                Assembly_Backbone_List = []
                            if(len(Assembly_Plasmid_List) == 1 and Assembly_Plasmid_List[0] == ''):
                                Assembly_Plasmid_List = []
                                # print(f"plasmid_list:{Assembly_Plasmid_List}")
                            part_ids = []
                            for each_part in Assembly_Part_List:
                                part_obj = session.get(f"{BASE_URL}PartName?name={each_part.strip()}",cookies=django_request.COOKIES)
                                if(part_obj.status_code == 200):
                                    # print(part_obj.json()['data'])
                                    part_ids.append(part_obj.json()['data']['partid'])
                                else:
                                    raise ValueError
                            # print(part_ids)
                            backbone_ids = []
                            for each_backbone in Assembly_Backbone_List:
                                backbone_obj = session.get(f"{BASE_URL}BackboneName?name={each_backbone.strip()}",cookies=django_request.COOKIES)
                                if(backbone_obj.status_code == 200):
                                    backbone_ids.append(backbone_obj.json()['data']['id'])
                                else:
                                    raise ValueError
                            # print(backbone_ids)
                            plasmid_ids = []
                            # print(f"plasmid_list:{Assembly_Plasmid_List}")
                            for each_plasmid in Assembly_Plasmid_List:
                                plasmid_obj = session.get(f"{BASE_URL}PlasmidName?name={each_plasmid.strip()}",cookies=django_request.COOKIES)
                                if(plasmid_obj.status_code == 200):
                                    plasmid_ids.append(plasmid_obj.json()["data"]['plasmidid'])
                                else:
                                    raise ValueError
                        request_part_body = {"RepoName":row["AssemblyName"],'part_ids':part_ids}
                        request_backbone_body = {"RepoName":row["AssemblyName"],"backbone_ids":backbone_ids}
                        request_plasmid_body = {"RepoName":row["AssemblyName"],"plasmid_ids":plasmid_ids}
                        
                        
                        add_part_response = session.post(f"{BASE_URL}addparts",json=request_part_body,cookies=django_request.COOKIES)
                        add_backbone_response = session.post(f"{BASE_URL}addbackbones",json=request_backbone_body,cookies=django_request.COOKIES)
                        add_plasmid_response = session.post(f"{BASE_URL}addplasmids",json=request_plasmid_body, cookies=django_request.COOKIES)
                        if(add_part_response.status_code != 200):
                            error_rows.extend(f"第{index}行，加入元件失败")
                            continue
                        if(add_backbone_response.status_code != 200):
                            error_rows.extend(f"第{index}行，加入元件失败")
                            continue
                        if(add_plasmid_response.status_code != 200):
                            error_rows.extend(f"第{index}行，加入元件失败")
                            continue
            #             """
            #             组装部分
            #             """
                        
            #             file_address_list = []
            #             file_name_list = []
            #             for each_part in part_ids:
            #                 sequence = (session.get(f'{BASE_URL}GetPartSeqByID?partid={each_part}',cookies = django_request.COOKIES)).json()['data']['level0sequence'].lower()
            #                 partType = (session.get(f"{BASE_URL}TypeByID?ID={each_part}", cookies=django_request.COOKIES)).json()['Type'].lower()
            #                 partName = (session.get(f"{BASE_URL}PartNameByID?ID={each_part}",cookies=django_request.COOKIES)).json()['PartName']
            #                 # print(partType)
            #                 partSource = (session.get(f"{BASE_URL}partSource/{each_part}",cookies=django_request.COOKIES)).json()
            #                 # print(partSource)
            #                 if(partSource['success'] != True):
            #                     error_rows.extend(f"第{index}行，元件物种信息获取失败")
            #                     continue
            #                 if(partSource['source'].lower() != "saccharomyces cerevisiae"):
            #                     if(partType == "promoter"):
            #                         sequence = "GAAGACCTGTGC" + sequence + "ATCAAGGTCTTC"
            #                     elif(partType == "terminator"):
            #                         sequence = "GAAGACCTTAAA" + sequence + "CCTCAGGTCTTC"
            #                     elif(partType == "cds"):
            #                         sequence = "GAAGACCTAATG" + sequence + "TAAAAGGTCTTC"
            #                     elif(partType == "rbs"):
            #                         sequence = "GAAGACCTATCA" + sequence + "AATGAGGTCTTC"
            #                     elif(partType == "p+r"):
            #                         sequence = "GAAGACCTGTGC" + sequence + "AATGAGGTCTTC"
            #                 else:
            #                     if(partType == "promoter"):
            #                         sequence = "GAAGACCTGTGC" + sequence + "AATGAGGTCTTC"
            #                     elif(partType == "terminator"):
            #                         sequence = "GAAGACCTTAAA" + sequence + "CCTCAGGTCTTC"
            #                     elif(partType == "cds"):
            #                         sequence = "GAAGACCTAATG" + sequence + "TAAAAGGTCTTC"
            
            #                 seq_obj = Seq(sequence)
            #                 seq_reverse = str(seq_obj.reverse_complement())
            #                 fi = featureIdentify()
            #                 feature_list = fi.featureMatch(sequence)
            #                 reverse_feature_list = fi.featureMatch(seq_reverse)
            #                 scar_list = scarPosition(sequence)
            #                 sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'part-{partType}-{partName}')
            #                 file_address = os.path.join(File_Address, "AssemblyFile")
            #                 sa.GenerateGBKFile(file_address)
            #                 file_address_list.append(os.path.join(f"{file_address}",f"part-{partType}-{partName}.gbk"))
            #                 file_name_list.append(f'part-{partType}-{partName}')
            #             for each_backbone in backbone_ids:
            #                 sequence = (session.get(f'{BASE_URL}GetBackboneSeqByID?backboneid={each_backbone}',cookies = django_request.COOKIES)).json()['data']['sequence'].lower()
            #                 backboneName = (session.get(f'{BASE_URL}BackboneNameByID?ID={each_backbone}',cookies=django_request.COOKIES)).json()['BackboneName']
            #                 # print(sequence)
            #                 backboneFeature = (session.get(f"{BASE_URL}GetBackboneFeature/{each_backbone}",cookies=django_request.COOKIES)).json()
            #                 file_address = os.path.join(File_Address, "AssemblyFile")
            #                 if(backboneFeature["success"] != True):
            #                     seq_obj = Seq(sequence)
            #                     seq_reverse = str(seq_obj.reverse_complement())
            #                     fi = featureIdentify()
            #                     feature_list = fi.featureMatch(sequence)
            #                     reverse_feature_list = fi.featureMatch(seq_reverse)
            #                     scar_list = scarPosition(sequence)
            #                     sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'backbone-{backboneName}')
            #                     sa.GenerateGBKFile(file_address)
            #                 else:
            #                     SequenceAnnotator.GeneratorBackboneNoSa(f'backbone-{backboneName}',sequence,file_address,backboneFeature['data'])
            #                 file_address_list.append(os.path.join(f"{file_address}",f"backbone-{backboneName}.gbk"))
            #                 file_name_list.append(f"backbone-{backboneName}")
            #             for each_plasmid in plasmid_ids:
            #                 plasmidName = (session.get(f'{BASE_URL}PlasmidNameByID?ID={each_plasmid}',cookies=django_request.COOKIES)).json()['PlasmidName']
            #                 if(os.path.exists(os.path.join(Assembly_File_Address,f"{plasmidName}.gb"))):
            #                     file_address_list.append(os.path.join(Assembly_File_Address,f"{plasmidName}.gb"))
            #                     file_name_list.append(plasmidName)
            #                 else:
            #                     sequence = (session.get(f'{Assembly_File_Address}PlasmidSeqByID?plasmidid={each_plasmid}',cookies = django_request.COOKIES)).json()['data']['sequenceconfirm'].lower()
            #                     seq_obj = Seq(sequence)
            #                     seq_reverse = str(seq_obj.reverse_complement())
            #                     fi = featureIdentify()
            #                     feature_list = fi.featureMatch(sequence)
            #                     reverse_feature_list = fi.featureMatch(seq_reverse)
            #                     scar_list = scarPosition(sequence)
            #                     sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'plasmid-{plasmidName}')
            #                     file_address = os.path.join(File_Address, "AssemblyFile")
            #                     sa.GenerateGBKFile(file_address)
            #                     file_address_list.append(os.path.join(f"{file_address}",f"plasmid-{plasmidName}.gbk"))
            #                     file_name_list.append(f"plasmid-{plasmidName}")
            
            #             GG = SupportGG.SupportGG(file_address_list,file_name_list)
            #             GG.assemblyPart(Assembly_Plan_Name)
            #             GG.show()
            #             if(os.path.exists(os.path.join(Assembly_File_Address,f"{Assembly_Plan_Name}.gb"))):
            #                 records = parse(os.path.join(Assembly_File_Address,f"{Assembly_Plan_Name}.gb"), "genbank")
            #                 for record in records:
            #                     Sequence = str(record.seq)
            #                 response = AssemblyResultUpload(django_request, Assembly_Plan_Name, Sequence, part_ids, backbone_ids, plasmid_ids, BASE_URL)
            #                 if(response["success"]):
            #                     continue
            #                 else:
            #                     error_rows.extend(f"第{index}行上传数据失败")
            #                     continue
            #             else:
            #                 error_rows.extend(f"第{index}行，组装文件不存在")
            #         except Exception as e:
            #             logger.error(f"创建仓库失败：{str(e.args)}")
            #             error_rows.append(f"第{index}行，创建仓库失败")
            # if(len(error_rows) == 0):
            #     return {"success":True}
            # else:
            #     return {"success":True,"error_row":error_rows}
                
                    except Exception as e:
                        logger.error(f"处理Excel文件失败: {str(e.args)}")
                        return {
                            'success':False,
                            'error': str(e.args),
                        }
        except Exception as e:
            return {
                'success':False,
                'error': str(e.args),
                }
            
            
            
def AssemblyResultUpload(django_request,Name, Sequence, partList, BackboneList, PlasmidList, Base_URL):\
    
    session = requests.Session()
    token = django_request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    if(len(partList) != 0):
        level = 2
    else:
        level = 3
    data_body = {'name':Name,'alias':Name,'level':level,'sequence':Sequence,'note':"",'ParentInfo':""}
    response = session.post(f'{Base_URL}AddPlasmidData',json=data_body,cookies=django_request.COOKIES)
    if(response.status_code != 200):
        return {"success":False, "message":"添加质粒错误"}
    Ori_list = []
    Marker_list = []
    OriAndMarkerLabel = FittingLabels(Sequence)
    # print(OriAndMarkerLabel)
    for each_ori in OriAndMarkerLabel['Origin']:
        Ori_list.append(each_ori['Name'])
    for each_marker in OriAndMarkerLabel['Marker']:
        Marker_list.append(each_marker['Name'])
    # print(OriAndMarkerLabel)
    plasmid_culture_body = {"name":Name, "ori":Ori_list,"marker":Marker_list}
    plasmid_culture_response = session.post(f"{Base_URL}setPlasmidCulture",json = plasmid_culture_body, cookies=django_request.COOKIES)
    if(plasmid_culture_response.status_code != 200):
        return {"success":False, "message":"质粒培养信息添加错误"}
    scar_result_list = scarFunction(Sequence)
    scar_data_body = {'name':Name,'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
    scar_response = session.post(f'{Base_URL}setPlasmidScar',json=scar_data_body,cookies=django_request.COOKIES)
    if(scar_response.status_code != 200):
        return {"success":False, "message":"质粒scar信息添加错误"}
    for each_part in partList:
        request_body = {"SonPlasmidName":Name,"ParentPartID":each_part}
        part_response = session.post(f"{Base_URL}AddPartParentByID",json=request_body,cookies=django_request.COOKIES)
        if(part_response.status_code != 200):
            return {"success":False,"message":"Parent Part 添加失败"}
    for each_backbone in BackboneList:
        request_body = {"SonPlasmidName":Name,"ParentBackboneID":each_backbone}
        backbone_response = session.post(f"{Base_URL}AddBackboneParentByID",json=request_body,cookies=django_request.COOKIES)
        if(backbone_response.status_code != 200):
            return {"success":False,"message":"Parent Backbone 添加失败"}
    for each_plasmid in PlasmidList:
        request_body = {"SonPlasmidName":Name,"ParentPlasmidID":each_plasmid}
        plasmid_response = session.post(f"{Base_URL}AddPlasmidParentByID",json=request_body,cookies=django_request.COOKIES)
        if(plasmid_response.status_code != 200):
            return {"success":False,"message":"Parent Plasmid 添加失败"}
    return {"success":True}