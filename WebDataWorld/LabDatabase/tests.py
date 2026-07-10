# # from django.test import TestCase
# import requests
# # Create your tests here.
# session = requests.Session()
# session.headers.update({
#     'User-Agent':'Django-App/1.0',
#     'Content-Type':'application/json',
# })

# def test_PartFilter():
#     response = session.post('http://10.30.76.2:8000/WebDatabase/PartFilter',data = {"name":"pro","Type":"promoter",'Enzyme':'','Scar':"",'page':1,'page_size':10})
#     print(response.status_code)
#     print(response.url)

# test_PartFilter()

# from Bio.Restriction import BsaI
# from Bio.Seq import Seq
# Sequence = "GGTCTCAGTGCggttgcttcctataaaaaacTTGACTctatatctactagaggtttTCTAATgatggcatccggggaaaaccttgtcaatgaagagcgatctatgATCAagagacc"
# Enzyme_result = BsaI.search(Seq(Sequence))
# if(len(Enzyme_result) == 2):
#     target_seq = Sequence[Enzyme_result[0]-1:Enzyme_result[1]-1]
#     target_start = Enzyme_result[0]
#     target_end = Enzyme_result[1]
# print(target_seq)
# if(target_seq[:4].upper() == "GTGC" or target_seq[:4].upper() == "GCAC" or target_seq[:4].upper() == "ATCA"
#     or target_seq[:4].upper() == "TGAT" or target_seq[:4].upper() == "AATG" or target_seq[:4].upper() == "CATT"
#     or target_seq[:4].upper() == "TAAA" or target_seq[:4].upper() == "TTTA" or target_seq[:4].upper() == "CCTC"
#     or target_seq[:4].upper() == "GAGG"):
#     target_seq = target_seq[4:]
#     target_start += 4
# print(target_seq[-4:])
# if(target_seq[-4:].upper() == "GTGC" or target_seq[-4:].upper() == "GCAC" or target_seq[-4:].upper() == "ATCA"
#     or target_seq[-4:].upper() == "TGAT" or target_seq[-4:].upper() == "AATG" or target_seq[-4:].upper() == "CATT"
#     or target_seq[-4:].upper() == "TAAA" or target_seq[-4:].upper() == "TTTA" or target_seq[-4:].upper() == "CCTC"
#     or target_seq[-4:].upper() == "GAGG"):
#     print(111)
#     target_seq = target_seq[:-5]
#     target_end -= 4
        
# print(target_seq)
# import pandas as pd

import pandas as pd
fill_column = ['AssemblyName','Alias','Level','Backbone','Plasmid','Note']
df = pd.read_excel(r'C:\Users\admin\Downloads\AssemblyPlan_template (6).xlsx',engine='openpyxl')
# print(df.head(10))
for col in df.columns:
    if col in fill_column:
        df[col] = df[col].ffill()
groups = {}
for name, group in df.groupby('AssemblyName'):
    groups[name] = group.drop(columns="AssemblyName")

for level_index, level_value in enumerate(['1', '2', '3'], start=1):
    level_frames = []
    assembly_names = []
    for assembly_name, assembly_df in groups.items():
        if assembly_df.empty:
            continue
        assembly_level = str(assembly_df['Level'].iloc[0]).strip().replace('.0', '')
        if assembly_level != level_value:
            continue

        level_frame = assembly_df.copy()
        level_frame.insert(0, 'AssemblyName', assembly_name)
        level_frames.append(level_frame)
        assembly_names.append(assembly_name)

        if not level_frames:
            continue

        print(level_frame)
        level_data = pd.concat(level_frames, ignore_index=True)
        
        print(level_data)
    
    
    
# print(groups)


