import configparser
import io
import json
import os
import re
import threading
import zipfile
from pathlib import Path
from wsgiref.util import FileWrapper

import pymysql
from datetime import datetime
from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from DataModel.AnalysisData import AnalysisData
from DataModel.LoadAllData import LoadAllData
from DataModel.LoadIndustryData import LoadIndustryData
from DataModel.LoadSingleData import LoadSingleData
from DataModel.models import LoadDataStatus, AnalysisDataStatus, Role, Resource, User
import django.utils.timezone as timezone

lock = threading.Lock()
globalwkdir=''
globaldatadict={}
globaltablenames=[]

def QueryExportStatus(request):
    if globaldatadict.get('cleandata') is None:
        return JsonResponse({"result": {"status": '200', 'data': []}})
    chooselist = globaldatadict['cleandata']
    reschooselist = []
    for tmp in chooselist:
         reschooselist.append(tmp)
    return JsonResponse({"result": {"status": '200', 'data': reschooselist}})

def CheckCleanExist(request):
    try:
        cleantablename=request.POST['cleantablename']
        existflag=False
        tablelist = ''
        for tmp in globaltablenames:
            if tmp==cleantablename:
                existflag=True
            tablelist=tablelist+tmp+","
        if existflag is True:
            return JsonResponse({"status": '201', "data": tablelist})
        return JsonResponse({"status": '200'})
    except Exception as ex:
        print("Exception: %s" % ex)
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def ExportData2Tables(requset):
    datatablename1=requset.POST['basetable1']
    datatablename2 = requset.POST['basetable2']
    datatablename3 = requset.POST['basetable3']
    industrytablename=requset.POST['industrytable']
    cleantable=requset.POST['cleantable']
    tabletype='cleandata'
    try:
        loadDataStatuslist = LoadDataStatus.objects.filter(status='0', type=tabletype)
        if len(loadDataStatuslist) > 0:
            loadDataStatuslistres = serializers.serialize("json", loadDataStatuslist)
            return JsonResponse({"result": {"status": '201', "data": loadDataStatuslistres}})
        loaddatastatus = LoadDataStatus(type=tabletype, dirpath=cleantable, status='0',updatetime=timezone.now())
        loaddatastatus.save()
        LoadAllData(datatablename3, datatablename2, datatablename1,
                    industrytablename,cleantable,loaddatastatus.id)
        print("-------end----------")
        return JsonResponse({"result": {"status": '200'}})
    except Exception as ex:
        print("Exception: %s" % ex)
        if loaddatastatus is not None and loaddatastatus.id is not None:
            LoadDataStatus.objects.filter(id=loaddatastatus.id).update(status='1',exceptionmsgs=ex,updatetime=timezone.now())
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def testroute(request,m):
    print(m)
    return render(request, 'runoob.html', {'fuck': m, 'name': 'picture'})

def testupload(request):
    print("--------------------------")
    foldername=request.POST.get('foldername')
    file=request.FILES.get('file')
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    currentdir = os.getcwd()
    basedata = config['loaddatadir']['datadir']
    currentbasedir = currentdir + "\\" + basedata + "\\" + foldername + "\\"
    lock.acquire()
    if not os.path.exists(currentbasedir):
        os.makedirs(currentbasedir)
        print("------------目录创建成功！")
    currentfile=currentbasedir+file.name
    lock.release()
    f = open(currentfile,'wb+')
    for chunk in file.chunks():
        f.write(chunk)
    f.close()
    return JsonResponse({"result": 'ok'})

def QueryByData(request):
    type=request.POST['type']
    tablename=request.POST['tablename']
    if globaldatadict.get(type) is None:
       loadDataStatus = LoadDataStatus.objects.filter(type=type, status='1')
       datadictlist = []
       for tmp in loadDataStatus:
           datadict = {}
           datadict['id'] = tmp.id
           createtime = tmp.createtime
           datadict['createtime'] = createtime
           filename = tmp.dirpath.split("\\")[len(tmp.dirpath.split("\\")) - 2]
           datadict['dirpath'] = filename
           datadictlist.append(datadict)
       globaldatadict[type] = datadictlist
    chooselist=globaldatadict[type]
    pareent=".*?"+tablename+".*?"
    regex_start = re.compile(pareent)
    reschooselist=[]
    for tmp in chooselist:
        reschoosedict={}
        if re.match(regex_start, tmp['dirpath']) is not None:
            reschoosedict=tmp
            reschooselist.append(reschoosedict)
    return JsonResponse({"result": {"status": '200','data':reschooselist}})

