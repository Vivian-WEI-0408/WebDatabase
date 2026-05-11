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
from LabDatabase.genbank_format_checker import process_uploaded_genbank
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
from .CaculateModule.ScarIdentify import scarPosition,scarFunction,scarIdentSitePosition
from .CaculateModule.snapgene_reader import snapgene_to_dict
from .ControllerModule import FittingLabels
from .CaculateModule.KmerIndex import KmerIndex
# from GGModule import SupportGG
from .GGModule import SupportGG
from Bio.SeqIO import parse
import queue
import shutil
from django.utils import timezone


import uuid
from .design_engine import (
    create_design_repository,
    get_design_form_context,
    recommend_design,
    search_gene_candidates,
)


TEXT_MAP_FILE_TYPES = {"fasta", "gb", "gbk", "ape", "str"}
BINARY_MAP_FILE_TYPES = {"dna"}
TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "gb18030", "gbk", "latin-1")

Base_URL = "http://10.30.76.2:8080/WebDatabase/"
Exp_URL = "http://10.30.76.75:8009/"
# File_Address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\\"
Assembly_File_Address = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\output"
TASK_STATUS_PREFIX = 'file_task_'
TASK_STATUS_LOCK = threading.Lock()
CUSTOM_SCAR_LOCK = threading.Lock()
CUSTOM_SCAR_FILE = os.path.join(settings.BASE_DIR, "LabDatabase", "static", "LabDatabase", "CustomScarInfo.txt")
ASSEMBLY_DIR = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile\AssemblyFile\\"
GENBANK_FIXED_OUTPUT_DIR = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\GenerateFile"
DOWNLOAD_FILE_ADDRESS = r"C:\Users\admin\Desktop\WebDatabase\WebDataWorld\LabDatabase\static\LabDatabase\DownloadFile\\"


def _sanitize_assembly_name(name):
    text = str(name or "").strip()
    if not text:
        return "unnamed"
    invalid_chars = '\\/:*?"<>|'
    sanitized = "".join("_" if char in invalid_chars else char for char in text)
    sanitized = sanitized.rstrip(". ")
    return sanitized or "unnamed"


def _assembly_file_basename(name):
    return _sanitize_assembly_name(name)


def _assembly_file_path(name):
    return os.path.join(ASSEMBLY_DIR, f"{_assembly_file_basename(name)}.gbk")


def _get_task_output_dir(task_id):
    return os.path.join(Assembly_File_Address, str(task_id))


def _ensure_task_output_dir(task_id):
    task_output_dir = _get_task_output_dir(task_id)
    os.makedirs(task_output_dir, exist_ok=True)
    return task_output_dir


def _get_task_assembly_file(task_id, file_name):
    return os.path.join(_get_task_output_dir(task_id), f"{file_name}.gb")


def _looks_like_binary(content: bytes) -> bool:
    if not content:
        return False
    if b"\x00" in content:
        return True

    sample = content[:1024]
    text_bytes = set(range(32, 127)) | {9, 10, 13}
    non_text_count = sum(1 for byte in sample if byte not in text_bytes)
    return non_text_count / max(len(sample), 1) > 0.30


def _decode_uploaded_text(content: bytes) -> str:
    last_error = None
    for encoding in TEXT_ENCODINGS:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc

    if last_error is not None:
        raise ValueError(
            "Unable to detect uploaded file encoding. Please save the file as UTF-8, GBK, or GB18030 and try again."
        ) from last_error
    raise ValueError("Uploaded file is empty or cannot be decoded.")


def _build_map_file_object(file_content: bytes, file_type: str):
    file_type = (file_type or "").lower()

    if file_type in BINARY_MAP_FILE_TYPES:
        return io.BytesIO(file_content)

    if file_type in TEXT_MAP_FILE_TYPES:
        if _looks_like_binary(file_content):
            raise ValueError(f".{file_type} file looks like binary content and cannot be parsed as text.")
        return io.StringIO(_decode_uploaded_text(file_content))

    if _looks_like_binary(file_content):
        return io.BytesIO(file_content)
    return io.StringIO(_decode_uploaded_text(file_content))
# class User_auth(MiddlewareMixin):

#     def process_request(self,request):
#         #閹烘帡娅庢稉宥夋付鐟曚胶娅ヨぐ鏇炴皑閼冲€燁問闂傤喚娈戞い鐢告桨
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
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        print(request.session.get('info'))
        print(request.user)
        try:
            username = request.user.uname
            userid = request.user.uid
            user_repository_count = session.get(f"{Base_URL}getrepocountbyuser/{userid}",cookies=request.COOKIES).json()['count']
            user_part_count = session.get(f"{Base_URL}getuserpartcount/{username}",cookies=request.COOKIES).json()['count']
            user_backbone_count = session.get(f"{Base_URL}getuserbackbonecount/{username}",cookies=request.COOKIES).json()['count']
            user_plasmid_count = session.get(f"{Base_URL}getuserplasmidcount/{username}",cookies=request.COOKIES).json()['count']
            user_info = {}
            user_info['repoCount'] = user_repository_count
            user_info['partCount'] = user_part_count
            user_info['backboneCount'] = user_backbone_count
            user_info['plasmidCount'] = user_plasmid_count
            return render(request,'index.html',{"user":request.user,"user_info":user_info})
        except AttributeError as e:
            return redirect("/WebDatabase/login")


def _load_custom_scar_records():
    if not os.path.exists(CUSTOM_SCAR_FILE):
        return []

    records = []
    with open(CUSTOM_SCAR_FILE, "r", encoding="utf-8") as file_obj:
        for line in file_obj:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def CustomScar(request):
    if request.method == "GET":
        try:
            with CUSTOM_SCAR_LOCK:
                records = _load_custom_scar_records()
            return JsonResponse({"success": True, "data": records}, status=200, safe=False)
        except Exception as exc:
            return JsonResponse({"success": False, "message": str(exc)}, status=400, safe=False)

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Just GET or POST method"}, status=405, safe=False)

    try:
        if request.content_type and "application/json" in request.content_type:
            request_data = json.loads(request.body.decode("utf-8") or "{}")
        else:
            request_data = request.POST

        scar_name = str(request_data.get("scar_name") or request_data.get("name") or "").strip()
        scar_sequence = str(request_data.get("scar_sequence") or request_data.get("sequence") or "").strip().upper()
        scar_description = str(request_data.get("scar_description") or request_data.get("description") or "").strip()
        scar_sequence = re.sub(r"\s+", "", scar_sequence)

        if not scar_name:
            return JsonResponse({"success": False, "message": "scar_name cannot be empty"}, status=400, safe=False)
        if not scar_sequence:
            return JsonResponse({"success": False, "message": "scar_sequence cannot be empty"}, status=400, safe=False)
        if not re.fullmatch(r"[ACGTRYSWKMBDHVN]+", scar_sequence):
            return JsonResponse({"success": False, "message": "scar_sequence contains invalid base characters"}, status=400, safe=False)

        username = getattr(request.user, "username", "") or getattr(request.user, "uname", "")
        record = {
            "scar_name": scar_name,
            "scar_sequence": scar_sequence,
            "scar_description": scar_description,
            "created_by": username,
            "created_at": timezone.now().isoformat(),
        }

        os.makedirs(os.path.dirname(CUSTOM_SCAR_FILE), exist_ok=True)
        with CUSTOM_SCAR_LOCK:
            records = _load_custom_scar_records()
            if any(item.get("scar_name", "").lower() == scar_name.lower() for item in records):
                return JsonResponse({"success": False, "message": "scar_name already exists"}, status=409, safe=False)
            with open(CUSTOM_SCAR_FILE, "a", encoding="utf-8") as file_obj:
                file_obj.write(json.dumps(record, ensure_ascii=False) + "\n")

        return JsonResponse({"success": True, "data": record}, status=200, safe=False)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON format"}, status=400, safe=False)
    except Exception as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=400, safe=False)


