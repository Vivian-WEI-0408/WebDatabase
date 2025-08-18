from django.urls import path,include
from rest_framework.routers import DefaultRouter


# from WebDatabase.views import BackbonetableViewSet,ParentplasmidtableViewSet,PartrputableViewSet,ParttableViewSet,PlasmidneedViewSet,TbBackboneUserfileaddressViewSet,TbPartUserfileaddressViewSet,TbPlasmidUserfileaddressViewSet,TestdatatableViewSet,StraintableViewSet,createBackbone
from WebDatabase import views,account
# router = DefaultRouter()
# router.register('Backbone',BackbonetableViewSet,basename='Backbone')
# router.register('Plasmid',PlasmidneedViewSet,basename='Plasmid')
# router.register('Part',ParttableViewSet,basename='Part')
# router.register('PlasmidParent',ParentplasmidtableViewSet,basename='PlasmidParent')
# router.register('PartRpu',PartrputableViewSet,basename='PartRpu')
# router.register('BackboneFile',TbBackboneUserfileaddressViewSet,basename='BackboneFile')
# router.register('PartFile',TbPartUserfileaddressViewSet,basename='PartFile')
# router.register('PlasmidFile',TbPlasmidUserfileaddressViewSet,basename='PlasmidFile')
# router.register('Testdatatable',TestdatatableViewSet,basename='Testdatatable')
# router.register('Straintable',StraintableViewSet,basename='Straintable')
urlpatterns = [
    # path("",v),
    path("StrainName",views.SearchByStrainName,name="StrainName"),
    path("Part",views.PartDataALL,name="Part"),
    path("PartName",views.SearchByPartName,name="PartName"),
    path("PartAlias",views.SearchByPartAlterName,name="PartAlias"),
    path("PartType",views.SearchByPartType,name="PartType"),
    path("TypeByName",views.SearchPartTypeByName,name="TypeByName"),
    path("PartRPU",views.SearchByRPU,name="PartRPU"),
    path("PartSeq",views.SearchBySeq,name="PartSeq"),
    path("PartFile",views.SearchPartFile,name="PartFile"),
    path("AddPartRPU",views.AddPartRPU,name="AddPartRPU"),


    path("AddPartData",views.AddPartData,name="AddPartData"),
    path("AddPartFile",views.AddPartFileAddress,name="AddPartFile"),
    path("UpdatePart",views.UpdatePart,name="UpdatePart"),
    path("UpdatePartFile",views.UpdatePartFileAddress,name="UpdatePartFile"),
    path("UpdatePartRPU",views.UpdatePartRPU,name="UpdatePartRPU"),
    path("deletePart",views.deletePartData,name="deletePart"),
    path("deletePartFile",views.deletePartFile,name="deletePartFile"),
    path("PlamsidName",views.SearchByPlasmidName,name="PlamsidName"),
    path("PlasmidAlterName",views.SearchByPlasmidAlterName,name="PlasmidAlterName"),
    path("PlasmidSeqByName",views.SearchPlasmidSequenceByName,name="PlasmidSeq"),
    path("PlasmidSeq",views.SearchByPlasmidSeq,name="PlasmidSeq"),
    path("PlasmidOriClone",views.SearchByOriClone,name="PlasmidOriClone"),
    path("PlasmidOriHost",views.SearchByOriHost,name="PlasmidOriHost"),
    path("PlasmidMarkerClone",views.SearchByMarkerClone,name="PlasmidMarkerClone"),
    path("PlasmidMarkerHost",views.SearchByMarkerHost,name="PlasmidMarkerHost"),
    path("PlasmidLevel",views.SearchByLevel,name="PlasmidLevel"),
    path("PlasmidPlate",views.SearchByPlate,name="PlasmidPlate"),
    path("PlasmidParent",views.SearchPlasmidParent,name="PlasmidParent"),
    path("PlasmidFile",views.SearchPlasmidFileAddress,name="PlasmidFile"),
    path("AddPlasmidFile",views.AddPlasmidFileAddress,name="AddPlasmidFile"),
    path("AddPlasmidData",views.AddPlasmidData,name="AddPlasmidData"),
    path("AddPlasmidParent",views.AddParentPlasmid,name="AddParentPlasmid"),
    path("UpdatePlasmid",views.UpdatePlasmidData,name="UpdatePlasmid"),
    path("UpdatePlasmidFile",views.UpdatePlasmidFileAddress,name="UpdatePlasmidFile"),
    path("deletePlasmid",views.deletePlasmidData,name="deletePlasmid"),
    path("deletePlasmidFile",views.deletePlasmidFileAddress,name="deletePlasmidFile"),
    path("deletePlasmidParent",views.DeleteParentPlasmid,name="deletePlasmidParent"),
    path("BackboneName",views.SearchByBackboneName,name="BackboneName"),
    path("BackboneSeq",views.SearchByBackboneSeq,name="BackboneSeq"),
    path("BackboneSpecies",views.SearchByBackboneSpecies,name="BackboneSpecies"),
    path("BackboneOri",views.SearchByBackboneOri,name="BackboneOri"),
    path("BackboneMarker",views.SearchByBackboneMarker,name="BackboneMarker"),
    path("BackboneCopyNumber",views.SearchByCopyNumber,name="BackboneCopyNumber"),
    path("BackboneFile",views.SearchBackboneFileAddress,name="BackboneFile"),
    path("AddBackbone",views.AddBackboneData,name="AddBackbone"),
    path("AddBackboneFile",views.AddBackboneFileAddress,name="AddBackboneFile"),
    path("UpdateBackbone",views.UpdateBackboneData,name="/UpdateBackbone"),
    path("UpdateBackboneFile",views.UpdateBackboneFileAddress,name="UpdateBackboneFile"),
    path("deleteBackbone",views.DeleteBackboneData,name="deleteBackbone"),
    path("deleteBackboneFile",views.DeleteBackboneFileAddress,name="deleteBackboneFile"),
    path("TestDataName",views.SearchByTestdataName,name="TestDataName"),
    path("GetDBDList",views.GetDBDList,name="GetDBDList"),
    path("GetDBDNameList",views.GetDBDNameList,name="GetDBDNameList"),
    path("GetDBDKdList",views.GetDBDKdList,name="GetDBDKdList"),
    path("GetDBD",views.GetDBD,name="GetDBD"),
    path("GetDBDMenu",views.GetDBDMenu,name="GetDBDMenu"),
    path("GetDBDKd",views.GetDBDKd,name="GetDBDKd"),
    path("AddDBD",views.AddDBD,name="AddDBD"),
    path("UpdateDBD",views.UpdateDBD,name="UpdateDBD"),
    path("GetLBDDimer",views.GetLBDDimer,name="GetLBDDimer"),
    path("GetLBDDimerMenu",views.GetLBDDimerMenu,name="GetLBDDimerMenu"),
    path("GetLBDDimerNameList",views.GetLBDDimerNameList,name="GetLBDDimerNameList"),
    path("ADDLBDDimer",views.AddLBDDimer,name="ADDLBDDimer"),
    path("UpdateLbdDimer",views.UpdateLbdDimer,name="UpdateLbdDimer"),
    path("GetLBDNr",views.GetLBDNr,name="GetLBDNr"),
    path("GetLBDNRMenu",views.GetLBDNRMenu,name="GetLBDNRMenu"),
    path("GetLBDNRNameList",views.GetLBDNRNameList,name="GetLBDNRNameList"),
    path("AddLbdnr",views.AddLbdnr,name="AddLbdnr"),
    path("UpdateLBDnr",views.UpdateLBDnr,name="UpdateLBDnr"),
    path("login",account.login,name="login"),
    path("logout",account.logout,name="logout"),
]
