import django.core.exceptions
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.core import serializers
from django.db.utils import OperationalError
import math
import json
import uuid
from django.db import transaction
import time
from django.utils import timezone
from django.db.models import Q
from django.utils.deprecation import MiddlewareMixin
from .models import (Backbonetable,Parentplasmidtable,
                    Partrputable,Parttable,Plasmidneed,
                    Straintable,TbBackboneUserfileaddress,
                    TbPartUserfileaddress,TbPlasmidUserfileaddress,
                    Testdatatable,User,Lbdnrtable,Lbddimertable,Dbdtable,Parentbackbonetable,\
                    Parentparttable, Partscartable, Backbonescartable, Plasmidscartable, \
                    Plasmid_Culture_Functions,Backbone_Culture_Functions)
from django.views.decorators.csrf import csrf_exempt
# from .serializers import StraintableSerializer, BackbonetableSerializer, ParentplasmidtableSerializer, \
#     PartrputableSerializer,ParttableSerializer,PlasmidneedSerializer,TbBackboneUserfileaddressSerializer,\
#     TbPartUserfileaddressSerializer,TbPlasmidUserfileaddressSerializer,TestdatatableSerializer

#----------------------------------------------------------
#用户登录验证(中间件)
class User_auth(MiddlewareMixin):

    def process_request(self,request):
        #排除不需要登录就能访问的页面
        if request.path_info == "/WebDatabase/login" or request.path_info == "/WebDatabase/register":
            return
        info = request.session.get('info')
        print(f'User_auth{info}')
        # print(info)
        if not info:
            return redirect('/WebDatabase/login')
        else:
            return

    def process_response(self,request,response):
        return response
    # if not info:
    #     return JsonResponse({'status': 'Not logged in'})