def QueryData(request):
    loadOgrdataDataStatus=LoadDataStatus.objects.filter(type='orgdata',status='1')
    if len(loadOgrdataDataStatus)>0:
        globaldatadict['orgdata']=[]
        loadOgrdataDataStatusjsonstr = serializers.serialize("json", loadOgrdataDataStatus)
        loadOgrdataDataStatusjson=json.loads(loadOgrdataDataStatusjsonstr)
        orgdatadictlist=[]
        for tmp in loadOgrdataDataStatusjson:
            orgdatadict = {}
            orgdatadict['id']=tmp['pk']
            orcreatetime= tmp["fields"]['createtime']
            orgdatadict['createtime']=orcreatetime
            filename=tmp['fields']['dirpath'].split("\\")[len(tmp['fields']['dirpath'].split("\\"))-2]
            orgdatadict['dirpath'] = filename
            orgdatadictlist.append(orgdatadict)
        globaldatadict['orgdata']=orgdatadictlist
    loadIndustryDataStatus = LoadDataStatus.objects.filter(type='industry', status='0')
    if len(loadIndustryDataStatus)>0:
        globaldatadict['industry'] = []
        loadIndustryDataStatusjsonstr = serializers.serialize("json", loadIndustryDataStatus)
        loadIndustryDataStatusjson = json.loads(loadIndustryDataStatusjsonstr)
        industrydatadictlist = []
        for tmp1 in loadIndustryDataStatusjson:
            industrydatadict = {}
            industrydatadict['id'] = tmp1['pk']
            industrydatadict['createtime'] = tmp1["fields"]['createtime']
            filename = tmp1['fields']['dirpath'].split("\\")[len(tmp1['fields']['dirpath'].split("\\")) - 2]
            industrydatadict['dirpath'] = filename
            industrydatadictlist.append(industrydatadict)
        globaldatadict['industry'] = industrydatadictlist
    loadCleanDataStatus = LoadDataStatus.objects.filter(type='cleandata', status='0')
    if len(loadCleanDataStatus)>0:
        globaldatadict['cleandata'] = []
        loadCleanDataStatusjsonstr = serializers.serialize("json", loadCleanDataStatus)
        loadCleanDataStatusjson = json.loads(loadCleanDataStatusjsonstr)
        cleandatadictlist = []
        for tmp1 in loadCleanDataStatusjson:
            cleandatadict = {}
            cleandatadict['id'] = tmp1['pk']
            cleandatadict['createtime'] = tmp1["fields"]['createtime']
            cleandatadict['dirpath'] = filename
            cleandatadictlist.append(cleandatadict)
        globaldatadict['cleandata'] = cleandatadictlist
    print("---------------query tables---------------------")
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    print(config['db']['host'])
    print(config['db']['user'])
    print(config['db']['database'])
    print(config['db']['port'])
    print(config['db']['password'])
    host = config['db']['host']
    user = config['db']['user']
    password = config['db']['password']
    database = config['db']['database']
    port = int(config['db']['port'])
    db = pymysql.connect(host=host, user=user,
                         password=password, database=database, port=port)
    tablessql = "show tables;"
    cursor = db.cursor()
    cursor.execute(tablessql)
    tableresults = cursor.fetchall()
    i=0
    while i<len(tableresults):
        globaltablenames.append(tableresults[i][0])
        i=i+1
    return JsonResponse({"result": {"status": '200'}})

def renderQueryAnalysisStatusHtml(request):
    return render(request, 'queryanalysisstatustable.html')

def renderExportLayHtml(request):
    return render(request, 'exportlayinput.html')

def renderShowStaticsDetail(request):
    return render(request,'showstaticsdetail.html')

def renderBaseHtml(request):
    return render(request, 'fileinput.html')

