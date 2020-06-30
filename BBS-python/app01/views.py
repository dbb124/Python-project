from django.shortcuts import render,HttpResponse,redirect

# Create your views here.

#导入forms组件校验用户名密码
from app01.myforms import MyRegForm
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
#统计文章类别需要导入一个聚合函数
from django.db.models import Count



"""
我们之前是直接在views.py中书写的forms组件代码
但是为了接耦合 应该将所有的forms组件代码单独写到一个地方

如果你的项目至始至终只用到一个forms组件那么你可以直接建一个py文件书写即可
	myforms.py
但是如果你的项目需要使用多个forms组件，那么你可以创建一个文件夹在文件夹内根据
forms组件功能的不同创建不同的py文件
	myforms文件夹
		regform.py
		loginform.py
		userform.py
		orderform.py
		...
"""
def register(request):
    """
    注册登录等功能，需要进行用户名校验，也要提示错误信息，所以我们使用forms组件
    """
    form_obj = MyRegForm()
    if request.method=='POST':
        back_dic = {'code': 1000, 'msg': ''}
        #检验数据是否合法
        form_obj=MyRegForm(request.POST)
        #判断数据是否合法
        if form_obj.is_valid():
            # print(form_obj.cleaned_data)#{'username': 'jason', 'password': '123', 'confirm_password': '123', 'email': '123@qq.com'}
            #将检验通过的数据字典赋值给一个变量
            clean_data=form_obj.cleaned_data
            #将字典里面的confirm_password键值对删除
            clean_data.pop('confirm_password')#{'username': 'jason', 'password': '123', 'email': '123@qq.com'}
            #用户头像
            file_obj=request.FILES.get('avatar')
            """
            针对用户头像一定要先判断是否传值，不能直接添加到字典里面去，用户不传时这个字段是none
            """
            if file_obj:
                clean_data['avatar']=file_obj
            #直接操作数据库，保存数据
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url']='/login/'
        else:
            back_dic['code']=2000
            back_dic['msg']=form_obj.errors
        return JsonResponse(back_dic)
    return render(request,'register.html',locals())

def login(request):
    if request.method=='POST':
        back_dic={'code':1000,'msg':''}
        username=request.POST.get('username')
        password=request.POST.get('password')
        code=request.POST.get('code')
        #先检验验证码是否正确（自己决定是否忽略大小写）[统一转大写或者小写再比较]
        if request.session.get('code').upper()==code.upper():
            #校验用户名密码是否正确,用auth 模块校验
            user_obj=auth.authenticate(request,username=username,password=password)
            if user_obj:
                #保存用户状态
                auth.login(request,user_obj)
                back_dic['url']='/home/'
            else:
                back_dic['code']=2000
                back_dic['msg']='用户名或密码错误'
        else:
            back_dic['code']=3000
            back_dic['msg']='验证码错误'
        return JsonResponse(back_dic)
    return render(request,'login.html')

#验证码

from PIL import Image,ImageDraw,ImageFont
"""
图片相关的模块
    pip3 install pillow

导入模块
from PIL import Image,ImageDraw,ImageFont
      Image：生成图片
      ImageDraw：能够在图片上乱涂乱画
      ImageFont：控制字体样式
"""
from io import BytesIO,StringIO
"""
内存管理器模块io导入
from io import BytesIO,StringIO
BytesIO:临时帮你存储数据，返回的时候数据是二进制
StringIO:临时帮你存储数据，返回的时候数据是字符串
"""
#获取图片颜色随机数
import random
def get_random():
    #python中return多个数，返回为一个元组（， ， ，）
    return random.randint(0,255),random.randint(0,255),random.randint(0,255)
