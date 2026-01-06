from Bio.SeqIO import parse, write
import requests
import sys
# sys.path.append(r"C:\Users\admin\Desktop\WebDatabaseBeta\WebDatabase\WebDataWorld\LabDatabase\CaculateModule")
# from .snapgene_readersnapgene_reader import snapgene_to_dict
from .CaculateModule import snapgene_reader
from ControllerModule import FittingLabels
from CaculateModule.ScarIdentify import scarPosition,scarFunction
def process_map_file(upload_map, file_name, upload_type, django_request,Base_URL):
    FeatureList = []
    if (file_name[1] == "fasta"):
        records = parse(upload_map, "fasta")
        for record in records:
            Sequence = str(record.seq)
            break
    elif(file_name[1] == "gb" or file_name[1] == "gbk" or file_name[1] == "ape" or file_name[1] == "str"):
        records = parse(upload_map, "genbank")
        for record in records:
            Sequence = str(record.seq)
            FeatureList = record.features
            print(Sequence)
            break
    elif(file_name[1] == "dna"):
        record = snapgene_reader.snapgene_to_dict(upload_map)
        print(record)
        FeatureList = record['features']
        Sequence = record['seq']
    if(Sequence != ""):
        session = requests.Session()
        token = django_request.COOKIES.get('csrftoken')
        session.headers.update({
            'User-Agent':'Django-App/1.0',
            'Content-Type':'application/json',
            'X-CSRFToken':token,
        })
        name = file_name[0]
        if(upload_type == "plasmid"):
            Ori_list = []
            Marker_list = []
            OriAndMarkerLabel = FittingLabels(sequence= Sequence)
            for each_ori in OriAndMarkerLabel['Origin']:
                Ori_list.append(each_ori['Name'])
            for each_marker in OriAndMarkerLabel['Marker']:
                Marker_list.append(each_marker['Name'])
            scar_data_body = scarFunction(Sequence)
            request_body = {"name":name, "sequence":Sequence}
            SequenceUpdateResponse = session.post(f"{Base_URL}UpdatePlasmidSequence",json=request_body,cookies=django_request.COOKIES)
            if(SequenceUpdateResponse.json()['success'] == False and SequenceUpdateResponse.json()['message'] == "Plasmid Does Not Exist"):
                add_request_body = {"name":name,"sequence":Sequence,"alias":""}
                AddSequenceUpdateResponse = session.post(f"{Base_URL}AddPlasmidData",json=add_request_body,cookies=django_request.COOKIES)
                if(AddSequenceUpdateResponse.status_code!= 200):
                    return False
            Culture_request_body = {"name":name,"ori" : Ori_list,"marker":Marker_list}
            CultureResponseResponse = session.post(f"{Base_URL}setPlasmidCulture",json = Culture_request_body, cookies = django_request.COOKIES)
            scar_request_body = {"name":name,"bsmbi":scar_data_body[0],"bsai":scar_data_body[1],"bbsi":scar_data_body[2],"aari":scar_data_body[3],"sapi":scar_data_body[4]}
            ScarUpdateResponse = session.post(f"{Base_URL}setPlasmidScar",json = scar_request_body,cookies=django_request.COOKIES)
            if(SequenceUpdateResponse.status_code == 200 and CultureResponseResponse.status_code == 200 and ScarUpdateResponse.status_code == 200):
                return True
            else:
                return False
        elif(upload_type == "backbone"):
            Ori_list = []
            Marker_list = []
            OriAndMarkerLabel = FittingLabels(sequence= Sequence)
            for each_ori in OriAndMarkerLabel['Origin']:
                Ori_list.append(each_ori['Name'])
            for each_marker in OriAndMarkerLabel['Marker']:
                Marker_list.append(each_marker['Name'])
            scar_data_body = scarFunction(Sequence)
            request_body = {"name":name, "sequence":Sequence}
            SequenceUpdateResponse = session.post(f"{Base_URL}UpdateBackboneSequence",json=request_body,cookies=django_request.COOKIES)
            print(SequenceUpdateResponse.json())
            if(SequenceUpdateResponse.json()['success'] == False and SequenceUpdateResponse.json()['message'] == "Backbone Does Not Exist"):
                add_request_body = {"name":name,"sequence":Sequence}
                print(add_request_body)
                AddBackboneResponse = session.post(f"{Base_URL}AddBackbone",json=add_request_body,cookies=django_request.COOKIES)
                print(AddBackboneResponse.json())
                if(AddBackboneResponse.status_code != 200):
                    return False
            if(file_name[1] == "gb" or file_name[1] == "gbk" or file_name[1] == "ape" or file_name[1] == "str"):
                for each_feature in FeatureList:
                    try:
                        start_position = each_feature.location.start
                        end_position = each_feature.location.end
                        label = each_feature.qualifiers['label'][0] if "label" in each_feature.qualifiers else ""
                        feature_type = each_feature.type
                        color = each_feature.qualifiers['color'][0] if 'color' in each_feature.qualifiers else ""
                        ape_info = each_feature.qualifiers['ApEinfo_fwdcolor'][0] if 'ApEinfo_fwdcolor' in each_feature.qualifiers else ""
                        request_body = {"start_position":start_position,"end_position":end_position,"label":label,"feature_type":feature_type,"color":color,"ape_info":ape_info}
                        add_feature_response = session.post(f"{Base_URL}AddBackboneFeature/{name}",json=request_body,cookies = django_request.COOKIES)
                    except Exception as e:
                        continue
            elif(file_name[1] == "dna"):
                print(FeatureList)
                for each_feature in FeatureList:
                    try:
                        start_position = each_feature['start']
                        end_position = each_feature['end']
                        label = each_feature['name']
                        feature_type = each_feature['type']
                        color = each_feature['color']
                        ape_info = each_feature['color']
                        request_body = {"start_position":start_position,"end_position":end_position,"label":label,"feature_type":feature_type,"color":color,"ape_info":ape_info}
                        add_feature_response = session.post(f"{Base_URL}AddBackboneFeature/{name}",json=request_body,cookies = django_request.COOKIES)
                        print(add_feature_response.json())
                    except Exception as e:
                        continue
            Culture_request_body = {"name":name,"ori" : Ori_list,"marker":Marker_list}
            CultureResponseResponse = session.post(f"{Base_URL}setBackboneCulture",json = Culture_request_body, cookies = django_request.COOKIES)
            scar_request_body = {"name":name,"bsmbi":scar_data_body[0],"bsai":scar_data_body[1],"bbsi":scar_data_body[2],"aari":scar_data_body[3],"sapi":scar_data_body[4]}
            ScarUpdateResponse = session.post(f"{Base_URL}setBackboneScar",json = scar_request_body,cookies=django_request.COOKIES)
            if((SequenceUpdateResponse.status_code == 200 or AddBackboneResponse.status_code == 200) and CultureResponseResponse.status_code == 200 and ScarUpdateResponse.status_code == 200):
                return True
            else:
                print(SequenceUpdateResponse)
                print(CultureResponseResponse)
                print(ScarUpdateResponse)
                return False
        elif(upload_type == "part"):
            request_body = {"name":name, "Level0Sequence":Sequence}
            SequenceUpdateResponse = session.post(f"{Base_URL}UpdatePartSequence",json=request_body,cookies=django_request.COOKIES)
            if(SequenceUpdateResponse.status_code == 200):
                return True
            elif(SequenceUpdateResponse.json()['success'] == False and SequenceUpdateResponse.json()['message'] == "Part Does Not Exist"):
                add_request_body = {"name":name,"alias":"","Level0Sequence":Sequence,"type":"promoter"}
                SequenceAddResponse = session.post(f"{Base_URL}AddPartData",json=add_request_body,cookies=django_request.COOKIES)
                if(SequenceAddResponse.status_code != 200):
                    return False
            else:
                print(SequenceUpdateResponse)
                return False
            
            