def renderAnalysisHtml(request):
    return render(request, 'showstatics.html')

def renderIndustryHtml(request):
    return render(request, 'industryinput.html')

def renderQueryHtml(request):
    return render(request, 'querystatustable.html')

def renderindexcompare(request):
    return render(request, 'showstatics.html')

def renderinsureanalysislayhtml(request):
    return render(request, 'insureanalysislay.html')

def QueryBaseDataDir(request):
    foldername = request.POST.get('foldername')
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    currentdir = os.getcwd()
    basedata = config['loaddatadir']['datadir']
    querycurrentbasedir = currentdir + "\\" + basedata + "\\"
    try:
        for root, dirs, files in os.walk(querycurrentbasedir):
            print(root)  # 当前目录路径
            print(dirs)  # 当前路径下所有子目录
            print(files)  # 当前路径下所有非目录      子文件
            break
        for dir in dirs:
            print("------------------------------------", dir)
            if dir == foldername:
                return JsonResponse({"result": {"status": '202', "data": dirs}})
        return JsonResponse({"result": {"status": '200'}})
    except Exception as ex:
        print("Exception: %s" % ex)
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def QueryBaseDataStatus(request):
    type=request.POST.get('type')
    try:
        loadDataStatuslist = LoadDataStatus.objects.filter(status='0',type=type)
        if len(loadDataStatuslist)>0:
            loadDataStatuslistres = serializers.serialize("json", loadDataStatuslist)
            return JsonResponse({"result": {"status": '201',"data":loadDataStatuslistres}})
        else:
            return JsonResponse({"result": {"status": '200'}})
    except Exception as ex:
        print("Exception: %s "%ex)
        return JsonResponse({"result": {"status": '500',"msg":"内部异常"}})

def EditStatus(request):
    try:
        print("------------edit-------------------")
        id=request.POST.get('id')
        LoadDataStatus.objects.filter(id=id).update(status='1')
        return JsonResponse({"result": {"status": '200'}})
    except Exception as ex:
        print("Exception-----------------: %s" %ex)
        return JsonResponse({"result": {"status": '500'}})

def deleteTable(tablename):
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    print(config['db']['host'])
    print(config['db']['user'])
    print(config['db']['database'])
    print(config['db']['port'])
    print(config['db']['password'])
    host = config['db']['host']
    user = config['db']['user']
    password = config['db']['password']
    database = config['db']['database']
    port = int(config['db']['port'])
    db = pymysql.connect(host=host, user=user,
                         password=password, database=database, port=port)
    cur = db.cursor()
    droptablesql = "drop table if exists " + tablename + ";"
    print("droptablesql:-----------",droptablesql)
    cur.execute(droptablesql)
    cur.close()

