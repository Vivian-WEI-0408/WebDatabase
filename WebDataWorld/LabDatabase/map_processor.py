from Bio.SeqIO import parse, write
import requests
from .CaculateModule.snapgene_reader import snapgene_to_dict
from .ControllerModule import FittingLabels
from .CaculateModule.ScarIdentify import scarPosition,scarFunction
def process_map_file(upload_map, file_name, upload_type, django_request,Base_URL):
    if (file_name[1] == "fasta"):
        records = parse(upload_map, "fasta")
        for record in records:
            Sequence = str(record.seq)
            break
    elif(file_name[1] == "gb" or file_name[1] == "gbk" or file_name[1] == "ape" or file_name[1] == "str"):
        records = parse(upload_map, "genbank")
        for record in records:
            Sequence = str(record.seq)
            print(Sequence)
            break
    elif(file_name[1] == "dna"):
        record = snapgene_to_dict(upload_map)
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
            Culture_request_body = {"name":name,"ori" : Ori_list,"marker":Marker_list}
            CultureResponseResponse = session.post(f"{Base_URL}setPlasmidCulture",json = Culture_request_body, cookies = django_request.COOKIES)
            scar_request_body = {"name":name,"bsmbi":scar_data_body[0],"bsai":scar_data_body[1],"bbsi":scar_data_body[2],"aari":scar_data_body[3],"sapi":scar_data_body[4]}
            ScarUpdateResponse = session.post(f"{Base_URL}setPlasmidScar",json = scar_request_body,cookies=django_request.COOKIES)
            if(SequenceUpdateResponse.status_code == 200 and CultureResponseResponse.status_code == 200 and ScarUpdateResponse.status_code == 200):
                return True
            else:
                print(SequenceUpdateResponse)
                print(CultureResponseResponse)
                print(ScarUpdateResponse)
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
            Culture_request_body = {"name":name,"ori" : Ori_list,"marker":Marker_list}
            CultureResponseResponse = session.post(f"{Base_URL}setBackboneCulture",json = Culture_request_body, cookies = django_request.COOKIES)
            scar_request_body = {"name":name,"bsmbi":scar_data_body[0],"bsai":scar_data_body[1],"bbsi":scar_data_body[2],"aari":scar_data_body[3],"sapi":scar_data_body[4]}
            ScarUpdateResponse = session.post(f"{Base_URL}setBackboneScar",json = scar_request_body,cookies=django_request.COOKIES)
            if(SequenceUpdateResponse.status_code == 200 and CultureResponseResponse.status_code == 200 and ScarUpdateResponse.status_code == 200):
                return True
            else:
                print(SequenceUpdateResponse)
                print(CultureResponseResponse)
                print(ScarUpdateResponse)
                return False
        elif(upload_type == "part"):
            request_body = {"name":name, "sequence":Sequence}
            SequenceUpdateResponse = session.post(f"{Base_URL}UpdatePartSequence",json=request_body,cookies=django_request.COOKIES)
            if(SequenceUpdateResponse.status_code == 200):
                return True
            else:
                print(SequenceUpdateResponse)
                return False