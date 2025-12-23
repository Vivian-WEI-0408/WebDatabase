import io
import time
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse,FileResponse,Http404
from django.views import View
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from LabDatabase.excel_processor import ExcelProcessor
from LabDatabase.map_processor import process_map_file
import requests
from LabDatabase.CaculateModule import GGAssembly
# from WebDatabase.models import UploadedFile
import threading
import openpyxl
import os
import pandas as pd
import json
from Bio.Seq import Seq
import re
from .CaculateModule.FeatureIdentify import featureIdentify
from .CaculateModule.FileGenerator import SequenceAnnotator
from .CaculateModule.ScarIdentify import scarPosition,scarFunction
from .CaculateModule.snapgene_reader import snapgene_to_dict
from .ControllerModule import FittingLabels
from GGModule import SupportGG
from Bio.SeqIO import parse


import uuid

Base_URL = "http://10.30.76.2:8000/WebDatabase/"
Exp_URL = "http://10.30.76.75:8009/"
File_Address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\\"
Assembly_File_Address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\output"
TASK_STATUS_PREFIX = 'file_task_'
# class User_auth(MiddlewareMixin):

#     def process_request(self,request):
#         #排除不需要登录就能访问的页面
#         if request.path_info == "/WebDatabase/login" or request.path_info == "":
#             return
#         info = request.session.get('info')
#         print(info)
#         if not info:
#             return redirect('/WebDatabase/login')
#         else:
#             return

#     def process_response(self,request,response):
#         return response



def index(request):
    if(request.method == "GET"):
        return render(request,'index.html',{"user":request.user})

