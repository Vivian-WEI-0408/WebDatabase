import json
import logging
import requests
from django.forms import ValidationError


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
    def createTemporaryRepo(cls,django_request,upload_record, BASE_URL):
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
                        print(request_body)
                        tempRepo_response = session.post(f"{BASE_URL}createRepo",json=request_body,cookies=django_request.COOKIES)
                        print(tempRepo_response.json())
                        if(tempRepo_response.status_code != 200):
                            print("false")
                            error_rows.append(f"第{index}行，创建仓库失败")
                        else:
                            print(tempRepo_response.json()["repository_id"])
                            print(tempRepo_response.json()["repository_name"])
                            print(tempRepo_response.json()["expires_at"])
                            Assembly_Part_List = row["Part"].split(",")
                            Assembly_Backbone_List = row["Backbone"].split(",")
                            Assembly_Plasmid_List = row["Plasmid"].split(",")
                            if(len(Assembly_Part_List) == 1 and Assembly_Part_List[0] == ''):
                                Assembly_Part_List = []
                            if(len(Assembly_Backbone_List) == 1 and Assembly_Backbone_List[0] == ''):
                                Assembly_Backbone_List = []
                            if(len(Assembly_Plasmid_List) == 1 and Assembly_Plasmid_List[0] == ''):
                                Assembly_Plasmid_List = []
                                print(f"plasmid_list:{Assembly_Plasmid_List}")
                            part_ids = []
                            for each_part in Assembly_Part_List:
                                part_obj = session.get(f"{BASE_URL}PartName?name={each_part.strip()}",cookies=django_request.COOKIES)
                                if(part_obj.status_code == 200):
                                    print(part_obj.json()['data'])
                                    part_ids.append(part_obj.json()['data']['partid'])
                                else:
                                    raise ValueError
                            print(part_ids)
                            backbone_ids = []
                            for each_backbone in Assembly_Backbone_List:
                                backbone_obj = session.get(f"{BASE_URL}BackboneName?name={each_backbone.strip()}",cookies=django_request.COOKIES)
                                if(backbone_obj.status_code == 200):
                                    backbone_ids.append(backbone_obj.json()['data']['id'])
                                else:
                                    raise ValueError
                            print(backbone_ids)
                            plasmid_ids = []
                            print(f"plasmid_list:{Assembly_Plasmid_List}")
                            for each_plasmid in Assembly_Plasmid_List:
                                plasmid_obj = session.get(f"{BASE_URL}PlasmidName?name={each_plasmid.strip()}",cookies=django_request.COOKIES)
                                if(plasmid_obj.status_code == 200):
                                    plasmid_ids.append(plasmid_obj.json()["data"]['plasmidid'])
                                else:
                                    raise ValueError
                            print(plasmid_ids)
                        request_part_body = {"RepoName":row["AssemblyName"],'part_ids':part_ids}
                        request_backbone_body = {"RepoName":row["AssemblyName"],"backbone_ids":backbone_ids}
                        request_plasmid_body = {"RepoName":row["AssemblyName"],"plasmid_ids":plasmid_ids}
                        print(request_part_body)
                        
                        add_part_response = session.post(f"{BASE_URL}addparts",json=request_part_body,cookies=django_request.COOKIES)
                        add_backbone_response = session.post(f"{BASE_URL}addbackbones",json=request_backbone_body,cookies=django_request.COOKIES)
                        add_plasmid_response = session.post(f"{BASE_URL}addplasmids",json=request_plasmid_body, cookies=django_request.COOKIES)
                        if(add_part_response.status_code != 200):
                            error_rows.extend(f"第{index}行，加入元件失败")
                        if(add_backbone_response.status_code != 200):
                            error_rows.extend(f"第{index}行，加入元件失败")
                        if(add_plasmid_response.status_code != 200):
                            error_rows.extend(f"第{index}行，加入元件失败")
                    except Exception as e:
                        logger.error(f"创建仓库失败：{str(e.args)}")
                        error_rows.append(f"第{index}行，创建仓库失败")
            if(len(error_rows) == 0):
                return {"success":True}
            else:
                return {"success":True,"error_row":error_rows}
                
        except Exception as e:
            logger.error(f"处理Excel文件失败: {str(e.args)}")
            return {
                'success': False,
                'error': str(e.args),
            }