def get_code(request):
    #推导步骤1：直接获取后端现成的图片二进制数据发给前端
    # with open(r'static\image\111.jpeg','rb')as f:
    #     data=f.read()
    # return HttpResponse(data)

    #推导步骤2：利用pillow模块动态产生图片
    # img_obj=Image.new('RGB',(420,36),get_random())#(模式，尺寸420,36是前端你设置的图片尺寸，颜色:k可以放英文，也可以放颜色参数)
    # #先将图片对象保存起来
    # with open('xxx.png','wb')as f:
    #     img_obj.save(f,'png')
    # #再将图片读取出来
    # with open('xxx.png','rb')as f:
    #     data=f.read()
    # return HttpResponse(data)

    # 推导步骤3：玩具存储繁琐IO操作效率低，借助于内存管理器模块
    # img_obj = Image.new('RGB', (420, 36), get_random())
    # io_obj = BytesIO() #生成一个内存管理器对象，你可以看成是一个文件句柄
    # img_obj.save(io_obj,'png') #后面一定要指定图片格式
    # return HttpResponse(io_obj.getvalue())  #从内存管理器中读取图片二进制数据返回给前端

    #步骤四：给图片上加字，显示验证码
    img_obj = Image.new('RGB', (420, 36), get_random())
    img_draw = ImageDraw.Draw(img_obj) #产生一个画笔对象
    # img_font = ImageFont.truetype('static\font\111.ttf',30)   #字体样式(路径，字体大小)

    #随机验证码  五位数的随机验证码（数字，大小写字母）
    code=''
    for i in range(5):
        random_upper=chr(random.randint(65,90))
        random_lower=chr(random.randint(97,122))
        random_int=str(random.randint(0,9))
        #从上面三个里面随机选择一个
        tmp=random.choice([random_upper,random_lower,random_int])
        #将产生的随机字符创写入到图片上
        """
        此处为什么一个个写而不是生成好了之后写
        因为一个个写能控制每个字体的间隙，而生成好之后再写的话间隙就没法控制了
        """
        # img_draw.text((i*45,0),tmp,get_random(),img_font)  #((坐标位置)，验证码，图片，字体)
        #将随机字符串进行拼接
        code+=tmp
    print(code)
    #随机验证码再等了的视图函数里面需要用到，要比对，所以要找地方存起来并且其他视图函数也能拿到
    request.session['code']=code
    io_obj=BytesIO()
    img_obj.save(io_obj,'png')
    return HttpResponse(io_obj.getvalue())



#bbs首页（展示用户所以文章信息到首页）
#导入分页器第三方模块
from utils.mypage import Pagination
def home(request):
    #查询本网站所有的文章数据展示到前端页面，这里可以使用分页器做分页
    article_queryset=models.Article.objects.all() #拿到所有文章
    current_page = request.GET.get('page', 1)  # 获取当前页
    all_count = article_queryset.count()  # 获取总数据条数
    # 实例化传值生成对象
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    # 直接对总数据进行切片操作(按实例化对象里面的起始页和结束页进行切)
    page_queryset = article_queryset[page_obj.start:page_obj.end]
    return render(request,'home.html',locals())

#修改密码(这个操作必须是登陆的用户才可以操作，所以需要登陆装饰器)
"""
登陆装饰器模块导入
from django.contrib.auth.decorators import login_required
下面@login_required（）装饰器使用时涉及到全局和局部配置，在settings里面，这里就用全局配置
"""
@login_required
def set_password(request):
    if request.is_ajax():
        back_dic={'code':1000,'msg':''}
        if request.method=='POST':
            old_password=request.POST.get('old_password')
            new_password=request.POST.get('new_password')
            confirm_password=request.POST.get('confirm_password')
            is_right=request.user.check_password(old_password)
            if is_right:
                if new_password==confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg']='修改成功'
                else:
                    back_dic['code']=1001
                    back_dic['msg']='两次密码不一致'
            else:
                back_dic['code']=1002
                back_dic['msg']='原始密码错误'
        return JsonResponse(back_dic)

#退出登陆（用户登陆后才可以这步退出操作）
@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


#个人站点接口
def site(request,username):
    #先校验当前用户名对应的个人站点是否存在
    user_obj=models.UserInfo.objects.filter(username=username).first()
    #用户如果用户不存在则返回一个404页面
    if not user_obj:
        return render(request,'errors.html')
    #用户如果存在，拿到个人站点
    blog=user_obj.blog
    #查询个人站点下所有的文章并展示
    article_list=models.Article.objects.filter(blog=blog)#获取个人站点下的所有文章列表
    current_page = request.GET.get('page', 1)  # 获取当前页
    all_count = article_list.count()  # 获取总数据条数
    # 实例化传值生成对象
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    # 直接对总数据进行切片操作(按实例化对象里面的起始页和结束页进行切)
    page_queryset = article_list[page_obj.start:page_obj.end]

    #1.查询当前用户所有分类及分类下的文章
    category_list=models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values('name','count_num')
    """
    .annotate聚合函数统计之前先分组
    values('name','count_num')  拿到名字跟统计个数
    """
    # print(category_list)#<QuerySet [{'name': 'jason的分类一', 'count_num': 2}, {'name': 'jason的分类二', 'count_num': 1}, {'name': 'jason的分类三', 'count_num': 1}]>

    #2.查询当前用户所有的标签及标签下的文章数
    tag_list=models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values('name','count_num')
    print(tag_list)

    #3.按年月统计分组，导入T润肠Month
    return render(request,'site.html',locals())