def deleteDir(dirname):
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    currentdir = os.getcwd()
    basedata = config['loaddatadir']['datadir']
    currentbasedir = currentdir + "\\" + basedata + "\\" + dirname + "\\"
    my_file = Path(currentbasedir)
    if my_file.is_dir():
        for root, dirs, files in os.walk(currentbasedir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(currentbasedir)

def DeleteStatus(request):
    try:
        print("------------delete table-------------------")
        tablename=request.POST.get('filename')
        deleteTable(tablename)
    except Exception as ex:
        print("------------delete-------------------")
        id = request.POST.get('id')
        LoadDataStatus.objects.filter(id=id).update(status='2',exceptionmsgs=ex,updatetime=timezone.now())
        print("Exception-----------------: %s" % ex)
        return JsonResponse({"result": {"status": '500','msg':"表删除出现异常"}})
    try:
        print("------------delete firdir-------------------")
        deleteDir(tablename)
    except Exception as ex:
        print("------------delete-------------------")
        id = request.POST.get('id')
        LoadDataStatus.objects.filter(id=id).update(status='2',exceptionmsgs=ex,updatetime=timezone.now())
        print("Exception-----------------: %s" %ex)
        return JsonResponse({"result": {"status": '500', 'msg': "文件夹删除出现异常"}})
    print("------------delete-------------------")
    id = request.POST.get('id')
    LoadDataStatus.objects.filter(id=id).update(status='2',updatetime=timezone.now())
    return JsonResponse({"result": {"status": '200'}})

def QueryAnysisStatus(request):
    print("------------------ query page ---------------------")
    page = request.GET.get('page')
    pageSize = int(request.GET.get('pageSize'))

    cleantablename = request.GET.get('analysistablename')
    industry = request.GET.get('industry')
    status = request.GET.get('status')
    createtime = request.GET.get('createtime')
    updatetime = request.GET.get('updatetime')
    queryparam={}
    if cleantablename is not None and len(cleantablename.strip()) != 0:
        queryparam['cleantablename'] = cleantablename
    if industry is not None and len(industry.strip()) != 0:
        queryparam['industrytablename'] = type
    if status is not None and len(status.strip()) != 0:
        queryparam['status'] = status
    if createtime is not None and len(createtime.strip()) != 0:
        createtimedatetime = datetime.strptime(createtime.strip(), '%Y-%m-%d')
        createtimeyear = createtimedatetime.date().year
        createtimemonth = createtimedatetime.date().month
        createtimeday = createtimedatetime.date().day
        queryparam['createtime__year'] = createtimeyear
        queryparam['createtime__month'] = createtimemonth
        queryparam['createtime__day'] = createtimeday
    if updatetime is not None and len(updatetime.strip()) != 0:
        updatetimedatetime = datetime.strptime(updatetime.strip(), '%Y-%m-%d')
        updatetimeyear = updatetimedatetime.date().year
        updatetimemonth = updatetimedatetime.date().month
        updatetimeday = updatetimedatetime.date().day
        queryparam['updatetime__year'] = updatetimeyear
        queryparam['updatetime__month'] = updatetimemonth
        queryparam['updatetime__day'] = updatetimeday
    if queryparam is None or queryparam == {}:
        loadDataStatuslist = AnalysisDataStatus.objects.all()
    else:
        loadDataStatuslist = AnalysisDataStatus.objects.filter(**queryparam)
    response = {}
    paginator = Paginator(loadDataStatuslist, pageSize)
    total = paginator.count
    try:
        loadDataStatus = paginator.page(page)
        rows = []
        for tmp in loadDataStatus.object_list:
            # print({'id': tmp.id, 'type': tmp.type, 'status': tmp.status,
            #              'createtime': tmp.createtime,
            #              'updatetime': tmp.updatetime,
            #              'dirpath': tmp.dirpath})
            rows.append({'id': tmp.id, 'cleantablename': tmp.cleantablename, 'industrytablename': tmp.industrytablename,
                         'dirpath': tmp.dirpath, 'status': tmp.status, 'createtime': tmp.createtime.strftime('%Y-%m-%d %H:%M:%S'),
                         'updatetime': tmp.updatetime.strftime('%Y-%m-%d %H:%M:%S'),
                         'exceptionmsgs': tmp.exceptionmsgs})
            print(tmp)
        # data = serializers.serialize("json", loadDataStatus.object_list)
        # jsonarray=json.loads(data)
        # rows=[]
        # for tmp in jsonarray:
        return JsonResponse({'total': total, 'rows': rows})
    except PageNotAnInteger as ex:
        print("PageNotAnInteger------------: %s " % ex)
        return JsonResponse(response)
    except EmptyPage as ex:
        print("EmptyPage-----------------: %s" % ex)
        return JsonResponse(response)


def QueryStatusPage(request):
    print("------------------ query page ---------------------")
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    currentdir = os.getcwd()
    basedata = config['loaddatadir']['datadir']

    page = request.GET.get('page')
    pageSize = int(request.GET.get('pageSize'))

    dirpath = request.GET.get('dirpath')
    type = request.GET.get('type')
    status = request.GET.get('status')
    createtime = request.GET.get('createtime')
    updatetime = request.GET.get('updatetime')
    queryparam={}
    if dirpath is not None and len(dirpath.strip())!=0:
        queryparam['dirpath'] = currentdir + "\\" +   basedata + "\\" + dirpath + "\\"
    if type is not None and len(type.strip())!=0:
        queryparam['type'] = type
    if status is not None and len(status.strip())!=0:
        queryparam['status'] = status
    if createtime is not None and len(createtime.strip())!=0:
        createtimedatetime=datetime.strptime(createtime.strip(),'%Y-%m-%d')
        createtimeyear=createtimedatetime.date().year
        createtimemonth = createtimedatetime.date().month
        createtimeday = createtimedatetime.date().day
        queryparam['createtime__year'] = createtimeyear
        queryparam['createtime__month'] = createtimemonth
        queryparam['createtime__day'] = createtimeday
    if updatetime is not None and len(updatetime.strip())!=0:
        updatetimedatetime = datetime.strptime(updatetime.strip(), '%Y-%m-%d')
        updatetimeyear = updatetimedatetime.date().year
        updatetimemonth = updatetimedatetime.date().month
        updatetimeday = updatetimedatetime.date().day
        queryparam['updatetime__year'] = updatetimeyear
        queryparam['updatetime__month'] = updatetimemonth
        queryparam['updatetime__day'] = updatetimeday
    if queryparam is None or queryparam=={}:
        loadDataStatuslist = LoadDataStatus.objects.all()
    else:
        loadDataStatuslist = LoadDataStatus.objects.filter(**queryparam)
    response = {}
    paginator = Paginator(loadDataStatuslist, pageSize)
    total = paginator.count
    try:
        loadDataStatus = paginator.page(page)
        rows = []
        for tmp in loadDataStatus.object_list:
            # print({'id': tmp.id, 'type': tmp.type, 'status': tmp.status,
            #              'createtime': tmp.createtime,
            #              'updatetime': tmp.updatetime,
            #              'dirpath': tmp.dirpath})
            rows.append({'id': tmp.id, 'type': tmp.type, 'status': tmp.status,
                         'createtime': tmp.createtime.strftime('%Y-%m-%d %H:%M:%S'),
                         'updatetime': tmp.updatetime.strftime('%Y-%m-%d %H:%M:%S'),
                         'dirpath': tmp.dirpath})
            print(tmp)
        # data = serializers.serialize("json", loadDataStatus.object_list)
        # jsonarray=json.loads(data)
        # rows=[]
        # for tmp in jsonarray:
        return JsonResponse({'total': total, 'rows': rows})
    except PageNotAnInteger as ex:
        print("PageNotAnInteger------------: %s " % ex)
        return JsonResponse(response)
    except EmptyPage as ex:
        print("EmptyPage-----------------: %s" % ex)
        return JsonResponse(response)


def CreateTableAndInsertIndustry(request):
    print("------------------------------industrydata--------------------------")
    print(request)
    foldername = request.POST.get('foldername')
    tablename = request.POST.get('tablename')
    tabletype = request.POST.get('tabletype')
    filename = request.POST.get('filename')
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    currentdir = os.getcwd()
    basedata = config['loaddatadir']['datadir']
    loaddatastatus = None
    try:
        # status:0--进行中 1--完成 2--删除
        loadDataStatuslist = LoadDataStatus.objects.filter(status='0', type=tabletype)
        if len(loadDataStatuslist) > 0:
            loadDataStatuslistres = serializers.serialize("json", loadDataStatuslist)
            return JsonResponse({"result": {"status": '201', "data": loadDataStatuslistres}})
        currentbasedir = currentdir + "\\" + basedata + "\\" + foldername + "\\"
        loaddatastatus = LoadDataStatus(type=tabletype, dirpath=currentbasedir, status='0')
        loaddatastatus.save()
        print("loaddatastatus save--------------------------")
        LoadIndustryData(currentbasedir, tablename, filename)
        LoadDataStatus.objects.filter(id=loaddatastatus.id).update(status='1', updatetime=timezone.now())
        return JsonResponse({"result": {"status": '200'}})
    except Exception as ex:
        print("Exception: %s" % ex)
        if loaddatastatus is not None and loaddatastatus.id is not None:
            LoadDataStatus.objects.filter(id=loaddatastatus.id).update(status='1', exceptionmsgs=ex,
                                                                       updatetime=timezone.now())
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def CreateTableAndInsertBaseData(request):
    print("------------------------------basedata--------------------------")
    print(request)
    foldername = request.POST.get('foldername')
    tablename = request.POST.get('tablename')
    tabletype = request.POST.get('tabletype')
    filename = request.POST.get('filename')
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    currentdir = os.getcwd()
    basedata = config['loaddatadir']['datadir']
    loaddatastatus=None
    try:
        # for root, dirs, files in os.walk(querycurrentbasedir):
        #     print(root)  # 当前目录路径
        #     print(dirs)  # 当前路径下所有子目录
        #     print(files)  # 当前路径下所有非目录      子文件
        #     break
        # for dir in dirs:
        #     print("------------------------------------", dir)
        #     if dir == foldername:
        #         return JsonResponse({"result": {"status": '202', "data": dirs}})
        globalwkdir = currentdir + "\\" + basedata + "\\"
        #查询表名是否存在
        # if tabletype=='orgdata':
         # 查询是否存在未完成任务
        loadDataStatuslist=LoadDataStatus.objects.filter(status='0',type=tabletype)
        if len(loadDataStatuslist)>0:
            loadDataStatuslistres = serializers.serialize("json", loadDataStatuslist)
            return JsonResponse({"result": {"status": '201', "data": loadDataStatuslistres}})
        currentbasedir = currentdir + "\\" + basedata + "\\" + foldername + "\\"
        loaddatastatus=LoadDataStatus(type=tabletype,dirpath=currentbasedir,status='0')
        loaddatastatus.save()
        LoadSingleData(currentbasedir,tablename,loaddatastatus.id)
        print("-------end----------")
        # if tabletype=='industry':
        #     #status:0--进行中 1--完成 2--删除
        #     loadDataStatuslist = LoadDataStatus.objects.filter(status='0', type=tabletype)
        #     if len(loadDataStatuslist) > 0:
        #         loadDataStatuslistres = serializers.serialize("json", loadDataStatuslist)
        #         return JsonResponse({"result": {"status": '201', "data": loadDataStatuslistres}})
        #     currentbasedir = currentdir + "\\" + basedata + "\\" + foldername + "\\"
        #     loaddatastatus = LoadDataStatus(type=tabletype, dirpath=currentbasedir, status='0')
        #     loaddatastatus.save()
        #     print("loaddatastatus save--------------------------")
        #     LoadIndustryData(currentbasedir,tablename,filename)
        #     LoadDataStatus.objects.filter(id=loaddatastatus.id).update(status='1',updatetime=timezone.now())
        return JsonResponse({"result": {"status":'200'}})
    except Exception as ex:
        print("Exception: %s" % ex)
        if loaddatastatus is not None and loaddatastatus.id is not None:
            LoadDataStatus.objects.filter(id=loaddatastatus.id).update(status='1',exceptionmsgs=ex,updatetime=timezone.now())
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def AnalysisProc(cleantablename,industrytable,currentdir):
    try:
        # todo:查询表是否存在，有返回，无创建文件夹，分析生成数据
        analysisDataStatus = AnalysisDataStatus.objects.filter(status='0', cleantablename=cleantablename,
                                                               industrytablename=industrytable)
        if len(analysisDataStatus) > 0:
            return JsonResponse({"result": {"status": '500', "msg": "存在相同的量两个表数据在分析"}})
        analysisDataStatus = AnalysisDataStatus.objects.filter(status='1', cleantablename=cleantablename,
                                                               industrytablename=industrytable)
        if len(analysisDataStatus) > 0:
            return JsonResponse({"result": {"status": '500', "msg": "已经存在两个表数据分析结果"}})
        # todo:插入状态
        lock.acquire()
        if not os.path.exists(currentdir):
            os.makedirs(currentdir)
            print("------------目录创建成功！")
        lock.release()
        analysisDataStatus = AnalysisDataStatus(cleantablename=cleantablename, industrytablename=industrytable,
                                                dirpath=(cleantablename + industrytable), status='0')
        analysisDataStatus.save()
        # 分析
        AnalysisData((cleantablename + industrytable), currentdir, cleantablename, industrytable, analysisDataStatus.id)
        # todo:插入完成状态
        AnalysisDataStatus.objects.filter(id=analysisDataStatus.id).update(status='1', updatetime=timezone.now())
        return JsonResponse({"result": {"status": '200'}})
    except Exception as ex:
        print("Exception: %s" % ex)
        if analysisDataStatus is not None and analysisDataStatus.id is not None:
            AnalysisDataStatus.objects.filter(id=analysisDataStatus.id).update(status='2', exceptionmsgs=ex,
                                                                               updatetime=timezone.now())
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})


