from django.contrib import admin

# Register your models here.
from app01 import models

admin.site.register(models.UserInfo)
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article)
admin.site.register(models.Article2Tag)
admin.site.register(models.UpAndDown)
admin.site.register(models.Comment)

"""
1.在admin后台管理里面，数据绑定的时候，尤其需要注意的是用户和个人站点不要忘记绑定了！！！！
2.标签
3.标签和文章
"""