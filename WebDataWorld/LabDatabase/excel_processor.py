import pandas as pd
import numpy as np
from django.core.exceptions import ValidationError
import logging
# from WebDatabase.models import Parttable,Backbonetable,Plasmidneed,\
#                                Parentparttable,Parentbackbonetable,Parentplasmidtable
import requests
from .ControllerModule import FittingLabels
from .CaculateModule.ScarIdentify import scarFunction

BASE_URL = 'http://10.30.76.2:8000/WebDatabase'
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
        'LengthOfSequence': 'Lengthinlevel0',
        'Sequence': 'Level0Sequence',
        'Species': 'SourceOrganism',
    }

    BACKBONE_COLUMN_MAPPING = {
        'BackboneName':'name',
        'Alias':'alias',
        'Length of Sequence': 'length',
        'Sequence':'sequence',
        'Species':'species',
        'Note':'Note',
    }

    PLASMID_COLUMN_MAPPING = {
        'PlasmidName':'name',
        'Alias':'alias',
        'Level':'level',
        'Length Of Sequence':'length',
        'Sequence':'sequenceConfirm',
        'ParentPart':'',
        'ParentBackbone':'',
        'ParentSourceNote':'',
    }
    
    PART_REQUIRED_COLUMNS = ['PartName','Alias','Type','Sequence','Species']
    BACKBONE_REQUIRED_COLUMNS = ['BackboneName','Alias','Sequence','Species','Note',]
    PLASMID_REQUIRED_COLUMNS = ['PlasmidName','Alias','Level','Sequence','ParentSourceNote',]
    
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
                    errors.append(f'第 {row_index} 行：{col}为必填项')
        elif(type == 'backbone'):
            for col in cls.BACKBONE_REQUIRED_COLUMNS:
                if not row_data.get(col):
                    errors.append(f'第 {row_index} 行：{col}为必填项')
        elif(type == 'plasmid'):
            for col in cls.PLASMID_REQUIRED_COLUMNS:
                if not row_data.get(col):
                    errors.append(f'第 {row_index} 行：{col}为必填项')
            if( not row_data.get(cls.PLASMID_PARENT_COLUMNS[0]) and not row_data.get(cls.PLASMID_PARENT_COLUMNS[1]) and 
                not row_data.get(cls.PLASMID_PARENT_COLUMNS[2]) and not row_data.get(cls.PLASMID_PARENT_COLUMNS[3])):
                errors.append(f'Parent 信息需至少填写一项')
        
        return errors
    
    @classmethod
    def process_excel_file(cls,django_request,upload_record, type):
        """处理 Excel 文件"""
        try:
            # 读取 Excel 文件
            df = upload_record
            
            # 验证文件结构
            cls.validate_excel_structure(df, type)

            # 清理数据
            df = cls.clean_dataframe(df)

            error_rows = []
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
                        response = session.post(f'{BASE_URL}/AddPartData',json=data_body,cookies=django_request.COOKIES)
                        scar_result_list = scarFunction(row['Sequence'])
                        scar_data_body = {'name':row['PartName'],'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
                        scar_response = session.post(f'{BASE_URL}/setPartScar',json=scar_data_body,cookies=django_request.COOKIES)
                        if(response.status_code == 200 and scar_response.status_code == 200):
                            return True
            elif(type == 'backbone'):
                for index, row in df.iterrows():
                    row_data = row.to_dict()
                    row_errors = cls.validate_row_data(row_data, index + 2,type)  # +2 因为 Excel 从第2行开始数据
                    if row_errors:
                        error_rows.extend(row_errors)
                        continue
                    else:
                        Ori = ""
                        Marker = ""
                        OriAndMarkerLabel = FittingLabels(row['Sequence'])
                        if(OriAndMarkerLabel["Origin"] == ""):
                            Ori = OriAndMarkerLabel["Origin"]
                        if(OriAndMarkerLabel["Marker"] == ""):
                            Marker = OriAndMarkerLabel["Marker"]
                        data_body = {'name':row['BackboneName'],'alias':row['Alias'],'sequence':row['Sequence'],'ori':Ori,'marker':Marker,'species':row['Species'],'note':row['Note'],'copynumber':''}
                        response = session.post(f'{BASE_URL}/AddBackbone',json=data_body,cookies=django_request.COOKIES)
                        print(response.status_code)
                        scar_result_list = scarFunction(row['Sequence'])
                        scar_data_body = {'name':row['BackboneName'],'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
                        scar_response = session.post(f'{BASE_URL}/setBackboneScar',json=scar_data_body,cookies=django_request.COOKIES)
                        if(response.status_code == 200):
                            return True
            elif(type == 'plasmid'):
                for index, row in df.iterrows():
                    row_data = row.to_dict()
                    row_errors = cls.validate_row_data(row_data, index + 2,type)  # +2 因为 Excel 从第2行开始数据
                    if row_errors:
                        error_rows.extend(row_errors)
                        continue
                    else:
                        OriClone = "default"
                        OriHost = "default"
                        MarkerClone = "default"
                        MarkerHost = "default"
                        OriAndMarkerLabel = FittingLabels(row['Sequence'])
                        if(len(OriAndMarkerLabel["Origin"]) == 1):
                            OriClone = OriAndMarkerLabel['Origin'][0]
                        elif(len(OriAndMarkerLabel["Origin"]) == 2):
                            OriClone = OriAndMarkerLabel['Origin'][0]
                            OriHost = OriAndMarkerLabel['Marker'][1]
                        if(len(OriAndMarkerLabel["Marker"]) == 1):
                            MarkerClone = OriAndMarkerLabel["Marker"][0]
                        elif(len(OriAndMarkerLabel['Marker']) == 2):
                            MarkerClone = OriAndMarkerLabel['Marker'][0]
                            MarkerHost = OriAndMarkerLabel['Marker'][1]
                        data_body = {'name':row['PlasmidName'],'alias':row['Alias'],'oriclone':OriClone,'orihost':OriHost,'markerclone':MarkerClone,'markerhost':MarkerHost,'level':row['Level'],'sequence':row['Sequence'],'ParentInfo':row['ParentSourceNote']}
                        # print(data_body)
                        response = session.post(f'{BASE_URL}/AddPlasmidData',json=data_body,cookies=django_request.COOKIES)
                        # print(response.status_code)
                        scar_result_list = scarFunction(row['Sequence'])
                        scar_data_body = {'name':row['PlasmidName'],'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
                        scar_response = session.post(f'{BASE_URL}/setPlasmidScar',json=scar_data_body,cookies=django_request.COOKIES)
                        if(response.status_code != 200):
                            return False
                        ParentPart = row['ParentPart']
                        ParentBackbone = row['ParentBackbone']
                        ParentPlasmid = row['ParentPlasmid']
                        if(ParentPart != ""):
                            ParentPartList = ParentPart.split(',')
                            for each_part in ParentPartList:
                                request_body = {'SonPlasmidName':row['PlasmidName'],'ParentPartName':each_part}
                                ParentPartResponse = session.post(f'{BASE_URL}/AddPartParent',json=request_body,cookies=django_request.COOKIES)
                                if(ParentPartResponse.status_code != 200):
                                    if(response.status_code == 200):
                                        return {'success':False,'error':'Plasmid upload success, Parent part upload fail'}
                                # return {'success':False,'error':response.json()}
                        if(ParentBackbone != ""):
                            ParentBackboneList = ParentBackbone.split(',')
                            for each_backbone in ParentBackboneList:
                                request_body = {'SonPlasmidName':row['PlasmidName'],'ParentBackboneName':each_backbone}
                                ParentBackboneResponse = session.post(f'{BASE_URL}/AddBackboneParent',json=request_body,cookies=django_request.COOKIES)
                                if(ParentBackboneResponse.status_code != 200):
                                    if(response.status_code == 200):
                                        return {'success':False,'error':'Plasmid upload success, Parent Backbone upload fail'}
                        if(ParentPlasmid != ""):
                            ParentPlasmidList = ParentPlasmid.split(',')
                            for each_plasmid in ParentPlasmidList:
                                request_body = {'SonPlasmidName':row['PlasmidName'],'ParentPlasmidName':each_plasmid}
                                ParentPlasmidResponse = session.post(f'{BASE_URL}/AddPlasmidParent',json=request_body,cookies=django_request.COOKIES)
                                if(ParentPlasmidResponse.status_code != 200):
                                    if(response.status_code == 200):
                                        return {'success':False,'error':'Plasmid upload success, Parent plasmid upload fail'}
            return {'success':True}
        except Exception as e:
            logger.error(f"处理 Excel 文件失败: {str(e)}")
            
            return {
                'success': False,
                'error': str(e)
            }