import uuid

import django.utils.timezone as timezone
from django.db import models


class Test(models.Model):
    id=models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=20)
    code=models.IntegerField(default=0)
    grade=models.CharField(max_length=10,default='')


class LoadDataStatus(models.Model):
    type=models.TextField(default=None)
    dirpath=models.TextField(default=None)
    exceptionmsgs=models.TextField(default='')
    status=models.CharField(max_length=2)
    createtime=models.DateTimeField('createtime',auto_now_add=True)
    updatetime=models.DateTimeField('updatetime',default=timezone.now)


class AnalysisDataStatus(models.Model):
    cleantablename = models.TextField(default='')
    industrytablename = models.TextField(default='')
    mvpmsg = models.TextField(default='')
    mgpmsg = models.TextField(default='')
    mvimsg = models.TextField(default='')
    mgimsg = models.TextField(default='')
    dirpath = models.TextField(default='')
    status = models.CharField(max_length=2)
    exceptionmsgs = models.TextField(default='')
    createtime = models.DateTimeField('createtime', auto_now_add=True)
    updatetime = models.DateTimeField('updatetime', default=timezone.now)


class User(models.Model):
    username=models.TextField(default='')
    usermobile=models.TextField(default='')
    password=models.TextField(default='')
    realname=models.TextField(default='')
    email=models.TextField(default='')
    is_active=models.TextField(default='')
    createtime = models.DateTimeField('createtime', auto_now_add=True)
    updatetime = models.DateTimeField('updatetime', default=timezone.now)
    class Meta:
        db_table = 'user'

class Role(models.Model):
    roleid=models.TextField(default='')
    rolename=models.TextField(default='')
    usermobile=models.TextField(default='')
    class Meta:
        db_table = 'role'

class Resource(models.Model):
    roleid = models.TextField(default='')
    resourceid=models.TextField(default='')
    resourcename=models.TextField(default='')
    resourceurl=models.TextField(default='')
    resourceparentid=models.TextField(default='')
    resourceparentname=models.TextField(default='')
    class Meta:
        db_table = 'resource'