def AnysisData(request):
        cleantablename=request.POST['cleantablename']
        industrytable = request.POST['industrytable']
        taskid=request.POST['taskid']
        config = configparser.ConfigParser()
        config.read('loadsingledataproperties.conf')
        currentdir = os.getcwd()
        basedata = config['analysisdir']['datadir']
        currentdir = currentdir + "\\" + basedata + "\\" + cleantablename + industrytable + "\\"
        return AnalysisProc(cleantablename,industrytable,currentdir)

def DownLoadAnalysisFile(request):
    cleantablename = request.GET['cleantablename']
    industrytable = request.GET['industrytable']
    dirpath = request.GET['dirpath']
    config = configparser.ConfigParser()
    config.read('loadsingledataproperties.conf')
    currentdir = os.getcwd()
    basedata = config['analysisdir']['datadir']
    currentdir = currentdir + "\\" + basedata + "\\" + dirpath + "\\"
    if os.path.exists(currentdir):
        # 创建BytesIO
        s = io.BytesIO()
        zip = zipfile.ZipFile(s, 'w')
        for root, dirs, files in os.walk(currentdir):
            print(root)  # 当前目录路径
            print(dirs)  # 当前路径下所有子目录
            print(files)  # 当前路径下所有非目录      子文件
        for file in files:
            tmpexcelpath = currentdir + file
            print("------------------------------------tmpexcelpath：", tmpexcelpath)
            zip.write(tmpexcelpath, file)
            # 关闭文件
        zip.close()
        s.seek(0)
        # 用FileWrapper类来迭代器化一下文件对象，实例化出一个经过更适合大文件下载场景的文件对象，实现原理相当与把内容一点点从文件中读取，放到内存，下载下来，直到完成整个下载过程。这样内存就不会担心你一下子占用它那么多空间了。
        wrapper = FileWrapper(s)
        response = HttpResponse(wrapper)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(datetime.now().strftime("%Y-%m-%d"))
        # 指针回到初始位置，没有这一句前端得到的zip文件会损坏
        return response

