from datetime import datetime
from platform import uname

# from anaconda_navigator.api.external_apps.exceptions import ValidationError
from django.contrib import admin
from django.http import JsonResponse

from .models import User,Parttable,Backbonetable,Plasmidneed
import hashlib
from django.shortcuts import render, HttpResponse,redirect
from django import forms
from .models import User

#md5加密
def md5(data):
    m = hashlib.md5()
    m.update(data.encode('utf-8'))
    return m.hexdigest()

class LoginModelForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入密码','minlength':6,"maxlength":100,'required':True}))
    class Meta:
        model = User
        fields = ['uname','password']
    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)
    
class RegisterModelForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请输入密码','minlength':6,"maxlength":100,'required':True}))
    password_Confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'请再次输入密码','minlength':6,"maxlength":100,'required':True}))

    class Meta:
        model = User
        fields = ['uname','email','password']
    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        if len(pwd)<6:
            raise Exception("密码长度不能少于6位")
        return md5(pwd)
    def clean_password_Confirm(self):
        pwd = self.cleaned_data.get('password_Confirm')
        if len(pwd)<6:
            raise Exception("密码长度不能少于6位")
        return md5(pwd)
    def validPassword(self):
        # print("validPassword")
        pwd = self.cleaned_data.get('password')
        pwdConfirm = self.cleaned_data.get('password_Confirm')
        if(pwd == pwdConfirm):
            return True
        else:
            return False
        

def login(request):
    """登录页面"""
    next = request.GET.get('next','')
    if(request.method == 'GET'):
        form = LoginModelForm()
        next = request.GET.get('next','')
        return render(request,"Login.html",{'form':form})
    form = LoginModelForm(data= request.POST)
    if form.is_valid():
        # print(next)
        #数据库校验，获取用户对象,ERROR:None
        admin_object = User.objects.filter(uname=form.cleaned_data['uname'],password=form.cleaned_data['password']).first()
        if(not admin_object):
            # print(form.cleaned_data)
            form.add_error("uname","用户名或密码错误")
            form.add_error("password","用户名或密码错误")
            return render(request, "Login.html", {'form': form})
        #验证正确之后
        #网站生成随机字符串，写到浏览器cookie中；再写入session
        request.session['info'] = {'uid':admin_object.uid,'uname':admin_object.uname}
        if(next != ''):
            return redirect(next)
        else:
            return redirect("/LabDatabase/index")
    else:
        return render(request,"Login.html",{'form':form})


def logout(request):
    request.session.clear()
    return redirect("/myapp/login")

def register(request):
    if(request.method == 'GET'):
        form = RegisterModelForm()
        return render(request,"Register.html",{'form':form})
    form = RegisterModelForm(data= request.POST)
    # print(form)
    if form.is_valid():
        # print("AAAAAA")
        # print(form.cleaned_data)
        if(form.validPassword() == False):
            # print("111111111")
            form.add_error("password","两次输入的密码不一致")
            form.add_error("password_Confirm","两次输入的密码不一致")
            return render(request,"Register.html",{'form':form})
        #数据库校验，获取用户对象,ERROR:None
        admin_object = User.objects.filter(uname=form.cleaned_data['uname']).first()
        # print(admin_object)
        if(admin_object != None):
            form.add_error("uname","用户名已存在")
            # form.add_error("uname","用户名已存在")
            return render(request, "Register.html", {'success': False,'message':"用户名已存在",'form':form})
        #验证正确之后
        #网站生成随机字符串，写到浏览器cookie中；再写入session
        try:
            User.objects.create(uname=form.cleaned_data['uname'], email=form.cleaned_data['email'], password=form.cleaned_data['password'],create_time=datetime.now())
            return redirect("/LabDatabase/login")
        except Exception as e:
            form.add_error("password","密码长度不能少于6位")
            return render(request,'Register.html',{'form':form})
    else:
        return render(request,"Register.html",{'form':form})