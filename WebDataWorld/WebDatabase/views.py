import django.core.exceptions
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.core import serializers
import math
from django.core import serializers
from django.utils.deprecation import MiddlewareMixin
from .models import (Backbonetable,Parentplasmidtable,
                    Partrputable,Parttable,Plasmidneed,
                    Straintable,TbBackboneUserfileaddress,
                    TbPartUserfileaddress,TbPlasmidUserfileaddress,
                    Testdatatable,User,Lbdnrtable,Lbddimertable,Dbdtable)
from .serializers import StraintableSerializer, BackbonetableSerializer, ParentplasmidtableSerializer, \
    PartrputableSerializer,ParttableSerializer,PlasmidneedSerializer,TbBackboneUserfileaddressSerializer,\
    TbPartUserfileaddressSerializer,TbPlasmidUserfileaddressSerializer,TestdatatableSerializer

#----------------------------------------------------------
#用户登录验证(中间件)
class User_auth(MiddlewareMixin):

    def process_request(self,request):
        #排除不需要登录就能访问的页面
        if request.path_info == "/WebDatabase/login":
            return
        info = request.session.get('info')
        print(info)
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
    if(request.method == "GET"):
        PartData = Parttable.objects.all().order_by('name')
        if(len(PartData) > 0):
            return JsonResponse(data=list(PartData.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'data':list(PartData.values())})
        else:
            return JsonResponse(data="No such part", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': []})
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
        name = request.POST.get('name')
        alias = request.POST.get('alias')
        length = len(request.POST.get('Level0Sequence'))
        level0Seq = request.POST.get('Level0Sequence')
        ConfirmedSequence = request.POST.get('ConfirmedSequence')
        InsertSequence = request.POST.get('InsertSequence')
        sourceOrganism = request.POST.get("source")
        reference = request.POST.get("reference")
        note = request.POST.get("note")
        type = request.POST.get("type")
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
        if(name == "" or name == None or level0Seq == "" or ConfirmedSequence == "" or InsertSequence == ""):
            return JsonResponse(data="Parameters name, sequence cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name or Sequence can not be empty'})
        Parttable.objects.create(name=name, alias=alias, lengthinlevel0=length, level0sequence=level0Seq,
                                confirmedsequence = ConfirmedSequence, insertsequence = InsertSequence,
                                sourceorganism = sourceOrganism, reference=reference, note=note, type=type,)
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

def SearchByPlasmidAlterName(request):
    if(request.method == "GET"):
        AlterName = request.GET.get('altername')
        if(AlterName == None or AlterName == ""):
            return JsonResponse(data="AlterName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name can not be empty'})
        PlasmidList = Plasmidneed.objects.filter(alter_name=AlterName)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
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
        PlasmidList = Plasmidneed.objects.filter(sequenceconfirm__contains=Seq)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
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

def SearchByOriClone(request):
    if(request.method == "GET"):
        Ori = request.GET.get('oriClone')
        if(Ori == None or Ori == ""):
            return JsonResponse(data="OriClone cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Ori can not be empty'})
        PlasmidList = Plasmidneed.objects.filter(oricloning=Ori)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':200,'status':'failed','data':'Plasmid Not Found'})



def SearchByOriHost(request):
    if(request.method == "GET"):
        Ori = request.GET.get('oriHost')
        if(Ori == None or Ori == ""):
            return JsonResponse(data="OriHost cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Ori can not be empty'})
        PlasmidList = Plasmidneed.objects.filter(orihost=Ori)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':"Plasmid Not Found"})

def SearchByMarkerClone(request):
    if(request.method == "GET"):
        marker = request.GET.get('markerClone')
        if(marker == None or marker ==""):
            return JsonResponse(data="MarkerClone cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Marker can not be empty'})
        PlasmidList = Plasmidneed.objects.filter(markercloning=marker)
        if (len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
            # return JsonResponse({'code':200,'status':'success','data':list(PlasmidList.values())})
        else:
            return JsonResponse(data="No such Plasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Plasmid Not Found'})

def SearchByMarkerHost(request):
    if(request.method == "GET"):
        Marker = request.GET.get('markerHost')
        if(Marker == None or Marker == ""):
            return JsonResponse(data="Marker cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Marker can not be empty'})
        PlasmidList = Plasmidneed.objects.filter(markerhost=Marker)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
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
        PlasmidList = Plasmidneed.objects.filter(level=Level)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
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
        PlasmidList = Plasmidneed.objects.filter(plate=Plate)
        if(len(PlasmidList) > 0):
            return JsonResponse(data=list(PlasmidList.values()), status=200)
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
        name = request.POST.get('name')
        oriclone = request.POST.get('oriclone')
        orihost = request.POST.get('orihost')
        markerclone = request.POST.get('markerclone')
        markerhost = request.POST.get('markerhost')
        level = request.POST.get('level')
        length = len(request.POST.get('sequence'))
        sequence = request.POST.get('sequence')
        plate = request.POST.get('plate')
        state = request.POST.get('state')
        note = request.POST.get('note')
        alias = request.POST.get('alias')
        if(name == None or name == "" or level == None or level == "" or sequence == None or sequence == ""
                 or orihost == None or orihost == "" or markerclone == None or markerclone == "" or oriclone == None
                 or orihost == "" or markerhost == None or markerhost == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name,Level,Sequence,ori,marker information can not be empty'})
        Plasmidneed.objects.create(name=name, oricloning=oriclone, orihost=orihost, markercloning=markerclone,
                                   markerhost=markerhost, level = level, length = length, sequenceconfirm=sequence,
                                   plate=plate, state = state, note=note, alias=alias)
        return JsonResponse(data="Plasmid Data Added", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Plasmid Data Added'})

def AddParentPlasmid(request):
    if(request.method == "POST"):
        sonPlasmidName = request.POST.get('SonPlasmidName')
        ParentPlasmidName = request.POST.get('ParentPlasmidName')
        if(sonPlasmidName == None or sonPlasmidName == "" or ParentPlasmidName == None or ParentPlasmidName == ""):
            return JsonResponse(data="SonPlasmidName cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Name can not be empty'})
        sonPlasmidID = Plasmidneed.objects.filter(name=sonPlasmidName).first().plasmidid
        if(sonPlasmidID == None):
            return JsonResponse(data="No such SonPlasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Plasmid Not Found'})
        parentPlasmidList = ParentPlasmidName.split(',')
        if(len(parentPlasmidList) == 0):
            return JsonResponse(data="No such ParentPlasmid", status=404,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'The Number of Parent Plasmid should greater than 0'})
        for parent in parentPlasmidList:
            parentplasmidID = Plasmidneed.objects.filter(name=parent).first().plasmidid
            if(parentplasmidID != None):
                Parentplasmidtable.objects.create(sonplasmidid=sonPlasmidID, parentplasmidid=parentplasmidID)
            else:
                return JsonResponse(data="Parent Plasmid Not Found", status=404,safe=False)
                # return JsonResponse({'code':403,'status':'failed','data':'Parent Plasmid Not Found'})
        return JsonResponse(data="Parent Plasmid Added", status=200)
        # return JsonResponse({'code':200,'status':'success','data':'Parent Plasmid Added'})

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
        newOriCloning = request.POST.get('newOriCloning')
        newOriHost = request.POST.get('newOriHost')
        newMarkerCloning = request.POST.get('newMarkerCloning')
        newMarkerHost = request.POST.get('newMarkerHost')
        newLevel = request.POST.get('newLevel')
        newLength = len(request.POST.get('newSequence'))
        newSequence = request.POST.get('newSequence')
        newPlate = request.POST.get('newPlate')
        newState = request.POST.get('newState')
        newUser = request.session.get('info')['uname']
        newNote = request.POST.get('newNote')
        newAlias = request.POST.get('newAlias')
        if(newName == None or newName == "" or newOriCloning == None or newOriCloning == "" or newOriHost == None or newOriHost == ""
          or newMarkerHost == None or newMarkerHost == "" or newMarkerCloning == None or newMarkerCloning == "" or newSequence == None
          or newSequence == ""):
            return JsonResponse(data="New Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status': 'failed', 'data': 'Name,Ori,Marker,Sequence can not be empty'})
        Plasmidneed.objects.filter(plasmidid=PlasmidID).update(name=newName,oricloning=newOriCloning,orihost=newOriHost,markercloning=newMarkerCloning,
                                                               markerhost=newMarkerHost,level=newLevel,length=newLength,sequenceconfirm=newSequence,
                                                               plate=newPlate,alias=newAlias,state = newState,newUser=newUser,newNote=newNote)
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











#----------------------------------------------------------
#Backbone table
#Search
def SearchByBackboneName(request):
    if(request.method == "GET"):
        Name = request.GET.get('name')
        if(Name == None or Name == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Name can not be empty'})
        BackboneList = Backbonetable.objects.filter(name=Name)
        if(len(BackboneList) > 0):
            return JsonResponse(data=list(BackboneList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such Name", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchByBackboneSeq(request):
    if(request.method == "GET"):
        Seq = request.GET.get('seq')
        if(Seq == None or Seq == ""):
            return JsonResponse(data="Seq cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Sequence can not be empty'})
        BackboneList = Backbonetable.objects.filter(sequence=Seq)
        if(len(BackboneList) > 0):
            return JsonResponse(data=list(BackboneList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such backbone", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchByBackboneSpecies(request):
    if(request.method == "GET"):
        Species = request.GET.get('species')
        if(Species == None or Species == ""):
            return JsonResponse(data="Species cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'Species can not be empty'})
        BackboneList = Backbonetable.objects.filter(species=Species)
        if(len(BackboneList) > 0):
            return JsonResponse(data=list(BackboneList.values()), status=200,safe=False)
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
        BackboneList = Backbonetable.objects.filter(marker=Marker)
        if(len(BackboneList) > 0):
            return JsonResponse(data=list(BackboneList.values()), status=200,safe=False)
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
        BackboneList = Backbonetable.objects.filter(ori=Ori)
        if(len(BackboneList) > 0):
            return JsonResponse(data=list(BackboneList.values()), status=200,safe=False)
            # return JsonResponse({'code':200,'status':'success','data':list(BackboneList.values())})
        else:
            return JsonResponse(data="No such Ori", status=404,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'No Backbone Found'})

def SearchByCopyNumber(request):
    if(request.method == 'GET'):
        CopyNumber = request.GET.get('copynumber')
        if(CopyNumber == None or CopyNumber == ""):
            return JsonResponse(data="CopyNumber cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'CopyNumber can not be empty'})
        BackboneList = Backbonetable.objects.filter(copynumber = CopyNumber)
        if(len(BackboneList) > 0):
            return JsonResponse(data=list(BackboneList.values()), status=200,safe=False)
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
        name = request.POST.get('name')
        length = len(request.POST.get('sequence'))
        sequence = request.POST.get('sequence')
        ori = request.POST.get('ori')
        marker = request.POST.get('marker')
        species = request.POST.get('species')
        copynumber = request.POST.get('copynumber')
        note = request.POST.get('note')
        scar = request.POST.get('scar')
        alias = request.POST.get('alias')
        if(name == None or name == "" or sequence == None or sequence == ""):
            return JsonResponse(data="Name cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name, sequence can not be empty'})
        Backbonetable.objects.create(name=name, length=length, sequence=sequence, ori=ori, marker=marker,
                                     species = species,copynumber=copynumber, notes=note, scar=scar, alias=alias)
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
        newOri = request.POST.get('ori')
        newMarker = request.POST.get('marker')
        newSpecies = request.POST.get('species')
        newCopynumber = request.POST.get('copynumber')
        newNote = request.POST.get('note')
        newScar = request.POST.get('scar')
        newAlias = request.POST.get('alias')
        newUser = request.session.get('info')['uid']
        if(newName == None or newName == "" or newSequence == None or newSequence == ""):
            return JsonResponse(data="Name and sequence cannot be empty", status=400,safe=False)
            # return JsonResponse({'code':204,'status':'failed','data':'name, Sequence can not be empty'})
        Backbonetable.objects.filter(id=BackboneID).update(name=newName, length=newLength, sequence=newSequence,ori=newOri, marker=newMarker,
                                                           species=newSpecies,copynumber=newCopynumber,notes=newNote,
                                                           scar=newScar,alias=newAlias,user=newUser)
        return JsonResponse(data="Added backbone data", status=200,safe=False)
        # return JsonResponse({'code':200,'status':'success','data':'Backbone Data Updated'})

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
            ID = Parttable.objects.filter(Name = Name).first().partid
            return JsonResponse(data = {"PartID":ID},status=200,safe=False)
        else:
            return JsonResponse(data = "Name cannot be empty",status=400,safe=False)




# def deleteBackbone(request):
#     #filter表示筛选
#     Backbonetable.objects.filter(name="Django").delete()
#     return HttpResponse("成功")
#
# #获取数据
# def getBackbone(request):
#     #[]queryset可以理解成列表，行行行的对象数据
#     queryset = Backbonetable.objects.all()
#
#     row_obj = Backbonetable.objects.filter(name="Django").first()
#     return HttpResponse("chenggong")
#
# def Update(request):
#     #这一行不要执行会改所有
#     # Backbonetable.objects.all().update(name="777")
#     Backbonetable.objects.filter(name="Django").update(name="Django2")
#     return HttpResponse("chenggong")