def getData(request):
    # print(request.session['info']['uname'])
    session = requests.Session()
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
    })
    if(request.method == "GET"):
        type = request.GET.get("type")
        page = request.GET.get("page",1)
        if(type == "part"):
            try:
                # sessionid = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
                # print(sessionid)
                # cookies = {}
                # if(sessionid):
                #     cookies[settings.SESSION_COOKIE_NAME] = sessionid
                promoterResponse = requests.get(f'{Base_URL}Part?page={page}',cookies=request.COOKIES)
                # print(promoterResponse.url)
                if(promoterResponse.status_code == 200):
                    promoter = promoterResponse.json()
                    return JsonResponse(promoter,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse(str(e),status = 400, safe=False)
        elif(type == "backbone"):
            try:
                backboneResponse = requests.get(f'{Base_URL}Backbone?page={page}',cookies=request.COOKIES)
                if(backboneResponse.status_code == 200):
                    backbone = backboneResponse.json()
                    return JsonResponse(backbone,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse(str(e),status = 400, safe=False)
        elif(type == "plasmid"):
            try:
                plasmidResponse = session.get(f'{Base_URL}Plasmid?page={page}',cookies=request.COOKIES)
                if(plasmidResponse.status_code == 200):
                    plasmid = plasmidResponse.json()
                    return JsonResponse(plasmid,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse(str(e),status = 400, safe=False)
            

def DataFilter(request):
    # print(request.session['info']['uname'])
    session = requests.Session()
    token = request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    if(request.method == "POST"):
        data = json.loads(request.body)
        print(data)
        type = data.get("SearchType")
        page = data.get("page",1)
        print(type)
        if(type == "part"):
            try:
                request_body = {'type':data.get('Type',""),"Enzyme":data.get('Enzyme',""),"Scar":data.get('Scar',""),"name":data.get('name',""),"page":page,"page_size":10}
                promoterResponse = session.post(f'{Base_URL}PartFilter',json=request_body,cookies=request.COOKIES)
                if(promoterResponse.status_code == 200):
                    promoter = promoterResponse.json()
                    return JsonResponse(promoter,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse({'success':False,'error':str(e)},status = 400, safe=False)
        elif(type == "backbone"):
            try:
                request_body = {'ori':data.get('Ori',""),'marker':data.get('Marker',""),'Enzyme':data.get('Enzyme',""),'Scar':data.get('Scar',""),'name':data.get("name",""),"page":page,"page_size":10}
                backboneResponse = session.post(f'{Base_URL}BackboneFilter',json=request_body,cookies=request.COOKIES)
                if(backboneResponse.status_code == 200):
                    backbone = backboneResponse.json()
                    print(backbone)
                    return JsonResponse(backbone,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse(str(e),status = 400, safe=False)
        elif(type == "plasmid"):
            try:
                request_body = {'ori':data.get('Ori',""),'marker':data.get('Marker',""),'Enzyme':data.get('Enzyme',""),'Scar':data.get('Scar',""),'name':data.get('name',""),'page':page,"page_size":10}
                plasmidResponse = session.post(f'{Base_URL}PlasmidFilter',json = request_body,cookies=request.COOKIES)
                if(plasmidResponse.status_code == 200):
                    plasmid = plasmidResponse.json()
                    return JsonResponse(plasmid,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse(str(e),status = 400, safe=False)

def UploadPartMap(request):
    if(request.method == 'POST' and request.FILES):
        # file = request.FILES.get('file')
        # title = request.POST.get('title', file.name)
        # thread = threading.Thread(
        #     target = process_excel_async,
        #     args= (file,request)
        # )
        # thread.daemon = True
        # thread.start()
        return JsonResponse(data={'success':True},status = 200, safe=False)
    else:
        return JsonResponse({'success':False,'message':'Upload record is empty'},status = 400, safe = False)
    

def UploadBackboneMap(request):
    pass

def UploadPlasmidMap(request):
    pass

def download_template(request,type):
    print(type)
    if(type == 'part'):
        template_path = r'C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\PartColumn.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='part_template.xlsx')
            return response
    elif(type == 'backbone'):
        template_path = r'C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\BackboneColumn.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='Backbone_template.xlsx')
            return response
    elif(type == 'plasmid'):
        template_path = r'C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\PlasmidColumn.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='plasmid_template.xlsx')
            return response
    elif(type == "assembly"):
        template_path = r'C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\AssemblyPlan.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='AssemblyPlan_template.xlsx')
            return response
    else:
        raise Http404('模板文件不存在')


"""
file_name: [filename, file_type]
"""
def process_map_async(upload_map, file_name, upload_type, django_request, task_id, index, number_of_task):
    try:
        Sequence = ""
        upload_map_temp = upload_map.read()
        upload_map.seek(0)
        if(file_name[1] == "dna"):
            print("file_name_dna")
            result = process_map_file(upload_map, file_name, upload_type,django_request,Base_URL)
        else:
            upload_map_temp = upload_map_temp.decode("utf-8")
            upload_map = io.StringIO(upload_map_temp)
            result = process_map_file(upload_map, file_name, upload_type,django_request,Base_URL)
        print(result)
        task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
        if(result):
            task_status_new = {
                'status':'processing',
                'progress':max(task_status['progress'], round((index+1)/number_of_task)*100),
                'result':None,
                'error':[]
            }
            # print(task_id)
            # print(task_status)
            cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status_new,timeout=3600)
        else:
            task_status_new = {
                'status':'processing',
                'progress':max(task_status['progress'], round((index+1)/number_of_task)*100),
                'result':None,
            }
            task_status_new['error'].append(f'{file_name} 上传失败')
            # print(task_id)
            # print(task_status)
            cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status_new,timeout=3600)
            print(task_status_new)
    except Exception as e:
        print(str(e))
        
                


def process_excel_async(upload_record,django_request,task_id):
    Error_rows = []
    Empty_sequence_rows = []
    try:
        task_status = {
            'status':'processing',
            'progress':10,
            'result':None,
            'error':[]
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        file_content = upload_record.read()
        excel_data = pd.read_excel(io.BytesIO(file_content))
        print(excel_data.columns)
        if(excel_data.columns.tolist()[0] == "PartName"):
            type = "part"
        elif(excel_data.columns.tolist()[0] == "BackboneName"):
            type = "backbone"
        elif(excel_data.columns.tolist()[0] == "PlasmidName"):
            type = "plasmid"
        print(type)
        result = ExcelProcessor.process_excel_file(django_request,excel_data,type,Base_URL)
        print(result)
        task_status['progress'] = 100
        task_status['status'] = 'completed'
        Error_rows = result['error_row']
        Empty_sequence_rows = result['empty_Seq_rows']
        if len(Error_rows) == 0 and len(Empty_sequence_rows) == 0:
            task_status['result'] = {
                'success':True,
                'message':"文件上传成功"
            }
        else:
            message = ""
            if(len(Error_rows) != 0):
                message += "上传出错的有以下：\n"+str(Error_rows)+"/n"
            if(len(Empty_sequence_rows) != 0):
                message += "需要补充序列有以下：\n"+str(Empty_sequence_rows)
            task_status['result'] = {
                'success':True,
                'message':message,
            }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        
        # print(Empty_sequence_rows)
    except Exception as e:
        task_status = {
            'status':'failed',
            'progress':100,
            'result':None,
            'error':str(e.args),
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)

    # ExcelProcessor.process_excel_file(upload_record)

def process_gg_assembly_async(upload_file, django_request, task_id):
    try:
        task_status = {
            'status':'processing',
            'progress':10,
            'result':None,
            'error':[]
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        file_content = upload_file.read()
        excel_data = pd.read_excel(io.BytesIO(file_content))
        
        result = GGAssembly.GGFileProcessor.createTemporaryRepo(django_request,excel_data,Base_URL)
        print(result)
        if(result['success']):
            if("error_row" not in result):
                task_status['progress'] = 100
                task_status['status'] = 'completed'
                task_status['result'] = {
                    'success':True,
                    'message':"文件上传成功"
                }
            else:
                task_status['progress'] = 100
                task_status['status'] = "completed"
                task_status['result'] = {
                    'success':True,
                    'message':result["error_row"]
                }
        else:
            message = ""
            task_status['status'] = "failed"
            task_status['error'] = result["error"]
            task_status['result'] = {
                'success':False,
                'message':"文件上传失败"
            }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        
        # print(Empty_sequence_rows)
    except Exception as e:
        task_status = {
            'status':'failed',
            'progress':100,
            'result':None,
            'error':str(e.args),
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)



def CreateTempRepository(request):
    print(request.FILES)
    if(request.method == "POST" and request.FILES):
        file = request.FILES.get('file')
        
        task_id = str(uuid.uuid4())
        task_status = {
            'status':'processing',
            'progress':0,
            'result':None,
            'error':None,
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        
        thread = threading.Thread(
            target=process_gg_assembly_async,
            args=(file, request, task_id)
        )
        thread.daemon = True
        thread.start()
        return JsonResponse({'task_id':task_id,'status':'processing','message':"文件上传成功，正在处理中..."},status = 200, safe = False)
    else:
        return JsonResponse({'success':False,'message':'方法不允许'},status = 405, safe = False)
    
    
@csrf_exempt
def UploadFile(request):
    print(request.FILES)
    if(request.method == 'POST' and request.FILES):
        file = request.FILES.get('file')
        title = request.POST.get('title', file.name)

        task_id = str(uuid.uuid4())
        # print(title)
        task_status = {
            'status':'processing',
            'progress':0,
            'result':None,
            'error':None,
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        thread = threading.Thread(
            target = process_excel_async,
            args= (file,request,task_id)
        )
        thread.daemon = True
        thread.start()
        return JsonResponse({'task_id':task_id,'status':'processing','message':"文件上传成功，正在处理中..."},status = 200, safe = False)
    #     print(len(Empty_sequence_rows))
    #     if(len(Error_rows) == 0 and len(Empty_sequence_rows) == 0):
    #         return JsonResponse(data={'success':True,'message':"文件上传成功"},status = 200, safe=False)
    #     else:
    #         message = ""
    #         if(len(Error_rows) != 0):
    #             message += "上传出错的行有以下：\n"+str(Error_rows)+"\n"
    #         if(len(Empty_sequence_rows) != 0):
    #             print("aaaaaaa")
    #             message += "需要补充序列的有以下：\n"+str(Empty_sequence_rows)
    #         return JsonResponse(data = {'success':True, 'message': message},status = 200, safe=False)
    else:
        return JsonResponse({'success':False,'message':'方法不允许'},status = 405, safe = False)
    
def task_status(request, task_id):
    task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    print(task_status)
    if(not task_status):
        return JsonResponse({'error':"任务不存在或已过期"},status=404)
    if(task_status['progress'] == 100 and task_status['status'] != "failed"):
        task_status['status'] = 'completed'
    response_data = {
        'task_id':task_id,
        'status':task_status['status'],
        'progress':task_status['progress'],
    }
    if task_status['status'] == 'completed':
        if(task_status['result'] != None):
            response_data.update(task_status['result'])
        if(task_status['error'] != None):
            response_data['error'] = task_status['error']
    elif task_status['status'] == 'failed':
        response_data['error'] = task_status['error']
        print(response_data)
    return JsonResponse(response_data)

def excel_task_status(request, task_id):
    task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    print(task_status)
    if(not task_status):
        return JsonResponse({'error':"任务不存在或已过期"},status=404)
    if(task_status['progress'] == 100 and task_status['status'] != "failed"):
        task_status['status'] = 'completed'
    if task_status['status'] == 'completed':
        if(os.path.exists(task_status['file_address'])):
            print("AAAAAAAAAAAAAAAAAAAAAAA")
            response_status = {
                "status" : "completed",
                "file_id" : task_status['file_id'],
            }
            return JsonResponse(response_status)
            # return FileResponse(open(task_status['file_address'],'rb'),as_attachment=True,filename=task_status['file_name'])
    elif task_status['status'] == 'failed':
        task_status['error'] = task_status['error']
    return JsonResponse(task_status)


# @csrf_exempt
def UploadMap(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')
        task_status = {
            'status':'processing',
            'progress':0,
            'result':None,
            'error':[],
        }
        task_id = str(uuid.uuid4())
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        # upload_map,file_name,upload_type,django_request, task_id
        
        # title = request.POST.get('title', file.name)
        pattern = r'^([^\_|.]+)'
        number_of_task = len(files)
        index = 0
        for each in files:
            suffix = each.name.split('.')[1]
            each_name = []
            match = re.match(pattern, each.name)
            each_name.append(match.group(1).strip())
            each_name.append(suffix)
            # print(title)
            type = request.POST.get('type')
            # print(file)
            # upload_map, file_name, upload_type, django_request, task_id, index, number_of_task
            thread = threading.Thread(
                target = process_map_async,
                args= (each,each_name,type,request,task_id,index,number_of_task)
            )
            thread.daemon = True
            thread.start()
            index+=1
        return JsonResponse({'task_id':task_id,'status':'processing','message':"文件上传成功，正在处理中..."},status = 200, safe = False)
    else:
        return JsonResponse({'success':False,'message':'Upload record is empty'})

def UploadBackboneFile(request):
    pass

def UploadPlasmidFile(request):
    pass

def part_detail_show(request,partid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        partResponse = session.get(f'{Base_URL}PartByID?ID={partid}',cookies=request.COOKIES)
        if(partResponse.status_code == 200):
            part = partResponse.json()[0]
            if(part['type'] == 1):
                part['type'] = "Promoter"
            elif(part['type'] == 2):
                part['type'] = "CDS"
            elif(part['type'] == 3):
                part['type'] = "Terminator"
            elif(part['type'] == 4):
                part['type'] = "RBS"
            elif(part['type'] == 5):
                part['type'] = "P+R"
            print(part)
            return render(request,'part.html',{'part':part})
        else:
            return render(request,'error.html',{'error':partResponse.text})

def backbone_detail_show(request,backboneid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        backboneResponse = session.get(f'{Base_URL}BackboneByID?ID={backboneid}',cookies=request.COOKIES)
        backbonescar = session.get(f"{Base_URL}getBackboneScar?id={backboneid}",cookies=request.COOKIES)
        if(backboneResponse.status_code == 200 and backbonescar.status_code == 200):
            backbone = backboneResponse.json()[0]
            backbone['ori'] = ", ".join(backbone['ori'])
            backbone['marker'] = ", ".join(backbone['marker'])
            print(backbone)
            print(backbonescar.json())
            if(backbonescar.json()['success']):
                scar_info = backbonescar.json()['scar_info'][0]
            else:
                scar_info = backbonescar.json()['error']
            return render(request,'backbone.html',{'backbone':backbone, "scar":scar_info})
        else:
            return render(request,'error.html',{'error':backboneResponse.text})

def plasmid_detail_show(request,plasmidid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        plasmidResponse = session.get(f'{Base_URL}PlasmidByID?ID={plasmidid}',cookies=request.COOKIES)
        plasmidScar = session.get(f'{Base_URL}getPlasmidScar?plasmidid={plasmidid}',cookies = request.COOKIES)
        # print(plasmidScar)
        # print(plasmidScar.json()["scar_info"][0])
        plasmidParentPart = session.get(f'{Base_URL}GetPartParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        plasmidParentBackbone = session.get(f'{Base_URL}GetBackboneParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        plasmidParentPlasmid = session.get(f'{Base_URL}GetPlasmidParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        plasmidSonPlasmid = session.get(f'{Base_URL}GetPlasmidSon?plasmidid={plasmidid}',cookies = request.COOKIES)

        if(plasmidResponse.status_code == 200 and plasmidParentPart.status_code == 200 and plasmidParentBackbone.status_code == 200 and
            plasmidParentPlasmid.status_code == 200 and plasmidSonPlasmid.status_code == 200 and plasmidScar.status_code == 200):
            plasmid = plasmidResponse.json()[0]
            plasmid["ori_info"] = ", ".join(plasmid["ori_info"])
            plasmid["marker_info"] = ", ".join(plasmid["marker_info"])
            result = {
                    'Part':[],
                    "Backbone":[],
                    "Plasmid":[],
                }
            if(plasmidScar.json()['success']):
                scar_info = plasmidScar.json()['scar_info'][0]
            else:
                scar_info = plasmidScar.json()['error']
            if(plasmid['customparentinformation'] != "" and plasmid['customparentinformation']!= None and plasmid['customparentinformation'] != 'None' and plasmid['customparentinformation'] != 'NULL'):
                plasmidParentInfo = plasmid['customparentinformation']
                pattern = r'(\w+)\(([ a-zA-z0-9]+)\)'
                matches = re.findall(pattern, plasmidParentInfo)
                print(result)
                for component_type, letter in matches:
                    if(component_type == "Part"):
                        result['Part'].append(letter)
                    elif(component_type == "Backbone"):
                        result['Backbone'].append(letter)
                    elif(component_type == "Plasmid"):
                        result['Plasmid'].append(letter)
            return render(request,'plasmid.html',{'plasmid':plasmid,'partparent':plasmidParentPart.json()['data'] if len(plasmidParentPart.json()['data']) >0 else [],'backboneparent':plasmidParentBackbone.json()['data'] if len(plasmidParentBackbone.json()['data']) > 0 else [],
                                    'plasmidparent':plasmidParentPlasmid.json()['data'] if len(plasmidParentPlasmid.json()['data']) > 0 else [],'plasmidson':plasmidSonPlasmid.json()['data'] if len(plasmidSonPlasmid.json()['data']) > 0 else [], 'ParentPartInfo':result["Part"],
                                    'ParentBackboneInfo':result['Backbone'],'ParentPlasmidInfo':result['Plasmid'],"scar":scar_info})
        else:
            return render(request,'error.html',{'error':plasmidResponse.text})

def downloadPartMap(request,partid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        sequence = (session.get(f'{Base_URL}GetPartSeqByID?partid={partid}',cookies = request.COOKIES)).json()['data']['level0sequence'].lower()
        print(sequence)
        seq_obj = Seq(sequence)
        seq_reverse = str(seq_obj.reverse_complement())
        fi = featureIdentify()
        feature_list = fi.featureMatch(sequence)
        reverse_feature_list = fi.featureMatch(seq_reverse)
        scar_list = scarPosition(sequence)
        sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'part-{partid}')
        file_address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\\"
        thread = threading.Thread(
            target = sa.GenerateGBKFile(),
            args= (file_address)
        )
        thread.daemon = True
        thread.start()
        # sa.GenerateGBKFile()
        map_path = rf'{file_address}\part-{partid}.gbk'
        if(os.path.exists(map_path)):
            response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'part-{partid}.gbk')
            return response
        else:
            return JsonResponse(data={'success':False,'data':'Generate fail'},status = 400, safe = False)

def downloadBackboneMap(request,backboneid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        sequence = (session.get(f'{Base_URL}GetBackboneSeqByID?backboneid={backboneid}',cookies = request.COOKIES)).json()['data']['sequence'].lower()
        seq_obj = Seq(sequence)
        seq_reverse = str(seq_obj.reverse_complement())
        fi = featureIdentify()
        feature_list = fi.featureMatch(sequence)
        reverse_feature_list = fi.featureMatch(seq_reverse)
        scar_list = scarPosition(sequence)
        sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'backbone-{backboneid}')
        file_address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\\"
        thread = threading.Thread(
            target = sa.GenerateGBKFile(),
            args= (file_address)
        )
        thread.daemon = True
        thread.start()
        # sa.GenerateGBKFile()
        map_path = rf'{file_address}backbone-{backboneid}.gbk'
        if(os.path.exists(map_path)):
            response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'backbone-{backboneid}.gbk')
            return response
        else:
            return JsonResponse(data={'success':False,'data':'Generate fail'},status = 400, safe = False)

def downloadPlasmidMap(request,plasmidid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        sequence = (session.get(f'{Base_URL}PlasmidSeqByID?plasmidid={plasmidid}',cookies = request.COOKIES)).json()['data']['sequenceconfirm'].lower()
        seq_obj = Seq(sequence)
        seq_reverse = str(seq_obj.reverse_complement())
        fi = featureIdentify()
        feature_list = fi.featureMatch(sequence)
        reverse_feature_list = fi.featureMatch(seq_reverse)
        scar_list = scarPosition(sequence)
        sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'plasmid-{plasmidid}')
        file_address = r'C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\\'
        thread = threading.Thread(
            target = sa.GenerateGBKFile(),
            args= (file_address)
        )
        thread.daemon = True
        thread.start()
        # sa.GenerateGBKFile()
        map_path = rf'{file_address}plasmid-{plasmidid}.gbk'
        if(os.path.exists(map_path)):
            response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'plasmid-{plasmidid}.gbk')
            return response
        else:
            return JsonResponse(data={'success':False,'data':'Generate fail'},status = 400, safe = False)

# def adminPage(request):
#     pass

def delete_part(request):
    if(request.method == "POST"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        partid = json.loads(request.body)["partid"]
        delete_part_response = session.get(f"{Base_URL}deletePart?partid={partid}", cookies = request.COOKIES)
        if(delete_part_response.status_code != 200):
            return JsonResponse(data = {"success":False, "message":delete_part_response.json()["message"]},status = 400, safe = False)
        else:
            return JsonResponse(data={"success":True},status = 200, safe=False)
    else:
        return JsonResponse(data = {"success":False, "message":"Just GET Method"}, status = 404, safe = False)

def delete_backbone(request):
    if(request.method == "POST"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        backboneid = json.loads(request.body)["backboneid"]
        delete_backbone_response = session.get(f"{Base_URL}deleteBackbone?backboneid={backboneid}", cookies = request.COOKIES)
        if(delete_backbone_response.status_code != 200):
            return JsonResponse(data = {"success":False, "message":delete_backbone_response.json()["message"]},status = 400, safe = False)
        else:
            return JsonResponse(data={"success":True},status = 200, safe=False)
    else:
        return JsonResponse(data = {"success":False, "message":"Just GET Method"}, status = 404, safe = False)


def delete_plasmid(request):
    if(request.method == "POST"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        plasmidid = json.loads(request.body)["Plasmidid"]
        # print(plasmidid)
        delete_plasmid_response = session.get(f"{Base_URL}deletePlasmid?plasmidid={plasmidid}", cookies=request.COOKIES)
        print(delete_plasmid_response.json())
        if(delete_plasmid_response.status_code != 200):
            return JsonResponse(data = {"success":False, "message":delete_plasmid_response.json()["message"]},status = 400, safe = False)
        else:
            return JsonResponse(data={"success":True},status = 200, safe=False)
    else:
        return JsonResponse(data = {"success":False, "message":"Just GET Method"}, status = 404, safe = False)

def exportuserdata(request,username):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        if(username != None and username != ""):
            excel_id = str(uuid.uuid4())
            excel_address = rf"{File_Address}{username}-{excel_id}.xlsx"
            task_status = {
                'status':'processing',
                'progress':0,
                'result':None,
                'error':[],
                'file_name':f"{username}-status.xlsx",
                'file_address':excel_address,
                'file_id':f"{username}-{excel_id}"
            }
            cache.set(f'{TASK_STATUS_PREFIX}{excel_id}',task_status,timeout=3600)
            thread = threading.Thread(
                target = exportuserdataprocess,
                args=(request, session, excel_id,username)
            )
            thread.daemon = True
            thread.start()
            return JsonResponse(data={'task_id':excel_id,'status':'processing','message':"任务已创建，结束后请在右侧弹窗获取文件"},status=200, safe = False)
        else:
            return JsonResponse(data={"success":False,"message":"parameter cannot be empty"}, status=400, safe=False)
    else:
        return JsonResponse(data={"success":False,"message":"Just GET method"}, status=400, safe=False)

            
            
        # if(os.path.exists(excel_address)):
        #     response = FileResponse(open(excel_address,'rb'),as_attachment=True,filename=f'{username}-stats.xlsx')
        #     return response
        # else:
        #     return JsonResponse(data={'success':False,'data':'Generate fail'},status = 400, safe = False)

def exportuserdataprocess(request,session,task_id,username):
    excel_address = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')['file_address']
            
    excel_part_data = {}
    part_field = (session.get(f"{Base_URL}partfields",cookies=request.COOKIES)).json()['data']
    print(part_field)
    for each_field in part_field:
        excel_part_data[each_field] = []
    part_result = session.get(f"{Base_URL}partlistbyuser/{username}", cookies=request.COOKIES)
    if(part_result.status_code == 200):
        part_data = part_result.json()['data']
        for each_data in part_data:
            for each_key in each_data.keys():
                excel_part_data[each_key].append(each_data[each_key])
    df_part = pd.DataFrame(excel_part_data)

    excel_backbone_data = {}
    backbone_field = (session.get(f"{Base_URL}backbonefields",cookies=request.COOKIES)).json()['data']
    print(backbone_field)
    for each_field in backbone_field:
        excel_backbone_data[each_field] = []
    backbone_result = session.get(f"{Base_URL}backbonelistbyuser/{username}", cookies=request.COOKIES)
    if(backbone_result.status_code == 200):
        backbone_data = backbone_result.json()['data']
        for each_data in backbone_data:
            for each_key in each_data.keys():
                excel_backbone_data[each_key].append(each_data[each_key])
    df_backbone = pd.DataFrame(excel_backbone_data)
            
            
    excel_plasmid_data = {}
    plasmid_field = (session.get(f"{Base_URL}plasmidfields",cookies=request.COOKIES)).json()['data']
    print(plasmid_field)
    for each_field in plasmid_field:
        excel_plasmid_data[each_field] = []
    plasmid_result = session.get(f"{Base_URL}plasmidlistbyuser/{username}", cookies=request.COOKIES)
    if(plasmid_result.status_code == 200):
        plasmid_data = plasmid_result.json()['data']
        for each_data in plasmid_data:
            for each_key in each_data.keys():
                excel_plasmid_data[each_key].append(each_data[each_key])
    df_plasmid = pd.DataFrame(excel_plasmid_data)
            
    with pd.ExcelWriter(excel_address, engine="openpyxl") as writer:
        df_part.to_excel(writer, sheet_name="part",index = False)
        
        df_backbone.to_excel(writer, sheet_name="backbone", index = False)
                
        df_plasmid.to_excel(writer, sheet_name="plasmid",index=False)
    
    task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    task_status["status"] = "completed"
    task_status["progress"] = 100
    cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    
    
def ExportAllData(request):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        excel_id = str(uuid.uuid4())
        excel_address = rf"{File_Address}{excel_id}.xlsx"
        task_status = {
                'status':'processing',
                'progress':0,
                'result':None,
                'error':[],
                'file_name':'stats.xlsx',
                'file_address':excel_address,
                'file_id':f"{excel_id}"
        }
        cache.set(f'{TASK_STATUS_PREFIX}{excel_id}',task_status,timeout=3600)
        print(cache.get(f'{TASK_STATUS_PREFIX}{excel_id}'))
        thread = threading.Thread(
            target = ExportAllDataProcess,
            args=(request, session, excel_id)
        )
        thread.daemon = True
        thread.start()
        
        return JsonResponse(data={'task_id':excel_id,'status':'processing','message':"任务已创建，结束后请在右侧弹窗获取文件"}, status=200, safe=False)
    else:
        return JsonResponse(data={'success':False,'message':"Just GET method"}, status=400, safe=False)

def ExportAllDataProcess(request, session, task_id):
    print(cache.get(f'{TASK_STATUS_PREFIX}{task_id}'))
    excel_address = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')['file_address']
    userlist = (session.get(f"{Base_URL}getuserlist",cookies=request.COOKIES)).json()['data']
    for each_user in userlist:
        print(each_user['uname'])
        excel_part_data = {}
        part_field = (session.get(f"{Base_URL}partfields",cookies=request.COOKIES)).json()['data']
        print(part_field)
        for each_field in part_field:
            excel_part_data[each_field] = []
        part_result = session.get(f"{Base_URL}partlistbyuser/{each_user['uname']}", cookies=request.COOKIES)
        if(part_result.status_code == 200):
            part_data = part_result.json()['data']
            for each_data in part_data:
                for each_key in each_data.keys():
                    excel_part_data[each_key].append(each_data[each_key])
        df_part = pd.DataFrame(excel_part_data)
            
            
        excel_backbone_data = {}
        backbone_field = (session.get(f"{Base_URL}backbonefields",cookies=request.COOKIES)).json()['data']
        print(backbone_field)
        for each_field in backbone_field:
            excel_backbone_data[each_field] = []
        backbone_result = session.get(f"{Base_URL}backbonelistbyuser/{each_user['uname']}", cookies=request.COOKIES)
        if(backbone_result.status_code == 200):
            backbone_data = backbone_result.json()['data']
            for each_data in backbone_data:
                for each_key in each_data.keys():
                    excel_backbone_data[each_key].append(each_data[each_key])
        df_backbone = pd.DataFrame(excel_backbone_data)
            
            
            
        excel_plasmid_data = {}
        plasmid_field = (session.get(f"{Base_URL}plasmidfields",cookies=request.COOKIES)).json()['data']
        print(plasmid_field)
        for each_field in plasmid_field:
            excel_plasmid_data[each_field] = []
        plasmid_result = session.get(f"{Base_URL}plasmidlistbyuser/{each_user['uname']}", cookies=request.COOKIES)
        if(plasmid_result.status_code == 200):
            plasmid_data = plasmid_result.json()['data']
            for each_data in plasmid_data:
                for each_key in each_data.keys():
                    excel_plasmid_data[each_key].append(each_data[each_key])
        df_plasmid = pd.DataFrame(excel_plasmid_data)
        
        if(os.path.exists(excel_address) == False):
            print("qqqqq")
            with pd.ExcelWriter(excel_address, engine="openpyxl") as writer:
                df_part.to_excel(writer, sheet_name=f"{each_user['uname']}(part)",index = False)
            
                df_backbone.to_excel(writer, sheet_name=f"{each_user['uname']}(backbone)", index = False)
            
                df_plasmid.to_excel(writer, sheet_name=f"{each_user['uname']}(plasmid)",index=False)
        else:
            with pd.ExcelWriter(excel_address, engine="openpyxl",mode='a',if_sheet_exists='replace') as writer:
                df_part.to_excel(writer, sheet_name=f"{each_user['uname']}(part)",index = False)
            
                df_backbone.to_excel(writer, sheet_name=f"{each_user['uname']}(backbone)", index = False)
            
                df_plasmid.to_excel(writer, sheet_name=f"{each_user['uname']}(plasmid)",index=False)
    task_status =cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    task_status['status'] = "completed"
    task_status['progress'] = 100
    cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status, timeout=3600)

def getDocument(request, fileid):
    if(request.method == "GET"):
        file_address = rf"{File_Address}{fileid}.xlsx"
        print(file_address)
        if(os.path.exists(file_address)):
            response = FileResponse(open(file_address,'rb'),as_attachment=True)
            return response
        else:
            return JsonResponse(data={"success":False},status=400, safe=False)

def getAssemblyFile(request, fileName):
    if(request.method == "GET"):
        file_address = os.path.join(Assembly_File_Address,f"{fileName}.gb")
        print(file_address)
        if(os.path.exists(file_address)):
            response = FileResponse(open(file_address,'rb'),as_attachment=True)
            return response
        else:
            return JsonResponse(data={"success":False},status=400, safe=False)


def AssemblyRepo(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        repositoryName = data['repositoryName']
        task_id = str(uuid.uuid4())
        task_status = {
            'status':'processing',
            'progress':0,
            'result':None,
            'error':None,
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=100000)
        thread = threading.Thread(
            target=process_assembly_repo,
            args=(repositoryName,request,task_id)
        )
        thread.daemon = True
        thread.start()
        return JsonResponse({"task_id":task_id,'status':'processing','message':"任务已创建，正在组装中"},status=200,safe=False)
    else:
        return JsonResponse({'success':False,'message':'方法不允许'},status = 405, safe = False)

def process_assembly_repo(repositoryName, django_request, task_id):
    session = requests.Session()
    session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
    })
    request_body = {"Name":repositoryName}
    try:
        repository_response = session.post(f"{Base_URL}getrepo",json=request_body,cookies=django_request.COOKIES)
    except Exception as e:
        print(repository_response.json())
    if(repository_response.status_code == 200):
        repository_data = repository_response.json()['data']
        part = repository_data['parts']
        backbone = repository_data['backbones']
        plasmid = repository_data['plasmids']
        file_address_list = []
        file_name_list = []
        for each_part in part:
            sequence = (session.get(f'{Base_URL}GetPartSeqByID?partid={each_part}',cookies = django_request.COOKIES)).json()['data']['level0sequence'].lower()
            partType = (session.get(f"{Base_URL}TypeByID?ID={each_part}", cookies=django_request.COOKIES)).json()['Type'].lower()
            partName = (session.get(f"{Base_URL}PartNameByID?ID={each_part}",cookies=django_request.COOKIES)).json()['PartName']
            print(partType)
            if(partType == "promoter"):
                sequence = "GGTCTCAGTGC" + sequence + "ATCAAGAGACC"
            elif(partType == "terminator"):
                sequence = "GGTCTCATAAA" + sequence + "CCTCAGAGACC"
            elif(partType == "cds"):
                sequence = "GGTCTCAAATG" + sequence + "TAAAAGAGACC"
            elif(partType == "rbs"):
                sequence = "GGTCTCAATCA" + sequence + "AATGAGAGACC"
            elif(partType == "p+r"):
                sequence = "GGTCTCAGTGC" + sequence + "AATGAGAGACC"
            print(sequence)
            seq_obj = Seq(sequence)
            seq_reverse = str(seq_obj.reverse_complement())
            fi = featureIdentify()
            feature_list = fi.featureMatch(sequence)
            reverse_feature_list = fi.featureMatch(seq_reverse)
            scar_list = scarPosition(sequence)
            sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'part-{partType}-{partName}')
            file_address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\AssemblyFile"
            sa.GenerateGBKFile(file_address)
            file_address_list.append(os.path.join(f"{file_address}",f"part-{partType}-{partName}.gbk"))
            file_name_list.append(f'part-{partType}-{partName}')
        for each_backbone in backbone:
            sequence = (session.get(f'{Base_URL}GetBackboneSeqByID?backboneid={each_backbone}',cookies = django_request.COOKIES)).json()['data']['sequence'].lower()
            backboneName = (session.get(f'{Base_URL}BackboneNameByID?ID={each_backbone}',cookies=django_request.COOKIES)).json()['BackboneName']
            print(sequence)
            seq_obj = Seq(sequence)
            seq_reverse = str(seq_obj.reverse_complement())
            fi = featureIdentify()
            feature_list = fi.featureMatch(sequence)
            reverse_feature_list = fi.featureMatch(seq_reverse)
            scar_list = scarPosition(sequence)
            sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'backbone-{backboneName}')
            file_address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\AssemblyFile"
            sa.GenerateGBKFile(file_address)
            file_address_list.append(os.path.join(f"{file_address}",f"backbone-{backboneName}.gbk"))
            file_name_list.append(f"backbone-{backboneName}")
        for each_plasmid in plasmid:
            plasmidName = (session.get(f'{Base_URL}PlasmidNameByID?ID={each_plasmid}',cookies=django_request.COOKIES)).json()['PlasmidName']
            if(os.path.exists(os.path.join(Assembly_File_Address,f"{plasmidName}.gb"))):
                file_address_list.append(os.path.join(Assembly_File_Address,f"{plasmidName}.gb"))
                file_name_list.append(plasmidName)
            else:
                sequence = (session.get(f'{Base_URL}PlasmidSeqByID?plasmidid={each_plasmid}',cookies = django_request.COOKIES)).json()['data']['sequenceconfirm'].lower()
                seq_obj = Seq(sequence)
                seq_reverse = str(seq_obj.reverse_complement())
                fi = featureIdentify()
                feature_list = fi.featureMatch(sequence)
                reverse_feature_list = fi.featureMatch(seq_reverse)
                scar_list = scarPosition(sequence)
                sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'plasmid-{plasmidName}')
                file_address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\AssemblyFile"
                sa.GenerateGBKFile(file_address)
                file_address_list.append(os.path.join(f"{file_address}",f"plasmid-{plasmidName}.gbk"))
                file_name_list.append(f"plasmid-{plasmidName}")
        print(file_address_list)
            
        GG = SupportGG.SupportGG(file_address_list,file_name_list)
        GG.assemblyPart(repositoryName)
        GG.show()
        print(os.path.join(Assembly_File_Address,f"{repositoryName}.gb"))
        if(os.path.exists(os.path.join(Assembly_File_Address,f"{repositoryName}.gb"))):
            records = parse(os.path.join(Assembly_File_Address,f"{repositoryName}.gb"), "genbank")
            for record in records:
                Sequence = str(record.seq)
            response = AssemblyResultUpload(django_request,repositoryName,Sequence,part,backbone,plasmid)
            print(response)
            if(response["success"]):
                task_status =cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
                task_status['status'] = "completed"
                task_status['progress'] = 100
                cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status, timeout=100000)
            else:
                task_status =cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
                task_status['status'] = "completed"
                task_status['progress'] = 100
                task_status['result'] = {"message":"添加质粒到数据库失败"}
                cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status, timeout=100000)
        else:
            task_status = {
                'status':'failed',
                'progress':0,
                'result':None,
                'error':"组装Scar错误",
            }
            cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=100000)
    else:
        task_status = {
            'status':'failed',
            'progress':0,
            'result':None,
            'error':"没有获取到仓库信息",
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=100000)


def AssemblyResultUpload(django_request,Name, Sequence, partList, BackboneList, PlasmidList):
    session = requests.Session()
    token = django_request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    if(len(PlasmidList) == 0):
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
    print(OriAndMarkerLabel)
    for each_ori in OriAndMarkerLabel['Origin']:
        Ori_list.append(each_ori['Name'])
    for each_marker in OriAndMarkerLabel['Marker']:
        Marker_list.append(each_marker['Name'])
    print(OriAndMarkerLabel)
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


def modify_part(request,partid):
    session = requests.Session()
    token = request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    
    if(request.method != "POST"):
        if(partid == None or partid == ""):
            return JsonResponse({"success":False,"message":"Parameter is empty"},status = 400, safe = False)
        part_obj = (session.get(f"{Base_URL}PartByID?ID={partid}",cookies=request.COOKIES).json())[0]
        return render(request,"PartEdit.html",{"part":part_obj})
    else:
        data = json.loads(request.body)
        if(data['elementType'].lower() == "promoter"):
            type = 1
        elif(data['elementType'].lower() == "rbs"):
            type = 4
        elif(data['elementType'].lower() == "terminator"):
            type = 3
        elif(data['elementType'].lower() == "cds"):
            type = 2
        elif(data['elementType'].lower() == "p+r"):
            type = 5
        request_body = {"PartID":partid,"Name":data['geneName'],"Alias":data['geneAlias'],"Type":type,"Level0Sequence":data['sequence'],
                        "ConfirmedSequence":"","InsertSequence":"","source":data["speciesSource"],"reference":data["references"],
                        "note":data["notes"]}
        part_update_response = (session.post(f'{Base_URL}UpdatePart',json=request_body,cookies=request.COOKIES))
        if(part_update_response.status_code != 200):
            print(part_update_response)
            return JsonResponse({"success":False,"message":part_update_response.json()},status = 400, safe=False)
        else:
            return JsonResponse({"success":True},status=200,safe=False)
def modify_backbone(request,backboneid):
    session = requests.Session()
    token = request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    if(request.method != "POST"):
        if(backboneid == None or backboneid == ""):
            return JsonResponse({"success":False,"message":"Parameter cannot be empty"}, status = 400, safe=False)
        Backbone_obj = (session.get(f"{Base_URL}BackboneByID?ID={backboneid}",cookies=request.COOKIES).json())[0]
        backbonescar = session.get(f"{Base_URL}getBackboneScar?id={backboneid}",cookies=request.COOKIES)
        if(backbonescar.json()['success']):
            print(backbonescar.json())
            Backbone_obj['scar_info'] = backbonescar.json()['scar_info'][0]
        print(Backbone_obj)
        return render(request,"BackboneEdit.html",{"backbone":Backbone_obj})
    else:
        data = json.loads(request.body)
        print(data)
        request_body = {"BackboneID":data['vectorId'],"newName":data['vectorName'],"sequence":data['sequence'],"species":data['host'],"copynumber":data['copyNumber'],"note":data['notes'],"alias":data['vectorAlias'],"tag":"abnormal" if (len(data['ori']) > 1 or len(data['marker']) > 1) else "normal"}
        
        update_backbone_response = session.post(f"{Base_URL}UpdateBackbone",json=request_body,cookies = request.COOKIES)
        update_backbone_culture_response = session.post(f"{Base_URL}setBackboneCulture",json={"id":data["vectorId"],"ori":data['ori'],"marker":data['marker']},cookies=request.COOKIES)
        update_backbone_scar_response = session.post(f"{Base_URL}setBackboneScar",json={"backboneid":data['vectorId'],'bsmbi':data['scarSites']['BsmBI'],'bsai':data['scarSites']['BsaI'],
                                                                                        'bbsi':data['scarSites']['BbsI'],'aari':data['scarSites']['Aari'],'sapi':data['scarSites']['Sapi']},cookies=request.COOKIES)
        if(update_backbone_response.status_code == 200 and update_backbone_culture_response.status_code == 200 and update_backbone_scar_response.status_code == 200):
            return JsonResponse({"success":True},status = 200, safe=False)
        else:
            return JsonResponse({"success":False,"message":"更新失败"},status=400,safe=False)
        
def modify_plasmid(request,plasmidid):
    session = requests.Session()
    token = request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    if(request.method != "POST"):
        if(plasmidid == None or plasmidid == ""):
            return JsonResponse({"success":False,"message":"Parameter cannot be empty"}, status = 400, safe=False)
        Plasmid_obj = (session.get(f"{Base_URL}PlasmidByID?ID={plasmidid}",cookies=request.COOKIES).json())[0]
        plasmidscar = session.get(f"{Base_URL}getPlasmidScar?plasmidid={plasmidid}",cookies=request.COOKIES)
        if(plasmidscar.json()['success']):
            print(plasmidscar.json())
            Plasmid_obj['scar_info'] = plasmidscar.json()['scar_info'][0]
        
        plasmidParentPart = session.get(f'{Base_URL}GetPartParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        plasmidParentBackbone = session.get(f'{Base_URL}GetBackboneParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        plasmidParentPlasmid = session.get(f'{Base_URL}GetPlasmidParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        
        result = {
                    'Part':[],
                    "Backbone":[],
                    "Plasmid":[],
                }
        if(plasmidParentPart.status_code == 200):
            for each_Part in plasmidParentPart.json()['data']:
                result['Part'].append(each_Part["name"])
        if(plasmidParentBackbone.status_code == 200):
            for each_Backbone in plasmidParentBackbone.json()['data']:
                result['Backbone'].append(each_Backbone["name"])
        if(plasmidParentPlasmid.status_code == 200):
            for each_Plasmid in plasmidParentPlasmid.json()['data']:
                result['Plasmid'].append(each_Plasmid["name"])
        if(Plasmid_obj['customparentinformation'] != "" and Plasmid_obj['customparentinformation']!= None and Plasmid_obj['customparentinformation'] != 'None' and Plasmid_obj['customparentinformation'] != 'NULL' and Plasmid_obj['customparentinformation'] != 'nan'):
            plasmidParentInfo = Plasmid_obj['customparentinformation']
            pattern = r'(\w+)\(([ a-zA-z0-9]+)\)'
            matches = re.findall(pattern, plasmidParentInfo)
            print(result)
            for component_type, letter in matches:
                if(component_type == "Part"):
                    result['Part'].append(letter)
                elif(component_type == "Backbone"):
                    result['Backbone'].append(letter)
                elif(component_type == "Plasmid"):
                    result['Plasmid'].append(letter)
        return render(request,'PlasmidEdit.html',{'plasmid':Plasmid_obj,'partparent':result['Part'],'backboneparent':result['Backbone'],
                                    'plasmidparent':result['Plasmid']})
    else:
        data = json.loads(request.body)
        print(data)
        # UpdatePlasmid
        request_body = {"id":data['plasmidId'],"newName":data['plasmidName'],"newAlias":data["plasmidAlias"],"newLevel":data['level'],"newSequence":data['sequence'],"newOri":data['ori'],"newMarker":data['marker'],"newNote":data['notes'],"tag":"abnormal" if (len(data['ori']) > 1 or len(data['marker']) > 1) else "normal"}
        
        update_plasmid_response = session.post(f"{Base_URL}UpdatePlasmid",json=request_body,cookies=request.COOKIES)
        
        
        
        update_plasmid_scar_response = session.post(f"{Base_URL}setPlasmidScar",json={"plasmidid":plasmidid,'bsmbi':data['scarSites']['BsmBI'],'bsai':data['scarSites']['BsaI'],
                                                                                        'bbsi':data['scarSites']['BbsI'],'aari':data['scarSites']['Aari'],'sapi':data['scarSites']['Sapi']},cookies=request.COOKIES)
        delete_parent = session.get(f"{Base_URL}DeletePlasmidParent?plasmidid={plasmidid}",cookies=request.COOKIES)
        if(delete_parent.status_code ==200):
            customParentInfo = ""
            for each_part in data['parentPart']:
                addPartResponse = session.post(f"{Base_URL}AddPartParent",json={"SonPlasmidId":plasmidid,"ParentPartName":each_part},cookies=request.COOKIES)
                if(addPartResponse.status_code != 200):
                    customParentInfo += f"Part({each_part})"
            for each_backbone in data['parentBackbone']:
                addBackboneResponse = session.post(f"{Base_URL}AddBackboneParent",json={"SonPlasmidId":plasmidid,"ParentBackboneName":each_backbone},cookies=request.COOKIES)
                if(addBackboneResponse.status_code != 200):
                    customParentInfo += f"Backbone({each_part})"
            for each_plasmid in data['parentPlasmid']:
                addPlasmidResponse = session.post(f"{Base_URL}AddPlasmidParent",json={"SonPlasmidId":plasmidid,"ParentPlasmidName":each_plasmid},cookies=request.COOKIES)
                if(addPlasmidResponse.status_code != 200):
                    customParentInfo += f"Plasmid({each_part})"
            if(customParentInfo != ""):
                request_body = {"PlasmidID":plasmidid,"PlasmidParentInfo":customParentInfo}
                session.post(f'{Base_URL}UpdateParentInfo',json=request_body,cookies=request.COOKIES)
        
        if(update_plasmid_response.status_code == 200 and update_plasmid_scar_response.status_code == 200):
            return JsonResponse({"success":True},status = 200, safe=False)
        else:
            return JsonResponse({"success":False,"message":"更新失败"},status=400,safe=False)

def GetExperienceDetail(request, partName):
    session = requests.session()
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
    })
    response = session.get(f"{Exp_URL}/api/part/view?filter=name={partName}")
    print(response.json())
    ID = response.json()['parts'][0]['ID']
    return redirect(f"{Exp_URL}/part/{ID}")