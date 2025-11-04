import io
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse,FileResponse,Http404
from django.views import View
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from LabDatabase.excel_processor import ExcelProcessor
import requests
# from WebDatabase.models import UploadedFile
import threading
import openpyxl
import os
import pandas as pd
import json
# from .forms import FileUploadForm

Base_URL = "http://10.30.76.2:8000/WebDatabase/"

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

# class FileUploadView(View):
#     def get(self, request):
#         form = FileUploadForm()
#         files = UploadedFile.objects.all()
#         return render(request, 'file_upload.html', {
#             'form': form,
#             'files': files
#         })
    
#     def post(self, request):
#         form = FileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = form.save()
#             messages.success(request, f'文件 "{uploaded_file.title}" 上传成功！')
#             return redirect('file_upload')
#         else:
#             messages.error(request, '文件上传失败，请检查表单错误。')
#             files = UploadedFile.objects.all()
#             return render(request, 'file_upload.html', {
#                 'form': form,
#                 'files': files
#             })

# def ajax_file_upload(request):
#     """AJAX文件上传接口"""
#     if request.method == 'POST' and request.FILES:
#         file = request.FILES.get('file')
#         title = request.POST.get('title', file.name)
        
#         # 创建文件记录
#         uploaded_file = UploadedFile.objects.create(
#             title=title,
#             file=file,
#             description=request.POST.get('description', '')
#         )
        
#         return JsonResponse({
#             'success': True,
#             'file_id': uploaded_file.id,
#             'file_name': uploaded_file.title,
#             'file_url': uploaded_file.file.url,
#             'file_size': uploaded_file.file_size,
#             'message': '文件上传成功'
#         })
    
#     return JsonResponse({
#         'success': False,
#         'message': '上传失败'
#     })



def index(request):
    if(request.method == "GET"):
        return render(request,'index.html')

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
                print(promoterResponse.url)
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
                    return JsonResponse(backbone,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse(str(e),status = 400, safe=False)
        elif(type == "plasmid"):
            try:
                request_body = {'oriClone':data.get('OriClone'),'markerClone':data.get('MarkerClone'),'oriHost':data.get('OriHost'),'markerHost':data.get('MarkerHost'),'Enzyme':data.get('Enzyme'),'Scar':data.get('Scar'),'name':data.get('name'),'page':page,"page_size":10}
                plasmidResponse = session.post(f'{Base_URL}PlasmidFilter',json = request_body,cookies=request.COOKIES)
                if(plasmidResponse.status_code == 200):
                    plasmid = plasmidResponse.json()
                    return JsonResponse(plasmid,status=200,safe=False)
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as e:
                return JsonResponse(str(e),status = 400, safe=False)

def UploadPartMap(request):
    pass

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
    else:
        raise Http404('模板文件不存在')


def process_excel_async(upload_record,django_request):
    try:
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
        result = ExcelProcessor.process_excel_file(django_request,excel_data,type)
    except Exception as e:
        print(e.args)

    # ExcelProcessor.process_excel_file(upload_record)
def UploadFile(request):
    if(request.method == 'POST' and request.FILES):
        file = request.FILES.get('file')
        title = request.POST.get('title', file.name)
        thread = threading.Thread(
            target = process_excel_async,
            args= (file,request)
        )
        thread.daemon = True
        thread.start()
        return JsonResponse(data={'success':True})
    else:
        return JsonResponse({'success':False,'message':'Upload record is empty'})
    

# def UploadPartFile(request):
#     if request.method == 'POST' and request.FILES:
#         file = request.FILES.get('file')
#         title = request.POST.get('title', file.name)
#         username = request.session['info']['uname']
#         print(file)
#         thread = threading.Thread(
#             target = process_excel_async,
#             args= (file,username)
#         )
#         thread.daemon = True
#         thread.start()
#         return JsonResponse({'success':True})
#     else:
#         return JsonResponse({'success':False,'message':'Upload record is empty'})

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
            print(part)
            if(part['type'] == 1):
                part['type'] = "Promoter"
            elif(part['type'] == 2):
                part['type'] = "CDS"
            elif(part['type'] == 3):
                part['type'] = "Terminator"
            elif(part['type'] == 4):
                part['type'] = "RBS"
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
        if(backboneResponse.status_code == 200):
            backbone = backboneResponse.json()[0]
            return render(request,'backbone.html',{'backbone':backbone})
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
        plasmidParentPart = session.get(f'{Base_URL}GetPartParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        plasmidParentBackbone = session.get(f'{Base_URL}GetBackboneParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        plasmidParentPlasmid = session.get(f'{Base_URL}GetPlasmidParent?plasmidid={plasmidid}',cookies=request.COOKIES)
        plasmidSonPlasmid = session.get(f'{Base_URL}GetPlasmidSon?plasmidid={plasmidid}',cookies = request.COOKIES)
        if(plasmidResponse.status_code == 200 and plasmidParentPart.status_code == 200 and plasmidParentBackbone.status_code == 200 and
            plasmidParentPlasmid.status_code == 200 and plasmidSonPlasmid.status_code == 200):
            plasmid = plasmidResponse.json()[0]
            return render(request,'plasmid.html',{'plasmid':plasmid,'partparent':plasmidParentPart.json()['data'][0] if len(plasmidParentPart.json()['data']) >0 else [],'backboneparent':plasmidParentBackbone.json()['data'][0] if len(plasmidParentBackbone.json()['data']) > 0 else [],
                                    'plasmidparent':plasmidParentPlasmid.json()['data'][0] if len(plasmidParentPlasmid.json()['data']) > 0 else [],'plasmidson':plasmidSonPlasmid.json()['data'][0] if len(plasmidSonPlasmid.json()['data']) > 0 else []})
        else:
            return render(request,'error.html',{'error':plasmidResponse.text})


def delete_part(request,partid):
    pass

def delete_backbone(request,backboneid):
    pass

def delete_plasmid(request,plasmidid):
    pass

def modify_part(request,partid):
    pass

def modify_backbone(request,backboneid):
    pass

def modify_plasmid(request,plasmidid):
    pass

