"""day72bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views

#用户文件数据存储需要开设接口，所以要导入下面两个模块
from django.views.static import serve
from day72bbs import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',views.home,name='home'),
    url(r'^home/',views.home,name='home'),
    url(r'^register/',views.register,name='reg'),
    url(r'^login/',views.login,name='login'),

    #图片验证码相关URL操作
    url(r'^get_code/',views.get_code,name='gc'),
    #修改密码
    url(r'^set_password/',views.set_password,name='set_pwd'),
    #退出登陆
    url(r'^logout/',views.logout,name='logout'),

    #让后端的指定文件暴露，让用户可以访问到该资源
    url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),  #固定写法，这样可以使media这个文件路径暴露给外界
    # url(r'^app01/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT})  #把app01源码暴露出去

    #个人站点页面搭建
    url(r'^(?P<username>\w+)/$',views.site,name='site'),


]