def design_builder(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Just GET method"}, status=405)
    context = get_design_form_context()
    context["user"] = request.user
    return render(request, "design_builder.html", context)


def design_gene_search(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Just GET method"}, status=405)

    query = request.GET.get("q", "")
    genes = search_gene_candidates(query)
    return JsonResponse({"success": True, "data": genes}, status=200)


def submit_design_assembly(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Just POST method"}, status=405)

    try:
        payload = json.loads(request.body)
        design_result = recommend_design(payload)
        repository = create_design_repository(request, design_result)

        task_id = str(uuid.uuid4())
        cache.set(
            f"{TASK_STATUS_PREFIX}{task_id}",
            {"status": "processing", "progress": 0, "result": None, "error": None},
            timeout=100000,
        )

        thread = threading.Thread(
            target=process_assembly_repo,
            args=(repository.name, request, task_id),
        )
        thread.daemon = False
        thread.start()

        return JsonResponse(
            {
                "success": True,
                "task_id": task_id,
                "repository_name": repository.name,
                "selected_parts": design_result["selected_parts"],
                "selected_backbone": design_result["selected_backbone"],
                "strengths": design_result["strengths"],
                "message": "仓库创建成功",
            },
            status=200,
        )
    except ValueError as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=500)
    
    
    
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
        type = data.get("SearchType")
        page = data.get("page",1)
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
                    # print(backbone)
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
    # print(type)
    if(type == 'part'):
        template_path = f'{DOWNLOAD_FILE_ADDRESS}PartColumn.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='part_template.xlsx')
            return response
    elif(type == 'backbone'):
        template_path = f'{DOWNLOAD_FILE_ADDRESS}BackboneColumn.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='Backbone_template.xlsx')
            return response
    elif(type == 'plasmid'):
        template_path = f'{DOWNLOAD_FILE_ADDRESS}\PlasmidColumn.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='plasmid_template.xlsx')
            return response
    elif(type == "assembly"):
        template_path = f'{DOWNLOAD_FILE_ADDRESS}\AssemblyPlan.xlsx'
        if(os.path.exists(template_path)):
            response = FileResponse(open(template_path,'rb'),as_attachment=True,filename='AssemblyPlan_template.xlsx')
            return response
    else:
        raise Http404('Template file not found.')


"""
file_name: [filename, file_type]
"""
def process_map_async(upload_map, file_name, upload_type, django_request, task_id, index, number_of_task, save_feature=False):
    result = False
    task_error = None
    try:
        upload_map_temp = upload_map.read()
        upload_map.seek(0)
        try:
            file_obj = _build_map_file_object(upload_map_temp, file_name[1])
            result = process_map_file(file_obj, file_name, upload_type, django_request, Base_URL, save_feature=save_feature)
        except ValueError as e:
            task_error = f"{file_name[0]} upload failed: {str(e)}"
        except Exception as e:
            task_error = f"{file_name[0]} upload failed"
        if(not result and task_error is None):
            task_error = f"{file_name[0]} upload failed"
    except Exception as e:
        task_error = f"{file_name[0]} upload failed"

    with TASK_STATUS_LOCK:
        task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}') or {
            'status':'processing',
            'progress':0,
            'result':None,
            'error':[],
            'processed_count':0,
            'total_count':number_of_task,
        }
        if(task_status.get('error') is None):
            task_status['error'] = []
        if(task_error is not None):
            task_status['error'].append(task_error)

        processed_count = task_status.get('processed_count', 0) + 1
        total_count = task_status.get('total_count', number_of_task)
        progress = int(processed_count * 100 / max(total_count, 1))

        task_status_new = {
            'status':'completed' if processed_count >= total_count else 'processing',
            'progress':progress,
            'result':task_status.get('result'),
            'error':task_status['error'],
            'processed_count':processed_count,
            'total_count':total_count,
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status_new,timeout=3600)

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
        # print(result)
        if(result["success"]):
            task_status['progress'] = 100
            task_status['status'] = 'completed'
            Error_rows = result['error_row']
            Empty_sequence_rows = result['empty_Seq_rows']
            if len(Error_rows) == 0 and len(Empty_sequence_rows) == 0:
                task_status['result'] = {
                    'success':True,
                    'message':"涓婁紶鎴愬姛"
                }
            else:
                message = ""
                if(len(Error_rows) != 0):
                    message += "涓婁紶澶辫触鐨勮濡備笅锛歕n" + str(Error_rows) + "\n"
                if(len(Empty_sequence_rows) != 0):
                    message += "搴忓垪涓虹┖鐨勮濡備笅锛歕n" + str(Empty_sequence_rows)
                task_status['result'] = {
                    'success':True,
                    'message':message,
                }
        else:
            task_status['progress'] = 0
            task_status['status'] = 'failed'
            task_status['error'] = result['error']
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
        if 'Assembly' in excel_data.columns and 'AssemblyName' not in excel_data.columns:
            excel_data = excel_data.rename(columns={'Assembly':'AssemblyName'})
        if 'Level' not in excel_data.columns:
            task_status['status'] = 'failed'
            task_status['progress'] = 100
            task_status['error'] = 'Excel is missing the Level column.'
            task_status['result'] = {
                'success':False,
                'message':'Excel is missing the Level column.'
            }
            cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
            return

        excel_data = excel_data.copy()
        excel_data['Level'] = excel_data['Level'].apply(
            lambda value: str(value).strip().replace('.0', '') if pd.notna(value) else ''
        )
        completed_assemblies = []
        failed_assemblies = {}
        total_assemblies = sum(
            1 for name in excel_data.get('AssemblyName', pd.Series(dtype=object)).tolist()
            if str(name).strip()
        )
        if total_assemblies == 0:
            task_status['status'] = 'failed'
            task_status['progress'] = 100
            task_status['error'] = '组装文件为空'
            task_status['result'] = {
                'success':False,
                'message':'组装文件为空'
            }
            cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
            return

        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })

        for level_index, level_value in enumerate(['1', '2', '3'], start=1):
            level_data = excel_data[excel_data['Level'] == level_value].copy()
            if level_data.empty:
                continue

            result = GGAssembly.GGFileProcessor.createTemporaryRepo(
                django_request,
                level_data,
                Base_URL,
            )
            if not result['success']:
                task_status['status'] = 'failed'
                task_status['progress'] = 100
                task_status['error'] = result['error']
                task_status['result'] = {
                    'success':False,
                    'message':'仓库创建失败'
                }
                cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
                return
            if 'error_row' in result:
                task_status['progress'] = 100
                task_status['status'] = 'completed'
                task_status['result'] = {
                    'success':True,
                    'message':result['error_row']
                }
                cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
                return

            assembly_names = [
                str(name).strip()
                for name in level_data.get('AssemblyName', pd.Series(dtype=object)).dropna().tolist()
                if str(name).strip()
            ]
            empty_repositories = []
            assembly_queue = queue.Queue()
            for assembly_name in assembly_names:
                repository_response = session.post(
                    f"{Base_URL}getrepo",
                    json={'Name':assembly_name},
                    cookies=django_request.COOKIES
                )
                if repository_response.status_code != 200:
                    failed_assemblies[assembly_name] = '获取仓库失败'
                    continue
                repository_data = repository_response.json().get('data', {})
                if (
                    repository_data.get('total_parts', 0) == 0 and
                    repository_data.get('total_plasmids', 0) == 0 and
                    repository_data.get('total_backbones', 0) == 0
                ):
                    empty_repositories.append(assembly_name)
                    continue
                assembly_queue.put(assembly_name)

            if empty_repositories:
                task_status['status'] = 'failed'
                task_status['progress'] = 100
                task_status['error'] = f"空仓库: {', '.join(empty_repositories)}"
                task_status['result'] = {
                    'success':False,
                    'message':f"空仓库: {', '.join(empty_repositories)}"
                }
                cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
                return

            while not assembly_queue.empty():
                queue_size = assembly_queue.qsize()
                completed_this_round = 0
                for _ in range(queue_size):
                    assembly_name = assembly_queue.get()
                    current_task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}', task_status)
                    current_task_status['status'] = 'processing'
                    current_task_status['progress'] = 10 + int((len(completed_assemblies) / max(total_assemblies, 1)) * 80)
                    current_task_status['result'] = {
                        'completed': completed_assemblies,
                        'current': assembly_name,
                        'current_level': level_value,
                        'queue': list(assembly_queue.queue),
                        'levels': {
                            'current': level_value,
                            'step': f'{level_index}/3',
                        },
                    }
                    cache.set(f'{TASK_STATUS_PREFIX}{task_id}',current_task_status,timeout=3600)

                    try:
                        process_assembly_repo(assembly_name, django_request, task_id)
                        current_task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}', {})
                    except Exception as e:
                        current_task_status = {'status':'failed','error':str(e.args)}
                    if current_task_status.get('status') == 'completed':
                        completed_assemblies.append(assembly_name)
                        failed_assemblies.pop(assembly_name, None)
                        completed_this_round += 1
                    else:
                        failed_assemblies[assembly_name] = current_task_status.get('error') or 'assembly failed'
                        assembly_queue.put(assembly_name)

                if completed_this_round == 0 and not assembly_queue.empty():
                    task_status = {
                        'status':'failed',
                        'progress':100,
                        'result':{
                            'completed': completed_assemblies,
                            'pending': list(assembly_queue.queue),
                            'current_level': level_value,
                        },
                        'error': failed_assemblies,
                    }
                    cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
                    return

        task_status['progress'] = 100
        task_status['status'] = 'completed'
        task_status['result'] = {
            'success':True,
            'message':'涓婁紶鎴愬姛',
            'completed': completed_assemblies,
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    except Exception as e:
        task_status = {
            'status':'failed',
            'progress':100,
            'result':None,
            'error':str(e.args),
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)



def CreateTempRepository(request):
    # print(request.FILES)
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
        thread.daemon = False
        thread.start()
        return JsonResponse({'task_id':task_id,'status':'processing','message':"上传成功，数据分析中"},status = 200, safe = False)
    else:
        return JsonResponse({'success':False,'message':'上传失败'},status = 405, safe = False)
    
    
@csrf_exempt
def UploadFile(request):
    # print(request.FILES)
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
        thread.daemon = False
        thread.start()
        return JsonResponse({'task_id':task_id,'status':'processing','message':"上传成功，数据处理中"},status = 200, safe = False)
    #     print(len(Empty_sequence_rows))
    #     if(len(Error_rows) == 0 and len(Empty_sequence_rows) == 0):
    #         return JsonResponse(data={'success':True,'message':"閺傚洣娆㈡稉濠佺炊閹存劕濮?},status = 200, safe=False)
    #     else:
    #         message = ""
    #         if(len(Error_rows) != 0):
    #             message += "娑撳﹣绱堕崙娲晩閻ㄥ嫯顢戦張澶変簰娑撳绱癨n"+str(Error_rows)+"\n"
    #         if(len(Empty_sequence_rows) != 0):
    #             print("aaaaaaa")
    #             message += "闂団偓鐟曚浇藟閸忓懎绨崚妤冩畱閺堝浜掓稉瀣剁窗\n"+str(Empty_sequence_rows)
    #         return JsonResponse(data = {'success':True, 'message': message},status = 200, safe=False)
    else:
        return JsonResponse({'success':False,'message':'上传失败'},status = 405, safe = False)
    
def task_status(request, task_id):
    task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    print(task_status)
    if(not task_status):
        return JsonResponse({
            'task_id':task_id,
            'status':'failed',
            'progress':0,
            'error':"Task does not exist or has expired."
        },status=404)

    if(task_status['progress'] == 100 and task_status['status'] != "failed"):
        task_status['status'] = 'completed'
    response_data = {
        'task_id':task_id,
        'status':task_status['status'],
        'progress':task_status['progress'],
    }
    if task_status['status'] == 'completed':
        if(task_status['result'] != None):
            response_data['result']=task_status['result']
        if(task_status['error'] != None):
            response_data['error'] = task_status['error']
    elif task_status['status'] == 'failed':
        response_data['error'] = task_status['error']
        # print(response_data)
    return JsonResponse(response_data)

def excel_task_status(request, task_id):
    task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    # print(task_status)
    if(not task_status):
        return JsonResponse({'error':"Task does not exist or has expired."},status=404)
    if(task_status['progress'] == 100 and task_status['status'] != "failed"):
        task_status['status'] = 'completed'
    if task_status['status'] == 'completed':
        if(os.path.exists(task_status['file_address'])):
            # print("AAAAAAAAAAAAAAAAAAAAAAA")
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
        number_of_task = len(files)
        task_status = {
            'status':'processing',
            'progress':0,
            'result':None,
            'error':[],
            'processed_count':0,
            'total_count':number_of_task,
        }
        task_id = str(uuid.uuid4())
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
        # upload_map,file_name,upload_type,django_request, task_id
        
        # title = request.POST.get('title', file.name)
        pattern = r'^([^\_|.]+)'
        # print(number_of_task)
        index = 0
        save_feature = str(request.POST.get('save_feature', 'false')).lower() in ['true', '1', 'yes', 'on']
        for each in files:
            # print(each)
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
                args= (each,each_name,type,request,task_id,index,number_of_task,save_feature)
            )
            thread.daemon = False
            thread.start()
            index+=1
        return JsonResponse({'task_id':task_id,'status':'processing','message':"上传成功，数据处理中"},status = 200, safe = False)
    else:
        return JsonResponse({'success':False,'message':'Upload record is empty'})


@csrf_exempt
def CheckAndFixGenBank(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST method is allowed"}, status=405, safe=False)

    upload_file = request.FILES.get("file")
    if upload_file is None:
        return JsonResponse({"success": False, "message": "file is required"}, status=400, safe=False)

    try:
        result = process_uploaded_genbank(upload_file)
        fixed_text = result["fixed_bytes"].decode(result["encoding"], errors="replace")

        upload_name = os.path.basename(getattr(upload_file, "name", "uploaded"))
        upload_base = os.path.splitext(upload_name)[0].strip()
        if not upload_base:
            upload_base = "uploaded"
        safe_base = re.sub(r'[\\/:*?"<>|]+', "_", upload_base)
        save_name = f"{safe_base}.gb"

        os.makedirs(GENBANK_FIXED_OUTPUT_DIR, exist_ok=True)
        save_path = os.path.join(GENBANK_FIXED_OUTPUT_DIR, save_name)

        with open(save_path, "wb") as f:
            f.write(result["fixed_bytes"])

        response = {
            "success": True,
            "changed": result["changed"],
            "issue_count": len(result["issues"]),
            "issues": result["issues"],
            "fixed_filename": save_name,
            "fixed_content": fixed_text,
            "file_path": save_path,
        }
        return JsonResponse(response, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500, safe=False)



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
            # print(part)
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
            # print(backbone)
            # print(backbonescar.json())
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
                # print(result)
                for component_type, letter in matches:
                    if(component_type == "Part"):
                        result['Part'].append(letter)
                    elif(component_type == "Backbone"):
                        result['Backbone'].append(letter)
                    elif(component_type == "Plasmid"):
                        result['Plasmid'].append(letter)
            return render(request,'plasmid.html',{'plasmid':plasmid,'partparent':plasmidParentPart.json()['data'] if (plasmidParentPart.json()["success"] and len(plasmidParentPart.json()['data']) >0) else [],'backboneparent':plasmidParentBackbone.json()['data'] if (plasmidParentBackbone.json()["success"] and len(plasmidParentBackbone.json()['data']) > 0) else [],
                                    'plasmidparent':plasmidParentPlasmid.json()['data'] if (plasmidParentPlasmid.json()["success"] and len(plasmidParentPlasmid.json()['data']) > 0) else [],'plasmidson':plasmidSonPlasmid.json()['data'] if (plasmidSonPlasmid.json()["success"] and len(plasmidSonPlasmid.json()['data']) > 0) else [], 'ParentPartInfo':result["Part"],
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
        name = (session.get(f"{Base_URL}PartNameByID?ID={partid}",cookies=request.COOKIES)).json()['PartName']
        alias = (session.get(f"{Base_URL}PartAliasByID?ID={partid}",cookies=request.COOKIES)).json()['PartAlias']
        if(os.path.exists(os.path.join(ASSEMBLY_DIR,f'part-{partid}-{name}-{alias}.gbk'))):
            response = FileResponse(open(os.path.join(ASSEMBLY_DIR,f'part-{partid}-{name}-{alias}.gbk'),'rb'),as_attachment=True,filename=f'part-{partid}-{name}-{alias}.gbk')
            return response
        type = (session.get(f"{Base_URL}TypeByID?ID={partid}",cookies=request.COOKIES)).json()['Type'].lower()
        part_feature_response = session.get(f"{Base_URL}GetPartFeature/{partid}", cookies=request.COOKIES).json()
        map_path = rf'{ASSEMBLY_DIR}\part-{partid}-{name}-{alias}.gbk'
        if(part_feature_response.get("success") and part_feature_response.get("data")):
            try:
                thread = threading.Thread(
                    target = SequenceAnnotator.GeneratorPartNoSa,
                    args = (f'part-{partid}-{name}-{alias}',sequence,ASSEMBLY_DIR,part_feature_response['data'])
                )
                thread.daemon = False
                thread.start()
                start_time = time.time()
                max_wait_time = 5
                while time.time() - start_time < max_wait_time:
                    if(os.path.exists(map_path) and os.stat(map_path).st_size != 0):
                        response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'part-{partid}-{name}-{alias}.gbk')
                        return response
                    time.sleep(1)
            except Exception:
                pass
        # print(sequence)
        seq_obj = Seq(sequence)
        seq_reverse = str(seq_obj.reverse_complement())
        fi = featureIdentify()
        feature_list = fi.featureMatch(sequence)
        reverse_feature_list = fi.featureMatch(seq_reverse)
        scar_list = scarPosition(sequence)
        sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'part-{partid}-{name}-{alias}')
        thread = threading.Thread(
            target = sa.GenerateGBKFile,
            args= (ASSEMBLY_DIR,type)
        )
        thread.daemon = False
        thread.start()
        # sa.GenerateGBKFile()
        max_wait_time = 5
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            if(os.path.exists(map_path) and os.stat(map_path).st_size != 0):
                response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'part-{partid}-{name}-{alias}.gbk')
                return response
            else:
                time.sleep(1)
                continue
        return JsonResponse(data={'success':False,'data':'Generate fail'},status = 400, safe = False)