#-----------------------------------------------------------
#Strain Table
#新增数据方法
def SearchByStrainName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'status': 201, 'data': "Name cannot be empty"})
        StrainList = Straintable.objects.filter(strainname=Name)
        if(len(StrainList) > 0):
            # return HttpResponse("成功",data = StrainList)
            return JsonResponse(data=list(StrainList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status': 'success', 'data': list(StrainList.values())})
        else:
            return JsonResponse(data="No such strain", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Strain Not Found"})



#-------------------------------------------------------------
#Part Table
#ALL
def PartDataALL(request):
    print("PartDataAll")
    if(request.method == "GET"):
        page = int(request.GET.get('page',0))
        if(page == 0):
            PartData = Parttable.objects.all().order_by('name')
            if(len(PartData) > 0):
                return JsonResponse(data=list(PartData.values()), status=200,safe=False)
                # return JsonResponse({'code':200,'data':list(PartData.values())})
            else:
                return JsonResponse(data="No such part", status=404,safe=False)
                # return JsonResponse({'code':204,'status': 'failed', 'data': []})
        else:
            page_size = int(request.GET.get('page_size',10))
            offset = (page -1)*page_size
            total_count = Parttable.objects.count()
            total_pages = (total_count + page_size -1) // page_size
            query_set = list(Parttable.objects.order_by('name').values('partid','name','alias','type','sourceorganism','reference','tag'))[offset:offset+page_size]
            # query_set = Parttable.objects.only('partid','name','type','sourceorganism','reference').order_by('name')[offset:offset+page_size]
            has_next = page < total_pages
            has_previous = page > 1
            return JsonResponse(data={'success':True,
                                      'data':query_set,
                                      'pagination':{
                                          'current_page' : page,
                                          'total_pages' : total_pages,
                                          'total_count' : total_count,
                                          'has_next':has_next,
                                          'has_previous' : has_previous,
                                          'page_size':page_size,
                                          'offset':offset
                                          }
                                        },status = 200, safe=False
                                )

#PartFilter
def PartFilter(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        type = data["type"]
        Enzyme = data['Enzyme']
        Scar = data['Scar']
        name = data['name']
        page = data['page']
        page_size = data['page_size']
        offset = (page - 1) * page_size
        if(type != ""):
            if(type.lower() == "promoter"):
                type = 1
            elif(type.lower() == "terminator"):
                type = 3
            elif(type.lower() == "rbs"):
                type = 4
            elif(type.lower() == "cds"):
                type = 2
        scarpartid = []
        if(Enzyme == "BsmBI"):
            scarpartid = list(Partscartable.objects.filter(bsmbi = Scar).values('partid'))
        elif(Enzyme == "BsaI"):
            scarpartid = list(Partscartable.objects.filter(bsai = Scar).values('partid'))
        elif(Enzyme == "BbsI"):
            scarpartid = list(Partscartable.objects.filter(bbsi = Scar).values('partid'))
        elif(Enzyme == "AarI"):
            scarpartid = list(Partscartable.objects.filter(aari = Scar).values('partid'))
        elif(Enzyme == "SapI"):
            scarpartid = list(Partscartable.objects.filter(sapi = Scar).values('partid'))
        if(Enzyme != "" and len(scarpartid) == 0):
            return JsonResponse(data={'success':False,'error':'No data'}, status = 400, safe = False)
        # result = Parttable.objects
        PartResult = []
        if(len(scarpartid) != 0):
            for each_id in scarpartid:
                result = Parttable.objects
                result = result.filter(partid = each_id['partid'])
                if(type != "" and result != None):
                    # 'partid','name','type','sourceorganism','reference'
                    result = result.filter(type = type)
                if(name != "" and result != None):
                    result = result.filter(Q(name__icontains = name) | Q(alias__icontains = name))
                if(result != None):
                    PartResult.append(list(result.order_by('name').values('partid','name','alias','type','sourceorganism','reference','tag'))[0])
        else:
            result = Parttable.objects
            if(type != "" and result != None):
                # 'partid','name','type','sourceorganism','reference'
                result = result.filter(type = type)
            if(name != "" and result != None):
                print(name)
                result = result.filter(Q(name__icontains = name) | Q(alias__icontains = name))
            if(result != None):
                PartResult = (list(result.order_by('name').values('partid','name','alias','type','sourceorganism','reference','tag')))
        print(PartResult)
        if(len(PartResult) != 0):
            total_count = len(PartResult)
            total_pages = (total_count + page_size -1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            if(len(PartResult) > page_size):
                return JsonResponse(data = {'success':True, 'data': list(PartResult[offset:offset+page_size]),
                                        'pagination':{
                                            'current_page' : page,
                                            'total_pages' : total_pages,
                                            'total_count' : total_count,
                                            'has_next' : has_next,
                                            'has_previous' : has_previous,
                                            'page_size' : page_size,
                                            'offset' : offset
                                            }
                                        },status = 200, safe = False)
            else:
                return JsonResponse(data = {'success':True, 'data': list(PartResult[:]),
                                        'pagination':{
                                            'current_page' : page,
                                            'total_pages' : total_pages,
                                            'total_count' : total_count,
                                            'has_next' : has_next,
                                            'has_previous' : has_previous,
                                            'page_size' : page_size,
                                            'offset' : offset
                                            }
                                        },status = 200, safe = False)
        else:
            return JsonResponse(data = {'success':False, 'data': [],
                                        'pagination':{
                                            'current_page' : 0,
                                            'total_pages' : 0,
                                            'total_count' : 0,
                                            'has_next' : 0,
                                            'has_previous' : 0,
                                            'page_size' : 0,
                                            'offset' : 0
                                            }
                                        },status = 200, safe = False)
            # return JsonResponse(data = {'success':False, 'error':'No data'},status = 404, safe = False)


#Search
def SearchByPartName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Name cannot be empty"})
        PartList = Parttable.objects.filter(name=Name)
        if(len(PartList) > 0):
            return JsonResponse(data=list(PartList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status': 'success', 'data': list(PartList.values())})
        else:
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': []})

def SearchByPartNameFilter(request):
    if(request.method == "GET"):
        Name = request.GET.get('keywords')
        Type = request.GET.get('Type')
        print(Name)
        print(Type)
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty",status=400,safe=False)
        else:
            try:
                promoterResult = list(Parttable.objects.filter(name__icontains = Name,type=Type).values('partid','name','sourceorganism','reference'))
                if(len(promoterResult[0]) > 0):
                    return JsonResponse(data=promoterResult,status=200,safe=False)
                else:
                    return JsonResponse(data = [],status=200,safe=False)
            except Exception as e:
                return JsonResponse(data = str(e),status=404,safe=False)

def getBackboneOriAndMarker(Backboneid):
    ori_list = []
    marker_list = []
    ori_info = Backbone_Culture_Functions.objects.filter(backbone_id = Backboneid,function_type = 'ori').values('function_content')
    # print(ori_info)
    marker_info = Backbone_Culture_Functions.objects.filter(backbone_id = Backboneid,function_type = 'marker').values('function_content')
    for each_ori in ori_info:
        ori_list.append(each_ori['function_content'])
    for each_marker in marker_info:
        marker_list.append(each_marker['function_content'])
    return [ori_list, marker_list]

def SearchByBackboneNameFilter(request):
    if(request.method == "GET"):
        Name = request.GET.get('keywords')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty",status=400,safe=False)
        else:
            try:
                # backboneResult = list(Backbonetable.objects.filter(name__icontains = Name).values('id','name','ori','marker','species'))
                backboneResult = list(Backbonetable.objects.filter(name__icontains = Name).values('id','name','species'))
                #TODO: 标记ori，marker
                for each in backboneResult:
                    info_list = getBackboneOriAndMarker(each['id'])
                    each['ori'] = info_list[0]
                    each['marker'] = info_list[1]
                if(len(backboneResult) > 0):
                    return JsonResponse(data=backboneResult,status=200,safe=False)
                else:
                    return JsonResponse(data = [],status=200,safe=False)
            except Exception as e:
                return JsonResponse(data = str(e),status=404,safe=False)


def SearchByPlasmidNameFilter(request):
    if(request.method == 'GET'):
        Name = request.GET.get('keywords')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty",status=400,safe=False)
        else:
            try:
                plasmidResult = list(Plasmidneed.objects.filter(name__icontains=Name).values('plasmidid','name'))
                if(len(plasmidResult) > 0):
                    for each in plasmidResult:
                        info_list = getOriAndMarker(each['plasmidid'])
                        each['ori_info'] = info_list[0]
                        each['marker_info'] = info_list[1]
                    return JsonResponse(data = plasmidResult,status=200,safe=False)
                else:
                    return JsonResponse(data = [],status=200,safe=False)
            except Exception as e:
                return JsonResponse(data = str(e),status=404,safe=False)

def SearchByPartID(request):
    if(request.method == "GET"):
        ID = request.GET.get('ID')
        if(ID == None or ID == ""):
            return JsonResponse(data="ID cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Name cannot be empty"})
        PartList = Parttable.objects.filter(partid=ID)
        if(len(PartList) > 0):
            return JsonResponse(data=list(PartList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status': 'success', 'data': list(PartList.values())})
        else:
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': []})

def SearchByPartAlterName(request):
    if(request.method == "GET"):
        try:
            AlterName = request.GET.get('AlterName')
            if(AlterName == None or AlterName == ""):
                return JsonResponse(data="AlterName cannot be empty", status=400,safe=False)
                # return JsonResponse({'code':204,'status': 'failed', 'data': "AlterName cannot be empty"})
            PartList = Parttable.objects.filter(alias=AlterName)
            if(len(PartList) > 0):
                return JsonResponse(data=list(PartList.values()), status=200,safe=False)
                # return JsonResponse({'code':200,'status': 'success', 'data': list(PartList.values())})
            else:
                return JsonResponse(data="No such part", status=404,safe=False)
                # return JsonResponse({'code':204,'status': 'failed', 'data': []})
        except Exception as e:
            return JsonResponse(data=e, status=404,safe=False)


def SearchByPartType(request):
    if(request.method == "GET"):
        Type = request.GET.get('type')
        if(Type == None or Type == ""):
            return JsonResponse(data="Type cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Type cannot be empty"})
        if(Type.lower() == "promoter"):
            PartList = Parttable.objects.filter(type=1)
        elif(Type.lower() == "terminator"):
            PartList = Parttable.objects.filter(type=2)
        elif(Type.lower() == "cds"):
            PartList = Parttable.objects.filter(type=3)
        elif(Type.lower() == "rbs"):
            PartList = Parttable.objects.filter(type=4)
        else:
            PartList = Parttable.objects.filter(type=5)
        if(len(PartList) > 0):
            return JsonResponse(data=list(PartList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status': 'success', 'data': list(PartList.values())})
        else:
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Part Not Found"})

def SearchPartTypeByName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Name cannot be empty"})
        Type = Parttable.objects.filter(name=Name).first().type
        if(Type != None):
            if(Type == 1):
                return JsonResponse(data={"Type":"Promoter"},status=200)
                # return JsonResponse({'code':200,'status': 'success', 'data': {"Type":"Promoter"}})
            elif(Type == 2):
                return JsonResponse(data={"Type":"Terminator"},status=200)
                # return JsonResponse({'code':200,'status':'success','data':{"Type":"Terminator"}})
            elif(Type == 3):
                # return HttpResponse("CDS")
                return JsonResponse(data={"Type":"CDS"},status=200)
                # return JsonResponse({'code':200,'status': 'success', 'data': {"Type": "CDS"}})
            elif(Type == 4):
                return JsonResponse(data={"Type":"RBS"},status=200)
                # return JsonResponse({'code':200,'status': 'success', 'data': {"Type": "RBS"}})
            else:
                return JsonResponse(data={"Type":"Carb"}, status=200)
                # return JsonResponse({'code':200,'status': 'success', 'data': {"Type": "Carb"}})
        else:
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Part Not Found"})

# def SearchPartByStrength(request):
#     Strength = float(request.GET.get('strength'))
#     StrengthLow = math.ceil(Strength)
#     StrengthHigh = math.floor(Strength)
#     PartList = Parttable.objects.filter(strength_in=[StrengthLow, StrengthHigh])
#     if(len(PartList) > 0):
#         return HttpResponse(PartList)
#     else:
#         return HttpResponse("")


def SearchByRPU(request):
    if (request.method == "GET"):
        RPU = float(request.GET.get('rpu'))
        if (RPU == None or RPU == 0):
            return JsonResponse(data="RPU cannot be empty", status=400,safe=False)
            # return JsonResponse({'code': 204, 'status': 'failed', 'data': "RPU cannot be empty"})
        RPULow = math.ceil(RPU)
        RPUHigh = math.floor(RPU)
        PartIDList = Partrputable.objects.filter(rpu__in=[RPULow, RPUHigh])
        if (len(PartIDList) > 0):
            PartList = []
            for obj in PartIDList:
                PartList.append(list(Parttable.objects.filter(partid=obj.partid.partid).values())[0])
                # PartList.append(obj.partid.values())
            if (len(PartList) > 0):
                return JsonResponse(data=PartList, status=200,safe=False)
                # return JsonResponse({'code': 200, 'status': 'success', 'data': list(PartList)})
        return JsonResponse(data="No such part", status=404,safe=False)
        # return JsonResponse({'code': 204, 'status': 'failed', 'data': "Part Not Found"})


def GetPartRPU(request):
    if(request.method == "GET"):
        partID = request.GET.get('partID')
        if(partID == None or partID == ""):
            return JsonResponse("PartID cannot be empty", status = 400, safe=False)
        PartRPUList = Partrputable.objects.filter(partid = partID)
        if(len(PartRPUList) > 0):
            return JsonResponse(data=list(PartRPUList.values()),status=200,safe=False)
        else:
            return JsonResponse("Part RPU Data doesn't exist",status=404, safe=False)


def SearchBySeq(request):
    if(request.method == "GET"):
        Seq = request.GET.get('seq')
        if(Seq == None or Seq == ""):
            return JsonResponse(data="Seq cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Sequence cannot be empty"})
        PartList = Parttable.objects.filter(level0sequence__contains=Seq)
        if len(PartList) > 0:
            # return HttpResponse(PartList)
            return JsonResponse(data=list(PartList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status': 'success', 'data': list(PartList.values())})
        else:
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Part Not Found"})


def SearchPartFile(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Name cannot be empty"})
        PartID = Parttable.objects.filter(name=Name).first()
        if(PartID == None):
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Part Not Found"})
        PartID = PartID.id
        userid = request.session.get('info')['uid']
        FilterDict = {"partid":PartID,"userid":userid}
        # Address = TbPartUserfileaddress.objects.filter(**FilterDict).first()
        Obj = TbPartUserfileaddress.objects.filter(**FilterDict).first()
        if(Obj!=None):
            return JsonResponse(data={"FileAddress":Obj.fileaddress}, status=200)
            # return JsonResponse({'code':200,'status': 'success', 'data': {"FileAddress":Address}})
        else:
            return JsonResponse(data="No such par file address", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Address Not Found"})


#Add
def AddPartRPU(request):
    if(request.method == "POST"):
        name = request.POST.get('Name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': "Name cannot be empty"})
        PartID = Parttable.objects.filter(name=name).first()
        if(PartID == None):
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Part Not Found'})
        rpu = float(request.POST.get('rpu'))
        testStrain = request.POST.get('testStrain')
        Note = request.POST.get('Note')
        Partrputable.objects.create(partid=PartID.partid, rpu=rpu, testStrain=testStrain,note=Note)
        return JsonResponse(data="Added part rpu", status=200)
        # return JsonResponse({'code':200,'status': 'success','data':'Part RPU added'})


def AddPartData(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        print(data)
        name = data['name']
        alias = data['alias']
        if(data['Level0Sequence'] != ""):
            length = len(data['Level0Sequence'])
            level0Seq = data['Level0Sequence']
        else:
            length = 0
            level0Seq = ""
        ConfirmedSequence = data['ConfirmedSequence'] if'ConfirmedSequence' in data else ""
        InsertSequence = data['InsertSequence'] if 'InsertSequence' in data else ""
        sourceOrganism = data['source'] if 'source' in data else ""
        reference = data['reference']  if 'reference' in data else ""
        note = data['note'] if 'note' in data else ""
        type = data['type']
        if(type == None or type == ""):
            return JsonResponse(data="Type cannot be empty", status=400,safe=False)
        if(type.lower() == "promoter"):
            type = 1
        elif(type.lower() == "terminator"):
            type = 3
        elif(type.lower() == "cds"):
            type = 2
        elif(type.lower() == "rbs"):
            type = 4
        elif(type.lower() == "carb"):
            type = 5
        username = request.session['info']['uname']
        if(name == "" or name == None):
            return JsonResponse(data="Parameters name", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name or Sequence can not be empty'})
        if(Parttable.objects.filter(name=name).first() != None):
            Parttable.objects.filter(name = name).update(name=name, alias=alias, lengthinlevel0=length, level0sequence=level0Seq,
                                confirmedsequence = ConfirmedSequence, insertsequence = InsertSequence,
                                sourceorganism = sourceOrganism, reference=reference, note=note, type=type,user=username)
        else:
            Parttable.objects.create(name=name, alias=alias, lengthinlevel0=length, level0sequence=level0Seq,
                                confirmedsequence = ConfirmedSequence, insertsequence = InsertSequence,
                                sourceorganism = sourceOrganism, reference=reference, note=note, type=type,user=username)
        return JsonResponse(data="Added part data", status=200,safe=False)
        # return JsonResponse({'code':200,'status': 'success','data':'Part data added'})



def AddPartFileAddress(request):
    if(request.method == "POST"):
    # if(request.method == "GET"):
        userid = request.session.get('info')['uid']
        # userid = 8
        print(userid)
        partName = request.POST.get('PartName')
        fileAddress = request.POST.get('fileAddress')
        # partName=request.GET.get('name')
        # fileAddress = "TTT"
        if(partName == None or partName == "" or fileAddress == None or fileAddress == ""):
            return JsonResponse(data="Parameters cannot be empty", status=400,safe=False)
        partID = Parttable.objects.filter(name=partName).first()
        if(partID == None):
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Part Not Found'})
        # uid = User.objects.get(uid=userid)
        user = User.objects.filter(uid=userid).first()
        TbPartUserfileaddress.objects.create(userid=user, partid=partID, fileaddress=fileAddress)

        return JsonResponse(data="Added part address", status=200,safe=False)
        # return JsonResponse({'code':200,'status': 'success','data':'Part file address added'})


#Update
def UpdatePart(request):
    if(request.method == "POST"):
        OriginalName = request.POST.get('OriginalName')
        PartID = Parttable.objects.get(name=OriginalName).id
        if(PartID == None):
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Part Not Found'})
        NewName = request.POST.get('Name')
        NewAlias = request.POST.get('Alias')
        NewLength = len(request.POST.get('Level0Sequence'))
        NewLevel0Sequence = request.POST.get('Level0Sequence')
        NewConfirmedSequence = request.POST.get('ConfirmedSequence')
        NewInsertSequence = request.POST.get('InsertSequence')
        NewSourceOrganism = request.POST.get("source")
        NewReference = request.POST.get("reference")
        NewNote = request.POST.get("note")
        if(NewName == None or NewName == ""):
            return JsonResponse(data="Parameters Name cannot be empty", status=400,safe=False)
        Parttable.objects.filter(partid = PartID).update(name=NewName, alias=NewAlias,lengthinlevel0=NewLength,
                                                           level0sequence=NewLevel0Sequence,confirmedsequence=NewConfirmedSequence,
                                                           insertsequence=NewInsertSequence,sourceorganism = NewSourceOrganism,
                                                           reference=NewReference,note=NewNote)
        return JsonResponse(data="Updated part data", status=200)
        # return JsonResponse({'code':200,'status': 'success','data':'Part data updated'})

def UpdatePartRPU(request):
    if(request.method == "POST"):
        Name = request.POST.get('Name')
        rpu = float(request.POST.get('rpu'))
        testStrain = request.POST.get('testStrain')
        note = request.POST.get('note')
        if(Name == None or rpu == None or testStrain == None or Name == "" or rpu == 0 or testStrain == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name, rpu, testStrain can not be empty'})
        partID = Parttable.objects.filter(name=Name).first().id
        if(partID == None):
            return JsonResponse(data="No such part rpu", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Part Not Found'})
        filterDict = {"partid":partID,"testStrain":testStrain}
        Partrputable.objects.filter(**filterDict).update(rpu=rpu,note=note)
        return JsonResponse(data="Updated part rpu", status=200)
        # return JsonResponse({'code':200,'status': 'success','data':'Part RPU updated'})


def UpdatePartFileAddress(request):
    if(request.method == "POST"):
        PartName = request.POST.get('PartName')
        Address = request.POST.get('Address')
        userid = request.session.get('info')['uid']
        if(PartName == None or Address == None or PartName == "" or Address == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'PartName, Address can not be empty'})
        PartID = Parttable.objects.get(name=PartName).partid
        if(PartID == None):
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Part Not Found'})
        filterDict = {"PartID":PartID,"userid":userid}
        TbPartUserfileaddress.objects.filter(**filterDict).update(userid=userid,partid=PartID,fileaddress=Address)
        return JsonResponse(data="Added part address", status=200)
        # return JsonResponse({'code':200,'status': 'success','data':'Part file address updated'})

#Delete
def deletePartData(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PartID = Parttable.objects.get(name=name).id
        if(PartID == None):
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Part Not Found'})
        TbPartUserfileaddress.objects.filter(partid=PartID).delete()
        Partrputable.objects.filter(partid=PartID).delete()
        Parttable.objects.filter(name=name).delete()
        return JsonResponse(data="Deleted part", status=200)
        # return JsonResponse({'code':200,'status': 'success','data':'Part data deleted'})


def deletePartFile(request):
    if(request.method == "GET"):
        userid = request.session.get('info')['uid']
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PartID = Parttable.objects.get(name=name).id
        if(PartID == None):
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Part Not Found'})
        FilterDict = {"userid":userid,"partid":PartID}
        TbPartUserfileaddress.objects.filter(**FilterDict).delete()
        return JsonResponse(data="Deleted part", status=200)
        # return JsonResponse({'code':200,'status': 'success','data':'Part file address deleted'})







#---------------------------------------------------------------
#pladmid need

def getOriAndMarker(plasmid_id):
    ori_list = []
    marker_list = []
    ori_info = Plasmid_Culture_Functions.objects.filter(plasmid_id = plasmid_id,function_type = 'ori').values('function_content')
    # print(ori_info)
    marker_info = Plasmid_Culture_Functions.objects.filter(plasmid_id = plasmid_id,function_type = 'marker').values('function_content')
    for each_ori in ori_info:
        ori_list.append(each_ori['function_content'])
    for each_marker in marker_info:
        marker_list.append(each_marker['function_content'])
    return [ori_list, marker_list]

def getdefaultplasmidscar(plasmidid):
    scar_info = Plasmidscartable.objects.filter(plasmidid = plasmidid).first().bbsi
    return scar_info

def PlasmidDataALL(request):
    if(request.method == "GET"):
        page = int(request.GET.get('page',0))
        if(page == 0):
            PlasmidData = list(Plasmidneed.objects.all().order_by('name').values())
            if(len(PlasmidData) > 0):
                for each in PlasmidData:
                    info_list = getOriAndMarker(each['plasmidid'])
                    each['ori_info'] = info_list[0]
                    each['marker_info'] = info_list[1]
                    print(each['plasmidid'])
                    each['scar'] = getdefaultplasmidscar(each['plasmidid'])
                    print(each)
                return JsonResponse(data=PlasmidData, status=200,safe=False)
                # return JsonResponse({'code':200,'data':list(PartData.values())})
            else:
                return JsonResponse(data="No plasmid", status=404,safe=False)
                # return JsonResponse({'code':204,'status': 'failed', 'data': []})
        else:
            page_size = int(request.GET.get('page_size',10))
            offset = (page -1)*page_size
            total_count = Plasmidneed.objects.count()
            total_pages = (total_count + page_size -1) // page_size
            # query_set = Plasmidneed.objects.only('plasmidid','name','oricloning','orihost','markercloning','markerhost','level').all().order_by('name')[offset:offset+page_size]
            query_set = list(Plasmidneed.objects.order_by('name').values('plasmidid','name','alias','level','tag'))[offset:offset+page_size]
            for each_plasmid in query_set:
                info_list = getOriAndMarker(each_plasmid['plasmidid'])
                each_plasmid['ori_info'] = info_list[0]
                each_plasmid['marker_info'] = info_list[1]
                each_plasmid['scar'] = getdefaultplasmidscar(each_plasmid['plasmidid'])
                print(each_plasmid)
            # print(query_set)
            has_next = page < total_pages
            has_previous = page > 1
            return JsonResponse(data={'success':True,
                                      'data':query_set,
                                      'pagination':{
                                          'current_page' : page,
                                          'total_pages' : total_pages,
                                          'total_count' : total_count,
                                          'has_next':has_next,
                                          'has_previous' : has_previous,
                                          'page_size':page_size,
                                          'offset':offset
                                          }
                                        },status = 200, safe=False
                                )
        

#Plasmid Filter

def PlasmidFilter(request):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        Name = data['name']
        Ori = data['ori']
        Marker = data['marker']
        Enzyme = data['Enzyme']
        Scar = data['Scar']
        page = data['page']
        page_size = data['page_size']
        offset = (page -1)*page_size
        scarplasmidid = []
        if(Enzyme == "BsmBI"):
            scarplasmidid = list(Plasmidscartable.objects.filter(bsmbi = Scar).values('plasmidid'))
        elif(Enzyme == "BsaI"):
            scarplasmidid = list(Plasmidscartable.objects.filter(bsai = Scar).values('plasmidid'))
        elif(Enzyme == "BbsI"):
            scarplasmidid = list(Plasmidscartable.objects.filter(bbsi = Scar).values('plasmidid'))
        elif(Enzyme == "AarI"):
            scarplasmidid = list(Plasmidscartable.objects.filter(aari = Scar).values('plasmidid'))
        elif(Enzyme == "SapI"):
            scarplasmidid = list(Plasmidscartable.objects.filter(sapi = Scar).values('plasmidid'))
        if(Enzyme != "" and len(scarplasmidid) == 0):
            return JsonResponse(data={'success':False,'error':'No data'}, status = 404, safe = False)
        PlasmidResult = []
        if(len(scarplasmidid) != 0):
            for each_id in scarplasmidid:
                result = Plasmidneed.objects
                if(Ori != ""):
                    Ori_result = Plasmid_Culture_Functions.objects.filter(plasmid_id = each_id['plasmidid'], function_content = Ori, function_type="ori").values()
                    if(Ori_result == None):
                        continue
                if(Marker != ""):
                    Marker_result = Plasmid_Culture_Functions.objects.filter(plasmid_id = each_id['plasmidid'],function_content = Marker, function_type="marker").values()
                    if(Marker_result == None):
                        continue
                result = result.filter(plasmidid = each_id['plasmidid'])
                if(Name != '' and result != None):
                    result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                if(result != None):
                    temp_result = list(result.order_by('name').values('plasmidid','name','alias','level','tag'))[0]
                    # 'plasmidid','name','oricloning','orihost','markercloning','markerhost','level'
                    info_list = getOriAndMarker(temp_result['plasmidid'])
                    temp_result['ori_info'] = info_list[0]
                    temp_result['marker_info'] = info_list[1]
                    temp_result['scar'] = Scar
                    PlasmidResult.append(temp_result)
        else:
            Ori_plasmid_id_list = set()
            Marker_plasmid_id_list = set()
            final_plasmid_id_list = set()
            if(Ori != ""):
                Ori_result = Plasmid_Culture_Functions.objects.filter(function_content = Ori, function_type="ori").values("plasmid_id")
                for each in Ori_result:
                    Ori_plasmid_id_list.add(each['plasmid_id'])
            if(Marker != ""):
                Marker_result = Plasmid_Culture_Functions.objects.filter(function_content = Marker, function_type="marker").values("plasmid_id")
                for each in Marker_result:
                    Marker_plasmid_id_list.add(each['plasmid_id'])
            if(Ori != "" and Marker != ""):
                final_plasmid_id_list = Ori_plasmid_id_list & Marker_plasmid_id_list
            else:
                final_plasmid_id_list = Ori_plasmid_id_list | Marker_plasmid_id_list
            # print(Ori_plasmid_id_list)
            # print(Marker_plasmid_id_list)
            # print(final_plasmid_id_list)
            if(len(final_plasmid_id_list) == 0):
                # if(Name != "" and result != None):
                #     result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                # if(result != None):
                if(Ori != "" or Marker != ""):
                    return JsonResponse(data = {'success':False, 'data': [],
                                        'pagination':{
                                            'current_page' : 0,
                                            'total_pages' : 0,
                                            'total_count' : 0,
                                            'has_next' : 0,
                                            'has_previous' : 0,
                                            'page_size' : 0,
                                            'offset' : 0
                                            }
                                        },status = 200, safe = False)
                    # PlasmidResult = (list(result.order_by('name').values('plasmidid','name','alias','oricloning','orihost','markercloning','markerhost','level')))
                else:
                    PlasmidResult = []
                    result = Plasmidneed.objects
                    if(Name != "" and result != None):
                        result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                    if(len(result) != 0):
                        temp_result = list(result.values('plasmidid','name','alias','level','tag'))
                        print(temp_result)
                        for each in temp_result:
                            info_list = getOriAndMarker(each['plasmidid'])
                            each['ori_info'] = info_list[0]
                            each['marker_info'] = info_list[1]
                            each['scar'] = Plasmidscartable.objects.filter(plasmidid = each['plasmidid']).first().bbsi
                            PlasmidResult.append(each)
            else:
                PlasmidResult = []
                for each_id in final_plasmid_id_list:
                    result = Plasmidneed.objects.filter(plasmidid = each_id)
                    if(Name != "" and result != None):
                        result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                    if(len(result) != 0):
                        print(result)
                        temp_result = (list(result.values('plasmidid','name','alias','level','tag')))[0]
                        info_list = getOriAndMarker(temp_result['plasmidid'])
                        temp_result['ori_info'] = info_list[0]
                        temp_result['marker_info'] = info_list[1]
                        temp_result['scar'] = Plasmidscartable.objects.filter(plasmidid = temp_result['plasmidid']).first().bbsi
                        PlasmidResult.append(temp_result)
        # print(PlasmidResult)
        if(len(PlasmidResult) != 0):
            total_count = len(PlasmidResult)
            total_pages = (total_count + page_size -1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            if(len(PlasmidResult) < page_size):
                return JsonResponse(data = {'success':True, 'data': list(PlasmidResult[:]),
                                        'pagination':{
                                            'current_page' : page,
                                            'total_pages' : total_pages,
                                            'total_count' : total_count,
                                            'has_next' : has_next,
                                            'has_previous' : has_previous,
                                            'page_size' : page_size,
                                            'offset' : offset
                                            }
                                        })
            return JsonResponse(data = {'success':True, 'data': list(PlasmidResult[offset:offset+page_size]),
                                        'pagination':{
                                            'current_page' : page,
                                            'total_pages' : total_pages,
                                            'total_count' : total_count,
                                            'has_next' : has_next,
                                            'has_previous' : has_previous,
                                            'page_size' : page_size,
                                            'offset' : offset
                                            }
                                        })
        else:
            return JsonResponse(data = {'success':False, 'data': [],
                                        'pagination':{
                                            'current_page' : 0,
                                            'total_pages' : 0,
                                            'total_count' : 0,
                                            'has_next' : 0,
                                            'has_previous' : 0,
                                            'page_size' : 0,
                                            'offset' : 0
                                            }
                                        },status = 200, safe = False)


#search
def SearchByPlasmidName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        print(Name)
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PlasmidList = Plasmidneed.objects.filter(name=Name)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plamsid Not Found"})

def SearchByPlasmidID(request):
    if(request.method == "GET"):
        ID = request.GET.get('ID')
        if(ID == None or ID == ""):
            return JsonResponse(data="ID cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PlasmidList = list(Plasmidneed.objects.filter(plasmidid=ID).values())
        if(len(PlasmidList) > 0):
            for each in PlasmidList:
                info_list = getOriAndMarker(each['plasmidid'])
                each["ori_info"] = info_list[0]
                each["marker_info"] = info_list[1]
            return JsonResponse(data=PlasmidList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plamsid Not Found"})

def SearchByPlasmidAlterName(request):
    if(request.method == "GET"):
        AlterName = request.GET.get('altername')
        if(AlterName == None or AlterName == ""):
            return JsonResponse(data="AlterName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PlasmidList = list(Plasmidneed.objects.filter(alter_name=AlterName).values())
        if(len(PlasmidList) > 0):
            for each in PlasmidList:
                info_list = getOriAndMarker(each['plasmidid'])
                each['ori_info'] = info_list[0]
                each['marker_info'] = info_list[0]
            return JsonResponse(data=PlasmidList, status=200)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':[]})

def SearchByPlasmidSeq(request):
    if(request.method == "GET"):
        Seq = request.GET.get('seq')
        if(Seq == None or Seq == ""):
            return JsonResponse(data="Seq cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Seq can not be empty'})
        PlasmidList = list(Plasmidneed.objects.filter(sequenceconfirm__contains=Seq).values())
        if(len(PlasmidList) > 0):
            for each in PlasmidList:
                info_list = getOriAndMarker(each['plasmidid'])
                each['ori_info'] = info_list[0]
                each['marker_info'] = info_list[1]
            return JsonResponse(data=PlasmidList, status=200,safe = False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':[]})

def SearchPlasmidSequenceByName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name ==""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PlasmidList = Plasmidneed.objects.filter(name=Name)
        result = []
        if(len(PlasmidList) > 0):
            for obj in PlasmidList:
                temp = {}
                temp["Name"] = obj.name
                temp["Sequence"] = obj.sequenceconfirm
                result.append(temp)
            if(len(result) > 0):
                return JsonResponse(data=result, status=200)
                # return JsonResponse({'code':200,'status':'success','data':result})
            else:
                return JsonResponse(data="No such Plasmid", status=404,safe=False)
                # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Not Found'})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Not Found'})

def SearchPlasmidSequenceByID(request):
    if(request.method == "GET"):
        id = request.GET.get('plasmidid')
        if(id == None or id == 0):
            return JsonResponse(data="id cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PlasmidList = list(Plasmidneed.objects.filter(plasmidid = id).values('sequenceconfirm'))
        if(len(PlasmidList) > 0):
            return JsonResponse(data = {'success':True, "data":PlasmidList[0]}, status=200, safe = False)
                # return JsonResponse({'code':200,'status':'success','data':result})
        else:
            return JsonResponse(data={'success':False, "data":"No such Plasmid"}, status=404,safe=False)
                # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Not Found'})
    else:
        return JsonResponse(data={"success":False,'data':'Just GET method'}, status=404,safe=False)
        # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Not Found'})

def SearchByOri(request):
    if(request.method == "GET"):
        Ori = request.GET.get('oriClone')
        if(Ori == None or Ori == ""):
            return JsonResponse(data="OriClone cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Ori can not be empty'})
        plasmid_ori_result = list(Plasmid_Culture_Functions.objects.filter(function_content = Ori, function_type = "ori").values("plasmid_id").distinct())
        Plasmid_result = []
        for each in plasmid_ori_result:
            temp_plasmid = list(Plasmidneed.objects.filter(plasmidid = each['plasmid_id']).first())[0]
            info_list = getOriAndMarker(each['plasmid_id'])
            temp_plasmid["ori_info"] = info_list[0]
            temp_plasmid["marker_info"] = info_list[1]
            Plasmid_result.append(temp_plasmid)
        if(len(Plasmid_result) > 0):
            return JsonResponse(data=Plasmid_result, status=200, safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':200,'status':'failed','data':'Plasmid Not Found'})


def SearchByMarker(request):
    if(request.method == "GET"):
        Marker = request.GET.get('markerHost')
        if(Marker == None or Marker == ""):
            return JsonResponse(data="Marker cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Marker can not be empty'})
        plasmid_marker_result = list(Plasmid_Culture_Functions.objects.filter(function_content = Marker, function_type = "marker").values("plasmid_id").distinct())
        Plasmid_result = []
        for each in plasmid_marker_result:
            temp_plasmid = list(Plasmidneed.objects.filter(plasmidid = each['plasmid_id']).first())[0]
            info_list = getOriAndMarker(each['plasmid_id'])
            temp_plasmid["ori_info"] = info_list[0]
            temp_plasmid["marker_info"] = info_list[1]
            Plasmid_result.append(temp_plasmid)
        if(len(Plasmid_result) > 0):
            return JsonResponse(data=Plasmid_result, status=200, safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plasmid Not Found"})

def SearchByLevel(request):
    if(request.method == "GET"):
        Level = request.GET.get('level')
        if(Level == None or Level == ""):
            return JsonResponse(data="Level cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Level can not be empty'})
        PlasmidList = list(Plasmidneed.objects.filter(level=Level).values())
        if(len(PlasmidList) > 0):
            for each in PlasmidList:
                info_list = getOriAndMarker(each['plasmidid'])
                each['ori_info'] = info_list[0]
                each['marker_info'] = info_list[1]
            return JsonResponse(data=PlasmidList, status=200, safe = False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plasmid Not Found"})


def SearchByPlate(request):
    if(request.method == "GET"):
        Plate = request.GET.get('plate')
        if(Plate == None or Plate == ""):
            return JsonResponse(data="Plate cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plate can not be empty'})
        PlasmidList = list(Plasmidneed.objects.filter(plate=Plate).values())
        if(len(PlasmidList) > 0):
            for each in PlasmidList:
                info_list = getOriAndMarker(each['plasmidid'])
                each['ori_info'] = info_list[0]
                each['marker_info'] = info_list[1]
            return JsonResponse(data=PlasmidList, status=200, safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plasmid Not Found"})

def SearchPlasmidParent(request):
    if(request.method == "GET"):
        plasmidName = request.GET.get('plasmidName')
        if(plasmidName == None or plasmidName == ""):
            return JsonResponse(data="PlasmidName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Name can not be empty'})
        plasmidid = Plasmidneed.objects.filter(name = plasmidName).first().plasmidid
        PlasmidList = Parentplasmidtable.objects.filter(sonplasmidid=plasmidid)
        if(len(PlasmidList) == 0):
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Parent not Found'})
        plasmidNameList = []
        for obj in PlasmidList:
            name = Plasmidneed.objects.get(plasmidid=obj.parentplasmidid).name
            plasmidNameList.append(name)
        if(len(plasmidNameList) > 0):
            return JsonResponse(data=PlasmidList,status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':PlasmidList})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plasmid Parent not Found"})

def SearchPlasmidParentByID(request):
    if(request.method == "GET"):
        plasmidID = request.GET.get('plasmidID')
        if(plasmidID == None or plasmidID == ""):
            return JsonResponse(data="PlasmidID cannot be empty",status = 400, safe=False)
        ParentList = Parentplasmidtable.objects.filter(sonplasmidid=plasmidID)
        if(len(ParentList) == 0):
            return JsonResponse(data = "No Parent Plasmid", status = 404, safe=False)
        PlasmidNameList = []
        for obj in ParentList:
            name = Plasmidneed.objects.get(plasmidid=obj.parentplasmidid).name
            PlasmidNameList.append(name)
        if(len(PlasmidNameList) > 0):
            return JsonResponse(data=PlasmidNameList,status=200,safe=False)
        else:
            return JsonResponse(data = "No such plasmid",status=404,safe=False)
        
def GetParentID(request):
    if(request.method == "GET"):
        plasmidID = request.GET.get('plasmidID')
        if(plasmidID == None or plasmidID == ""):
            return JsonResponse(data="PlasmidID cannot be empty",status = 400, safe=False)
        ParentList = Parentplasmidtable.objects.filter(sonplasmidid=plasmidID)
        if(len(ParentList) == 0):
            return JsonResponse(data = "No Parent Plasmid", status = 404, safe=False)
        ParentIDList = []
        for obj in ParentList:
            ParentIDList.append(obj.parentplasmidid)
        if(len(ParentIDList) > 0):
            return JsonResponse(data=ParentIDList,status=200,safe=False)
        else:
            return JsonResponse(data = "No such plasmid",status=404,safe=False)
        



def SearchPlasmidFileAddress(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PlasmidID = Plasmidneed.objects.filter(name=Name).first().plasmidid
        if(PlasmidID == None):
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Not Found'})
        userid = request.session.get('info')['uid']
        FilterDict = {"userid": userid,"plasmidid": PlasmidID}
        Address = TbPlasmidUserfileaddress.objects.filter(FilterDict).first().fileaddress
        if(Address != ""):
            return JsonResponse(data=Address, status=200, safe=False)
            # return JsonResponse({'code':200,'status':'success','data':Address})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Address Not Found'})

#Add
#TODO:用户管理
def AddPlasmidFileAddress(request):
    if(request.method == "POST"):
        name = request.POST.get('name')
        Address = request.POST.get('address')
        if(name == None or name == "" or Address == None or Address == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name,Address can not be empty'})
        PlasmidID = Plasmidneed.objects.filter(name=name).first().plasmidid
        if(PlasmidID == None):
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Not Found'})
        userid = request.session.get('info')['uid']
        TbPlasmidUserfileaddress.objects.create(plasmidid=PlasmidID, fileaddress=Address, userid=userid)
        return JsonResponse(data="Plasmid Address Added", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Plasmid Address Added'})

def AddPlasmidData(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        name = data['name']
        ori = data['ori']
        marker = data['marker']
        # oriclone = data['oriclone']
        # orihost = data['orihost']
        # markerclone = data['markerclone']
        # markerhost = data['markerhost']
        level = data['level']
        length = len(data['sequence']) if data['sequence']!="" else 0
        sequence = data['sequence']
        plate = data['plate'] if 'plate' in data else ""
        state = data['state'] if 'state' in data else 0
        note = data['note'] if 'note' in data else ""
        alias = data['alias']
        username = request.session['info']['uname']
        ParentInfo = data['ParentInfo'] if 'ParentInfo' in data else ""
        username = request.session.get('info')['uname']
        tag = "abnormal" if (len(ori) > 1 or len(marker) > 1) else "normal"
        if(name == None or name == "" or level == None or level == "" or sequence == None):
            return JsonResponse(data="Required parameter cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name,Level,Sequence,ori,marker information can not be empty'})
        if(Plasmidneed.objects.filter(name = name).first() == None):
            Plasmidneed.objects.create(name=name, oricloning=oriclone, orihost=orihost, markercloning=markerclone,
                                   markerhost=markerhost, level = level, length = length, sequenceconfirm=sequence,
                                   plate=plate, state = state, note=note, alias=alias,CustomParentInfo = ParentInfo)
        else:
            Plasmidneed.objects.filter(name=name).update(name=name, level = level, length = length, sequenceconfirm=sequence,
                                   plate=plate, state = state, note=note, alias=alias,CustomParentInfo = ParentInfo,user=username, tag = tag)
            plasmidid = Plasmidneed.objects.filter(name = name).first()
        for each in ori:
            Plasmid_Culture_Functions.objects.create(plasmid_id = plasmidid, function_content = each, function_type = "ori")
        for each in marker:
            Plasmid_Culture_Functions.objects.create(plasmid_id = plasmidid, function_content = each, function_type = "marker")
        return JsonResponse(data="Plasmid Data Added", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Plasmid Data Added'})

def AddParentPlasmid(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        sonPlasmidName = data['SonPlasmidName']
        ParentPlasmidName = data['ParentPlasmidName']
        if(sonPlasmidName == None or sonPlasmidName == "" or ParentPlasmidName == None or ParentPlasmidName == ""):
            return JsonResponse(data="SonPlasmidName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Name can not be empty'})
        start_time = time.time()
        max_wait_time = 5
        while time.time() - start_time < max_wait_time:
            try:
                with transaction.atomic():
                    sonPlasmidObj = Plasmidneed.objects.select_for_update().get(name = sonPlasmidName)
                    parentPlasmidObj = Plasmidneed.objects.filter(name = ParentPlasmidName).first()
                    if(parentPlasmidObj == None):
                        return JsonResponse(data={"success":False},status=404,safe=False)
                    if(Parentplasmidtable.objects.filter(sonplasmidid = sonPlasmidObj,parentplasmidid = parentPlasmidObj).count() == 0):
                        Parentplasmidtable.objects.create(sonplasmidid=sonPlasmidObj,parentplasmidid = parentPlasmidObj)
                    return JsonResponse(data={"success":True},status=200,safe=False)
            except Plasmidneed.DoesNotExist:
                time.sleep(0.5)
                continue
            except OperationalError as e:
                if 'lock' in str(e).lower():
                    time.sleep(0.5)
                    continue
                raise
        return JsonResponse(data={'success':False,'error':'time out'},status = 400, safe = False)
        # return JsonResponse({'code':200,'status':'success','data':'Parent Plasmid Added'})

def GetParentPart(request):
    if(request.method == 'GET'):
        sonPlasmidid = Plasmidneed.objects.filter(plasmidid = request.GET.get('plasmidid')).first()
        ppResult = Parentparttable.objects.filter(sonplasmidid = sonPlasmidid).values('parentpartid')
        pplist = []
        # print(ppResult)
        for each_id in ppResult:
            pplist.append(list(Parttable.objects.filter(partid = each_id['parentpartid']).values('name','note'))[0])
        # print(pplist)
        return JsonResponse(data={'success':True,'data':pplist},status = 200, safe = False)

def GetParentBackbone(request):
    if(request.method == 'GET'):
        sonPlasmidid = Plasmidneed.objects.filter(plasmidid = request.GET.get('plasmidid')).first()
        pbResult = list(Parentbackbonetable.objects.filter(sonplasmidid = sonPlasmidid).values('parentbackboneid'))
        pblist = []
        for each_id in pbResult:
            pblist.append(list(Backbonetable.objects.filter(id = each_id['parentbackboneid']).values('name','notes'))[0])
        return JsonResponse(data={'success':True, 'data':pblist},status = 200, safe = False)

def GetParentPlasmid(request):
    if(request.method == 'GET'):
        sonPlasmidid = Plasmidneed.objects.filter(plasmidid = request.GET.get('plasmidid')).first()
        ppResult = list(Parentplasmidtable.objects.filter(sonplasmidid = sonPlasmidid).values('parentplasmidid'))
        pplist = []
        for each_id in ppResult:
            pplist.append(list(Plasmidneed.objects.filter(plasmidid = each_id['parentplasmidid']).values('name','note'))[0])
        return JsonResponse(data = {'success':True,'data':pplist},status = 200, safe = False)

def GetSonPlasmid(request):
    if(request.method == "GET"):
        parentPlasmidid = Plasmidneed.objects.filter(plasmidid = request.GET.get('plasmidid')).first()
        spResult = list(Parentplasmidtable.objects.filter(parentplasmidid = parentPlasmidid).values('sonplasmidid'))
        splist = []
        for each_id in spResult:
            splist.append(list(Plasmidneed.objects.filter(plasmidid = each_id['sonplasmidid']).values('name','note'))[0])
        return JsonResponse(data = {'success':True, 'data':splist},status = 200, safe = False)

#Update
def UpdatePlasmidData(request):
    if(request.method == "POST"):
        OriginName = request.POST.get('OriginName')
        if(OriginName == None or OriginName == ""):
            return JsonResponse(data="OriginName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'OriginName can not be empty'})
        PlasmidID = Plasmidneed.objects.get(name=OriginName).plasmidid
        if(PlasmidID == None):
            return JsonResponse(data="No such OriginName", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'OriginName Not Found'})
        newName = request.POST.get('newName')
        newOri = request.POST.get('newOri')
        newMarker = request.POST.get('newMarker')
        newLevel = request.POST.get('newLevel')
        newLength = len(request.POST.get('newSequence'))
        newSequence = request.POST.get('newSequence')
        newPlate = request.POST.get('newPlate')
        newState = request.POST.get('newState')
        newUser = request.session.get('info')['uname']
        newNote = request.POST.get('newNote')
        newAlias = request.POST.get('newAlias')
        tag = "abnormal" if(len(newOri) > 1 or len(newMarker) > 1) else "normal"
        if(newName == None or newName == "" or newSequence == None or newSequence == ""):
            return JsonResponse(data="New Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name,Ori,Marker,Sequence can not be empty'})
        Plasmidneed.objects.filter(plasmidid=PlasmidID).update(name=newName,level=newLevel,length=newLength,sequenceconfirm=newSequence,
                                                               plate=newPlate,alias=newAlias,state = newState,user=newUser,newNote=newNote,tag = tag)
        Plasmid_Culture_Functions.objects.filter(plasmid_id = PlasmidID).delete()
        for each in newOri:
            Plasmid_Culture_Functions.objects.create(plasmid_id = PlasmidID, function_content = each, function_type = "ori")
        for each in newMarker:
            Plasmid_Culture_Functions.objects.create(plasmid_id = PlasmidID, function_content = each, function_type = "marker")
        return JsonResponse(data="Plasmid Data Updated", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Plasmid Data Updated'})


def UpdatePlasmidFileAddress(request):
    if(request.method == "POST"):
        PlasmidName = request.POST.get('name')
        Address = request.POST.get('address')
        if(PlasmidName == None or PlasmidName == "" or Address == None or Address == ""):
            return JsonResponse(data="PlasmidName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed', 'data': 'Plasmid Name, Address can not be empty'})
        plasmidID = Plasmidneed.objects.filter(name=PlasmidName).first().plasmidid
        if(plasmidID == None):
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Not Found'})
        userID = request.session.get('info')['uid']
        FilterDict = {"userid": userID,"plasmidid": plasmidID}
        TbPlasmidUserfileaddress.objects.filter(FilterDict).update(userid=userID,plasmidid=plasmidID,fileaddress=Address)
        return JsonResponse(data="Plasmid File Address Updated", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Plasmid Address Updated'})


#delete
def deletePlasmidData(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed', 'data': 'Plasmid Name can not be empty'})
        PlasmidID = Plasmidneed.objects.filter(name=name).first().plasmidid
        if(PlasmidID == None):
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Not Found'})
        Parentplasmidtable.objects.filter(sonplasmidid=PlasmidID).delete()
        Parentplasmidtable.objects.filter(parenplasmidid=PlasmidID).delete()
        Parentparttable.objects.filter(sonplasmidid = PlasmidID).delete()
        Parentbackbonetable.objects.filter(sonplasmidid = PlasmidID).delete()
        Plasmidscartable.objects.filter(plasmidid = PlasmidID).delete()
        Plasmid_Culture_Functions.objects.filter(plasmid_id = PlasmidID).delete()
        TbPlasmidUserfileaddress.objects.filter(plasmidid=PlasmidID).delete()
        Plasmidneed.objects.filter(name=name).delete()
        return JsonResponse(data="Plasmid Data Deleted", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Plasmid Data Deleted'})

def deletePlasmidFileAddress(request):
    if(request.method == "GET"):
        PlasmidName = request.GET.get('PlasmidName')
        if(PlasmidName == None or PlasmidName == ""):
            return JsonResponse(data="PlasmidName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Name can not be empty'})
        PlasmidID = Plasmidneed.objects.filter(name=PlasmidName).first().plasmidid
        if(PlasmidID == None):
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Not Found'})
        userid = request.session.get('info')['uid']
        FilterDict = {"userid": userid,"plasmidid": PlasmidID}
        TbPlasmidUserfileaddress.objects.filter(**FilterDict).delete()
        return JsonResponse(data="Plasmid File Address Deleted", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Plasmid Address Deleted'})


def DeleteParentPlasmid(request):
    if(request.method == "GET"):
        ParentPlasmidName = request.GET.get('plasmidName')
        if(ParentPlasmidName == None or ParentPlasmidName == ""):
            return JsonResponse(data="ParentPlasmidName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Name can not be empty'})
        ParentPlasmidID = Plasmidneed.objects.filter(name=ParentPlasmidName).first().plasmidid
        if(ParentPlasmidID == None):
            return JsonResponse(data="No such ParentPlasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Not Found'})
        Parentplasmidtable.objects.get(parentplasmidid=ParentPlasmidID).delete()
        return JsonResponse(data="ParentPlasmid Deleted", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Parent Plasmid Deleted'})

def setPlasmidCulture(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        plasmidName = data["name"]
        Ori_list = data["ori"]
        Marker_list = data["marker"]
        print(data)
        start_time = time.time()
        max_wait_time = 5
        while time.time() - start_time < max_wait_time:
            try:
                with transaction.atomic():
                    plasmidid = Plasmidneed.objects.filter(name=plasmidName).first()
                    print(plasmidid)
                    Plasmid_culture_exist = Plasmid_Culture_Functions.objects.filter(plasmid_id = plasmidid).values()
                    if(len(Plasmid_culture_exist) != 0):
                        Plasmid_Culture_Functions.objects.filter(plasmid_id = plasmidid).delete()
                    for each_ori in Ori_list:
                        print(each_ori)
                        Plasmid_Culture_Functions.objects.create(plasmid_id = plasmidid,function_content = each_ori, function_type = "ori")
                    for each_marker in Marker_list:
                        print(each_marker)
                        Plasmid_Culture_Functions.objects.create(plasmid_id = plasmidid,function_content = each_marker, function_type="marker")
                    return JsonResponse(data = {"success":True,"data":"success upload"},status=200, safe=False)
            except Plasmidneed.DoesNotExist:
                time.sleep(0.5)
                continue
            except OperationalError as e:
                if 'lock' in str(e).lower():
                    time.sleep(0.5)
                    continue
                raise
        print("timeout")
        return JsonResponse(data={'success':False,'error':'time out'},status = 400, safe = False)










#----------------------------------------------------------
#Backbone table
def getdefaultbackbonescar(backboneid):
    scar_info = Backbonescartable.objects.filter(backboneid = backboneid).first().bbsi
    return scar_info
#Search
def BackboneDataALL(request):
    if(request.method == "GET"):
        page = int(request.GET.get('page',0))
        if(page == 0):
            BackboneData = Backbonetable.objects.all().order_by('name').values()
            if(len(BackboneData) > 0):
                BackboneData = list(BackboneData)
                for each in BackboneData:
                    info_list = getBackboneOriAndMarker(each['id'])
                    each['ori'] = info_list[0]
                    each['marker'] = info_list[1]
                    each['scar'] = getdefaultbackbonescar(each['id'])
                return JsonResponse(data={'success': True, 'data':BackboneData}, status=200,safe=False)
                # return JsonResponse({'code':200,'data':list(PartData.values())})
            else:
                return JsonResponse(data={'success':False, 'error':"No such backbone"}, status=404,safe=False)
                # return JsonResponse({'code':204,'status': 'failed', 'data': []})
        else:
            page_size = int(request.GET.get('page_size',10))
            offset = (page -1)*page_size
            total_count = Backbonetable.objects.count()
            total_pages = (total_count + page_size -1) // page_size
            query_set = Backbonetable.objects.order_by('name').values('id','name','alias','marker','ori','species','tag')[offset:offset+page_size]
            # query_set = Backbonetable.objects.only('id','name','marker','ori','species').all().order_by('name')[offset:offset+page_size]
            query_set = list(query_set)
            for each in query_set:
                info_list = getBackboneOriAndMarker(each['id'])
                each['ori'] = info_list[0]
                each['marker'] = info_list[1]
                each['scar'] = getdefaultbackbonescar(each['id'])
            has_next = page < total_pages
            has_previous = page > 1
            return JsonResponse(data={'success':True,
                                      'data':query_set,
                                      'pagination':{
                                          'current_page' : page,
                                          'total_pages' : total_pages,
                                          'total_count' : total_count,
                                          'has_next':has_next,
                                          'has_previous' : has_previous,
                                          'page_size':page_size,
                                          'offset':offset
                                          }
                                        },status = 200, safe=False
                                )

#Backbone filter

def BackboneFilter(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        # print(data)
        ori = data['ori']
        marker = data['marker']
        Enzyme = data['Enzyme']
        Scar = data['Scar']
        Name = data['name']
        page = data['page']
        page_size = data['page_size']
        offset = (page -1)*page_size
        scarBackboneid = []
        if(Enzyme == "BsmBI"):
            scarBackboneid = list(Backbonescartable.objects.filter(bsmbi = Scar).values('backboneid'))
        elif(Enzyme == "BsaI"):
            scarBackboneid = list(Backbonescartable.objects.filter(bsai = Scar).values('backboneid'))
        elif(Enzyme == "BbsI"):
            scarBackboneid = list(Backbonescartable.objects.filter(bbsi = Scar).values('backboneid'))
        elif(Enzyme == "AarI"):
            scarBackboneid = list(Backbonescartable.objects.filter(aari = Scar).values('backboneid'))
        elif(Enzyme == "SapI"):
            scarBackboneid = list(Backbonescartable.objects.filter(sapi = Scar).values('backboneid'))
        if(Enzyme != "" and len(scarBackboneid) == 0):
            return JsonResponse(data={'success':False,'error':'No data'}, status = 404, safe = False)
        # print(scarBackboneid)
        BackboneResult = []
        # print(scarBackboneid)
        if(len(scarBackboneid) != 0):
            for each_id in scarBackboneid:
                # print(each_id)
                result = Backbonetable.objects
                result = result.filter(id = each_id['backboneid'])
                if(ori != ""):
                    ori_result = Backbone_Culture_Functions.objects.filter(backbone_id =each_id['backboneid']).values()
                    if(len(ori_result) == 0):
                        continue
                if(marker != ""):
                    marker_result = Backbone_Culture_Functions.objects.filter(backbone_id = each_id['backboneid'].values())
                    if(len(marker_result) == 0):
                        continue
                # print(result)
                # if(ori != "" and result != None):
                #     # 'partid','name','type','sourceorganism','reference'
                #     result = result.filter(ori = ori)
                #     # print(result.values())
                # if(marker != "" and result != None):
                #     result = result.filter(marker = marker)
                if(Name != "" and result != None):
                    result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                if(len(result) != 0):
                    # print(result.order_by('name').values('id','name','marker','ori','species'))
                    # PartResult.append(result.order_by('name').values('partid','name','type','sourceorganism','reference'))
                    temp_result = list(result.order_by('name').values('id','name','alias','species','tag'))[0]
                    info_list = getBackboneOriAndMarker(temp_result['id'])
                    temp_result['ori'] = info_list[0]
                    temp_result['marker'] = info_list[1]
                    temp_result['scar'] = Scar
                    BackboneResult.append(temp_result)
        else:
            Ori_backbone_id_list = set()
            Marker_backbone_id_list = set()
            final_backbone_id_list = set()
            if(ori != ""):
                Ori_result = Backbone_Culture_Functions.objects.filter(function_content = ori, function_type="ori").values("backbone_id")
                for each in Ori_result:
                    Ori_backbone_id_list.add(each['backbone_id'])
            if(marker != ""):
                Marker_result = Backbone_Culture_Functions.objects.filter(function_content = marker, function_type="marker").values("backbone_id")
                for each in Marker_result:
                    Marker_backbone_id_list.add(each['backbone_id'])
            if(ori != "" and marker != ""):
                final_backbone_id_list = Ori_backbone_id_list & Marker_backbone_id_list
            else:
                final_backbone_id_list = Ori_backbone_id_list | Marker_backbone_id_list
            # print(Ori_plasmid_id_list)
            # print(Marker_plasmid_id_list)
            # print(final_plasmid_id_list)
            if(len(final_backbone_id_list) == 0):
                # if(Name != "" and result != None):
                #     result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                # if(result != None):
                if(ori != "" or marker != ""):
                    return JsonResponse(data = {'success':False, 'data': [],
                                        'pagination':{
                                            'current_page' : 0,
                                            'total_pages' : 0,
                                            'total_count' : 0,
                                            'has_next' : 0,
                                            'has_previous' : 0,
                                            'page_size' : 0,
                                            'offset' : 0
                                            }
                                        },status = 200, safe = False)
                else:
                    BackboneResult = []
                    result = Backbonetable.objects
                    if(Name != "" and result != None):
                        result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                    if(len(result) != 0):
                        temp_result = list(result.values('id','name','alias','marker','ori','species','tag'))
                        for each in temp_result:
                            info_list = getBackboneOriAndMarker(each['id'])
                            each['ori'] = info_list[0]
                            each['marker'] = info_list[1]
                            each['scar'] = Backbonescartable.objects.filter(backboneid = each['id']).first().bbsi
                            BackboneResult.append(each)
                    # PlasmidResult = (list(result.order_by('name').values('plasmidid','name','alias','oricloning','orihost','markercloning','markerhost','level')))
            else:
                BackboneResult = []
                for each_id in final_backbone_id_list:
                    result = Backbonetable.objects.filter(id = each_id)
                    if(Name != "" and result != None):
                        result = result.filter(Q(name__icontains = Name) | Q(alias__icontains = Name))
                    if(len(result) != 0):
                        print(result)
                        temp_result = (list(result.values('id','name','alias','marker','ori','species','tag')))[0]
                        info_list = getBackboneOriAndMarker(temp_result['id'])
                        temp_result['ori'] = info_list[0]
                        temp_result['marker'] = info_list[1]
                        temp_result['scar'] = Backbonescartable.objects.filter(backboneid = temp_result['id']).first().bbsi
                        BackboneResult.append(temp_result)
        print(BackboneResult)
        if(len(BackboneResult) != 0):
            total_count = len(BackboneResult)
            total_pages = (total_count + page_size -1) // page_size
            has_next = page < total_pages
            has_previous = page > 1

            # data={'success':True,
            #                           'data':list(query_set.values()),
            #                           'pagination':{
            #                               'current_page' : page,
            #                               'total_pages' : total_pages,
            #                               'total_count' : total_count,
            #                               'has_next':has_next,
            #                               'has_previous' : has_previous,
            #                               'page_size':page_size,
            #                               'offset':offset
            #                               }
            #                             },status = 200, safe=False
            if(len(BackboneResult) < page_size):
                return JsonResponse(data = {'success':True, 'data': list(BackboneResult[:]),
                                        'pagination':{
                                            'current_page' : page,
                                            'total_pages' : total_pages,
                                            'total_count' : total_count,
                                            'has_next' : has_next,
                                            'has_previous' : has_previous,
                                            'page_size' : page_size,
                                            'offset' : offset
                                            }
                                        })
            else:
                return JsonResponse(data = {'success':True, 'data': list(BackboneResult[offset:offset+page_size]),
                                        'pagination':{
                                            'current_page' : page,
                                            'total_pages' : total_pages,
                                            'total_count' : total_count,
                                            'has_next' : has_next,
                                            'has_previous' : has_previous,
                                            'page_size' : page_size,
                                            'offset' : offset
                                            }
                                        })
            
        else:
            # return JsonResponse(data = {'success':False, 'error':'No data'},status = 404, safe = False)
            return JsonResponse(data = {'success':False, 'data': [],
                                        'pagination':{
                                            'current_page' : 0,
                                            'total_pages' : 0,
                                            'total_count' : 0,
                                            'has_next' : 0,
                                            'has_previous' : 0,
                                            'page_size' : 0,
                                            'offset' : 0
                                            }
                                        },status = 200, safe = False)



def SearchByBackboneName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Name can not be empty'})
        BackboneList = list(Backbonetable.objects.filter(name=Name).values())
        if(len(BackboneList) > 0):
            for each_id in BackboneList:
                info_list = getBackboneOriAndMarker(each_id['id'])
                each_id['ori'] = info_list[0]
                each_id['marker'] = info_list[1]
            return JsonResponse(data=BackboneList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such Name", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchByBackboneID(request):
    if(request.method == "GET"):
        ID = request.GET.get('ID')
        if(ID == None or ID == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        BackboneList = list(Backbonetable.objects.filter(id=ID).values())
        if(len(BackboneList) > 0):
            for each in BackboneList:
                info_list = getBackboneOriAndMarker(each['id'])
                each['ori'] = info_list[0]
                each['marker'] = info_list[1]

            return JsonResponse(data=BackboneList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plamsid Not Found"})

def  SearchByBackboneSeq(request):
    if(request.method == "GET"):
        Seq = request.GET.get('seq')
        if(Seq == None or Seq == ""):
            return JsonResponse(data="Seq cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Sequence can not be empty'})
        BackboneList = list(Backbonetable.objects.filter(sequence=Seq).values())
        if(len(BackboneList) > 0):
            for each in BackboneList:
                info_list = getBackboneOriAndMarker(each['id'])
                each['ori'] = info_list[0]
                each['marker'] = info_list[1]
            return JsonResponse(data=BackboneList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such backbone", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def GetBackboneSeqByID(request):
    if(request.method == "GET"):
        ID = request.GET.get('backboneid')
        if(ID ==None or ID == 0):
            return JsonResponse(data = {'success':False,'data':"Parameter is empty"},status=404, safe = False)
        else:
            BackboneSeq = list(Backbonetable.objects.filter(id=ID).values('sequence'))
            if(len(BackboneSeq) > 0):
                return JsonResponse(data = {'success':True, 'data':BackboneSeq[0]},status = 200, safe = False)
            else:
                return JsonResponse(data = {'success':False,'data':"No such backbone"},status = 404, safe=False)
    else:
        return JsonResponse(data = {'success':False,'data':'Only Get method'},status = 400, safe = False)


def SearchByBackboneSpecies(request):
    if(request.method == "GET"):
        Species = request.GET.get('species')
        if(Species == None or Species == ""):
            return JsonResponse(data="Species cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Species can not be empty'})
        BackboneList = list(Backbonetable.objects.filter(species=Species).values())
        if(len(BackboneList) > 0):
            for each in BackboneList:
                info_list = getBackboneOriAndMarker(each['id'])
                each['ori'] = info_list[0]
                each['marker'] = info_list[1]
            return JsonResponse(data=BackboneList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such Species", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchByBackboneMarker(request):
    if(request.method == "GET"):
        Marker = request.GET.get('marker')
        if(Marker == None or Marker == ""):
            return JsonResponse(data="Marker cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Marker can not be empty'})
        backbone_result = list(Backbone_Culture_Functions.objects.filter(function_content = Marker, function_type = "marker").values('backbone_id').distinct())
        if(len(backbone_result) > 0):
            BackboneList = []
            for each in backbone_result:
                backbone_each_result = list(Backbonetable.objects.filter(id = each['backbone_id']).values())[0]
                info_list = getBackboneOriAndMarker(backbone_each_result['id'])
                backbone_each_result['ori'] = info_list[0]
                backbone_each_result['marker'] = info_list[1]
                BackboneList.append(backbone_each_result)
            return JsonResponse(data=BackboneList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such Marker", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchByBackboneOri(request):
    if(request.method == "GET"):
        Ori = request.GET.get('ori')
        if(Ori == None or Ori == ""):
            return JsonResponse(data="Ori cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Ori can not be empty'})
        backbone_result = list(Backbone_Culture_Functions.objects.filter(function_content = Ori, function_type = "ori").values('backbone_id').distinct())
        if(len(backbone_result) > 0):
            BackboneList = []
            for each in backbone_result:
                backbone_each_result = list(Backbonetable.objects.filter(id = each['backbone_id']).values())[0]
                info_list = getBackboneOriAndMarker(backbone_each_result['id'])
                backbone_each_result['ori'] = info_list[0]
                backbone_each_result['marker'] = info_list[1]
                BackboneList.append(backbone_each_result)
            return JsonResponse(data=BackboneList, status=200,safe=False)
        else:
            return JsonResponse(data="No such Ori", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchByCopyNumber(request):
    if(request.method == 'GET'):
        CopyNumber = request.GET.get('copynumber')
        if(CopyNumber == None or CopyNumber == ""):
            return JsonResponse(data="CopyNumber cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'CopyNumber can not be empty'})
        BackboneList = list(Backbonetable.objects.filter(copynumber = CopyNumber).values())
        if(len(BackboneList) > 0):
            for each in BackboneList:
                info_list = getBackboneOriAndMarker(each['id'])
                each['ori'] = info_list[0]
                each['marker'] = info_list[1]
            return JsonResponse(data=BackboneList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such CopyNumber", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchBackboneFileAddress(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name can not be empty'})
        BackboneID = Backbonetable.objects.filter(name=name).first().id
        if(BackboneID == None):
            return JsonResponse(data="No such Backbone", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Backbone Not Found'})
        userid = request.session.get('info')['uid']
        FilterDict = {"userid": userid,"backboneid":BackboneID}
        BackboneAddress = TbBackboneUserfileaddress.objects.filter(**FilterDict).first().fileaddress
        if(BackboneAddress != ""):
            return JsonResponse(data=BackboneAddress, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':BackboneAddress})
        else:
            return JsonResponse(data="No such Backbone Address", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Address Found'})
#Add
def AddBackboneData(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        name = data['name']
        length = len(data['sequence']) if data['sequence'] != "" else 0
        sequence = data['sequence']
        #list
        ori = data['ori']
        marker = data['marker']
        
        species = data['species']
        copynumber = data['copynumber'] if 'copynumber' in data else ""
        note = data['note'] if 'note' in data else ""
        alias = data['alias'] if 'alias' in data else ""
        username = request.session['info']['uname']
        print(data)
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name, sequence can not be empty'})
        tag = "abnormal" if (len(ori) > 1 or len(marker) > 1) else "normal"
        if(Backbonetable.objects.filter(name = name).first() != None):
            Backbonetable.objects.filter(name = name).update(name=name, length=length, sequence=sequence,
                                    species = species,copynumber=copynumber, notes=note, alias=alias,user=username, tag=tag)
            backbone_id = Backbonetable.objects.filter(name = name).first()
            Backbone_Culture_Functions.objects.filter(backbone_id = backbone_id.id).delete()
        else:
            Backbonetable.objects.create(name=name, length=length, sequence=sequence, ori=ori, marker=marker,
                                    species = species,copynumber=copynumber, notes=note, alias=alias,user=username, tag=tag)
            backbone_id = Backbonetable.objects.filter(name = name).first()
        for each in ori:
            Backbone_Culture_Functions.objects.create(backbone_id = backbone_id, function_content = each, function_type = 'ori')
        for each in marker:
            Backbone_Culture_Functions.objects.create(backbone_id = backbone_id, function_content = each, function_type = "marker")
        return JsonResponse(data="Added backbone data", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Backbone Data Added'})

#TODO:用户管理
def AddBackboneFileAddress(request):
    if(request.method == "POST"):
        Backbonename = request.POST.get('name')
        Address = request.POST.get('address')
        if(Backbonename == None or Backbonename == "" or Address == None or Address == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name,address can not be empty'})
        BackboneID = Backbonetable.objects.filter(name = Backbonename).first().id
        if(BackboneID == None):
            return JsonResponse(data="No such BackboneID", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Backbone Not Found'})
        userid = request.session.get('info')['uid']
        TbBackboneUserfileaddress.objects.create(userid=userid, backboneid=BackboneID, fileaddress=Address)
        return JsonResponse(data="Added backbone data", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Backbone Address Added'})

#Update
def UpdateBackboneData(request):
    if(request.method == "POST"):
        OriginalName = request.POST.get('OriginalName')
        if(OriginalName == None or OriginalName == ""):
            return JsonResponse(data="OriginalName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Original name can not be empty'})
        BackboneID = Backbonetable.objects.filter(name = OriginalName).first().id
        if(BackboneID == None):
            return JsonResponse(data="No such BackboneID", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Backbone Not Found'})
        newName = request.POST.get('newName')
        newLength = len(request.POST.get('sequence'))
        newSequence = request.POST.get('sequence')
        #list
        newOri = request.POST.get('ori')
        newMarker = request.POST.get('marker')
        
        newSpecies = request.POST.get('species')
        newCopynumber = request.POST.get('copynumber')
        newNote = request.POST.get('note')
        newScar = request.POST.get('scar')
        newAlias = request.POST.get('alias')
        newUser = request.session.get('info')['uname']
        tag = "abnormal" if (len(newOri) >1 or len(newMarker) > 1) else "normal"
        if(newName == None or newName == "" or newSequence == None or newSequence == ""):
            return JsonResponse(data="Name and sequence cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name, Sequence can not be empty'})
        Backbonetable.objects.filter(id=BackboneID).update(name=newName, length=newLength, sequence=newSequence,
                                                           species=newSpecies,copynumber=newCopynumber,notes=newNote,
                                                           scar=newScar,alias=newAlias,user=newUser)
        Backbone_Culture_Functions.objects.filter(backbone_id = BackboneID).delete()
        for each in newOri:
            Backbone_Culture_Functions.objects.create(backbone_id = BackboneID, function_content = each, function_type = "ori")
        for each in newMarker:
            Backbone_Culture_Functions.objects.create(backbone_id = BackboneID, function_content = each, function_type = "marker")
        return JsonResponse(data="Added backbone data", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Backbone Data Updated'})

def UpdateBackboneCultureInformation(request):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        id = data['backboneid']
        OriInfo = data['Ori']
        MarkerInfo = data['Marker']
        Backbonetable.objects.filter(id = id).update(ori = OriInfo,marker = MarkerInfo)
        return JsonResponse(data = {'success':True},status = 200, safe=False)
    

def UpdatePlasmidCultureInformation(request):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        id = data['plasmidid']
        OriInfo1 = data['Ori1']
        OriInfo2 = data['Ori2']
        MarkerInfo1 = data['Marker1']
        MarkerInfo2 = data['Marker2']
        Plasmidneed.objects.filter(plasmidid = id).update(oricloning = OriInfo1, orihost = OriInfo2, markercloning = MarkerInfo1, markerhost = MarkerInfo2)
        return JsonResponse(data = {'success':True},status = 200, safe=False)


def UpdateBackboneFileAddress(request):
    if(request.method == 'POST'):

        Name = request.POST.get('name')
        Address = request.POST.get('address')
        if(Name == None or Name == "" or Address == None or Address == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name can not be empty'})
        BackboneID = Backbonetable.objects.filter(name = Name).first().id
        if(BackboneID == None):
            return JsonResponse(data="No such BackboneID", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Backbone Not Found'})
        userID = request.session.get('info')['uid']
        FilterDict = {"backboneid": BackboneID,"userid": userID}
        TbBackboneUserfileaddress.objects.filter(**FilterDict).update(userid=userID, backboneid=BackboneID,fileaddress=Address)
        return JsonResponse(data="Added backbone data", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Backbone Address Updated'})

#Delete
def DeleteBackboneData(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name can not be empty'})
        BackboneID = Backbonetable.objects.filter(name = Name).first().id
        if(BackboneID == None):
            return JsonResponse(data="No such BackboneID", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Backbone Not Found'})
        TbBackboneUserfileaddress.objects.filter(backboneid=BackboneID).delete()
        Parentbackbonetable.objects.filter(parentbackboneid = BackboneID).delete()
        Backbonescartable.objects.filter(backboneid = BackboneID).delete()
        Backbone_Culture_Functions.objects.filter(backbone_id = BackboneID).delete()
        Backbonetable.objects.filter(id=BackboneID).delete()
        return JsonResponse(data="Deleted backbone data", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Backbone Data Deleted'})

def DeleteBackboneFileAddress(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name can not be empty'})
        BackboneID = Backbonetable.objects.filter(name = name).first().id
        if(BackboneID == None):
            return JsonResponse(data="No such BackboneID", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Backbone Not Found'})
        userid = request.session.get('info')['uid']
        FilterDict = {"userid": userid,"backboneid": BackboneID}
        TbBackboneUserfileaddress.objects.filter(**FilterDict).delete()
        return JsonResponse(data="Deleted backbone data", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Backbone Address Deleted'})


def setBackboneCulture(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        BackboneName = data["name"]
        Ori_list = data["ori"]
        Marker_list = data["marker"]
        start_time = time.time()
        max_wait_time = 5
        while time.time() - start_time < max_wait_time:
            try:
                with transaction.atomic():
                    backboneid = Backbonetable.objects.filter(name=BackboneName).first()
                    Backbone_culture_exist = Backbone_Culture_Functions.objects.filter(backbone_id = backboneid).values()
                    if(len(Backbone_culture_exist) != 0):
                        Backbone_Culture_Functions.objects.filter(backbone_id = backboneid).delete()
                    for each_ori in Ori_list:
                        Backbone_Culture_Functions.objects.create(backbone_id = backboneid,function_content = each_ori, function_type = "ori")
                    for each_marker in Marker_list:
                        Backbone_Culture_Functions.objects.create(backbone_id = backboneid,function_content = each_marker, function_type="marker")
                    return JsonResponse(data = {"success":True,"data":"success upload"},status=200, safe=False)
            except Plasmidneed.DoesNotExist:
                time.sleep(0.5)
                continue
            except OperationalError as e:
                if 'lock' in str(e).lower():
                    time.sleep(0.5)
                    continue
                raise
        print("timeout")
        return JsonResponse(data={'success':False,'error':'time out'},status = 400, safe = False)









#=========================================================================================
#TestData
def SearchByTestdataName(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name can not be empty'})
        TestData = Testdatatable.objects.filter(name = name)
        if(len(TestData) > 0):
            return JsonResponse(data=list(TestData.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(TestData.values())})
        else:
            return JsonResponse(data="No such TestData", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Test Data Found'})







#=============================================================================================
#DBD
def GetDBDList(request):
    if(request.method == "GET"):
        DBDList = Dbdtable.objects.all()
        DBDDict = []
        if(len(DBDList) > 0):
            for DBD in DBDList:
                PartObj = Parttable.objects.filter(name = DBD.name).first()
                # DBDDict[DBD.name] = [PartObj.alias,PartObj.level0sequence,PartObj.sourceorganism,PartObj.reference,PartObj.note,PartObj.confirmedsequence,PartObj.insertsequence,DBD.i0,DBD.kd]
                DBDDict.append({"Name":DBD.name,"Alias": PartObj.alias,"Level0Sequence":PartObj.level0sequence,"SourceOrganism":PartObj.sourceorganism,"Reference":PartObj.reference,"Note":PartObj.note,"ConfirmedSequence":PartObj.confirmedsequence,"InsertSequence":PartObj.insertsequence,"I0": DBD.i0,"kd": DBD.kd})
                # DBDDict.append([DBD.name,PartObj.alias,PartObj.level0sequence,PartObj.sourceorganism,PartObj.reference,PartObj.note,PartObj.confirmedsequence,PartObj.insertsequence,DBD.i0,DBD.kd])
            return JsonResponse(data=DBDDict, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(DBDList)})
        else:
            return JsonResponse(data="No such DBDList", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No DB Data Found'})

def GetDBDNameList(request):
    if(request.method == "GET"):
        DBDNameList = Dbdtable.objects.all()
        Namelist = []
        if(len(DBDNameList) > 0):
            for obj in DBDNameList:
                Namelist.append(obj.name)
            return JsonResponse(data=Namelist, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':Namelist})
        else:
            return JsonResponse(data="No DBD List", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No DB Data Found'})

def GetDBDKdList(request):
    if(request.method == "GET"):
        DBDKdList = Dbdtable.objects.all()
        KdList = []
        if(len(DBDKdList) > 0):
            for obj in DBDKdList:
                KdList.append(obj.kd)
            return JsonResponse(data=KdList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':KdList})
        else:
            return JsonResponse(data="No DBD List", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No DB Data Found'})

def GetDBD(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"name can not be empty"})
        DBD = Dbdtable.objects.filter(name = name)
        if(DBD != None):
            return JsonResponse(data=list(DBD.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(DBD)})
        else:
            return JsonResponse(data="No such DBD", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No DB Data Found'})

def GetDBDAllByName(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"name can not be empty"})
        DBD = Dbdtable.objects.filter(name = name).first()
        if(DBD != None):
            part_obj = Parttable.objects.filter(name = name).first()
            DBD_list = {"Name":DBD.name,"Alias": part_obj.alias,"Level0Sequence":part_obj.level0sequence,"SourceOrganism":part_obj.sourceorganism,"Reference":part_obj.reference,"Note":part_obj.note,"ConfirmedSequence":part_obj.confirmedsequence,"InsertSequence":part_obj.insertsequence,"I0": DBD.i0,"kd": DBD.kd}
            # DBD_list = [DBD.name,part_obj.alias,part_obj.level0sequence,part_obj.sourceorganism,part_obj.reference,part_obj.note,part_obj.confirmedsequence,part_obj.insertsequence,DBD.i0,DBD.kd]
            return JsonResponse(data = DBD_list, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(DBD)})
        else:
            return JsonResponse(data="No such DBD", status=404,safe=False)

def GetDBDMenu(request):
    if(request.method == "GET"):
        DBDList = Dbdtable.objects.all()
        DBDMenu = []
        if(len(DBDMenu) > 0):
            for obj in DBDMenu:
                DBDMenu.append({"name":"obj.name","i0":obj.i0,"kd":obj.kd})
                # DBDMenu[obj.name] = [obj.i0,obj.kd]
            return JsonResponse(data=DBDMenu, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':DBDMenu})
        else:
            return JsonResponse(data="No DBD Menu", status=404,safe=False)

def GetDBDKd(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name can not be empty'})
        DBDKd = Dbdtable.objects.filter(name=name).first().kd
        if(DBDKd != None):
            return JsonResponse(data={'Kd':DBDKd}, status=200)
            # return JsonResponse({'code':200,'status':'success','data':DBDKd})
        else:
            return JsonResponse(data="No such DBD", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No DB Data Found'})

def AddDBD(request):
    if(request.method == "POST"):
        Name = request.POST.get('name')
        I0 = float(request.POST.get('i0'))
        kd = float(request.POST.get('kd'))
        if(Name == None or I0 == None or kd == None or Name == "" or I0 == 0 or kd == 0):
            return JsonResponse(data="Name,I0,Kd cannot be empty", status=400,safe=False)
        else:
            Dbdtable.objects.create(name=Name, i0=I0, kd=kd)
            return JsonResponse(data="Added DBD", status=200,safe=False)

def UpdateDBD(request):
    if(request.method == "POST"):
        Name = request.POST.get('name')
        I0 = float(request.POST.get('i0'))
        kd = float(request.POST.get('kd'))
        if (Name == None or I0 == None or kd == None or Name == "" or I0 == 0 or kd == 0):
            return JsonResponse(data="Name,I0,Kd cannot be empty", status=400, safe=False)
        else:
            dbdobj = Dbdtable.objects.filter(name=Name)
            if(len(dbdobj)>0):
                dbdobj.update(i0=I0, kd=kd)
                return JsonResponse(data="Updated DBD", status=200, safe=False)
            else:
                return JsonResponse(data="No such DBD",status=404,safe=False)




#===================================================================================================
#LBD Dimer
def GetLBDDimer(request):
    if(request.method == "GET"):
        LBDDimerList = Lbddimertable.objects.all()
        LBDDimerDict = []
        if(len(LBDDimerList) > 0):
            for obj in LBDDimerList:
                PartObj = Parttable.objects.filter(name = obj.name).first()
                # LBDDimerDict[obj.name] = [PartObj.alias,PartObj.level0sequence,PartObj.sourceorganism,PartObj.reference,PartObj.note,PartObj.confirmedsequence,PartObj.insertsequence,obj.k1,obj.k2,obj.k3,obj.i]
                LBDDimerDict.append({"name":obj.name,"alias":PartObj.alias,"level0sequence":PartObj.level0sequence,"sourceorganism":PartObj.sourceorganism,"reference":PartObj.reference,"note":PartObj.note,"confirmedsequence":PartObj.confirmedsequence,"insertsequence":PartObj.insertsequence,"k1":obj.k1,"k2":obj.k2,"k3":obj.k3,"i":obj.i})
            return JsonResponse(data=LBDDimerDict, status=200)
            # return JsonResponse({'code':200,'status':'success','data':list(LBDDimerList)})
        else:
            return JsonResponse(data="No such LBDDimer", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No LBD Dimer Data Found'})


def GetLBDDimerMenu(request):
    if(request.method == "GET"):
        LBDDimerList = Lbddimertable.objects.all()
        LBDMenu = []
        if(len(LBDDimerList) > 0):
            for obj in LBDDimerList:
                LBDMenu.append({"name":obj.name,'k1':obj.k1,'k2':obj.k2,'k3':obj.k3,'i':obj.i})
                # LBDMenu[obj.name] = [obj.k1,obj.k2,obj.k3,obj.i]
            return JsonResponse(data=LBDMenu, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':LBDMenu})
        else:
            return JsonResponse(data="No such LBDDimer", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No LBD Dimer Data Found'})

def GetLBDDimerAllByName(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"name can not be empty"})
        LBD = Lbddimertable.objects.filter(name = name).first()
        if(LBD != None):
            part_obj = Parttable.objects.filter(name = name).first()
            LBD_list = {"name":LBD.name,"alias":part_obj.alias,"level0sequence":part_obj.level0sequence,"sourceorganism":part_obj.sourceorganism,"reference":part_obj.reference,"note":part_obj.note,"confirmedsequence":part_obj.confirmedsequence,"insertsequence":part_obj.insertsequence,"k1":LBD.k1,"k2":LBD.k2,"k3":LBD.k3,"i":LBD.i}
            # LBD_list = [LBD.name,part_obj.alias,part_obj.level0sequence,part_obj.sourceorganism,part_obj.reference,part_obj.note,part_obj.confirmedsequence,part_obj.insertsequence,LBD.k1,LBD.k2,LBD.k3,LBD.i]
            return JsonResponse(data = LBD_list, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(DBD)})
        else:
            return JsonResponse(data="No such LBD Dimer", status=404,safe=False)


def GetLBDDimerNameList(request):
    if(request.method == "GET"):
        LBDDimerList = Lbddimertable.objects.all()
        NameList = []
        if(len(LBDDimerList) > 0):
            for obj in LBDDimerList:
                NameList.append(obj.name)
            print(NameList)
            return JsonResponse(data=NameList, status=200, safe=False)
            # return JsonResponse({'code':200,'status':'success','data':NameList})
        else:
            return JsonResponse(data="No such LBDDimer", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No LBD Dimer Data Found'})

def AddLBDDimer(request):
    if(request.method == "POST"):
        Name = request.POST.get('name')
        k1 = float(request.POST.get('k1'))
        k2 = float(request.POST.get('k2'))
        k3 = float(request.POST.get('k3'))
        I = float(request.POST.get('i'))
        if(Name == None or Name == "" or k1 == None or k1 == 0 or k2 == None
                or k2 == 0 or k3 == None or k3 == 0 or I == None or I == 0):
            return JsonResponse(data="Name,k1,k2,k3,I cannot be empty", status=400,safe=False)
        else:
            Lbddimertable.objects.create(name=Name, k1=k1, k2=k2, k3=k3, I=I)
            return JsonResponse(data="Added LBDDimer", status=200,safe=False)

def UpdateLbdDimer(request):
    if(request.method == "POST"):
        Name = request.POST.get('name')
        k1 = float(request.POST.get('k1'))
        k2 = float(request.POST.get('k2'))
        k3 = float(request.POST.get('k3'))
        I = float(request.POST.get('i'))
        if (Name == None or Name == "" or k1 == None or k1 == 0 or k2 == None
                or k2 == 0 or k3 == None or k3 == 0 or I == None or I == 0):
            return JsonResponse(data="Name,k1,k2,k3,I cannot be empty", status=400, safe=False)
        else:
            LBDObj = Lbddimertable.objects.filter(name=Name)
            if(len(LBDObj)>0):
                LBDObj.update(k1=k1, k2=k2, k3=k3, I=I)
                return JsonResponse(data="Updated LBD Dimer", status=200, safe=False)
            else:
                return JsonResponse(data="No such LBD Dimer", status=404, safe=False)



#===================================================================================================
#LBD NR
def GetLBDNr(request):
    if(request.method == "GET"):
        LBDNrList = Lbdnrtable.objects.all()
        LBDList = []
        if(len(LBDNrList) > 0):
            for obj in LBDNrList:
                PartObj = Parttable.objects.filter(name=obj.name).first()
                LBDList.append({"name":obj.name,"alias":PartObj.alias,"level0sequence":PartObj.level0sequence,"sourceorganism":PartObj.sourceorganism,"reference":PartObj.reference,"note":PartObj.note,"confirmedsequence":PartObj.confirmedsequence,"insertsequence":PartObj.insertsequence,"k1":obj.k1,"k2":obj.k2,"k3":obj.k3,"kx1":obj.kx1,"kx2":obj.kx2})
                # LBDList[obj.name] = [PartObj.alias,PartObj.level0sequence,PartObj.sourceorganism,PartObj.reference,PartObj.note,PartObj.confirmedsequence,PartObj.insertsequence,obj.k1,obj.k2,obj.k3,obj.kx1,obj.kx2]
            return JsonResponse(data=LBDList, status=200)
            # return JsonResponse({'code':200,'status':'success','data':list(LBDList)})
        else:
            return JsonResponse(data="No such LBDNr", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No LBDNr Data Found'})




def GetLBDNRMenu(request):
    if(request.method == "GET"):
        LBDNrList = Lbdnrtable.objects.all()
        LBDNRMenu = []
        if(len(LBDNrList) > 0):
            for obj in LBDNrList:
                # LBDNRMenu[obj.name] = [obj.k1,obj.k2,obj.k3,obj.kx1,obj.kx2]
                LBDNRMenu.append({"name":obj.name,"k1":obj.k1,"k2":obj.k2,"k3":obj.k3,"kx1":obj.kx1,"kx2":obj.kx2})
            return JsonResponse(data=LBDNRMenu, status=200)
            # return JsonResponse({'code':200,'status':'success','data':LBDNRMenu})
        else:
            return JsonResponse(data="No such LBDNr", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No LBDNR Data Found'})

def GetLBDNRAllByName(request):
    if(request.method == "GET"):
        name = request.GET.get('name')
        if(name == None or name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"name can not be empty"})
        LBD = Lbdnrtable.objects.filter(name = name).first()
        if(LBD != None):
            part_obj = Parttable.objects.filter(name = name).first()
            LBD_list = {"name":LBD.name,"alias":part_obj.alias,"level0sequence":part_obj.level0sequence,"sourceorganism":part_obj.sourceorganism,"reference":part_obj.reference,"note":part_obj.note,"confirmedsequence":part_obj.confirmedsequence,"insertsequence":part_obj.insertsequence,"k1":LBD.k1,"k2":LBD.k2,"k3":LBD.k3,"kx1":LBD.kx1,"kx2":LBD.kx2}
            # LBD_list = [LBD.name,part_obj.alias,part_obj.level0sequence,part_obj.sourceorganism,part_obj.reference,part_obj.note,part_obj.confirmedsequence,part_obj.insertsequence,LBD.k1,LBD.k2,LBD.k3,LBD.i]
            return JsonResponse(data = LBD_list, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(DBD)})
        else:
            return JsonResponse(data="No such LBD Dimer", status=404,safe=False)


def GetLBDNRNameList(request):
    if(request.method == "GET"):
        LBDNRList = Lbdnrtable.objects.all()
        LBDNameList = []
        if(len(LBDNRList) > 0):
            for obj in LBDNRList:
                LBDNameList.append(obj.name)
            return JsonResponse(data=LBDNameList, status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':LBDNRMenu})
        else:
            return JsonResponse(data="No such LBDNR", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No LBDNR Data Found'})


def AddLbdnr(request):
    if(request.method == "POST"):
        Name = request.POST.get('name')
        k1 = float(request.POST.get('k1'))
        k2 = float(request.POST.get('k2'))
        k3 = float(request.POST.get('k3'))
        kx1 = float(request.POST.get('kx1'))
        kx2 = float(request.POST.get('kx2'))
        if(Name == None or Name == "" or k1 == None or k1 == 0 or k2 == None or k2 == 0 or k3 == None
        or k3 == 0 or kx1 == None or kx1 == 0 or kx2 == None or kx2 == 0):
            return JsonResponse(data="Name,k1,k2,k3,kx1,kx2 cannot be empty", status=400,safe=False)
        else:
            Lbdnrtable.objects.create(name=Name,k1=k1,k2=k2,k3=k3,kx1=kx1,kx2=kx2)
            return JsonResponse(data="Added LBD NR", status=200,safe=False)

def UpdateLBDnr(request):
    if(request.method == "POST"):
        Name = request.POST.get('name')
        k1 = float(request.POST.get('k1'))
        k2 = float(request.POST.get('k2'))
        k3 = float(request.POST.get('k3'))
        kx1 = float(request.POST.get('kx1'))
        kx2 = float(request.POST.get('kx2'))
        if (Name == None or Name == "" or k1 == None or k1 == 0 or k2 == None or k2 == 0 or k3 == None
                or k3 == 0 or kx1 == None or kx1 == 0 or kx2 == None or kx2 == 0):
            return JsonResponse(data="Name,k1,k2,k3,kx1,kx2 cannot be empty", status=400, safe=False)
        else:
            Lbdnrtable.objects.filter(name=Name).update(k1 = k1,k2=k2,k3=k3,kx1=kx1,kx2=kx2)
            return JsonResponse(data="Updated LBD NR", status=200, safe=False)

def GetPartIDByName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name != None and Name != ""):
            ID = Parttable.objects.filter(name = Name).first()
            if(ID != None):
                return JsonResponse(data = {"PartID":ID.partid},status=200,safe=False)
            else:
                return JsonResponse(data = "No such part",status=404, safe=False)
        else:
            return JsonResponse(data = "Name cannot be empty",status=400,safe=False)

def GetPartSeqByID(request):
    if(request.method == "GET"):
        ID = request.GET.get('partid')
        if(ID == None or ID == 0):
            return JsonResponse(data = {"success":False,"data":"Parameter is empty"}, status = 400, safe = False)
        else:
            sequence = list(Parttable.objects.filter(partid = ID).values('level0sequence'))
            if(len(sequence) > 0):
                return JsonResponse(data = {'success':True,'data':sequence[0]}, status = 200, safe = False)
            else:
                return JsonResponse(data = {'success':False, "data":"No such part"},status = 404, safe = False)
    else:
        return JsonResponse(data = {'success':False,'data':'Only GET method'},status = 404, safe = False)




def GetBackboneIDByName(request):
    if(request.method == 'GET'):
        Name = request.GET.get('name')
        if(Name != None and Name != ''):
            ID = Backbonetable.objects.filter(name=Name).first()
            if(ID != None):
                return JsonResponse(data={"BackboneID":ID.id},status=200,safe=False)
            else:
                return JsonResponse(data = "No such Backbone",status=404, safe=False)
        else:
            return JsonResponse(data="Name cannot be empty",status=400,safe=False)

def GetPlasmidIDByName(request):
    if(request.method=='GET'):
        Name = request.GET.get('name')
        if(Name != None and Name != ""):
            ID = Plasmidneed.objects.filter(name = Name).first()
            if(ID != None):
                return JsonResponse(data = {"PlasmidID":ID.plasmidid},status=200,safe=False)
            else:
                return JsonResponse(data = "No such Plasmid",status=400, safe=False)
        else:
            return JsonResponse(data = "Name cannot be empty",status=400,safe=False)


def AddPlasmidParentInfo(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        plasmidName = data["PlasmidName"]
        ParentInfo = data["PlasmidParentInfo"]
        print(data)
        if(plasmidName == "" or ParentInfo == ""):
            print("empty")
            return JsonResponse(data = {"success":False,"data":"Parameter is empty"},status = 400, safe=False)
        start_time = time.time()
        max_wait_time = 5
        while time.time() - start_time < max_wait_time:
            try:
                with transaction.atomic():
                    Plasmidneed.objects.filter(name=plasmidName).update(CustomParentInfo = ParentInfo)
                    return JsonResponse(data = {"success":True,"data":"success upload"},status=200, safe=False)
            except Plasmidneed.DoesNotExist:
                time.sleep(0.5)
                continue
            except OperationalError as e:
                if 'lock' in str(e).lower():
                    time.sleep(0.5)
                    continue
                raise
        print("timeout")
        return JsonResponse(data={'success':False,'error':'time out'},status = 400, safe = False)



    
def AddParentPart(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        print(data)
        sonPlasmidName = data['SonPlasmidName']
        ParentPartName = data['ParentPartName']
        print(sonPlasmidName)
        # print(sonPlasmidName)
        # print(ParentPartName)
        if(sonPlasmidName == None or sonPlasmidName == "" or ParentPartName == None or ParentPartName == ""):
            return JsonResponse(data="PlasmidName or PartName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Name can not be empty'})
        start_time = time.time()
        max_wait_time = 5
        while time.time() - start_time < max_wait_time:
            try:
                with transaction.atomic():
                    sonPlasmidObj = Plasmidneed.objects.select_for_update().get(name = sonPlasmidName)
                    parentPartObj = Parttable.objects.filter(name = ParentPartName).first()
                    if(parentPartObj == None):
                        return JsonResponse(data={"success":False},status=404,safe=False)
                    if(Parentparttable.objects.filter(sonplasmidid = sonPlasmidObj,parentpartid = parentPartObj).count() == 0):
                        Parentparttable.objects.create(sonplasmidid=sonPlasmidObj,parentpartid = parentPartObj)
                    return JsonResponse(data={"success":True},status=200,safe=False)
            except Plasmidneed.DoesNotExist:
                time.sleep(0.5)
                continue
            except Parttable.DoesNotExist:
                time.sleep(0.5)
                continue
            except OperationalError as e:
                if 'lock' in str(e).lower():
                    time.sleep(0.5)
                    continue
                raise
        return JsonResponse(data={'success':False,'error':'time out'},status = 400, safe = False)
                # sonPlasmidID = Plasmidneed.objects.filter(name=sonPlasmidName).first()
                # if(sonPlasmidID == None):
                    # return JsonResponse(data="No such SonPlasmid", status=404,safe=False)
                    # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Not Found'})
        # parentPartList = ParentPartName.split(',')
        # if(len(parentPartList) == 0):
        #     return JsonResponse(data="No such ParentPart", status=404,safe=False)
        #     # return JsonResponse({'code':204,'status': 'failed', 'data': 'The Number of Parent Plasmid should greater than 0'})
        # for parent in parentPartList:
        #     parentpartID = Parttable.objects.filter(name=parent).first()
        #     if(parentpartID != None):
        #         Parentparttable.objects.create(sonplasmidid=sonPlasmidID, parentpartid=parentpartID)
        #     else:
        #         return JsonResponse(data="Parent Part Not Found", status=404,safe=False)
        #         # return JsonResponse({'code':403,'status':'failed','data':'Parent Plasmid Not Found'})
        # return JsonResponse(data="Parent Part Added", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Parent Plasmid Added'})

def AddParentBackbone(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        sonPlasmidName = data['SonPlasmidName']
        ParentBackboneName = data['ParentBackboneName']
        print(data)
        if(sonPlasmidName == None or sonPlasmidName == "" or ParentBackboneName == None or ParentBackboneName == ""):
            return JsonResponse(data="PlasmidName or BackboneName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Name can not be empty'})
        start_time = time.time()
        max_wait_time = 5
        while time.time() - start_time < max_wait_time:
            try:
                with transaction.atomic():
                    sonPlasmidObj = Plasmidneed.objects.select_for_update().get(name = sonPlasmidName)
                    parentBackboneObj = Backbonetable.objects.filter(name = ParentBackboneName).first()
                    # print(parentBackboneObj)
                    if(parentBackboneObj == None):
                        return JsonResponse(data={"success":False},status=404,safe=False)
                    print(Parentbackbonetable.objects.filter(sonplasmidid = sonPlasmidObj,parentbackboneid = parentBackboneObj).count())
                    if(Parentbackbonetable.objects.filter(sonplasmidid = sonPlasmidObj,parentbackboneid = parentBackboneObj).count() == 0):
                        Parentbackbonetable.objects.create(sonplasmidid=sonPlasmidObj,parentbackboneid = parentBackboneObj)
                    return JsonResponse(data={"success":True},status=200,safe=False)
            except Plasmidneed.DoesNotExist:
                time.sleep(0.5)
                continue
            except Backbonetable.DoesNotExist:
                time.sleep(0.5)
                continue
            except OperationalError as e:
                if 'lock' in str(e).lower():
                    time.sleep(0.5)
                    continue
                raise
        return JsonResponse(data={'success':False,'error':'time out'},status = 400, safe = False)

        # sonPlasmidID = Plasmidneed.objects.filter(name=sonPlasmidName).first()
        # if(sonPlasmidID == None):
        #     return JsonResponse(data="No such SonPlasmid", status=404,safe=False)
        #     # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Not Found'})
        # parentBackboneList = ParentBackboneName.split(',')
        # if(len(parentBackboneList) == 0):
        #     return JsonResponse(data="No such Parent Backbone", status=404,safe=False)
        #     # return JsonResponse({'code':204,'status': 'failed', 'data': 'The Number of Parent Plasmid should greater than 0'})
        # for parent in parentBackboneList:
        #     parentBackboneID = Backbonetable.objects.filter(name=parent).first()
        #     if(parentBackboneID != None):
        #         Parentbackbonetable.objects.create(sonplasmidid=sonPlasmidID, parentbackboneid=parentBackboneID)
        #     else:
        #         return JsonResponse(data="Parent Backbone Not Found", status=404,safe=False)
        #         # return JsonResponse({'code':403,'status':'failed','data':'Parent Plasmid Not Found'})
        # return JsonResponse(data="Parent Backbone Added", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Parent Plasmid Added'})

def getPartValueList(request,column):
    if(request.method == 'GET'):
        if(column != None and column != ""):
            categories = Parttable.objects.values_list(column,flat=True).distinct()
            categories_list = list(categories)
            for each_cate in categories_list:
                if(each_cate == "_" or each_cate == ""):
                    categories_list.remove(each_cate)
            return JsonResponse(data={'success':True,'data':categories_list}, status = 200, safe=False)
        else:
            return JsonResponse(data="column cannot be empty",status=400, safe=False)
        
def getBackboneValueList(request,column):
    if(request.method == 'GET'):
        if(column != None and column != ""):
            if(column == "ori"):
                categories = Backbone_Culture_Functions.objects.filter(function_type = "ori").values_list("function_content").distinct()
                categories_list = list(categories)
            elif(column == "marker"):
                categories = Backbone_Culture_Functions.objects.filter(function_type = "marker").values_list("function_content").distinct()
                categories_list = list(categories)
            else:
                categories = Backbonetable.objects.values_list(column,flat=True).distinct()
                categories_list = list(categories)
            for each_cate in categories_list:
                if(each_cate == "_" or each_cate == ""):
                    categories_list.remove(each_cate)
            return JsonResponse(data={'success':True,'data':categories_list}, status = 200, safe=False)
        else:
            return JsonResponse(data="column cannot be empty",status=400, safe=False)

def getPlasmidValueList(request,column):
    if(request.method == 'GET'):
        if(column != None and column != ""):
            if(column == "ori" or column == "marker"):
                categories = list(Plasmid_Culture_Functions.objects.filter(function_type = column).values("function_content").distinct())
                categories_list = []
                for each_cate in categories:
                    categories_list.append(each_cate['function_content'])
                print(categories_list)
                return JsonResponse(data={'success':True,'data':categories_list}, status = 200, safe=False)
            else:
                categories = Plasmidneed.objects.values_list(column,flat=True).distinct()
                categories_list = list(categories)
                for each_cate in categories_list:
                    if(each_cate == "_" or each_cate == ""):
                        categories_list.remove(each_cate)
                return JsonResponse(data={'success':True,'data':categories_list}, status = 200, safe=False)
        else:
            return JsonResponse(data="column cannot be empty",status=400, safe=False)

#======================================================================
#Part Scar Operation      
def getPartScar(request):
    if(request.method == 'GET'):
        name = request.GET.get('name')
        if(name != None and name != ""):
            part_object = Parttable.objects.filter(name = name).first()
            scar_info = Partscartable.objects.filter(partid = part_object).first().values()
            if(scar_info != None):
                return JsonResponse(data = {'success':True,'scar_info':list(scar_info)},status = 200, safe = False)
            else:
                return JsonResponse(data = {'success': False,'error':"No such scar information"},status = 400, safe = False)
        else:
            return JsonResponse(data={'success':False, 'error':"Name cannot be empty"},status = 400,safe=False)


def setPartScar(request):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        print(data)
        name = data['name']
        bsmbi = data['bsmbi']
        bsai = data['bsai']
        bbsi = data['bbsi']
        aari = data['aari']
        sapi = data['sapi']
        if(name != None and name != ""):
            start_time = time.time()
            max_wait_time = 5
            while time.time() - start_time < max_wait_time:
                try:
                    with transaction.atomic():
                        # part_obj = Parttable.objects.filter(name = name).first()
                        part_obj = Parttable.objects.select_for_update().get(name=name)
                        if(len(Partscartable.objects.filter(partid = part_obj)) != 0):
                            Partscartable.objects.filter(partid = part_obj).update(bsmbi = bsmbi, bsai = bsai, bbsi = bbsi,aari = aari, sapi = sapi)
                        else:
                            Partscartable.objects.create(partid = part_obj, bsmbi = bsmbi, bsai = bsai, bbsi = bbsi,aari = aari, sapi = sapi)
                        return JsonResponse(data = {'success':True}, status = 200, safe = False)
                except Parttable.DoesNotExist:
                    time.sleep(0.5)
                    continue
                except OperationalError as e:
                    if 'lock' in str(e).lower():
                        time.sleep(0.5)
                        continue
                    raise
            return JsonResponse(data={'success':False,'error':'time out'},stauts = 400, safe = False)
        else:
            return JsonResponse(data={'success':False,'error':'Name cannot be empty'},stauts = 400, safe = False)
    else:
        return JsonResponse(data = {'success' : False,'error' : 'Just Post request'},status = 400, safe=False)

#==================================================================================
#Backbone Scar Operation
def getBackboneScar(request):
    if(request.method == 'GET'):
        id = request.GET.get('id')
        if(id != None and id != ""):
            # backbone_object = Backbonetable.objects.filter(name = ).first()
            scar_info = Backbonescartable.objects.filter(backboneid = id).values("bsmbi", "bsai", "bbsi", "aari", "sapi")
            if(scar_info != None):
                return JsonResponse(data = {'success':True,'scar_info':list(scar_info)},status = 200, safe = False)
            else:
                return JsonResponse(data = {'success': False,'error':"No such scar information"},status = 400, safe = False)
        else:
            return JsonResponse(data={'success':False, 'error':"id cannot be empty"},status = 400,safe=False)
    else:
        return JsonResponse(data = {'success':False, 'error':'Just GET method'},status = 400, safe=False)

def setBackboneScar(request):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        print(data)
        name = data['name']
        bsmbi = data['bsmbi']
        bsai = data['bsai']
        bbsi = data['bbsi']
        aari = data['aari']
        sapi = data['sapi']
        if(name != None and name != ""):
            start_time = time.time()
            max_wait_time = 5
            while time.time() - start_time < max_wait_time:
                try:
                    with transaction.atomic():
                        # backbone_obj = Backbonetable.objects.filter(name = name).first()
                        backbone_obj = Backbonetable.objects.get(name = name)
                        if(len(Backbonescartable.objects.filter(backboneid = backbone_obj)) != 0):
                            Backbonescartable.objects.filter(backboneid = backbone_obj).update(bsmbi = bsmbi, bsai = bsai, bbsi = bbsi,aari = aari, sapi = sapi)
                        else:
                            Backbonescartable.objects.create(backboneid = backbone_obj, bsmbi = bsmbi, bsai = bsai, bbsi = bbsi,aari = aari, sapi = sapi)
                        return JsonResponse(data = {'success':True}, status = 200, safe = False)
                except Backbonetable.DoesNotExist:
                    time.sleep(0.5)
                    print("7777777")
                    continue
                except OperationalError as e:
                    if 'lock' in str(e).lower():
                        time.sleep(0.5)
                        continue
                    raise
            return JsonResponse(data={'success':False,'error':'time out'},stauts = 400, safe = False)
        else:
            return JsonResponse(data={'success':False,'error':'Name cannot be empty'},status = 400, safe = False)
    else:
        return JsonResponse(data = {'success' : False,'error' : 'Just Post request'},status = 400, safe=False)
    


#=====================================================================================
#Plasmid Scar Operation
def getPlasmidScar(request):
    if(request.method == 'GET'):
        plasmidid = request.GET.get('plasmidid')
        if(plasmidid != None and plasmidid != ""):
            scar_info = Plasmidscartable.objects.filter(plasmidid = plasmidid).values()
            print(scar_info)
            if(scar_info != None):
                return JsonResponse(data = {'success':True,'scar_info':list(scar_info)},status = 200, safe = False)
            else:
                return JsonResponse(data = {'success': False,'error':"No such scar information"},status = 400, safe = False)
        else:
            return JsonResponse(data="Name cannot be empty",status = 400,safe=False)

def setPlasmidScar(request):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        print(data)
        name = data['name']
        bsmbi = data['bsmbi']
        bsai = data['bsai']
        bbsi = data['bbsi']
        aari = data['aari']
        sapi = data['sapi']
        if(name != None and name != ""):
            start_time = time.time()
            max_wait_time = 5
            while time.time() - start_time < max_wait_time:
                try:
                    with transaction.atomic():
                        # plasmid_obj = Plasmidneed.objects.filter(name = name).first()
                        plasmid_obj = Plasmidneed.objects.get(name = name)
                    if(len(Plasmidscartable.objects.filter(plasmidid = plasmid_obj)) != 0):
                        Plasmidscartable.objects.filter(plasmidid = plasmid_obj).update(bsmbi = bsmbi, bsai = bsai, bbsi = bbsi,aari = aari, sapi = sapi)
                    else:
                        Plasmidscartable.objects.create(plasmidid = plasmid_obj, bsmbi = bsmbi, bsai = bsai, bbsi = bbsi,aari = aari, sapi = sapi)
                    return JsonResponse(data = {'success':True}, status = 200, safe = False)
                except Plasmidneed.DoesNotExist:
                    time.sleep(0.5)
                    continue
                except OperationalError as e:
                    if 'lock' in str(e).lower():
                        time.sleep(0.5)
                        continue
                    raise
            return JsonResponse(data={'success':False,'error':'time out'},stauts = 400, safe = False)

        else:
            return JsonResponse(data={'success':False,'error':'Name cannot be empty'},stauts = 400, safe = False)
    else:
        return JsonResponse(data = {'success' : False,'error' : 'Just Post request'},status = 400, safe=False)
    

def getPartScarList(request):
    if(request.method == "GET"):
        # bsmbi = request.POST.get('bsmbi')
        # bsai = request.POST.get('bsai')
        # bbsi = request.POST.get('bbsi')
        # aari = request.POST.get('aari')
        # sapi = request.POST.get('sapi')
        categories1 = list(Partscartable.objects.values_list('bsmbi',flat = True).distinct())
        categories2 = list(Partscartable.objects.values_list('bsai',flat = True).distinct())
        categories3 = list(Partscartable.objects.values_list('bbsi',flat = True).distinct())
        categories4 = list(Partscartable.objects.values_list('aari',flat = True).distinct())
        categories5 = list(Partscartable.objects.values_list('sapi',flat = True).distinct())
        categories_list = []
        for each_cate in categories1:
            if(each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories2:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories3:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories4:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories5:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        return JsonResponse(data = {'success':True,'data':categories_list}, status=200,safe=False)

def getBackboneScarList(request):
    if(request.method == "GET"):
        # bsmbi = request.POST.get('bsmbi')
        # bsai = request.POST.get('bsai')
        # bbsi = request.POST.get('bbsi')
        # aari = request.POST.get('aari')
        # sapi = request.POST.get('sapi')
        categories1 = list(Backbonescartable.objects.values_list('bsmbi',flat = True).distinct())
        categories2 = list(Backbonescartable.objects.values_list('bsai',flat = True).distinct())
        categories3 = list(Backbonescartable.objects.values_list('bbsi',flat = True).distinct())
        categories4 = list(Backbonescartable.objects.values_list('aari',flat = True).distinct())
        categories5 = list(Backbonescartable.objects.values_list('sapi',flat = True).distinct())
        categories_list = []
        for each_cate in categories1:
            if(each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories2:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories3:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories4:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories5:
            if(categories_list.__contains__(each_cate) == False and each_cate != "_" and each_cate != ""):
                categories_list.append(each_cate)
        return JsonResponse(data = {'success':True,'data':categories_list}, status=200,safe=False)

def getPlasmidScarList(request):
    if(request.method == "GET"):
        # bsmbi = request.POST.get('bsmbi')
        # bsai = request.POST.get('bsai')
        # bbsi = request.POST.get('bbsi')
        # aari = request.POST.get('aari')
        # sapi = request.POST.get('sapi')
        categories1 = list(Plasmidscartable.objects.values_list('bsmbi',flat = True).distinct())
        categories2 = list(Plasmidscartable.objects.values_list('bsai',flat = True).distinct())
        categories3 = list(Plasmidscartable.objects.values_list('bbsi',flat = True).distinct())
        categories4 = list(Plasmidscartable.objects.values_list('aari',flat = True).distinct())
        categories5 = list(Plasmidscartable.objects.values_list('sapi',flat = True).distinct())
        categories_list = []
        for each_cate in categories1:
            if(each_cate != '_' and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories2:
            if(categories_list.__contains__(each_cate) == False and each_cate != '_' and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories3:
            if(categories_list.__contains__(each_cate) == False and each_cate != '_' and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories4:
            if(categories_list.__contains__(each_cate) == False and each_cate != '_' and each_cate != ""):
                categories_list.append(each_cate)
        for each_cate in categories5:
            if(categories_list.__contains__(each_cate) == False and each_cate != '_' and each_cate != ""):
                categories_list.append(each_cate)
        return JsonResponse(data = {'success':True,'data':categories_list}, status=200,safe=False)


def UpdatePartSequence(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        name = data['name']
        sequence = data['sequence']
        # NewLength = len(request.POST.get('Level0Sequence'))
        # NewLevel0Sequence = request.POST.get('Level0Sequence')
        try:
            part_obj = Parttable.objects.select_for_update().get(name = name)
            # Parttable.objects.filter(name = part_obj.name).update(lengthinlevel0 = len(sequence), Level0Sequence = sequence)
            part_obj.lengthinlevel0 = len(sequence)
            part_obj.level0sequence = sequence
            part_obj.save()
            return JsonResponse(data = {'success': True}, status = 200, safe = False)
        except Parttable.DoesNotExist:
            return JsonResponse(data = {'success':False, 'message':"Part Does Not Exist"}, status = 404, safe = False)
    else:
        return JsonResponse(data = {'success':False, 'message' : "just POST method"}, status = 500, safe = False)

def UpdateBackboneSequence(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        name = data['name']
        sequence = data['sequence']
        try:
            backbone_obj = Backbonetable.objects.select_for_update().get(name = name)
            # Backbonetable.objects.filter(id = backboneid).update(length = len(sequence), sequence = sequence)
            # Backbonetable.objects.filter(name = backbone_obj.name).update(length = len(sequence), sequence = sequence)
            backbone_obj.sequence = sequence
            backbone_obj.length = len(sequence)
            backbone_obj.save()
            return JsonResponse(data = {'success': True}, status = 200, safe = False)
        except Backbonetable.DoesNotExist:
            return JsonResponse(data = {'success':False, 'message':"Backbone Does Not Exist"}, status = 404, safe = False)
    else:
        return JsonResponse(data = {'success':False, 'message' : "just POST method"}, status = 500, safe = False)
    
def UpdatePlasmidSequence(request):
    if(request.method == "POST"):
        data = json.loads(request.body)
        name = data['name']
        sequence = data['sequence']
        try:
            with transaction.atomic():
                # sonPlasmidObj = Plasmidneed.objects.select_for_update().get(name = sonPlasmidName)
                plasmid_obj = Plasmidneed.objects.select_for_update().get(name = name)
                plasmid_obj.sequenceconfirm = sequence
                plasmid_obj.length = len(sequence)
                # Plasmidneed.objects.filter(name = plasmid_obj.name).update(length = len(sequence), sequenceconfirm = sequence)
                plasmid_obj.save()
                return JsonResponse(data = {'success': True}, status = 200, safe = False)
        except Plasmidneed.DoesNotExist:
            return JsonResponse(data = {'success':False, 'message':"Plasmid Does Not Exist"}, status = 404, safe = False)
    else:
        return JsonResponse(data = {'success':False, 'message' : "just POST method"}, status = 500, safe = False)