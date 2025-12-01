from django.urls import path,include
from rest_framework.routers import DefaultRouter

from LabDatabase import views,admin
urlpatterns = [
    #index
    path("index",views.index,name="index"),
    path("getdata",views.getData,name="getData"),
    path("filterdata",views.DataFilter,name="filterdata"),
    #user
    path("login",admin.login,name="login"),
    path("logout",admin.logout,name="logout"),
    path("register",admin.register,name="register"),
    

    #Upload Sequence Map
    path("UploadMap",views.UploadMap,name="UploadMap"),



    #Upload Excel File
    path("UploadFile",views.UploadFile,name="UploadFile"),
    path("task_status/<str:task_id>",views.task_status,name="task_status"),
    #Search Information
    path("part/<int:partid>",views.part_detail_show,name="part_detail"),
    path("backbone/<int:backboneid>",views.backbone_detail_show,name="backbone_detail"),
    path("plasmid/<int:plasmidid>",views.plasmid_detail_show,name="plasmid_detail"),

    #delete
    path("deletepart/<int:partid>",views.delete_part,name="delete_part"),
    path("deletebackbone/<int:backboneid>",views.delete_backbone,name="delete_backbone"),
    path("deleteplasmid/<int:plasmidid>",views.delete_plasmid,name="delete_plasmid"),

    #Modify
    path("modifypart/<int:partid>",views.modify_part,name="modify_part"),
    path("modifybackbone/<int:backboneid>",views.modify_backbone, name="modify_backbone"),
    path("modifyplasmid/<int:plasmidid>",views.modify_plasmid,name="modify_plasmid"),

    #download templates
    path("download/<str:type>",views.download_template,name="downloadtemplate"),
    
    #download part map
    path("downloadPlasmidMap/<int:plasmidid>",views.downloadPlasmidMap,name="downloadPlasmidMap"),
    path("downloadBackboneMap/<int:backboneid>",views.downloadBackboneMap,name="downloadBackboneMap"),
    path("downloadPartMap/<int:partid>",views.downloadPartMap,name="downloadPartMap"),
]