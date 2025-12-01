from django.core.exceptions import ValidationError
import logging
import requests
from .ControllerModule import FittingLabels
from .CaculateModule.ScarIdentify import scarFunction
from django.db import transaction
from django.db import DatabaseError
import time

# BASE_URL = 'http://10.30.76.2:8004/WebDatabase'
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

class ExcelProcessor:
    """Excel 文件处理工具类"""
    
    # 预期的列映射（Excel列名 -> 模型字段）
    PART_COLUMN_MAPPING = {
        'PartName': 'name',
        'Alias': 'Alias', 
        'Type': 'Type',
        'Sequence': 'Level0Sequence',
        'Species': 'SourceOrganism',
    }

    BACKBONE_COLUMN_MAPPING = {
        'BackboneName':'name',
        'Alias':'alias',
        'Sequence':'sequence',
        'Species':'species',
        'Note':'Note',
    }

    PLASMID_COLUMN_MAPPING = {
        'PlasmidName':'name',
        'Alias':'alias',
        'Level':'level',
        'Sequence':'sequenceConfirm',
        'ParentPart':'',
        'ParentBackbone':'',
        'ParentPlasmid':'',
        'ParentSourceNote':'',
    }
    
    PART_REQUIRED_COLUMNS = ['PartName','Alias','Type','Species']
    BACKBONE_REQUIRED_COLUMNS = ['BackboneName','Alias','Species','Note',]
    PLASMID_REQUIRED_COLUMNS = ['PlasmidName','Alias','Level',]
    
    PLASMID_PARENT_COLUMNS = ['ParentPart','ParentBackbone','ParentPlasmid','ParentSourceNote']
    @classmethod
    def validate_excel_structure(cls, df, type):
        """验证 Excel 文件结构"""
        missing_columns = []
        if(type == 'part'):
            for col in cls.PART_REQUIRED_COLUMNS:
                if col not in df.columns:
                    missing_columns.append(col)
        elif(type == 'backbone'):
            for col in cls.BACKBONE_REQUIRED_COLUMNS:
                if col not in df.columns:
                    missing_columns.append(col)
        elif(type == 'plasmid'):
            for col in cls.PLASMID_REQUIRED_COLUMNS:
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
    def validate_row_data(cls, row_data, row_index,type):
        """验证单行数据"""
        errors = []
        
        # 检查必填字段
        if(type == 'part'):
            for col in cls.PART_REQUIRED_COLUMNS:
                if not row_data.get(col):
                    errors.append(f'第 {row_index} 行：{col}为必填项\n')
        elif(type == 'backbone'):
            for col in cls.BACKBONE_REQUIRED_COLUMNS:
                if not row_data.get(col):
                    errors.append(f'第 {row_index} 行：{col}为必填项\n')
        elif(type == 'plasmid'):
            for col in cls.PLASMID_REQUIRED_COLUMNS:
                if not row_data.get(col):
                    print("required")
                    errors.append(f'第 {row_index} 行：{col}为必填项\n')
            if( not row_data.get(cls.PLASMID_PARENT_COLUMNS[0]) and not row_data.get(cls.PLASMID_PARENT_COLUMNS[1]) and 
                not row_data.get(cls.PLASMID_PARENT_COLUMNS[2]) and not row_data.get(cls.PLASMID_PARENT_COLUMNS[3])):
                print("parent")
                errors.append(f'第 {row_index}行： Parent 信息需至少填写一项\n')
        return errors
    
    @classmethod
    def process_excel_file(cls,django_request,upload_record, type, BASE_URL):
        """处理 Excel 文件"""
        try:
            # 读取 Excel 文件
            df = upload_record
            
            # 验证文件结构
            cls.validate_excel_structure(df, type)

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
            if(type == 'part'):
                for index, row in df.iterrows():
                    row_data = row.to_dict()
                    row_errors = cls.validate_row_data(row_data, index + 2,type)  # +2 因为 Excel 从第2行开始数据
                
                    if row_errors:
                        error_rows.extend(row_errors)
                        continue
                    else:
                        # session = createSession(django_request)
                        data_body = {'name':row['PartName'],'alias':row['Alias'],'Level0Sequence':row['Sequence'],'source':row['Species'],'type':row['Type'],'note':""}
                        response = session.post(f'{BASE_URL}AddPartData',json=data_body,cookies=django_request.COOKIES)
                        if(response.status_code != 200):
                            error_rows.append(f'第{index}行，{row["PartName"]} 添加数据失败\n')
                        if(row['Sequence'] != ""):
                            scar_result_list = scarFunction(row['Sequence'])
                            scar_data_body = {'name':row['PartName'],'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
                            scar_response = session.post(f'{BASE_URL}setPartScar',json=scar_data_body,cookies=django_request.COOKIES)
                            if(scar_response.status_code != 200):
                                error_rows.append(f'第{index}行，{row["PartName"]} scar添加失败\n')
                        else:
                            empty_seq_rows.append(f'第{index}行，{row["PartName"]} 序列为空，请后续补充序列信息\n')
                        
            elif(type == 'backbone'):
                for index, row in df.iterrows():
                    row_data = row.to_dict()
                    row_errors = cls.validate_row_data(row_data, index + 2,type)  # +2 因为 Excel 从第2行开始数据
                    if row_errors:
                        error_rows.extend(row_errors)
                        continue
                    else:
                        Ori = []
                        Marker = []
                        if(row['Sequence'] != ""):
                            OriAndMarkerLabel = FittingLabels(row['Sequence'])
                            for each in OriAndMarkerLabel['Origin']:
                                Ori.append(each['Name'])
                            for each in OriAndMarkerLabel['Marker']:
                                Marker.append(each['Name'])
                        else:
                            empty_seq_rows.append(f'第{index}行，{row["BackboneName"]} 序列为空，请后续补充序列信息\n')
                        data_body = {'name':row['BackboneName'],'alias':row['Alias'],'sequence':row['Sequence'],'ori':Ori,'marker':Marker,'species':row['Species'],'note':row['Note'],'copynumber':''}
                        print(data_body)
                        response = session.post(f'{BASE_URL}AddBackbone',json=data_body,cookies=django_request.COOKIES)
                        if(response.status_code != 200):
                            error_rows.append(f'第{index}行，{row["BackboneName"]} 添加数据失败\n')
                            continue
                        print(response.status_code)
                        if(row['Sequence'] != ""):
                            scar_result_list = scarFunction(row['Sequence'])
                            scar_data_body = {'name':row['BackboneName'],'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
                            scar_response = session.post(f'{BASE_URL}setBackboneScar',json=scar_data_body,cookies=django_request.COOKIES)
                            if(scar_response.status_code == 200):
                                continue
                            else:
                                error_rows.append(f'第{index}行，{row["BackboneName"]} scar添加失败\n')
                        
                        
            elif(type == 'plasmid'):
                for index, row in df.iterrows():
                    row_data = row.to_dict()
                    # print(row_data)
                    row_errors = cls.validate_row_data(row_data, index + 2,type)  # +2 因为 Excel 从第2行开始数据
                    if row_errors:
                        error_rows.extend(row_errors)
                        continue
                    else:
                        # OriClone = "default"
                        # OriHost = "default"
                        # MarkerClone = "default"
                        # MarkerHost = "default"
                        ParentPlasmidExtraNote = ""
                        ParentPlasmidExtraNote_Flag = False
                        # print(OriClone)
                        Ori_list = []
                        Marker_list = []
                        if(row["Sequence"] != ""):
                            OriAndMarkerLabel = FittingLabels(row['Sequence'])
                            print(OriAndMarkerLabel)
                            for each_ori in OriAndMarkerLabel['Origin']:
                                Ori_list.append(each_ori['Name'])
                            for each_marker in OriAndMarkerLabel['Marker']:
                                Marker_list.append(each_marker['Name'])
                        else:
                            empty_seq_rows.append(f'第{index}行，{row["PlasmidName"]} 序列为空，请后续补充序列信息\n')
                        data_body = {'name':row['PlasmidName'],'alias':row['Alias'],'level':row['Level'],'sequence':row['Sequence'],'ParentInfo':row['ParentSourceNote'],'ori':Ori_list, 'marker':Marker_list}
                        print(data_body)
                        response = session.post(f'{BASE_URL}AddPlasmidData',json=data_body,cookies=django_request.COOKIES)
                        if(response.status_code != 200):
                            continue
                        print(response.status_code)
                        print(Ori_list)
                        print(Marker_list)
                        # culture_response = session.post(f'{BASE_URL}setPlasmidCulture',json = {'name':row['PlasmidName'],'ori':Ori_list,'marker':Marker_list},cookies=django_request.COOKIES)
                        # # print(culture_response)
                        # if(culture_response.status_code != 200):
                        #     error_rows.append(f'第{index}行，{row["PlasmidName"]}Culture_Function添加数据失败\n')
                        if(response.status_code != 200):
                            error_rows.append(f'第{index}行，{row["PlasmidName"]}添加数据失败\n')
                            continue
                        # print(response.status_code)
                        if(row['Sequence'] != ""):
                            scar_result_list = scarFunction(row['Sequence'])
                            scar_data_body = {'name':row['PlasmidName'],'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
                            scar_response = session.post(f'{BASE_URL}setPlasmidScar',json=scar_data_body,cookies=django_request.COOKIES)
                            if(scar_response.status_code != 200):
                                error_rows.append(f'第{index}行，{row["PlasmidName"]}scar添加失败\n')
                        ParentPart = row['ParentPart']
                        ParentBackbone = row['ParentBackbone']
                        ParentPlasmid = row['ParentPlasmid']
                        if(ParentPart != ""):
                            ParentPartList = ParentPart.split(',')
                            for each_part in ParentPartList:
                                request_body = {'SonPlasmidName':row['PlasmidName'],'ParentPartName':each_part}
                                ParentPartResponse = session.post(f'{BASE_URL}AddPartParent',json=request_body,cookies=django_request.COOKIES)
                                if(ParentPartResponse.status_code != 200):
                                    ParentPlasmidExtraNote += f"Part({each_part})"
                                    print(ParentPlasmidExtraNote)
                                    error_rows.append(f'第{index}行，{row["PlasmidName"]} Parent Part 添加失败，ID已记录\n')
                                    if(response.status_code == 200):
                                        continue
                                        # return {'success':False,'error':'Plasmid upload success, Parent part upload fail'}
                                # return {'success':False,'error':response.json()}
                        if(ParentBackbone != ""):
                            ParentBackboneList = ParentBackbone.split(',')
                            for each_backbone in ParentBackboneList:
                                request_body = {'SonPlasmidName':row['PlasmidName'],'ParentBackboneName':each_backbone}
                                ParentBackboneResponse = session.post(f'{BASE_URL}AddBackboneParent',json=request_body,cookies=django_request.COOKIES)
                                if(ParentBackboneResponse.status_code != 200):
                                    ParentPlasmidExtraNote += f'Backbone({each_backbone})'
                                    print(ParentPlasmidExtraNote)
                                    error_rows.append(f'第{index}行，{row["PlasmidName"]} Parent Backbone 添加失败, ID已记录\n')
                                    if(response.status_code == 200):
                                        continue
                                        # return {'success':False,'error':'Plasmid upload success, Parent Backbone upload fail'}
                        if(ParentPlasmid != ""):
                            ParentPlasmidList = ParentPlasmid.split(',')
                            for each_plasmid in ParentPlasmidList:
                                request_body = {'SonPlasmidName':row['PlasmidName'],'ParentPlasmidName':each_plasmid}
                                ParentPlasmidResponse = session.post(f'{BASE_URL}AddPlasmidParent',json=request_body,cookies=django_request.COOKIES)
                                if(ParentPlasmidResponse.status_code != 200):
                                    ParentPlasmidExtraNote += f'Plasmid({each_plasmid})'
                                    print(ParentPlasmidExtraNote)
                                    error_rows.append(f'第{index}行，{row["PlasmidName"]} Parent Plasmid 添加失败，ID已记录\n')
                                    if(response.status_code == 200):
                                        continue
                                        # return {'success':False,'error':'Plasmid upload success, Parent plasmid upload fail'}
                        time.sleep(1)
                        request_body = {"PlasmidName":row["PlasmidName"],"PlasmidParentInfo":ParentPlasmidExtraNote}
                        session.post(f'{BASE_URL}UpdateParentInfo',json=request_body,cookies=django_request.COOKIES)
            print(error_rows)
            print(empty_seq_rows)
            return {'success':True,'error_row':error_rows,'empty_Seq_rows':empty_seq_rows}
        except Exception as e:
            logger.error(f"处理 Excel 文件失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }