from django.test import TestCase
from django.test import Client
# from rest_framework.test import APITransactionTestCase,RequestsClient
# from django.urls import reverse
from .views import *
from .models import *
from .account import login


class WebDataWorldTestCase(TestCase):
    def setUp(self):
        # self.BASE_URL = 'http://127.0.0.1:8000'
        self.client = Client()
        self.client.headers.update({
        'User-Agent':'Django-App/1.0',
        'Content-Type':'application/json',
    })
        self.client.session['info'] = {"uid":8,'uname':"root"}
        # self.client.session['info'] = {"uid": 8, 'uname': "root"}

    def test_AddPartData(self):
        response = self.client.post('/WebDatabase/AddPartData',
                                    data={"name": "", "alias": "testDjango", "Level0Sequence": "AACCGGTT",
                                          "ConfirmedSequence": "ATCGAATTCCGG", "InsertSequence": "ATCG", "source": "",
                                          "reference": "", "note": "", "type": "ProMoter"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Parameters name, sequence cannot be empty"')

        response = self.client.post('/WebDatabase/AddPartData',
                                    data={"name": "testDjango", "alias": "testDjango", "Level0Sequence": "",
                                          "ConfirmedSequence": "ATCGAATTCCGG", "InsertSequence": "ATCG", "source": "",
                                          "reference": "", "note": "", "type": "ProMoter"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Parameters name, sequence cannot be empty"')

        response = self.client.post('/WebDatabase/AddPartData',
                                    data={"name": "testDjango", "alias": "testDjango", "Level0Sequence": "AACCGGTT",
                                          "ConfirmedSequence": "", "InsertSequence": "ATCG", "source": "",
                                          "reference": "", "note": "", "type": "ProMoter"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Parameters name, sequence cannot be empty"')

        response = self.client.post('/WebDatabase/AddPartData',
                                    data={"name": "testDjango", "alias": "testDjango", "Level0Sequence": "AACCGGTT",
                                          "ConfirmedSequence": "ATCGAATTCCGG", "InsertSequence": "", "source": "",
                                          "reference": "", "note": "", "type": "ProMoter"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Parameters name, sequence cannot be empty"')

        response = self.client.post('/WebDatabase/AddPartData',
                                    data={"name": "testDjango", "alias": "testDjango", "Level0Sequence": "AACCGGTT",
                                          "ConfirmedSequence": "ATCGAATTCCGG", "InsertSequence": "ATCG", "source": "",
                                          "reference": "", "note": "", "type": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Type cannot be empty"')


        response = self.client.post('/WebDatabase/AddPartData',data={"name":"testDjango","alias":"testDjango","Level0Sequence":"AACCGGTT","ConfirmedSequence":"ATCGAATTCCGG","InsertSequence":"ATCG","source":"","reference":"","note":"","type":"ProMoter"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,b'"Added part data"')


    def test_AddPartRPU(self):
        response = self.client.post('/WebDatabase/AddPartRPU',
                                    data={'Name': "AAA", "rpu": 0.134, "testStrain": "testStrain",
                                          "Note": "test Note"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'"No such part"')

        response = self.client.post('/WebDatabase/AddPartRPU',
                                    data={'Name': "", "rpu": 0.134, "testStrain": "testStrain",
                                          "Note": "test Note"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Name cannot be empty"')



        response = self.client.post('/WebDatabase/AddPartRPU', data={'Name':"testA","rpu":0.134,"testStrain":"testStrain","Note":"test Note"})
        self.assertEqual(response.status_code, 404)

        self.assertEqual(response.content, b'"No such part"')
    def test_AddPartFileAddress(self):


        response = self.client.post('/WebDatabase/AddPartFile',{"PartName":"AAA","fileAddress":"Test"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'"No such part"')

        response = self.client.post('/WebDatabase/AddPartFile',{"PartName":"","fileAddress":"Test"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Parameters cannot be empty"')

        response = self.client.post('/WebDatabase/AddPartFile', {"PartName": "", "fileAddress": "Test"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'"Parameters cannot be empty"')

        response = self.client.post('/WebDatabase/AddPartData',data={"name":"testDjango","alias":"testDjango","Level0Sequence":"AACCGGTT","ConfirmedSequence":"ATCGAATTCCGG","InsertSequence":"ATCG","source":"","reference":"","note":"","type":"ProMoter"})

        # response = self.client.post('/WebDatabase/AddPartFile', {"PartName": "testDjango", "fileAddress": "Test"})
        # print(response.content)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.content, b'"Added part address"')

    def test_UpdatePart(self):
        pass
        # response = self.client.post('/WebDatabase/UpdatePart',{"OriginalName":"testA","Name":"testDjango","Alias":"test"})
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.content, b'"Updated part data"')
    
    def test_PartFilterT(self):
        response = self.client.post('/WebDatabase/PartFilter',data = {"name":"pro","Type":"promoter",'Enzyme':'','Scar':"",'page':1,'page_size':10})
        print(response.status_code)
        print(response.json())