def downloadBackboneMap(request,backboneid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        sequence = (session.get(f'{Base_URL}GetBackboneSeqByID?backboneid={backboneid}',cookies = request.COOKIES)).json()['data']['sequence'].lower()
        name = (session.get(f"{Base_URL}BackboneNameByID?ID={backboneid}",cookies=request.COOKIES)).json()['BackboneName']
        alias = (session.get(f"{Base_URL}BackboneAliasByID?ID={backboneid}",cookies=request.COOKIES)).json()['BackboneAlias']
        backboneFeature = (session.get(f"{Base_URL}GetBackboneFeature/{backboneid}",cookies=request.COOKIES)).json()
        if(os.path.exists(os.path.join(ASSEMBLY_DIR,f"backbone-{backboneid}-{name}-{alias}.gbk"))):
            response = FileResponse(open(os.path.join(ASSEMBLY_DIR,f"backbone-{backboneid}-{name}-{alias}.gbk"),'rb'),as_attachment=True,filename=f'backbone-{backboneid}-{name}-{alias}.gbk')
            return response

        if(backboneFeature["success"] != True):
            seq_obj = Seq(sequence)
            seq_reverse = str(seq_obj.reverse_complement())
            fi = featureIdentify()
            feature_list = fi.featureMatch(sequence)
            reverse_feature_list = fi.featureMatch(seq_reverse)
            scar_list = scarPosition(sequence)
            sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'backbone-{backboneid}-{name}-{alias}')
            thread = threading.Thread(
                target = sa.GenerateGBKFile,
                args= (ASSEMBLY_DIR,)
            )
            thread.daemon = False
            thread.start()
        else:
            thread = threading.Thread(
                target = SequenceAnnotator.GeneratorBackboneNoSa,
                args = (f'backbone-{backboneid}-{name}-{alias}',sequence,ASSEMBLY_DIR,backboneFeature['data'])
            )
            thread.daemon = False
            thread.start()
            # sa.GenerateGBKFile()
        map_path = rf'{ASSEMBLY_DIR}backbone-{backboneid}-{name}-{alias}.gbk'
        start_time = time.time()
        max_wait_time = 5
        while time.time() - start_time < max_wait_time:
            if(os.path.exists(map_path) and os.stat(map_path).st_size != 0):
                response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'backbone-{backboneid}-{name}-{alias}.gbk')
                return response
            else:
                time.sleep(1)
                continue
            
        return JsonResponse(data={'success':False,'data':'Generate fail'},status = 400, safe = False)

def downloadPlasmidMap(request,plasmidid):
    if(request.method == "GET"):
        session = requests.Session()
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
        })
        
        sequence = (session.get(f'{Base_URL}PlasmidSeqByID?plasmidid={plasmidid}',cookies = request.COOKIES)).json()['data']['sequenceconfirm'].lower()
        name = (session.get(f"{Base_URL}PlasmidNameByID?ID={plasmidid}",cookies=request.COOKIES)).json()["PlasmidName"]
        alias = (session.get(f"{Base_URL}PlasmidAliasByID?ID={plasmidid}",cookies=request.COOKIES)).json()["PlasmidAlias"]
        if(os.path.exists(os.path.join(ASSEMBLY_DIR,f"{name}.gbk"))):
            response = FileResponse(open(os.path.join(ASSEMBLY_DIR,f"{name}.gbk"),'rb'),as_attachment=True,filename=f'plasmid-{plasmidid}-{name}-{alias}.gbk')
            return response
        elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"plasmid-{plasmidid}-{name}-{alias}.gbk"))):
            response = FileResponse(open(os.path.join(ASSEMBLY_DIR,f"plasmid-{plasmidid}-{name}-{alias}.gbk"),'rb'),as_attachment=True,filename=f'plasmid-{plasmidid}-{name}-{alias}.gbk')
            return response
        plasmid_feature_response = session.get(f"{Base_URL}GetPlasmidFeature/{plasmidid}", cookies=request.COOKIES).json()
        map_path = rf'{ASSEMBLY_DIR}plasmid-{plasmidid}-{name}-{alias}.gbk'
        if(plasmid_feature_response.get("success") and plasmid_feature_response.get("data")):
            try:
                thread = threading.Thread(
                    target = SequenceAnnotator.GeneratorBackboneNoSa,
                    args = (f'plasmid-{plasmidid}-{name}-{alias}',sequence,ASSEMBLY_DIR,plasmid_feature_response['data'])
                )
                thread.daemon = False
                thread.start()
                start_time = time.time()
                max_wait_time = 5
                while time.time() - start_time < max_wait_time:
                    if(os.path.exists(map_path) and os.stat(map_path).st_size != 0):
                        response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'plasmid-{plasmidid}-{name}-{alias}.gbk')
                        return response
                    time.sleep(1)
            except Exception:
                pass
        seq_obj = Seq(sequence)
        
        scar_list = scarPosition(sequence)
        seq_reverse = str(seq_obj.reverse_complement())
        PlasmidParentBackboneResponse = (session.get(f"{Base_URL}GetBackboneParent?plasmidid={plasmidid}",cookies=request.COOKIES)).json()
        sa = SequenceAnnotator(sequence,{},{},scar_list,name=f'plasmid-{plasmidid}-{name}-{alias}')
        if(PlasmidParentBackboneResponse['success']):
            PlasmidParentBackbone = PlasmidParentBackboneResponse['data'][0]['id']
            ParentBackboneSequenceResponse = (session.get(f"{Base_URL}GetBackboneSeqByID?backboneid={PlasmidParentBackbone}", cookies=request.COOKIES)).json()
            if(ParentBackboneSequenceResponse['success']):
                ParentBackboneSequence = ParentBackboneSequenceResponse['data']['sequence']
                BackboneFeatureListResponse = (session.get(f"{Base_URL}GetBackboneFeature/{PlasmidParentBackbone}", cookies=request.COOKIES)).json()
                if(BackboneFeatureListResponse['success']):
                    backbone_fetch_kmer = KmerIndex()
                    for each_feature in BackboneFeatureListResponse['data']:
                        if(each_feature['feature_start']<each_feature['feature_end']):
                            backbone_fetch_kmer.add_sequence(each_feature["feature_label"],ParentBackboneSequence[each_feature["feature_start"]:each_feature["feature_end"]])
                        else:
                            backbone_fetch_kmer.add_sequence(each_feature["feature_label"],ParentBackboneSequence[each_feature["feature_start"]:]+ParentBackboneSequence[:each_feature["feature_end"]])
                    fetch_result = backbone_fetch_kmer.query(sequence)
                    for each_key in fetch_result.keys():
                        for each_feature in BackboneFeatureListResponse['data']:
                            if(each_feature["feature_label"] == fetch_result[each_key]["seq_id"]):
                                type = each_feature["feature_type"]
                                color = each_feature["feature_color"] if each_feature["feature_color"] != "" else each_feature["feature_apeinfo"]
                                print(color)
                                break
                        new_feature = {fetch_result[each_key]["seq_id"]:[fetch_result[each_key]["start"],fetch_result[each_key]['end'],type,color]}
                        sa.add_feature(new_feature)
                else:
                    fi = featureIdentify()
                    feature_list = fi.featureMatch(sequence)
                    reverse_feature_list = fi.featureMatch(seq_reverse)
                    sa.add_features(feature_list)
                    sa.add_reverse_features(reverse_feature_list)
                    # sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=f'plasmid-{plasmidid}')
        # PlasmidParentPartResponse = (session.get(f"{Base_URL}GetPartParent?plasmidid={plasmidid}",cookies=request.COOKIES)).json()
        # Part_fetch_kmer = KmerIndex()
        # if(PlasmidParentPartResponse['success']):
        #     PlasmidParentPart = PlasmidParentPartResponse['data']
        #     print(PlasmidParentPart)
        #     for each_part in PlasmidParentPart:
        #         partSeqResponse = (session.get(f"{Base_URL}GetPartSeqByID?partid={each_part['partid']}",cookies=request.COOKIES)).json()
        #         if(partSeqResponse['success']):
        #             partSeq = partSeqResponse['data']['level0sequence']
        #             part_reverse_Seq = str(Seq(partSeq).reverse_complement())
        #             Part_fetch_kmer.add_sequence(each_part['name'],partSeq)
        #             Part_fetch_kmer.add_sequence(each_part['name']+"'",part_reverse_Seq)
        #     fetch_result = Part_fetch_kmer.query(sequence)
        #     for each_key in fetch_result:
        #         if(each_key[-1] == "'"):
        #             each_key_temp = each_key[:-1]
        #             typeResponse = (session.get(f"{Base_URL}TypeByName?name={each_key_temp}",cookies=request.COOKIES))
        #         else:
        #             typeResponse = (session.get(f"{Base_URL}TypeByName?name={each_key}",cookies=request.COOKIES))
        #         if(typeResponse.status_code == 200):
        #             type = typeResponse.json()['Type'].lower()
        #             if(each_key[-1] == "'"):
        #                 new_feature = {each_key[:-1]:[fetch_result[each_key]['start'],fetch_result[each_key]['end'],type]}
        #             else:
        #                 new_feature = {each_key:[fetch_result[each_key]['start'],fetch_result[each_key]['end'],type]}
        #             sa.add_feature(new_feature)
        PlasmidParentPlasmidResponse = (session.get(f"{Base_URL}GetPlasmidParent?plasmidid={plasmidid}",cookies=request.COOKIES)).json()
        plasmid_fetch_kmer = KmerIndex()
        plasmid_parent_kmer = KmerIndex()
        if(PlasmidParentPlasmidResponse['success']):
            PlasmidParentPlasmid = PlasmidParentPlasmidResponse['data']
            for each_plasmid in PlasmidParentPlasmid:
                ParentPlasmidSequence = (session.get(f'{Base_URL}PlasmidSeqByID?plasmidid={each_plasmid["plasmidid"]}',cookies = request.COOKIES)).json()['data']['sequenceconfirm'].lower()
                plasmid_parent_kmer.add_sequence(each_plasmid["name"],ParentPlasmidSequence)
                plasmid_parent_kmer.add_sequence(each_plasmid["name"]+"'",str(Seq(ParentPlasmidSequence).reverse_complement()))
            plasmid_parent_fetch_result = plasmid_parent_kmer.query(sequence)
            for each_key in plasmid_parent_fetch_result.keys():
                if(each_key[-1] == "'"):
                    new_feature = {each_key[:-1]:[plasmid_parent_fetch_result[each_key]["start"],plasmid_parent_fetch_result[each_key]["end"],""]}
                else:
                    new_feature = {each_key:[plasmid_parent_fetch_result[each_key]["start"],plasmid_parent_fetch_result[each_key]["end"],""]}
                sa.add_feature(new_feature)
            ParentPartList = getplasmidAllParentPart(request,session,PlasmidParentPlasmid)
            for each_part in ParentPartList.keys():
                plasmid_fetch_kmer.add_sequence(each_part,ParentPartList[each_part])
                plasmid_fetch_kmer.add_sequence(each_part+"'",str(Seq(ParentPartList[each_part]).reverse_complement()))
            fetch_result = plasmid_fetch_kmer.query(sequence)
            fetch_result = Remove_duplicated_Part(fetch_result)
            # print(fetch_result)
            for each_key in fetch_result.keys():
                if(each_key[-1] == "'"):
                    each_key_temp = each_key[:-1]
                    typeResponse = (session.get(f"{Base_URL}TypeByName?name={each_key_temp}",cookies=request.COOKIES))
                else:
                    typeResponse = (session.get(f"{Base_URL}TypeByName?name={each_key}",cookies=request.COOKIES))
                if(typeResponse.status_code == 200):
                    type = typeResponse.json()['Type'].lower()
                    if(each_key[-1] == "'"):
                        new_feature = {each_key[:-1]:[fetch_result[each_key]["start"],fetch_result[each_key]["end"],type]}
                    else:
                        new_feature = {each_key:[fetch_result[each_key]["start"],fetch_result[each_key]["end"],type]}
                    sa.add_feature(new_feature)
        
        if(PlasmidParentBackboneResponse["success"] == False or PlasmidParentPlasmidResponse["success"] == False):
            fi = featureIdentify()
            feature_list = fi.featureMatch(sequence)
            reverse_feature_list = fi.featureMatch(seq_reverse)
            sa.add_features(feature_list)
            sa.add_reverse_features(reverse_feature_list)
        
        
        print(sa.feature_list)
        thread = threading.Thread(
            target = sa.GenerateGBKFile,
            args= (ASSEMBLY_DIR,)
        )
        thread.daemon = False
        thread.start()
        # sa.GenerateGBKFile()
        max_wait_time = 5
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            if(os.path.exists(map_path) and os.stat(map_path).st_size != 0):
                response = FileResponse(open(map_path,'rb'),as_attachment=True,filename=f'plasmid-{plasmidid}-{name}-{alias}.gbk')
                return response
            else:
                time.sleep(1)
                continue
        return JsonResponse(data={'success':False,'data':'Generate fail'},status = 400, safe = False)

