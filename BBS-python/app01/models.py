from django.db import models

# Create your models here.
"""
建表思路：先写普通字段，再写外键字段
"""
from django.contrib.auth.models import AbstractUser


# 面向对象的继承
# 用户信息表
class UserInfo(AbstractUser):
    """
    如果继承了AbstractUser
    那么在执行数据库迁移命令的时候auth_user表就不会再创建出来了
    而UserInfo表中会出现auth_user所有的字段外加自己扩展的字段
    这么做的好处在于你能够直接点击你自己的表更加快速的完成操作及扩展

    前提:
        1.在继承之前没有执行过数据库迁移命令
            auth_user没有被创建，如果当前库已经创建了那么你就重新换一个库
        2.继承的类里面不要覆盖AbstractUser里面的字段名
            表里面有的字段都不要动，只扩展额外字段即可
        3.需要在配置文件中告诉django你要用UserInfo替代auth_user(******)
            AUTH_USER_MODEL = 'app01.UserInfo'
                                '应用名.表名'
    """
    phone = models.BigIntegerField(verbose_name='手机号',null=True,blank=True)  #这个字段在admin管理里面会提示不允许为空，null这个字段是告诉数据库可以为空，告诉admin后台管理这个字段允许为空的字段是blank
    #头像
    avatar = models.FileField(upload_to='avatar/',default='avatar/default.png',verbose_name='用户头像')
    """
    给avatar字段传文件对象，该文件会自动存储到avatar文件下，然后avatar字段只保存文件路径avatar/default.png
    """
    create_time = models.DateField(auto_now_add=True)

    #用户表跟站点是一对一关系
    blog = models.OneToOneField(to='Blog',null=True)#为了方便编写所以设置下null=True

    #让admin.py里面建的表名字显示为中文
    # class Meta:
    #     verbose_name_plural='用户表'（修改admin后台管理默认的表名）
    # verbose_name='用户表' （自动加S）

    def __str__(self):
        return self.username
    """
    给每个表下面加上__str方法，方便admin后台管理里面Blog Object能够显示名字，否则都显示Blog Object对象，不太好识别
    """

#个人站点表
class Blog(models.Model):
    site_name = models.CharField(verbose_name='站点名称',max_length=32)
    site_title = models.CharField(verbose_name='站点标题',max_length=32)
    #简单模拟  带你认识样式内部的原理操作
    site_theme = models.CharField(verbose_name='站点样式',max_length=62)#存css/js的文件路径

    def __str__(self):
        return self.site_name

#文章分类表
class Category(models.Model):
    name = models.CharField(verbose_name='文章分类',max_length=32)
    blog = models.ForeignKey(to='Blog',null=True)

    def __str__(self):
        return self.name

#文章标签表
class Tag(models.Model):
    name = models.CharField(verbose_name='文章标签',max_length=32)
    blog = models.ForeignKey(to='Blog', null=True)

    def __str__(self):
        return self.name

#文章表
class Article(models.Model):
    title = models.CharField(verbose_name='文章标题',max_length=64)
    desc = models.CharField(verbose_name='文章简介',max_length=255)
    #文章内容有很多，一般情况下都是使用TextField，后面不需要指定长度了
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True) #文章创建时间

    #数据库字段设计优化
    up_num = models.BigIntegerField(verbose_name='点赞数',default=0)
    down_num = models.BigIntegerField(verbose_name='点踩数',default=0)
    comment_num = models.BigIntegerField(verbose_name='评论数',default=0)

    #外键字段
    blog = models.ForeignKey(to='Blog',null=True)
    category = models.ForeignKey(to='Category',null=True)
    tags = models.ManyToManyField(to='Tag',
                                  through='Article2Tag',
                                  through_fields=('article','tag')
                                  )

    def __str__(self):
        return self.title


#文章跟标签是多对多关系，所以创建一个第三张关系表（半自动的方式创建）
class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')


#点赞点踩表
class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()#按布尔值存储0/1


#评论表
class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content =  models.CharField(verbose_name='评论内容',max_length=255)
    comment_time = models.DateTimeField(verbose_name='评论时间',auto_now_add=True)
    #自关联
    parent = models.ForeignKey(to='self',null=True)#self就是Comment表，这里一定要有null=True,因为有些评论就是根评论