def ShowAllData(request):
    try:
        cleantablename = request.POST['cleantablename']
        industrytable = request.POST['industrytable']
        dirpath = request.POST['dirpath']
        querydata=AnalysisDataStatus.objects.filter(cleantablename=cleantablename,
                                          industrytablename=industrytable,status=1).first()

        resultdict={}
        #高价值行业
        mvi= json.loads(querydata.mvimsg)
        mvidict=[]
        mvilegendlist = []
        for k,v in mvi.items():
            mvilegendlist.append(k)
            tmpdict={}
            tmpdict['name'] = k
            tmpdict['value'] = v
            mvidict.append(tmpdict)
        resultdict['mvi']=mvidict
        resultdict['mvilegendlist'] = mvilegendlist

        #高渗透行业
        mgi = json.loads(querydata.mgimsg)
        mgidict = []
        mgilegendlist = []
        for k1,v1 in mgi.items():
            mgilegendlist.append(k1)
            tmpdict1={}
            tmpdict1['name'] = k1
            tmpdict1['value'] = v1
            mgidict.append(tmpdict1)
        resultdict['mgi'] = mgidict
        resultdict['mgilegendlist'] = mvilegendlist
        prolist=[]
        mvp = json.loads(querydata.mvpmsg)
        for k2,v2 in mvp.items():
            prolist.append(k2)
        resultdict['prolist'] = prolist
        print(resultdict)
        return JsonResponse({"result": {"status": '200', "data": resultdict}})
    except Exception as ex:
        print("Exception: %s" % ex)
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def ShowDetailData(request):
    try:
        cleantablename = request.POST['cleantablename']
        industrytable = request.POST['industrytable']
        dirpath = request.POST['dirpath']
        proname = request.POST['proname']
        querydata=AnalysisDataStatus.objects.filter(cleantablename=cleantablename,
                                          industrytablename=industrytable,status=1).first()

        resultdict={}
        #产品高价值行业
        mvp= json.loads(querydata.mvpmsg)
        mvpdict=[]
        mvplegendlist = []
        pos=0
        for k,v in mvp.get(proname).items():
            if pos==0:
                pos=pos+1
                continue
            mvplegendlist.append(k)
            tmpdict={}
            tmpdict['name'] = k
            tmpdict['value'] = v
            mvpdict.append(tmpdict)
        resultdict['mvp']=mvpdict
        resultdict['mvplegendlist'] = mvplegendlist

        #产品高渗透行业
        mgp = json.loads(querydata.mgpmsg)
        mgpdict = []
        mgplegendlist = []
        pos1 = 0
        for k1,v1 in mgp.get(proname).items():
            if pos1==0:
               pos1 = pos1 + 1
               continue
            mgplegendlist.append(k1)
            tmpdict1={}
            tmpdict1['name'] = k1
            tmpdict1['value'] = v1
            mgpdict.append(tmpdict1)
        resultdict['mgp'] = mgpdict
        resultdict['mgplegendlist'] = mgplegendlist
        print(resultdict)
        return JsonResponse({"result": {"status": '200', "data": resultdict}})
    except Exception as ex:
        print("Exception: %s" % ex)
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def GetMenu(request):
    username=request.POST['username']
    usermobile=request.POST['usermobile']
    try:
        userinfo=User.objects.filter(usermobile=usermobile).first()
        rolelist = Role.objects.filter(usermobile=usermobile).all()
        resourcedict = {}
        for tmprole in rolelist:
            resource = Resource.objects.filter(roleid=tmprole.roleid).all()
            for tmpresource in resource:
                if resourcedict.get(tmpresource.resourceparentid) is None:
                    tmplist = []
                    tmpresourcedict = {}
                    tmpresourcedict['id'] = tmpresource.resourceid
                    tmpresourcedict['name'] = tmpresource.resourcename
                    tmpresourcedict['url'] = tmpresource.resourceurl
                    tmplist.append(tmpresourcedict)
                    resourcedict[tmpresource.resourceparentid] = tmplist
                else:
                    tmpresourcedict = {}
                    tmpresourcedict['id'] = tmpresource.resourceid
                    tmpresourcedict['name'] = tmpresource.resourcename
                    tmpresourcedict['url'] = tmpresource.resourceurl
                    tmpresultlist = resourcedict.get(tmpresource.resourceparentid)
                    flag = False
                    for tmpdict in tmpresultlist:
                        if tmpdict.get('id') == tmpresource.resourceid:
                            flag = True
                            break
                    if flag is True:
                        continue
                    tmpresultlist.append(tmpresourcedict)
        resultlist = []
        for k, v in resourcedict.items():
            tmpresultdict = {}
            tmpparentresource = Resource.objects.filter(resourceparentid=k).first()
            tmpresultdict['id'] = tmpparentresource.resourceparentid
            tmpresultdict['name'] = tmpparentresource.resourceparentname
            tmpresultdict['content'] = v
            resultlist.append(tmpresultdict)
        return JsonResponse({"result": {"status": '200', "data": resultlist,'username':userinfo.realname}})
    except Exception as ex:
        print("Exception: %s" % ex)
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})

def LoginComfirm(request):
    try:
        ismobile=request.POST['ismobile']
        password=request.POST['password']
        username=request.POST['username']
        usermobile=request.POST['usermobile']
        if ismobile=='0':
            userinfo=User.objects.filter(username=username,password=password,is_active=1)
        if ismobile=='1':
            userinfo = User.objects.filter(usermobile=usermobile, password=password,is_active=1)
        if len(userinfo)>0:
            json={'uersmobile':userinfo.first().usermobile,'username':userinfo.first().usermobile,'realname':userinfo.first().realname}
            return JsonResponse({"result": {"status": '200', "data": json}})
        return JsonResponse({"result": {"status": '501', "msg": "登陆失败，登录名或者密码不正确或不存在"}})
    except Exception as ex:
        print("Exception: %s" % ex)
        return JsonResponse({"result": {"status": '500', "msg": "内部异常"}})