def Remove_duplicated_Part(fetch_result):
    fetch_result_keys = list(fetch_result.keys())
    for each_key in fetch_result_keys:
        try:
            if(each_key[-1] == "'" and fetch_result[each_key[:-1]] != None):
                density_reverse = fetch_result[each_key]["density"]
                density = fetch_result[each_key[:-1]]["density"]
                if(density_reverse >= density):
                    fetch_result.pop(each_key[:-1],None)
                else:
                    fetch_result.pop(each_key,None)
            else:
                density_reverse = fetch_result[each_key+"'"]["density"]
                density = fetch_result[each_key]["density"]
                if(density_reverse >= density):
                    fetch_result.pop(each_key,None)
                else:
                    fetch_result.pop(each_key+"'",None)
        except KeyError:
            continue
    return fetch_result
            

def getplasmidAllParentPart(django_request, session, PlasmidParentPlasmid):
    ParentPartList = {}
    PlasmidParentPlasmidQueue = queue.Queue()
    for each_plasmid in PlasmidParentPlasmid:
        PlasmidParentPlasmidQueue.put(each_plasmid['plasmidid'])
    while not PlasmidParentPlasmidQueue.empty():
        plasmidid = PlasmidParentPlasmidQueue.get()
        ParentPartResponse = (session.get(f"{Base_URL}GetPartParent?plasmidid={plasmidid}",cookies = django_request.COOKIES)).json()
        if(ParentPartResponse['success']):
            for each_part in ParentPartResponse['data']:
                partSeqResponse = (session.get(f"{Base_URL}GetPartSeqByID?partid={each_part['partid']}",cookies=django_request.COOKIES)).json()
                if(partSeqResponse['success']):
                    partSeq = partSeqResponse['data']['level0sequence'].lower()
                    ParentPartList[each_part['name']] = partSeq
        ParentPlasmidResponse = (session.get(f"{Base_URL}GetPlasmidParent?plasmidid={plasmidid}",cookies=django_request.COOKIES)).json()
        if(ParentPlasmidResponse['success']):
            for each_plasmid in ParentPlasmidResponse['data']:
                PlasmidParentPlasmidQueue.put(each_plasmid['plasmidid'])
    return ParentPartList
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
        print(delete_backbone_response.json())
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
        delete_plasmid_response = session.get(f"{Base_URL}deletePlasmid?plasmidid={plasmidid}", cookies=request.COOKIES)
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
            excel_address = rf"{GENBANK_FIXED_OUTPUT_DIR}{username}-{excel_id}.xlsx"
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
            thread.daemon = False
            thread.start()
            return JsonResponse(data={'task_id':excel_id,'status':'processing','message':"Export task created. Please download the result file later."},status=200, safe = False)
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
        excel_address = rf"{GENBANK_FIXED_OUTPUT_DIR}{excel_id}.xlsx"
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
        thread = threading.Thread(
            target = ExportAllDataProcess,
            args=(request, session, excel_id)
        )
        thread.daemon = False
        thread.start()
        
        return JsonResponse(data={'task_id':excel_id,'status':'processing','message':"Export task created. Please download the result file later."}, status=200, safe=False)
    else:
        return JsonResponse(data={'success':False,'message':"Just GET method"}, status=400, safe=False)

def ExportAllDataProcess(request, session, task_id):
    excel_address = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')['file_address']
    userlist = (session.get(f"{Base_URL}getuserlist",cookies=request.COOKIES)).json()['data']
    for each_user in userlist:
        excel_part_data = {}
        part_field = (session.get(f"{Base_URL}partfields",cookies=request.COOKIES)).json()['data']
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
        file_address = rf"{GENBANK_FIXED_OUTPUT_DIR}{fileid}.xlsx"
        if(os.path.exists(file_address)):
            response = FileResponse(open(file_address,'rb'),as_attachment=True)
            return response
        else:
            return JsonResponse(data={"success":False},status=400, safe=False)


def getDocumentByAddress(request):
    if(request.method == "GET"):
        file_address = request.GET.get("address")
        if(os.path.exists(file_address)):
            response = FileResponse(open(file_address,'rb'),as_attachment=True)
            return response
        else:
            return JsonResponse(data={"success":False},status=400,safe=False)


def getAssemblyFile(request, fileName):
    if(request.method == "GET"):
        task_id = request.GET.get("task_id")
        if task_id:
            file_address = _get_task_assembly_file(task_id, fileName)
        else:
            file_address = os.path.join(Assembly_File_Address,f"{fileName}.gb")
        if(os.path.exists(file_address)):
            copy_address = os.path.join(ASSEMBLY_DIR,f"{fileName}.gbk")
            shutil.copy(file_address,copy_address)
            response = FileResponse(open(file_address,'rb'),as_attachment=True)
            return response
        else:
            return JsonResponse(data={"success":False},status=400, safe=False)


def _create_api_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
    })
    return session


def _determine_target_enzyme(sequence):
    ccdb_sequence = "ggcttactaaaagccagataacagtatgcatatttgcgcgctgatttttgcggtataagaatatatactgatatgtatacccgaagtatgtcaaaaagaggtatgctatgaagcagcgtattacagtgacagttgacagcgacagctatcagttgctcaaggcatatatgatgtcaatatctccggtctggtaagcacaaccatgcagaatgaagcccgtcgtctgcgtgccgaacgctggaaagcggaaaatcaggaagggatggctgaggtcgcccggtttattgaaatgaacggctcttttgctgacgagaacaggggctggtgaaatgcagtttaaggtttacacctataaaagagagagccgttatcgtctgtttgtggatgtacagagtgatattattgacacgcccgggcgacggatggtgatccccctggccagtgcacgtctgctgtcagataaagtctcccgtgaactttacccggtggtgcatatcggggatgaaagctggcgcatgatgaccaccgatatggccagtgtgccggtttccgttatcggggaagaagtggctgatctcagccaccgcgaaaatgacatcaaaaacgccattaacctgatgttctggggaatataa"
    ccdb_reverse_sequence = "ttatattccccagaacatcaggttaatggcgtttttgatgtcattttcgcggtggctgagatcagccacttcttccccgataacggaaaccggcacactggccatatcggtggtcatcatgcgccagctttcatccccgatatgcaccaccgggtaaagttcacgggagactttatctgacagcagacgtgcactggccagggggatcaccatccgtcgcccgggcgtgtcaataatatcactctgtacatccacaaacagacgataacggctctctcttttataggtgtaaaccttaaactgcatttcaccagcccctgttctcgtcagcaaaagagccgttcatttcaataaaccgggcgacctcagccatcccttcctgattttccgctttccagcgttcggcacgcagacgacgggcttcattctgcatggttgtgcttaccagaccggagatattgacatcatatatgccttgagcaactgatagctgtcgctgtcaactgtcactgtaatacgctgcttcatagcatacctctttttgacatacttcgggtatacatatcagtatatattcttataccgcaaaaatcagcgcgcaaatatgcatactgttatctggcttttagtaagcc"
    ccdb_fi = KmerIndex()
    ccdb_fi.add_sequence("ccdb", ccdb_sequence)
    ccdb_fi.add_sequence("ccdb1", ccdb_reverse_sequence)
    ccdb_position = ccdb_fi.query(sequence)
    scar_ident_list = scarIdentSitePosition(sequence)
    if "ccdb" in ccdb_position.keys():
        ccdb_start_position = ccdb_position["ccdb"]["start"]
        ccdb_end_position = ccdb_position["ccdb"]["end"]
    elif "ccdb1" in ccdb_position.keys():
        ccdb_start_position = ccdb_position["ccdb1"]["start"]
        ccdb_end_position = ccdb_position["ccdb1"]["end"]
    else:
        return ""
    min_difference = 222222
    target_enzyme = ""
    for each_scar in scar_ident_list:
        scar_name = list(each_scar.keys())[0]
        scar_position = each_scar[scar_name]["index"]
        if(len(scar_position) >= 2):
            ccdb_min_position = min(ccdb_start_position, ccdb_end_position)
            ccdb_max_position = max(ccdb_start_position, ccdb_end_position)
            scar_min_position = min(scar_position[0], scar_position[1])
            scar_max_position = max(scar_position[0], scar_position[1])
            if(abs(ccdb_min_position-scar_min_position) + abs(ccdb_max_position - scar_max_position) < min_difference):
                min_difference = abs(ccdb_min_position-scar_min_position) + abs(ccdb_max_position - scar_max_position)
                target_enzyme = scar_name
    return target_enzyme


def _generate_plasmid_map_from_parents(session, django_request, plasmid_id, sequence, output_name):
    scar_list = scarPosition(sequence)
    seq_reverse = str(Seq(sequence).reverse_complement())
    PlasmidParentBackboneResponse = (session.get(f"{Base_URL}GetBackboneParent?plasmidid={plasmid_id}",cookies=django_request.COOKIES)).json()
    sa = SequenceAnnotator(sequence,{},{},scar_list,name=output_name)
    if(PlasmidParentBackboneResponse['success']):
        PlasmidParentBackbone = PlasmidParentBackboneResponse['data'][0]['id']
        ParentBackboneSequenceResponse = (session.get(f"{Base_URL}GetBackboneSeqByID?backboneid={PlasmidParentBackbone}", cookies=django_request.COOKIES)).json()
        if(ParentBackboneSequenceResponse['success']):
            ParentBackboneSequence = ParentBackboneSequenceResponse['data']['sequence']
            BackboneFeatureListResponse = (session.get(f"{Base_URL}GetBackboneFeature/{PlasmidParentBackbone}", cookies=django_request.COOKIES)).json()
            if(BackboneFeatureListResponse['success']):
                backbone_fetch_kmer = KmerIndex()
                for each_feature in BackboneFeatureListResponse['data']:
                    if(each_feature['feature_start']<each_feature['feature_end']):
                        backbone_fetch_kmer.add_sequence(each_feature["feature_label"],ParentBackboneSequence[each_feature["feature_start"]:each_feature["feature_end"]])
                    else:
                        backbone_fetch_kmer.add_sequence(each_feature["feature_label"],ParentBackboneSequence[each_feature["feature_start"]:]+ParentBackboneSequence[:each_feature["feature_end"]])
                fetch_result = backbone_fetch_kmer.query(sequence)
                for each_key in fetch_result.keys():
                    for each_feature in BackboneFeatureListResponse['data']:
                        if(each_feature["feature_label"] == fetch_result[each_key]["seq_id"]):
                            feature_type = each_feature["feature_type"]
                            break
                    new_feature = {fetch_result[each_key]["seq_id"]:[fetch_result[each_key]["start"],fetch_result[each_key]['end'],feature_type]}
                    sa.add_feature(new_feature)
            else:
                fi = featureIdentify()
                feature_list = fi.featureMatch(sequence)
                reverse_feature_list = fi.featureMatch(seq_reverse)
                sa.add_features(feature_list)
                sa.add_reverse_features(reverse_feature_list)
    PlasmidParentPartResponse = (session.get(f"{Base_URL}GetPartParent?plasmidid={plasmid_id}",cookies=django_request.COOKIES)).json()
    Part_fetch_kmer = KmerIndex()
    if(PlasmidParentPartResponse['success']):
        PlasmidParentPart = PlasmidParentPartResponse['data']
        for each_part in PlasmidParentPart:
            partSeqResponse = (session.get(f"{Base_URL}GetPartSeqByID?partid={each_part['partid']}",cookies=django_request.COOKIES)).json()
            if(partSeqResponse['success']):
                partSeq = partSeqResponse['data']['level0sequence']
                Part_fetch_kmer.add_sequence(each_part['name'],partSeq)
        fetch_result = Part_fetch_kmer.query(sequence)
        for each_key in fetch_result:
            typeResponse = (session.get(f"{Base_URL}TypeByName?name={each_key}",cookies=django_request.COOKIES))
            if(typeResponse.status_code == 200):
                feature_type = typeResponse.json()['Type'].lower()
                new_feature = {each_key:[fetch_result[each_key]['start'],fetch_result[each_key]['end'],feature_type]}
                sa.add_feature(new_feature)
    PlasmidParentPlasmidResponse = (session.get(f"{Base_URL}GetPlasmidParent?plasmidid={plasmid_id}",cookies=django_request.COOKIES)).json()
    plasmid_fetch_kmer = KmerIndex()
    if(PlasmidParentPlasmidResponse['success']):
        PlasmidParentPlasmid = PlasmidParentPlasmidResponse['data']
        ParentPartList = getplasmidAllParentPart(django_request,session,PlasmidParentPlasmid)
        for each_part in ParentPartList.keys():
            plasmid_fetch_kmer.add_sequence(each_part,ParentPartList[each_part])
        fetch_result = plasmid_fetch_kmer.query(sequence)
        for each_key in fetch_result.keys():
            typeResponse = (session.get(f"{Base_URL}TypeByName?name={each_key}",cookies=django_request.COOKIES))
            if(typeResponse.status_code == 200):
                feature_type = typeResponse.json()['Type'].lower()
                new_feature = {each_key:[fetch_result[each_key]["start"],fetch_result[each_key]["end"],feature_type]}
                sa.add_feature(new_feature)
    if(PlasmidParentBackboneResponse["success"] == False or PlasmidParentPlasmidResponse["success"] == False):
        fi = featureIdentify()
        feature_list = fi.featureMatch(sequence)
        reverse_feature_list = fi.featureMatch(seq_reverse)
        sa.add_features(feature_list)
        sa.add_reverse_features(reverse_feature_list)
    sa.GenerateGBKFile(ASSEMBLY_DIR)


