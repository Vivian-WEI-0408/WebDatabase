# from django.test import TestCase
import requests
# Create your tests here.
session = requests.Session()
session.headers.update({
    'User-Agent':'Django-App/1.0',
    'Content-Type':'application/json',
})

def test_PartFilter():
    response = session.post('http://10.30.76.2:8000/WebDatabase/PartFilter',data = {"name":"pro","Type":"promoter",'Enzyme':'','Scar':"",'page':1,'page_size':10})
    print(response.status_code)
    print(response.url)

test_PartFilter()