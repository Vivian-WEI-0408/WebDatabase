import hashlib

from django.shortcuts import render,HttpResponse,redirect
from django import forms
from WebDatabase import models
#md5加密
def md5(data):
    m = hashlib.md5()
    m.update(data.encode('utf-8'))
    return m.hexdigest()

class LoginModelForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['uname','password']
    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)

def login(request):
    """登录页面"""
    if(request.method == 'GET'):
        form = LoginModelForm()
        return render(request,"login.html",{'form':form})
    form = LoginModelForm(data= request.POST)
    if form.is_valid():
        # print(form.cleaned_data)
        #数据库校验，获取用户对象,ERROR:None
        admin_object = models.User.objects.filter(**form.cleaned_data).first()
        if(not admin_object):
            form.add_error("uname","用户名或密码错误")
            form.add_error("password","用户名或密码错误")
            return render(request, "login.html", {'form': form})
        #验证正确之后
        #网站生成随机字符串，写到浏览器cookie中；再写入session
        request.session['info'] = {'uid':admin_object.uid,'uname':admin_object.uname}
        return redirect("/WebDatabase/Part")
    else:
        return render(request,"login.html",{'form':form})

def logout(request):
    request.session.clear()
    return redirect("/WebDatabase/login")