def _run_assembly_simulation(file_address_list, file_name_list, assembly_name, task_output_dir, task_id):
    task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    task_status["status"] = "processing"
    task_status['progress'] = 50
    cache.set(f"{TASK_STATUS_PREFIX}{task_id}",task_status)
    GG = SupportGG.SupportGG(file_address_list,file_name_list)
    GG.assemblyPart(assembly_name)
    GG.show(output_dir=task_output_dir)


def _finalize_assembly_result(django_request, task_id, assembly_result_file, final_name, part, backbone, plasmid, alias="", Note="", Level=None):
    max_wait_time = 20
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        if(os.path.exists(assembly_result_file)):
            records = parse(assembly_result_file, "genbank")
            for record in records:
                Sequence = str(record.seq)
            response = AssemblyResultUpload(django_request, final_name[:20], Sequence, part, backbone, plasmid, alias, Note, Level)
            if(response["success"]):
                task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
                task_status["status"] = "completed"
                task_status['progress'] = 100
                task_status["result"] = {
                    "task_id": task_id,
                    "file_name": final_name,
                    "file_path": assembly_result_file,
                    "download_url": f"/LabDatabase/getAssembly/{final_name}?task_id={task_id}",
                }
                cache.set(f"{TASK_STATUS_PREFIX}{task_id}",task_status)
                return True
            task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
            task_status["status"] = "failed"
            task_status['progress'] = 100
            task_status["result"] = None
            task_status["error"] = response.get("message", "组装结果上传失败")
            cache.set(f"{TASK_STATUS_PREFIX}{task_id}",task_status)
            return False
        time.sleep(0.5)
    task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
    task_status["status"] = "failed"
    task_status['progress'] = 100
    task_status["result"] = None
    task_status["error"] = "组装失败"
    cache.set(f"{TASK_STATUS_PREFIX}{task_id}",task_status)
    return False





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
        thread.daemon = False
        thread.start()
        return JsonResponse({"task_id":task_id,'status':'processing','message':"正在组装..."},status=200,safe=False)
    else:
        return JsonResponse({'success':False,'message':'Just POST Method'},status = 405, safe = False)
    
def process_assembly_repo(repositoryName, django_request,task_id):
    session = _create_api_session()
    task_output_dir = _ensure_task_output_dir(task_id)
    assembly_result_file = _get_task_assembly_file(task_id, repositoryName)
    request_body = {"Name":repositoryName}
    print(repositoryName)
    try:
        repository_response = session.post(f"{Base_URL}getrepo",json=request_body,cookies=django_request.COOKIES)
        # print(repository_response.json())
    except Exception as e:
        return render(django_request,'error.html',{'error':"仓库获取失败"})
    if(repository_response.status_code == 200):
        repository_payload = repository_response.json()
        repository_data = repository_payload['data']
        print(repository_data)
        part = repository_data['parts']
        backbone = repository_data['backbones']
        plasmid = repository_data['plasmids']
        print(f"repository_payload:{repository_payload}")
        Level = repository_payload.get('level', repository_data.get('level'))
        Note = repository_payload.get('note', repository_data.get('note'))
        alias = repository_payload.get('alias', repository_data.get('alias'))
        
        file_address_list = []
        file_name_list = []
        target_enzyme = ""
        for each_backbone in backbone:
            sequence = (session.get(f'{Base_URL}GetBackboneSeqByID?backboneid={each_backbone}',cookies = django_request.COOKIES)).json()['data']['sequence'].lower()
            backboneName = (session.get(f'{Base_URL}BackboneNameByID?ID={each_backbone}',cookies=django_request.COOKIES)).json()['BackboneName']
            target_enzyme = _determine_target_enzyme(sequence)
            print(f"target:{target_enzyme}")
            alias = (session.get(f"{Base_URL}BackboneAliasByID?ID={each_backbone}",cookies=django_request.COOKIES)).json()['BackboneAlias']
            backbone_file_name = _assembly_file_basename(f"backbone-{each_backbone}-{backboneName}-{alias}")
            backbone_file_path = _assembly_file_path(backbone_file_name)
            if(os.path.exists(backbone_file_path)):
                file_address_list.append(backbone_file_path)
                file_name_list.append(backbone_file_name)
            else:
                backboneFeature = (session.get(f"{Base_URL}GetBackboneFeature/{each_backbone}",cookies=django_request.COOKIES)).json()
                if(backboneFeature["success"] != True):
                    seq_obj = Seq(sequence)
                    seq_reverse = str(seq_obj.reverse_complement())
                    fi = featureIdentify()
                    feature_list = fi.featureMatch(sequence)
                    reverse_feature_list = fi.featureMatch(seq_reverse)
                    scar_list = scarPosition(sequence)
                    sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=backbone_file_name)
                    sa.GenerateGBKFile(ASSEMBLY_DIR)
                else:
                    SequenceAnnotator.GeneratorBackboneNoSa(backbone_file_name,sequence,ASSEMBLY_DIR,backboneFeature['data'])
                file_address_list.append(backbone_file_path)
                file_name_list.append(backbone_file_name)
            
        for each_part in part:
            
            alias = (session.get(f"{Base_URL}PartAliasByID?ID={each_part}",cookies=django_request.COOKIES)).json()['PartAlias']
            partName = (session.get(f"{Base_URL}PartNameByID?ID={each_part}",cookies=django_request.COOKIES)).json()['PartName']
            partType = (session.get(f"{Base_URL}TypeByID?ID={each_part}", cookies=django_request.COOKIES)).json()['Type'].lower()
            
            # if(os.path.exists(os.path.join(ASSEMBLY_DIR,f"part-{partType}-{partName}-{each_part}-{alias}.gbk"))):
            #     file_address_list.append(os.path.join(ASSEMBLY_DIR,f"part-{partType}-{partName}-{each_part}-{alias}.gbk"))
            #     file_name_list.append(f"part-{partType}-{partName}-{each_part}-{alias}")
            # elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"{partName}.gbk"))):
            #     file_address_list.append(os.path.join(ASSEMBLY_DIR,f"{partName}.gbk"))
            #     file_name_list.append(f"{partName}")
            # else:
            part_feature_response = (session.get(f'{Base_URL}GetPartFeature/{each_part}',cookies=django_request.COOKIES)).json()
            sequence = (session.get(f'{Base_URL}GetPartSeqByID?partid={each_part}',cookies = django_request.COOKIES)).json()['data']['level0sequence'].lower()
            partSource = (session.get(f"{Base_URL}partSource/{each_part}",cookies=django_request.COOKIES)).json()
            if(partSource['success'] != True):
                return {"success":False}
            try:
                partAlias = (session.get(f"{Base_URL}PartAliasByID?ID={each_part}",cookies=django_request.COOKIES)).json()["PartAlias"]
            except Exception as e:
                partAlias = ""
            part_start_scar = ""
            part_end_scar = ""
            if(len(part) == 1):
                part_start_scar = repository_payload.get("part_start_scar")
                part_end_scar = repository_payload.get("part_end_scar")
                print(f"part_start_scar:{part_start_scar}")
                print(f"part_end_scar:{part_end_scar}")
            sequence = __process_part_sequence(sequence,partType,target_enzyme,partSource,partAlias,partName,part_start_scar,part_end_scar)
            print(f"part_feature_response:{part_feature_response}")
            part_file_name = _assembly_file_basename(f"part-{partType}-{partName}-{each_part}-{alias}")
            part_file_path = _assembly_file_path(part_file_name)
            if(part_feature_response["success"]):
                SequenceAnnotator.GeneratorPartNoSa(part_file_name,sequence,ASSEMBLY_DIR,part_feature_response["data"],target_enzyme.upper())
            else:
                seq_obj = Seq(sequence)
                seq_reverse = str(seq_obj.reverse_complement())
                # fi = featureIdentify()
                # feature_list = fi.featureMatch(sequence)
                # reverse_feature_list = fi.featureMatch(seq_reverse)
                feature_list = {}
                reverse_feature_list = {}
                scar_list = scarPosition(sequence)
                sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=part_file_name)
                sa.GenerateGBKFile(ASSEMBLY_DIR)
            file_address_list.append(part_file_path)
            file_name_list.append(part_file_name)
        for each_plasmid in plasmid:
            plasmidName = (session.get(f'{Base_URL}PlasmidNameByID?ID={each_plasmid}',cookies=django_request.COOKIES)).json()['PlasmidName']
            alias = (session.get(f"{Base_URL}PlasmidAliasByID?ID={each_plasmid}",cookies=django_request.COOKIES)).json()["PlasmidAlias"]
            if(os.path.exists(os.path.join(ASSEMBLY_DIR,f"{plasmidName}.gbk"))):
                file_address_list.append(os.path.join(ASSEMBLY_DIR,f"{plasmidName}.gbk"))
                file_name_list.append(plasmidName)
            elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"plasmid-{each_plasmid}-{plasmidName}-{alias}.gbk"))):
                file_address_list.append(os.path.join(ASSEMBLY_DIR,f"plasmid-{each_plasmid}-{plasmidName}-{alias}.gbk"))
                file_name_list.append(plasmidName)
            else:
                sequence = (session.get(f'{Base_URL}PlasmidSeqByID?plasmidid={each_plasmid}',cookies = django_request.COOKIES)).json()['data']['sequenceconfirm'].lower()
                seq_obj = Seq(sequence)
                plasmid_feature_response = (session.get(f'{Base_URL}GetPlasmidFeature/{each_plasmid}',cookies=django_request.COOKIES)).json()
                if(plasmid_feature_response["success"]):
                    SequenceAnnotator.GeneratorBackboneNoSa(f"plasmid-{each_plasmid}-{plasmidName}-{alias}",sequence,ASSEMBLY_DIR,plasmid_feature_response["data"])
                else:
                    _generate_plasmid_map_from_parents(
                        session,
                        django_request,
                        each_plasmid,
                        sequence,
                        f"plasmid-{each_plasmid}-{plasmidName}-{alias}"
                    )
                file_address_list.append(os.path.join(ASSEMBLY_DIR,f"plasmid-{each_plasmid}-{plasmidName}-{alias}.gbk"))
                file_name_list.append(f"plasmid-{each_plasmid}-{plasmidName}-{alias}")
        print(file_address_list)
        try:
            _run_assembly_simulation(file_address_list, file_name_list, repositoryName, task_output_dir, task_id)
        except Exception as e:
            task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
            task_status["status"] = "failed"
            task_status["error"] = str(e.args)
            cache.set(f"{TASK_STATUS_PREFIX}{task_id}",task_status)
            return
        _finalize_assembly_result(
            django_request,
            task_id,
            assembly_result_file,
            repositoryName,
            part,
            backbone,
            plasmid,
            alias,
            Note,
            Level,
        )
    else:
        task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
        task_status["status"] = "failed"
        task_status['progress'] = 100
        task_status["result"] = None
        task_status["error"] = "仓库不存在"
        cache.set(f"{TASK_STATUS_PREFIX}{task_id}",task_status)
                        