# def AnalysisFeature(file_obj, type, name, session, django_request, Base_URL):
#     print("AnalysisFeature")
#     if (type == "fasta"):
#         records = parse(file_obj, "fasta")
#         for record in records:
#             Sequence = str(record.seq)
#             break
#     elif(type == "gb" or type == "gbk" or type == "ape" or type == "str"):
#         records = parse(file_obj, "genbank")
#         for record in records:
#             FeartureList = record.features
#             for each_feature in FeartureList:
#                 try:
#                     start_position = each_feature.location.start
#                     end_position = each_feature.location.end
#                     label = each_feature.qualifiers['label'][0] if "label" in each_feature.qualifiers else ""
#                     feature_type = each_feature.type
#                     color = each_feature.qualifiers['color'][0] if 'color' in each_feature.qualifiers else ""
#                     ape_info = each_feature.qualifiers['ApEinfo_fwdcolor'][0] if 'ApEinfo_fwdcolor' in each_feature.qualifiers else ""
#                     request_body = {"start_position":start_position,"end_position":end_position,"label":label,"feature_type":feature_type,"color":color,"ape_info":ape_info}
#                     add_feature_response = session.post(f"{Base_URL}AddBackboneFeature/{name}",json=request_body,cookies = django_request.COOKIES)
#                 except Exception as e:
#                     continue
#             break
#     elif(type == "dna"):
#         print("process_map_file")
#         print(file_obj.closed)
#         print(str(file_obj))
#         if file_obj.closed:
#             file_obj = open(str(file_obj),"rb")
#         record = snapgene_to_dict(file_obj)
#         FeatureList = record['features']
#         print(FeatureList)
#         for each_feature in FeatureList:
#             try:
#                 start_position = each_feature['start']
#                 end_position = each_feature['end']
#                 label = each_feature['name']
#                 feature_type = each_feature['type']
#                 color = each_feature['color']
#                 ape_info = each_feature['color']
#                 request_body = {"start_position":start_position,"end_position":end_position,"label":label,"feature_type":feature_type,"color":color,"ape_info":ape_info}
#                 add_feature_response = session.post(f"{Base_URL}AddBackboneFeature/{name}",json=request_body,cookies = django_request.COOKIES)
#                 print(add_feature_response.json())
#             except Exception as e:
#                 continue


def AnalysisFeatureTemp(file_obj):
    print("process_map_file")
    record = snapgene_to_dict(open(file_obj,'rb'))
    FeatureList = record['features']
    for each_feature in FeatureList:
        start_position = each_feature['start']
        end_position = each_feature['end']
        label = each_feature['name']
        feature_type = each_feature['type']
        color = each_feature['color']
        ape_info = each_feature['color']
        print(each_feature)
    

if __name__ == "__main__":
    import io
    file_address = r"C:\Users\admin\Desktop\样例数据\level3\WBY6.dna"
    # upload_map_temp = open(file_address)
    # upload_map_temp = upload_map_temp.decode("utf-8")
    # upload_map = io.StringIO(upload_map_temp)
    AnalysisFeatureTemp(file_address)
    