# def process_gg_assembly_async(upload_file, django_request, task_id):
    # try:
    #     # task_status = {
    #     #     'status':'processing',
    #     #     'progress':10,
    #     #     'result':None,
    #     #     'error':[]
    #     # }
    #     cache_obj = CacheClass("processing",0)
    #     cache.set(f'{TASK_STATUS_PREFIX}{task_id}',cache_obj,timeout=3600)
    #     file_content = upload_file.read()
    #     excel_data = pd.read_excel(io.BytesIO(file_content),engine='openpyxl')
    #     if 'Assembly' in excel_data.columns and 'AssemblyName' not in excel_data.columns:
    #         excel_data = excel_data.rename(columns={'Assembly':'AssemblyName'})
    #     if 'Level' not in excel_data.columns:
    #         with TASK_STATUS_LOCK:
    #             cache_obj.setStatus("failed")
    #             cache_obj.setProgress(100)
    #             cache_obj.setMessage("上传表格中没有Level信息列,请更新组装表格模板")
    #         cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    #         return
    #         # task_status['status'] = 'failed'
    #         # task_status['progress'] = 100
    #         # task_status['error'] = 'Excel is missing the Level column.'
    #         # task_status['result'] = {
    #         #     'success':False,
    #         #     'message':'Excel is missing the Level column.'
    #         # }
    #         # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    #         # return
    #     excel_data = excel_data.copy()
    #     fill_column = ['AssemblyName','Alias','Level','Backbone','Plasmid','Note']
    #     for col in excel_data.columns:
    #         if col in fill_column:
    #             excel_data[col] = excel_data[col].ffill()
    #     excel_data['Level'] = excel_data['Level'].apply(
    #         lambda value: str(value).strip().replace('.0', '') if pd.notna(value) else ''
    #     )
    #     # 按组装名称分类，后续按 level 分桶时再补回 AssemblyName 列
    #     assembly_groups = {}
    #     for name, group in excel_data.groupby('AssemblyName'):
    #         assembly_name = str(name).strip()
    #         if not assembly_name:
    #             continue
    #         assembly_groups[assembly_name] = group.drop(columns='AssemblyName').copy()
    #     completed_assemblies = []
    #     failed_assemblies = {}
    #     # total_assemblies = sum(
    #     #     1 for name in excel_data.get('AssemblyName', pd.Series(dtype=object)).tolist()
    #     #     if str(name).strip()
    #     # )
    #     total_assemblies = len(assembly_groups)
    #     if total_assemblies == 0:
    #         with TASK_STATUS_LOCK:
    #             cache_obj.setStatus('failed')
    #             cache_obj.setProgress(100)
    #             cache_obj.setMessage("组装文件为空")
    #         cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    #         # task_status['status'] = 'failed'
    #         # task_status['progress'] = 100
    #         # task_status['error'] = '组装文件为空'
    #         # task_status['result'] = {
    #         #     'success':False,
    #         #     'message':'组装文件为空'
    #         # }
    #         # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    #         return

    #     session = requests.Session()
    #     session.headers.update({
    #         'User-Agent':'Django-App/1.0',
    #         'Content-Type':'application/json',
    #     })

    #     for level_index, level_value in enumerate(['1', '2', '3'], start=1):
    #         level_frames = []
    #         assembly_names = []
    #         for assembly_name, assembly_df in assembly_groups.items():
    #             if assembly_df.empty:
    #                 continue
    #             assembly_level = str(assembly_df['Level'].iloc[0]).strip().replace('.0', '')
    #             if assembly_level != level_value:
    #                 continue

    #             level_frame = assembly_df.copy()
    #             level_frame.insert(0, 'AssemblyName', assembly_name)
    #             level_frames.append(level_frame)
    #             assembly_names.append(assembly_name)

    #         if not level_frames:
    #             continue

    #         level_data = pd.concat(level_frames, ignore_index=True)

    #         result = GGAssembly.GGFileProcessor.createTemporaryRepo(
    #             django_request,
    #             level_data,
    #             Base_URL,
    #         )
    #         if not result['success']:
    #             with TASK_STATUS_LOCK:
    #                 cache_obj.setStatus("processing")
    #                 if(level_index == 1):
    #                     cache_obj.setProgress(10)
    #                 elif(level_index == 2):
    #                     cache_obj.setProgress(20)
    #                 elif(level_index == 3):
    #                     cache_obj.setProgress(30)
    #                 cache_obj.setMessage(cache_obj.getMessage() + "\n" + f"Level {level_index} 上传仓库失败: {result['error']}")
    #             cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    #             # task_status['status'] = 'failed'
    #             # task_status['progress'] = 100
    #             # task_status['error'] = result['error']
    #             # task_status['result'] = {
    #             #     'success':False,
    #             #     'message':'仓库创建失败'
    #             # }
    #             # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    #             continue
    #         if 'error_row' in result:
    #             with TASK_STATUS_LOCK:
    #                 cache_obj.setStatus("processing")
    #                 if(level_index == 1):
    #                     cache_obj.setProgress(10)
    #                 elif(level_index == 2):
    #                     cache_obj.setProgress(20)
    #                 elif(level_index == 3):
    #                     cache_obj.setProgress(30)
    #                 cache_obj.setMessage(cache_obj.getMessage() + "\n" + f"Level {level_index} 上传中出现如下错误 {result['error_row']}")
    #             cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    #                 # task_status['progress'] = 100
    #             # task_status['status'] = 'completed'
    #             # task_status['result'] = {
    #             #     'success':True,
    #             #     'message':result['error_row']
    #             # }
    #             # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    #             continue
    #         print("上传完成")
    #         empty_repositories = []
    #         assembly_queue = queue.Queue()
    #         for assembly_name in assembly_names:
    #             repository_response = session.post(
    #                 f"{Base_URL}getrepo",
    #                 json={'Name':assembly_name},
    #                 cookies=django_request.COOKIES
    #             )
    #             if repository_response.status_code != 200:
    #                 if(repository_response.status_code == 404):
    #                     failed_assemblies[assembly_name] = f'获取仓库 {assembly_name} 失败'
    #                     continue
    #                 else:
    #                     failed_assemblies[assembly_name] = f'{assembly_name} {repository_response.json()["message"]}'
    #                     continue
    #             repository_data = repository_response.json().get('data', {})
    #             if (
    #                 repository_data.get('total_parts', 0) == 0 and
    #                 repository_data.get('total_plasmids', 0) == 0 and
    #                 repository_data.get('total_backbones', 0) == 0
    #             ):
    #                 empty_repositories.append(assembly_name)
    #                 continue
    #             assembly_queue.put(assembly_name)

    #         if empty_repositories:
    #             with TASK_STATUS_LOCK:
    #                 cache_obj.setStatus('processing')
    #                 cache_obj.setProgress(40)
    #                 cache_obj.setMessage(cache_obj.getMessage() + "\n" + f"本批上传的仓库中空仓库有: {','.join(empty_repositories)}")
    #             cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    #             # task_status['status'] = 'failed'
    #             # task_status['progress'] = 100
    #             # task_status['error'] = f"空仓库: {', '.join(empty_repositories)}"
    #             # task_status['result'] = {
    #             #     'success':False,
    #             #     'message':f"空仓库: {', '.join(empty_repositories)}"
    #             # }
    #             # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)

    #         while not assembly_queue.empty():
    #             queue_size = assembly_queue.qsize()
    #             completed_this_round = 0
    #             for _ in range(queue_size):
    #                 assembly_name = assembly_queue.get()
    #                 cache_obj.setStatus('processing')
    #                 cache_obj.setProgress(40 + int((len(completed_assemblies) / max(total_assemblies, 1)) * 60))
    #                 # current_task_status = cache.get(f'{TASK_STATUS_PREFIX}{task_id}', task_status)
    #                 # current_task_status['status'] = 'processing'
    #                 # current_task_status['progress'] = 40 + int((len(completed_assemblies) / max(total_assemblies, 1)) * 60)
    #                 # current_task_status['result'] = {
    #                 #     'completed': completed_assemblies,
    #                 #     'current': assembly_name,
    #                 #     'current_level': level_value,
    #                 #     'queue': list(assembly_queue.queue),
    #                 #     'levels': {
    #                 #         'current': level_value,
    #                 #         'step': f'{level_index}/3',
    #                 #     },
    #                 # }
    #                 # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',current_task_status,timeout=3600)

    #                 try:
    #                     process_assembly_repo(assembly_name, django_request, task_id)
    #                     completed_assemblies.append(assembly_name)
    #                     failed_assemblies.pop(assembly_name, None)
    #                     completed_this_round += 1
    #                 except LabDatabaseException as exc:
    #                     error_message = exc.message
    #                     failed_assemblies[assembly_name] = error_message or 'assembly failed'
    #                     assembly_queue.put(assembly_name)
    #                     print(failed_assemblies)
    #                     print(error_message)
    #                     # cache_obj.setMessage(cache_obj.getMessage() + "\n" + f"仓库 {assembly_name} 组装失败, {error_message}")
    #                 except Exception as exc:
    #                     with TASK_STATUS_LOCK:
    #                         cache_obj.setMessage(cache_obj.getMessage() + "\n" + f"仓库 {assembly_name} 组装失败, {str(exc)}")
    #                 # completed_assemblies.append(assembly_name)
    #                 # failed_assemblies.pop(assembly_name, None)
    #                 # completed_this_round += 1
    #                 # else:
    #                 #     failed_assemblies[assembly_name] = current_task_status.get('error') or 'assembly failed'
    #                 #     assembly_queue.put(assembly_name)
    #                     # current_task_status = {'status':'failed','error':str(e.args)}
    #             print(completed_this_round)
    #             print(assembly_queue.empty())
    #             if completed_this_round == 0 and not assembly_queue.empty():
    #                 with TASK_STATUS_LOCK:
    #                     cache_obj.setStatus("failed")
    #                     cache_obj.setProgress(100)
    #                     error = ""
    #                     for each_key in failed_assemblies:
                            
    #                         error += failed_assemblies[each_key]+"\n"
    #                     cache_obj.setMessage(cache_obj.getMessage() + "\n" + error+"\n" + "批量组装失败")
    #                 cache.set(f'{TASK_STATUS_PREFIX}{task_id}',cache_obj)
    #                 return
    #                 # task_status = {
    #                 #     'status':'failed',
    #                 #     'progress':100,
    #                 #     'result':{
    #                 #         'completed': completed_assemblies,
    #                 #         'pending': list(assembly_queue.queue),
    #                 #         'current_level': level_value,
    #                 #     },
    #                 #     'error': failed_assemblies,
    #                 # }
    #                 # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    #                 # return
        
    #     with TASK_STATUS_LOCK:
    #         cache_obj.setStatus('completed')
    #         cache_obj.setProgress(100)
    #         result_payload = _build_task_result_payload(task_id)
    #         result_payload.update({
    #             'success': True,
    #             'completed': completed_assemblies,
    #         })
    #         cache_obj.setResult(result_payload)
    #         cache_obj.setMessage(cache_obj.getMessage() + "\n" + "组装结束")
    #     cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    #     # task_status['progress'] = 100
    #     # task_status['status'] = 'completed'
    #     # task_status['result'] = {
    #     #     'success':True,
    #     #     'message':'组装结束',
    #     #     'completed': completed_assemblies,
    #     # }
    #     # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)
    # except LabDatabaseException as exc:
    #     with TASK_STATUS_LOCK:
    #         cache_obj.setStatus("failed")
    #         cache_obj.setProgress(100)
    #         cache_obj.setMessage(cache_obj.getMessage() + "\n" + f"组装失败,{exc.message}")
    #     cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    # except Exception as e:
    #     with TASK_STATUS_LOCK:
    #         cache_obj.setStatus("failed")
    #         cache_obj.setProgress(100)
    #         cache_obj.setMessage(cache_obj.getMessage() + "\n" + f"组装失败,{str(e)}")
    #     cache.set(f"{TASK_STATUS_PREFIX}{task_id}",cache_obj)
    #     # task_status = {
    #     #     'status':'failed',
    #     #     'progress':100,
    #     #     'result':None,
    #     #     'error':str(e.args),
    #     # }
    #     # cache.set(f'{TASK_STATUS_PREFIX}{task_id}',task_status,timeout=3600)