def AssemblyWithoutRepo(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        plan_name = data.get('uuid')
        partList = data.get('part')
        backboneList = data.get('backbone')
        plasmidList = data.get('plasmid')
        task_id = str(uuid.uuid4())
        task_status = {
            'status':'processing',
            'progress':0,
            'result':None,
            'error':None,
        }
        cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=100000)
        thread = threading.Thread(
            target=process_assembly_without_repo,
            args=(partList, backboneList, plasmidList,request,task_id,plan_name)
        )
        thread.daemon = False
        thread.start()
        return JsonResponse({"task_id":task_id,'status':'processing','message':"正在组装..."},status=200,safe=False)
    else:
        return JsonResponse({'success':False,'message':'Just POST Method'},status = 405, safe = False)

def process_assembly_without_repo(partList, backboneList, plasmidList, django_request,task_id,plan_name):
    session = _create_api_session()
    task_output_dir = _ensure_task_output_dir(task_id)
    assembly_result_file = _get_task_assembly_file(task_id, plan_name)
    file_address_list = []
    file_name_list = []
    part = []
    backbone = []
    plasmid = []
    target_enzyme = ""
    for each_backbone in backboneList:
        backbone_id = (session.get(f'{Base_URL}BackboneID?name={each_backbone}',cookies=django_request.COOKIES)).json()["BackboneID"]
        backbone.append(backbone_id)
        sequence = (session.get(f'{Base_URL}GetBackboneSeqByID?backboneid={backbone_id}',cookies = django_request.COOKIES)).json()['data']['sequence'].lower()
        backboneFeature = (session.get(f"{Base_URL}GetBackboneFeature/{backbone_id}",cookies=django_request.COOKIES)).json()
        
        target_enzyme = _determine_target_enzyme(sequence)
        print(f"target:{target_enzyme}")
        alias = (session.get(f"{Base_URL}BackboneAliasByID?ID={backbone_id}",cookies=django_request.COOKIES)).json()['BackboneAlias']
        backbone_file_name = _assembly_file_basename(f"backbone-{backbone_id}-{each_backbone}-{alias}")
        if(os.path.exists(os.path.join(ASSEMBLY_DIR,f"backbone-{each_backbone}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"backbone-{each_backbone}.gbk"))
            file_name_list.append(f"backbone-{each_backbone}")
        elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"backbone-{backbone_id}-{each_backbone}-{alias}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"backbone-{backbone_id}-{each_backbone}-{alias}.gbk"))
            file_name_list.append(f"backbone-{backbone_id}-{each_backbone}-{alias}")
        else:
            if(backboneFeature["success"] != True):
                seq_obj = Seq(sequence)
                seq_reverse = str(seq_obj.reverse_complement())
                fi = featureIdentify()
                feature_list = fi.featureMatch(sequence)
                reverse_feature_list = fi.featureMatch(seq_reverse)
                scar_list = scarPosition(sequence)
                sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=backbone_file_name)
                sa.GenerateGBKFile(ASSEMBLY_DIR)
            else:
                SequenceAnnotator.GeneratorBackboneNoSa(backbone_file_name,sequence,ASSEMBLY_DIR,backboneFeature['data'])
            file_address_list.append(_assembly_file_path(backbone_file_name))
            file_name_list.append(backbone_file_name)
    for each_part in partList:
        #part涓篿d
        part.append(each_part)
        part_name = (session.get(f"{Base_URL}PartNameByID?ID={each_part}",cookies=django_request.COOKIES)).json()["PartName"]
        partType = (session.get(f"{Base_URL}TypeByID?ID={each_part}", cookies=django_request.COOKIES)).json()['Type'].lower()
        try:
            partAlias = (session.get(f"{Base_URL}PartAliasByID?ID={each_part}",cookies=django_request.COOKIES)).json()["PartAlias"]
        except Exception as e:
            partAlias = ""
        if(os.path.exists(os.path.join(ASSEMBLY_DIR,f"part-{partType}-{part_name}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"part-{partType}-{part_name}.gbk"))
            file_name_list.append(f"part-{partType}-{part_name}")
        elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"{part_name}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"{part_name}.gbk"))
            file_name_list.append(f"{part_name}")
        elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"part-{each_part}-{partType}-{part_name}-{partAlias}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"part-{each_part}-{partType}-{part_name}-{partAlias}.gbk"))
            file_name_list.append(f"part-{each_part}-{partType}-{part_name}-{partAlias}")
        # print(each_part)
        else:
            sequence_response = (session.get(f'{Base_URL}GetPartSeqByID?partid={each_part}',cookies = django_request.COOKIES)).json()
            # print(sequence_response)
            sequence = sequence_response['data']['level0sequence'].lower()
            part_feature_response = (session.get(f'{Base_URL}GetPartFeature/{each_part}',cookies=django_request.COOKIES)).json()
            print(part_feature_response)
            partSource = (session.get(f"{Base_URL}partSource/{each_part}",cookies=django_request.COOKIES)).json()
            if(partSource['success'] != True):
                return {"success":False}
            # print(partType)
            
            sequence = __process_part_sequence(sequence,partType,target_enzyme,partSource,partAlias,part_name)
            part_file_name = _assembly_file_basename(f"part-{each_part}-{partType}-{part_name}-{alias}")
            if(part_feature_response["success"]):
                SequenceAnnotator.GeneratorPartNoSa(part_file_name,sequence,ASSEMBLY_DIR,part_feature_response["data"],target_enzyme.upper())
            else:
                
                seq_obj = Seq(sequence)
                seq_reverse = str(seq_obj.reverse_complement())
                # fi = featureIdentify()
                # feature_list = fi.featureMatch(sequence)
                # reverse_feature_list = fi.featureMatch(seq_reverse)
                feature_list = {}
                reverse_feature_list = {}
                scar_list = scarPosition(sequence)
                sa = SequenceAnnotator(sequence,feature_list,reverse_feature_list,scar_list,name=part_file_name)
            
                sa.GenerateGBKFile(ASSEMBLY_DIR)
            file_address_list.append(_assembly_file_path(part_file_name))
            file_name_list.append(part_file_name)
    for each_plasmid in plasmidList:
        plasmidID = (session.get(f"{Base_URL}PlasmidID?name={each_plasmid[:20]}",cookies=django_request.COOKIES)).json()['PlasmidID']
        plasmid.append(plasmidID)
        alias = (session.get(f"{Base_URL}PlasmidAliasByID?ID={plasmidID}",cookies=django_request.COOKIES)).json()["PlasmidAlias"]
        if(os.path.exists(os.path.join(ASSEMBLY_DIR,f"{each_plasmid[:20]}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"{each_plasmid[:20]}.gbk"))
            file_name_list.append(each_plasmid[:20])
        elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"plasmid-{each_plasmid[:20]}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"plasmid-{each_plasmid[:20]}.gbk"))
            file_name_list.append(f"plasmid-{each_plasmid[:20]}")
        elif(os.path.exists(os.path.join(ASSEMBLY_DIR,f"plasmid-{plasmidID}-{each_plasmid[:20]}-{alias}.gbk"))):
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"plasmid-{plasmidID}-{each_plasmid[:20]}-{alias}.gbk"))
            file_name_list.append(f"plasmid-{plasmidID}-{each_plasmid[:20]}-{alias}")
        else:
            sequence = (session.get(f'{Base_URL}PlasmidSeqByID?plasmidid={plasmidID}',cookies = django_request.COOKIES)).json()['data']['sequenceconfirm'].lower()
            _generate_plasmid_map_from_parents(
                session,
                django_request,
                plasmidID,
                sequence,
                f"plasmid-{plasmidID}-{each_plasmid[:20]}-{alias}"
            )
            file_address_list.append(os.path.join(ASSEMBLY_DIR,f"plasmid-{plasmidID}-{each_plasmid[:20]}-{alias}.gbk"))
            file_name_list.append(f"plasmid-{plasmidID}-{each_plasmid[:20]}-{alias}")
    print(file_address_list)
    try:
        _run_assembly_simulation(file_address_list, file_name_list, plan_name, task_output_dir, task_id)
    except Exception as e:
        task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}')
        task_status["status"] = "failed"
        task_status["error"] = ("PermissionError: filename=%s, errno=%s, strerror=%s",getattr(e, "filename", None), e.errno, e.strerror)
        cache.set(f"{TASK_STATUS_PREFIX}{task_id}",task_status)
        return
    _finalize_assembly_result(
        django_request,
        task_id,
        assembly_result_file,
        plan_name,
        part,
        backbone,
        plasmid,
    )


def __process_part_sequence(sequence,partType,target_enzyme,partSource,partAlias,partName,part_start_scar="",part_end_scar=""):
    if(target_enzyme != ""):
        if(target_enzyme == "BbsI"):
            if(part_start_scar != "" and part_end_scar != ""):
                sequence = "GAAGACCT"+part_start_scar+sequence+part_end_scar+"AGGTCTTC"
            else:
                if(("saccharomyces" in partSource['source'].lower()) == False):
                    if(partType == "promoter"):
                        sequence = "GAAGACCTGTGC" + sequence + "ATCAAGGTCTTC"
                    elif(partType == "terminator"):
                        sequence = "GAAGACCTTAAA" + sequence + "CCTCAGGTCTTC"
                    elif(partType == "cds"):
                        if(sequence[:3] == "atg"):
                            sequence = "GAAGACCTA" + sequence + "TAAAAGGTCTTC"
                        else:
                            sequence = "GAAGACCTAATG" + sequence + "TAAAAGGTCTTC"
                    elif(partType == "rbs"):
                            #TODO: 澶勭悊Overlapping鐨勯棶棰?
                        # partAlias = (session.get(f"{Base_URL}PartAliasByID?ID={each_part}",cookies=django_request.COOKIES)).json()["PartAlias"]
                        #鍋囪Lac搴忓垪鍦ㄥ簭鍒椾腑
                        if(("AATTAAATTAATTGTGAGCGGATAACAATT".lower() in sequence) == True):
                            sequence = "GAAGACCTATCA" + sequence
                            if(sequence[-2:] == "aa"):
                                sequence = sequence + "TGAGGTCTTC"
                            elif(sequence[-1] == "a"):
                                sequence = sequence + "ATGAGGTCTTC"
                            else:
                                sequence = sequence + "AATGAGGTCTTC"
                        elif((("BCD" in partName) or ("BCD" in partAlias))):
                            if(sequence[:2] == "ca"):
                                sequence = "GAAGACCTAT" + sequence
                            elif(sequence[:4] == "atca"):
                                sequence = "GAAGACCT" + sequence
                            else:
                                sequence = "GAAGACCTATCA" + sequence
                            if(sequence[-2:] == "aa"):
                                sequence = sequence + "TGAGGTCTTC"
                            elif(sequence[-1] == "a"):
                                sequence = sequence + "ATGAGGTCTTC"
                            else:
                                sequence = sequence + "AATGAGGTCTTC"
                        else:
                            if(sequence[:4] == "atca"):
                                sequence = "GAAGACCT" + sequence
                            elif(sequence[:2] == "ca"):
                                sequence = "GAAGACCTAT" + sequence
                            else:
                                sequence = "GAAGACCTATCA" + sequence
                            if(sequence[-1] == "a"):
                                sequence = sequence + "ATGAGGTCTTC"
                            else:
                                sequence = sequence + "AATGAGGTCTTC"
                    elif(partType == "p+r"):
                            sequence = "GAAGACCTGTGC" + sequence + "AATGAGGTCTTC"
                else:
                    if(partType == "promoter"):
                        sequence = "GAAGACCTGTGC" + sequence + "AATGAGGTCTTC"
                    elif(partType == "terminator"):
                        sequence = "GAAGACCTTAAA" + sequence + "CCTCAGGTCTTC"
                    elif(partType == "cds"):
                        if(sequence[:3] == "atg"):
                            sequence = "GAAGACCTA" + sequence + "TAAAAGGTCTTC"
                        else:
                            sequence = "GAAGACCTAATG" + sequence + "TAAAAGGTCTTC"
        elif(target_enzyme == "BsaI"):
            if(part_start_scar != "" and part_end_scar != ""):
                sequence = "GGTCTCA"+part_start_scar + sequence + part_end_scar+"AGAGACC"
            else:
                if(("saccharomyces" in partSource['source'].lower()) == False):
                    if(partType == "promoter"):
                        sequence = "GGTCTCAGTGC" + sequence + "ATCAAGAGACC"
                    elif(partType == "terminator"):
                        sequence = "GGTCTCATAAA" + sequence + "CCTCAGAGACC"
                    elif(partType == "cds"):
                        if(sequence[:3] == "atg"):
                            sequence = "GGTCTCAA" + sequence + "TAAAAGAGACC"
                        else:
                            sequence = "GGTCTCAAATG" + sequence + "TAAAAGAGACC"
                    elif(partType == "rbs"):
                        # partAlias = (session.get(f"{Base_URL}PartAliasByID?ID={each_part}",cookies=django_request.COOKIES)).json()["PartAlias"]
                        if(("AATTAAATTAATTGTGAGCGGATAACAATT".lower() in sequence) == True):
                            sequence = "GGTCTCAATCA" + sequence
                            if(sequence[-2:] == "aa"):
                                sequence = sequence + "TGAGAGACC"
                            elif(sequence[-1] == "a"):
                                sequence = sequence + "ATGAGAGACC"
                            else:
                                sequence = sequence + "AATGAGAGACC"
                        elif((("BCD" in partName) or ("BCD" in partAlias))):
                            if(sequence[:2] == "ca"):
                                sequence = "GGTCTCAAT" + sequence
                            elif(sequence[:4] == "atca"):
                                sequence = "GGTCTCA" + sequence
                            else:
                                sequence = "GGTCTCAATCA" + sequence
                            if(sequence[-2:] == "aa"):
                                sequence = sequence + "TGAGAGACC"
                            elif(sequence[-1] == "a"):
                                sequence = sequence + "ATGAGAGACC"
                            else:
                                sequence = sequence + "AATGAGAGACC"
                        else:
                            if(sequence[:4] == "atca"):
                                sequence = "GGTCTCA" + sequence
                            elif(sequence[:2] == "ca"):
                                sequence = "GGTCTCAAT" + sequence
                            else:
                                sequence = "GGTCTCAATCA" + sequence
                            if(sequence[-1] == "a"):
                                sequence = sequence + "ATGAGAGACC"
                            else:
                                sequence = sequence + "AATGAGAGACC"
                    elif(partType == "p+r"):
                            sequence = "GGTCTCAGTGC" + sequence + "AATGAGAGACC"
                else:
                    if(partType == "promoter"):
                        sequence = "GGTCTCAGTGC" + sequence + "AATGAGAGACC"
                    elif(partType == "terminator"):
                        sequence = "GGTCTCATAAA" + sequence + "CCTCAGAGACC"
                    elif(partType == "cds"):
                        if(sequence[:3] == "atg"):
                            sequence = "GGTCTCAA" + sequence + "TAAAAGAGACC"
                        else:
                            sequence = "GGTCTCAAATG" + sequence + "TAAAAGAGACC"
    else:
        if(part_start_scar != "" and part_end_scar != ""):
            sequence = "GAAGACCT" + part_start_scar + sequence + part_end_scar + "AGGTCTTC"
        else:
            if(("saccharomyces" in partSource['source'].lower()) == False):
                if(partType == "promoter"):
                    sequence = "GAAGACCTGTGC" + sequence + "ATCAAGGTCTTC"
                elif(partType == "terminator"):
                    sequence = "GAAGACCTTAAA" + sequence + "CCTCAGGTCTTC"
                elif(partType == "cds"):
                    if(sequence[:3] == "atg"):
                        sequence = "GAAGACCTA" + sequence + "TAAAAGGTCTTC"
                    else:
                        sequence = "GAAGACCTAATG" + sequence + "TAAAAGGTCTTC"
                elif(partType == "rbs"):
                    # partAlias = (session.get(f"{Base_URL}PartAliasByID?ID={each_part}",cookies=django_request.COOKIES)).json()["PartAlias"]
                    if(("AATTAAATTAATTGTGAGCGGATAACAATT".lower() in sequence) == True):
                        sequence = "GAAGACCTATCA" + sequence
                        if(sequence[-2:] == "aa"):
                            sequence = sequence + "TGAGGTCTTC"
                        elif(sequence[-1] == "a"):
                            sequence = sequence + "ATGAGGTCTTC"
                        else:
                            sequence = sequence + "AATGAGGTCTTC"
                    elif((("BCD" in partName) or ("BCD" in partAlias))):
                        if(sequence[:2] == "ca"):
                            sequence = "GAAGACCTAT" + sequence
                        elif(sequence[:4] == "atca"):
                            sequence = "GAAGACCT" + sequence
                        else:
                            sequence = "GAAGACCTATCA" + sequence
                        if(sequence[-2:] == "aa"):
                            sequence = sequence + "TGAGGTCTTC"
                        elif(sequence[-1] == "a"):
                            sequence = sequence + "ATGAGGTCTTC"
                        else:
                            sequence = sequence + "AATGAGGTCTTC"
                    else:
                        if(sequence[:4] == "atca"):
                            sequence = "GAAGACCT" + sequence
                        elif(sequence[:2] == "ca"):
                            sequence = "GAAGACCTAT" + sequence
                        else:
                            sequence = "GAAGACCTATCA" + sequence
                        if(sequence[-1] == "a"):
                            sequence = sequence + "ATGAGGTCTTC"
                        else:
                            sequence = sequence + "AATGAGGTCTTC"
                elif(partType == "p+r"):
                    sequence = "GAAGACCTGTGC" + sequence + "AATGAGGTCTTC"
            else:
                if(partType == "promoter"):
                    sequence = "GAAGACCTGTGC" + sequence + "AATGAGGTCTTC"
                elif(partType == "terminator"):
                    sequence = "GAAGACCTTAAA" + sequence + "CCTCAGGTCTTC"
                elif(partType == "cds"):
                    if(sequence[:3] == "atg"):
                        sequence = "GAAGACCTA" + sequence + "TAAAAGGTCTTC"
                    else:
                        sequence = "GAAGACCTAATG" + sequence + "TAAAAGGTCTTC"
    return sequence
    


def AssemblyResultUpload(django_request,Name, Sequence, partList, BackboneList, PlasmidList, alias = "", Note = "", Level = None):
    session = requests.Session()
    token = django_request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    if(Level == None):
        if(len(partList) == 1):
            Level = 1
        if(len(PlasmidList) == 3 or len(PlasmidList) == 4):
            Level = 2
        else:
            Level = 3
    print(f"alias:{alias}")
    data_body = {'name':Name,'alias':alias,'level':Level,'sequence':Sequence,'note':Note,'ParentInfo':""}
    response = session.post(f'{Base_URL}AddPlasmidData',json=data_body,cookies=django_request.COOKIES)
    if(response.status_code != 200):
        print(response.json())
        return {"success":False, "message":"添加质粒失败"}
    plasmidid = session.get(f'{Base_URL}PlasmidID?name={Name}',cookies=django_request.COOKIES)
    Ori_list = []
    Marker_list = []
    OriAndMarkerLabel = FittingLabels(Sequence)
    for each_ori in OriAndMarkerLabel['Origin']:
        Ori_list.append(each_ori['Name'])
    for each_marker in OriAndMarkerLabel['Marker']:
        Marker_list.append(each_marker['Name'])
    plasmid_culture_body = {"name":Name, "ori":Ori_list,"marker":Marker_list}
    plasmid_culture_response = session.post(f"{Base_URL}setPlasmidCulture",json = plasmid_culture_body, cookies=django_request.COOKIES)
    if(plasmid_culture_response.status_code != 200):
        return {"success":False, "message":"添加质粒培养信息失败"}
    scar_result_list = scarFunction(Sequence)
    scar_data_body = {'name':Name,'bsmbi':scar_result_list[0],'bsai':scar_result_list[1],'bbsi':scar_result_list[2],'aari':scar_result_list[3],'sapi':scar_result_list[4]}
    scar_response = session.post(f'{Base_URL}setPlasmidScar',json=scar_data_body,cookies=django_request.COOKIES)
    if(scar_response.status_code != 200):
        return {"success":False, "message":"添加质粒Scar失败"}
    #濞撳懐鈹栬ぐ鎾冲plasmid鐎电懓绨查惃鍕湴缁狙備繆閹?
    delete_parent_info_thread = threading.Thread(target=delete_parent_info, args=(session,plasmidid.json()["PlasmidID"],django_request))
    add_parent_info_thread = threading.Thread(target=add_parent_info,args=(session,django_request,Name,partList,BackboneList,PlasmidList))
    
    delete_parent_info_thread.start()
    delete_parent_info_thread.join()
    
    add_parent_info_thread.start()
    add_parent_info_thread.join()
    # delete_parent_info_response = session.get(f"{Base_URL}DeletePlasmidParent")
    # for each_part in partList:
    #     request_body = {"SonPlasmidName":Name,"ParentPartID":each_part}
    #     part_response = session.post(f"{Base_URL}AddPartParentByID",json=request_body,cookies=django_request.COOKIES)
    #     if(part_response.status_code != 200):
    #         return {"success":False,"message":"Parent Part 濞ｈ濮炴径杈Е"}
    # for each_backbone in BackboneList:
    #     request_body = {"SonPlasmidName":Name,"ParentBackboneID":each_backbone}
    #     backbone_response = session.post(f"{Base_URL}AddBackboneParentByID",json=request_body,cookies=django_request.COOKIES)
    #     if(backbone_response.status_code != 200):
    #         return {"success":False,"message":"Parent Backbone 濞ｈ濮炴径杈Е"}
    # for each_plasmid in PlasmidList:
    #     request_body = {"SonPlasmidName":Name,"ParentPlasmidID":each_plasmid}
    #     plasmid_response = session.post(f"{Base_URL}AddPlasmidParentByID",json=request_body,cookies=django_request.COOKIES)
    #     if(plasmid_response.status_code != 200):
    #         return {"success":False,"message":"Parent Plasmid 濞ｈ濮炴径杈Е"}
    return {"success":True}

def delete_parent_info(session,plasmidid,django_request):
    delete_parent_info_response = session.get(f"{Base_URL}DeletePlasmidParent?plasmidid={plasmidid}",cookies=django_request.COOKIES)

def add_parent_info(session,django_request,Name,partList,BackboneList,PlasmidList):
    for each_part in partList:
        request_body = {"SonPlasmidName":Name,"ParentPartID":each_part}
        part_response = session.post(f"{Base_URL}AddPartParentByID",json=request_body,cookies=django_request.COOKIES)
    for each_backbone in BackboneList:
        request_body = {"SonPlasmidName":Name,"ParentBackboneID":each_backbone}
        backbone_response = session.post(f"{Base_URL}AddBackboneParentByID",json=request_body,cookies=django_request.COOKIES)
    for each_plasmid in PlasmidList:
        request_body = {"SonPlasmidName":Name,"ParentPlasmidID":each_plasmid}
        plasmid_response = session.post(f"{Base_URL}AddPlasmidParentByID",json=request_body,cookies=django_request.COOKIES)


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
            Backbone_obj['scar_info'] = backbonescar.json()['scar_info'][0]
        return render(request,"BackboneEdit.html",{"backbone":Backbone_obj})
    else:
        data = json.loads(request.body)
        request_body = {"BackboneID":data['vectorId'],"newName":data['vectorName'],"sequence":data['sequence'],"species":data['host'],"copynumber":data['copyNumber'],"note":data['notes'],"alias":data['vectorAlias'],"tag":"abnormal" if (len(data['ori']) > 1 or len(data['marker']) > 1) else "normal"}
        
        update_backbone_response = session.post(f"{Base_URL}UpdateBackbone",json=request_body,cookies = request.COOKIES)
        update_backbone_culture_response = session.post(f"{Base_URL}setBackboneCulture",json={"id":data["vectorId"],"ori":data['ori'],"marker":data['marker']},cookies=request.COOKIES)
        update_backbone_scar_response = session.post(f"{Base_URL}setBackboneScar",json={"backboneid":data['vectorId'],'bsmbi':data['scarSites']['BsmBI'],'bsai':data['scarSites']['BsaI'],
                                                                                        'bbsi':data['scarSites']['BbsI'],'aari':data['scarSites']['Aari'],'sapi':data['scarSites']['Sapi']},cookies=request.COOKIES)
        if(update_backbone_response.status_code == 200 and update_backbone_culture_response.status_code == 200 and update_backbone_scar_response.status_code == 200):
            return JsonResponse({"success":True},status = 200, safe=False)
        else:
            return JsonResponse({"success":False,"message":"淇濆瓨澶辫触"},status=400,safe=False)
        
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
            Plasmid_obj['scar_info'] = plasmidscar.json()['scar_info'][0]
        
        plasmidParentPart = session.get(f'{Base_URL}GetPartParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        plasmidParentBackbone = session.get(f'{Base_URL}GetBackboneParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        plasmidParentPlasmid = session.get(f'{Base_URL}GetPlasmidParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        
        result = {
                    'Part':[],
                    "Backbone":[],
                    "Plasmid":[],
                }
        if(plasmidParentPart.status_code == 200 and "data" in plasmidParentPart.json()):
            for each_Part in plasmidParentPart.json()['data']:
                result['Part'].append(each_Part["name"])
        if(plasmidParentBackbone.status_code == 200 and "data" in plasmidParentBackbone.json()):
            for each_Backbone in plasmidParentBackbone.json()['data']:
                result['Backbone'].append(each_Backbone["name"])
        if(plasmidParentPlasmid.status_code == 200 and "data" in plasmidParentPlasmid.json()):
            for each_Plasmid in plasmidParentPlasmid.json()['data']:
                result['Plasmid'].append(each_Plasmid["name"])
        if(Plasmid_obj['customparentinformation'] != "" and Plasmid_obj['customparentinformation']!= None and Plasmid_obj['customparentinformation'] != 'None' and Plasmid_obj['customparentinformation'] != 'NULL' and Plasmid_obj['customparentinformation'] != 'nan'):
            plasmidParentInfo = Plasmid_obj['customparentinformation']
            pattern = r'(\w+)\(([ a-zA-z0-9]+)\)'
            matches = re.findall(pattern, plasmidParentInfo)
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
        # UpdatePlasmid
        request_body = {"id":data['plasmidId'],"newName":data['plasmidName'],"newAlias":data["plasmidAlias"],"newLevel":data['level'],"newSequence":data['sequence'],"newOri":data['ori'],"newMarker":data['marker'],"newNote":data['notes'],"tag":"abnormal" if (len(data['ori']) > 1 or len(data['marker']) > 1) else "normal"}
        
        update_plasmid_response = session.post(f"{Base_URL}UpdatePlasmid",json=request_body,cookies=request.COOKIES)
        
        
        
        update_plasmid_scar_response = session.post(f"{Base_URL}setPlasmidScar",json={"plasmidid":plasmidid,'bsmbi':data['scarSites']['BsmBI'],'bsai':data['scarSites']['BsaI'],
                                                                                        'bbsi':data['scarSites']['BbsI'],'aari':data['scarSites']['Aari'],'sapi':data['scarSites']['Sapi']},cookies=request.COOKIES)
        
        delete_parent = session.get(f"{Base_URL}DeletePlasmidParent?plasmidid={plasmidid}",cookies=request.COOKIES)
        # if(delete_parent.status_code ==200):
        customParentInfo = ""
        parent_part_list = session.get(f"{Base_URL}")
        for each_part in data['parentPart']:
            addPartResponse = session.post(f"{Base_URL}AddPartParent",json={"SonPlasmidId":plasmidid,"ParentPartName":each_part},cookies=request.COOKIES)
            if(addPartResponse.status_code != 200):
                customParentInfo += f"Part({each_part})"
        for each_backbone in data['parentBackbone']:
            addBackboneResponse = session.post(f"{Base_URL}AddBackboneParent",json={"SonPlasmidId":plasmidid,"ParentBackboneName":each_backbone},cookies=request.COOKIES)
            if(addBackboneResponse.status_code != 200):
                customParentInfo += f"Backbone({each_backbone})"
        for each_plasmid in data['parentPlasmid']:
            addPlasmidResponse = session.post(f"{Base_URL}AddPlasmidParent",json={"SonPlasmidId":plasmidid,"ParentPlasmidName":each_plasmid},cookies=request.COOKIES)
            if(addPlasmidResponse.status_code != 200):
                customParentInfo += f"Plasmid({each_plasmid})"
        print(f"CustomParent:{customParentInfo}")
        request_body = {"PlasmidID":plasmidid,"PlasmidParentInfo":customParentInfo}
        session.post(f'{Base_URL}UpdateParentInfo',json=request_body,cookies=request.COOKIES)
        
        if(update_plasmid_response.status_code == 200 and update_plasmid_scar_response.status_code == 200):
            return JsonResponse({"success":True},status = 200, safe=False)
        else:
            return JsonResponse({"success":False,"message":"淇濆瓨澶辫触"},status=400,safe=False)

def GetExperienceDetail(request, partName):
    session = requests.session()
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
    })
    response = session.get(f"{Exp_URL}/api/part/view?filter=name={partName}")
    ID = response.json()['parts'][0]['ID']
    return redirect(f"{Exp_URL}/part/{ID}")


def user(request, username):
    session = requests.session()
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
    })
    if(request.method == "GET"):
        username = request.session['info']['uname']
        user = request.user
        userid = request.user.uid
        user_repository_count = session.get(f"{Base_URL}getrepocountbyuser/{userid}",cookies=request.COOKIES).json()['count']
        user_part_count = session.get(f"{Base_URL}getuserpartcount/{username}",cookies=request.COOKIES).json()['count']
        user_backbone_count = session.get(f"{Base_URL}getuserbackbonecount/{username}",cookies=request.COOKIES).json()['count']
        user_plasmid_count = session.get(f"{Base_URL}getuserplasmidcount/{username}",cookies=request.COOKIES).json()['count']
        user_info = {}
        user_info['repoCount'] = user_repository_count
        user_info['partCount'] = user_part_count
        user_info['backboneCount'] = user_backbone_count
        user_info['plasmidCount'] = user_plasmid_count
        return render(request,'ProfilePage.html',{"user":request.user,"user_info":user_info})
    
    


def GetParentInfo(request):
    session = requests.session()
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
    })
    if(request.method == "GET"):
        plasmidName = request.GET.get("PlasmidName");
        plasmidID = session.get(f"{Base_URL}PlasmidID?name={plasmidName}",cookies=request.COOKIES).json()["PlasmidID"];
        
        plasmidParentPart = session.get(f'{Base_URL}GetPartParent?plasmidid={plasmidID}',cookies=request.COOKIES)
        
        plasmidParentBackbone = session.get(f'{Base_URL}GetBackboneParent?plasmidid={plasmidID}',cookies=request.COOKIES)
        
        plasmidParentPlasmid = session.get(f'{Base_URL}GetPlasmidParent?plasmidid={plasmidID}',cookies=request.COOKIES)
        
        plasmidSonPlasmid = session.get(f'{Base_URL}GetPlasmidSon?plasmidid={plasmidID}',cookies = request.COOKIES)

        plasmidCustomInfo = session.get(f"{Base_URL}getPlasmidCulture?plasmidId={plasmidID}",cookies=request.COOKIES)
        print(plasmidParentPlasmid.json())
        if(plasmidParentPart.status_code == 200 and plasmidParentBackbone.status_code == 200 and
            plasmidParentPlasmid.status_code == 200 and plasmidSonPlasmid.status_code == 200 and plasmidCustomInfo.status_code == 200):
            result = {
                    'Part':[],
                    "Backbone":[],
                    "Plasmid":[],
                }
            CustomInfo = plasmidCustomInfo.json()['customInfo']
            if(CustomInfo != None and CustomInfo != 'None' and CustomInfo != 'NULL' and CustomInfo != "nan"):
                pattern = r'(\w+)\(([ a-zA-z0-9]+)\)'
                matches = re.findall(pattern, CustomInfo)
                for component_type, letter in matches:
                    if(component_type == "Part"):
                        result['Part'].append(letter)
                    elif(component_type == "Backbone"):
                        result['Backbone'].append(letter)
                    elif(component_type == "Plasmid"):
                        result['Plasmid'].append(letter)
            # print({"parentPart":plasmidParentPart.json()['data'],"parentBackbone":plasmidParentBackbone.json()['data'],
                                        # "parentPlasmid":plasmidParentPlasmid.json()['data'],"parentInfo":result})
            print(f"parentPart:{plasmidParentBackbone.json()}")
            return JsonResponse(data = {"success":True,"parentPart":plasmidParentPart.json()['data'] if 'data' in plasmidParentPart.json() else [],"parentBackbone":plasmidParentBackbone.json()['data'] if 'data' in plasmidParentBackbone.json() else [],
                                        "parentPlasmid":plasmidParentPlasmid.json()['data'] if 'data' in plasmidParentPlasmid.json() else [],"parentInfo":result},status=200,safe=False)
        else:
            return render(request,'error.html',{'error':"鑾峰彇鐖剁骇淇℃伅澶辫触"})
        


def showRepository(request, repositoryName):
    session = requests.Session()
    token = request.COOKIES.get('csrftoken')
    session.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
        'X-CSRFToken':token,
    })
    if(request.method == "GET"):
        request_body = {"Name":repositoryName}
        response = session.post(f"{Base_URL}getrepo",json=request_body,cookies=request.COOKIES)
        print(response.json())
        user = request.session['info']['uname']
        if(response.status_code == 200):
            part_id_list = response.json()["data"]["parts"]
            backbone_id_list = response.json()["data"]["backbones"]
            plasmid_id_list = response.json()["data"]["plasmids"]
            part_info_list = []
            for each_part in part_id_list:
                part_name_response = session.get(f"{Base_URL}PartNameByID?ID={each_part}",cookies=request.COOKIES)
                if(part_name_response.status_code == 200):
                    part_name = part_name_response.json()["PartName"]
                else:
                    # part name fetch failed
                    return HttpResponse("False",content_type="text")
                part_type_response = session.get(f"{Base_URL}TypeByID?ID={each_part}",cookies=request.COOKIES)
                if(part_type_response.status_code == 200):
                    part_type = part_type_response.json()["Type"]
                else:
                    # part type fetch failed
                    return HttpResponse("False",content_type="text")
                part_scar_response = session.get(f"{Base_URL}getPartScar?id={each_part}",cookies=request.COOKIES).json()
                print(part_scar_response)
                if(part_scar_response["success"] and len(part_scar_response["scar_info"])!=0):
                    part_scar = f"BsmBI({part_scar_response['scar_info'][0]['bsmbi']})BsaI({part_scar_response['scar_info'][0]['bsai']})BbsI({part_scar_response['scar_info'][0]['bbsi']})"

                else:
                    part_scar = f""
                part_info_list.append({"name":part_name,"Type":part_type,"scar":part_scar})
            backbone_info_list = []
            for each_backbone in backbone_id_list:
                backbone_response = session.get(f"{Base_URL}BackboneByID?ID={each_backbone}",cookies=request.COOKIES)
                if(backbone_response.status_code == 200):
                    backbone_scar_response = session.get(f"{Base_URL}getBackboneScar?id={each_backbone}",cookies=request.COOKIES).json()
                    if(backbone_scar_response["success"]):
                        backbone_scar = f"BsmBI({backbone_scar_response['scar_info'][0]['bsmbi']})BsaI({backbone_scar_response['scar_info'][0]['bsai']})BbsI({backbone_scar_response['scar_info'][0]['bbsi']})"
                        backbone_info_list.append({"name":backbone_response.json()[0]["name"],"ori":", ".join(backbone_response.json()[0]["ori"]),"marker":", ".join(backbone_response.json()[0]["marker"]),"scar":backbone_scar})
                    else:
                        return HttpResponse("False",content_type="text")
                else:
                    return HttpResponse("False",content_type="text")
            plasmid_info_list = []
            for each_plasmid in plasmid_id_list:
                plasmid_response = session.get(f"{Base_URL}PlasmidByID?ID={each_plasmid}",cookies=request.COOKIES)
                if(plasmid_response.status_code == 200):
                    plasmid_scar_response = session.get(f"{Base_URL}getPlasmidScar?plasmidid={each_plasmid}",cookies=request.COOKIES).json()
                    if(plasmid_scar_response['success']):
                        backbone_scar = f"BsmBI({plasmid_scar_response['scar_info'][0]['bsmbi']})BsaI({plasmid_scar_response['scar_info'][0]['bsai']})BbsI({plasmid_scar_response['scar_info'][0]['bbsi']})"
                        plasmid_info_list.append({"name":plasmid_response.json()[0]["name"],"length":plasmid_response.json()[0]["length"],"scar":backbone_scar})
                    else:
                        return HttpResponse("False",content_type="text")
                else:
                    return HttpResponse("False",content_type="text")
            repository_data = {"user":user,"name":repositoryName,"created_time":response.json()["created_time"],"expired_time":response.json()["expired_time"],"part_number":response.json()["data"]["total_parts"],"plasmid_number":response.json()["data"]["total_plasmids"],"parts":part_info_list,"backbones":backbone_info_list,"plasmids":plasmid_info_list}
            print(repository_data)
    return render(request, "repositoryPage.html",{"repository":repository_data})



