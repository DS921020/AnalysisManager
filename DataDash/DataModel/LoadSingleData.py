#!/usr/bin/python
# -*- coding: UTF-8 -*-
import configparser
import os
import pymysql
import re
from queue import Queue
from dbutils.pooled_db import PooledDB
import django.utils.timezone as timezone
import time
import xlrd
import logging

import threading

from DataModel.models import LoadDataStatus

logger = logging.getLogger(__name__)
threadnum = 0
Lock = threading.Lock()

class LoadSingleData:
    host=''
    user=''
    password=''
    database=''
    port=''
    db=None
    config=None
    currentbasedir=''
    loadtablename=''
    loadlimit=''
    insertlimit=''
    filelists=[]
    pool=None

    def __init__(self,currentbasedir,tablename,primaryid):
        config = configparser.ConfigParser()
        config.read('loadsingledataproperties.conf')
        logger.info("......loadsingledataproperties...........")
        logger.info(config['db']['host'])
        logger.info(config['db']['user'])
        logger.info(config['db']['database'])
        logger.info(config['db']['port'])
        logger.info(config['db']['password'])

        print(config['db']['host'])
        print(config['db']['user'])
        print(config['db']['database'])
        print(config['db']['port'])
        print(config['db']['password'])
        self.host = config['db']['host']
        self.user = config['db']['user']
        self.password = config['db']['password']
        self.database = config['db']['database']
        self.port = int(config['db']['port'])
        self.primaryid=primaryid
        maxconnections = 100  # 最大连接数
        self.pool = PooledDB(
            pymysql,
            maxconnections,
            host=self.host,
            user=self.user,
            port=3306,
            passwd=self.password,
            db=self.database,
            use_unicode=True)

        self.currentbasedir = currentbasedir
        self.loadtablename = tablename
        self.loadlimit = int(config['loadlimit']['limit'])
        self.insertlimit = int(config['insertlimit']['limit'])
        self.createTable()
        self.expoertExcel2Db()

    def createTable(self):
        logger.info("-------------------------createorgtable ")
        print("-------------------------createorgtable ")
        try:
            db=self.pool.connection()
            cur = db.cursor()
            droptablesql = "drop table if exists " + self.loadtablename + ";"
            cur.execute(droptablesql)
            createtablesql = "create table " + self.loadtablename + """(
                                              prodate 			VARCHAR(20),
                                              proarea 			VARCHAR(20),
                                              procounty 			VARCHAR(20),
                                              compamyid 			VARCHAR(40),
                                              compamyname 		VARCHAR(80),
                                              compamylevel 		VARCHAR(20),
                                              compamymanagernum 		VARCHAR(20),
                                              compamymanagername 		VARCHAR(40),
                                              period 					VARCHAR(6),
                                              customersincome 			float(20,6),
                                              customersincrease 			float(20,6),
                                              communicateincome 			float(20,6),
                                              communicateincrease 		float(20,6),
                                              communicateincome1 			float(20,6),
                                              communicateincrease1 		float(20,6),
                                              communicateincome2 			float(20,6),
                                              communicateincrease2 		float(20,6),
                                              companyproincome			float(20,6),
                                              companyproincrease			float(20,6),
                                              dictincome					float(20,6),
                                              dictincrease				float(20,6),
                                              dictrate					float(20,6),
                                              iopincome					float(20,6),
                                              iopincrease				float(20,6),
                                              ioprate					float(20,6),
                                              cloudincome				float(20,6),
                                              cloudincrease				float(20,6),
                                              idcincome					float(20,6),
                                              idcincrease				float(20,6),
                                              ictincome					float(20,6),
                                              ictincrease				float(20,6),
                                              eduincome				float(20,6),
                                              eduincrease				float(20,6),
                                              eduincome1				float(20,6),
                                              cloudmovieincome					float(20,6),
                                              cloudmovieincrease				float(20,6),
                                              andjiangincome				float(20,6),
                                              andjiangincrease				float(20,6),
                                              qianliyanincome				float(20,6),
                                              qianliyanincrease				float(20,6),
                                              cailinincome				float(20,6),
                                              cailinincrease				float(20,6),
                                              workmoblieincome				float(20,6),
                                              workmoblieincrease				float(20,6),
                                              prolanincome				float(20,6),
                                              prolanincrease				float(20,6),
                                              dataprolanincome				float(20,6),
                                              dataprolanincrease				float(20,6),
                                              netprolanincome				float(20,6),
                                              netprolanincrease				float(20,6),
                                              companyprolanincome				float(20,6),
                                              companyprolanincrease				float(20,6),
                                              comvoiceprolanincome				float(20,6),
                                              comvoiceprolanincrease				float(20,6),
                                              imsprolanincome				float(20,6),
                                              imsprolanincrease				float(20,6),
                                              voiceprolanincome				float(20,6),
                                              voiceprolanincrease				float(20,6),
                                              sibaiincome				float(20,6),
                                              sibaiincrease				float(20,6),
                                              comduancaiincome				float(20,6),
                                              comduancaiincrease				float(20,6),
                                              comduanincome				float(20,6),
                                              comduanincrease				float(20,6),
                                              comcaiincome				float(20,6),
                                              comcaiincrease				float(20,6),
                                              itoincome				float(20,6),
                                              itoincrease				float(20,6),
                                              andbussincome				float(20,6),
                                              andbussincrease				float(20,6),
                                              andbusstvincome				float(20,6),
                                              andbusstvincrease				float(20,6),
                                              commovieincome				float(20,6),
                                              commovieincrease					float(20,6),
                                              policeincome					float(20,6),
                                              policeincrease				float(20,6),
                                              comvsumincome				float(20,6),
                                              comvsumincrease				float(20,6),
                                              comvincome				float(20,6),
                                              comvincrease					float(20,6),
                                              comvmincome				float(20,6),
                                              comvmincrease				float(20,6),
                                              comvduanincome				float(20,6),
                                              comvduanincrease					float(20,6),
                                              otherincome				float(20,6),
                                              otherincrease				float(20,6)
                                           )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
            cur.execute(createtablesql)
            createindexsql = "ALTER TABLE " + self.loadtablename + " ADD INDEX index_name(compamyid);"
            cur.execute(createindexsql)
            cur.close()
        except:
            db.rollback()
        cur.close()

    def get_file_name(self,path_string):
        pattern = re.compile(r'([^<>/\\\|:""\*\?]+)\.\w+$')
        data = pattern.findall(path_string)
        if data:
            return data[0]

    def exportexcel(self,colnum, filepath):
        resultvalues = []
        # with open(filepath, 'r',encoding='gb18030',errors='ignore') as f:
        #     first=True
        #     for line in f.readlines():
        #         if first:
        #             first=False
        #             continue
        #         else:
        #             # print(line)
        #             tmpline = line.strip('\n').split(',')
        #             for j in range(0,len(tmpline)):
        #                 if tmpline[j]=='--':
        #                     tmpline[j]=None
        #     resultvalues.append(tmpline)
        file = xlrd.open_workbook(filepath)  # 打开Excel文件
        print(file.sheet_names())
        sheet = file.sheet_by_index(0)
        filternum=0
        for i in range(1, sheet.nrows):
            # print("--------------------------------nrows: ", i)
            replace = ['--', None]
            result = []
            j = 0
            firstpos = 25
            firstafterpos = 32
            secondpos = 34
            secondafter = 86
            pronum = 30
            flag=False
            for j in range(j, colnum):
                cellvalue = file.sheet_by_index(0).cell(i, j).value
                if file.sheet_by_index(0).cell(i, j).ctype == 3:
                    cellvalue = xlrd.xldate_as_datetime(cellvalue, 0)
                if cellvalue in replace:
                    cellvalue = None
                if j==8 and cellvalue=='月':
                    flag=True
                    break
                result.append(cellvalue)
                j += 1
            if flag is True:
                continue
            firstj = firstpos
            secondj = secondpos
            zerocount = 0
            while firstj < firstafterpos:
                tmp = result[firstj]
                if tmp is None or tmp == 0:
                    zerocount += 1
                firstj = firstj + 2
            while secondj < secondafter:
                secondtmp = result[secondj]
                if secondtmp is None or secondtmp == 0:
                    zerocount += 1
                secondj = secondj + 2
            if zerocount == pronum:
                filternum=filternum+1
                continue
            resultvalues.append(tuple(result))
        logger.info("filter num-------------: " + str(filternum))
        print("filter num-------------: ",filternum)
        return resultvalues

    def insertorgtable(self,excelpath,filenum):
        db = self.pool.connection()
        cursor = db.cursor()
        selectsql = "show columns from " + self.loadtablename + ";"
        colnum = cursor.execute(selectsql)
        logger.info("----------------------------------------excelpath" + excelpath)
        logger.info("----------------------------------------self.loadtablename" + self.loadtablename)
        logger.info("----------------------------------------self.loadlimit" + str(self.loadlimit))
        logger.info("----------------------------------------filenum " + str(filenum))

        print("----------------------------------------excelpath", excelpath)
        print("----------------------------------------self.loadtablename", self.loadtablename)
        print("----------------------------------------self.loadlimit", self.loadlimit)
        print("----------------------------------------filenum ", filenum)

        resultvalues = self.exportexcel(colnum, excelpath)
        insertsql = "insert into " + self.loadtablename + " values( "
        strsize = len(resultvalues[0])
        strcount = 0
        for strcount in range(strcount, strsize):
            insertsql += "%s" + ","
            strcount += 1
        insertsql = insertsql[0:len(insertsql) - 1]
        insertsql = insertsql + ")"
        logger.info("----------sql:" + insertsql)
        print("----------sql:", insertsql)
        size = len(resultvalues)
        count = int(size / self.loadlimit) + 1
        logger.info("----------szie: " + str(size))
        logger.info("------------self.loadlimit: " + str(self.loadlimit))
        logger.info("----------count: " + str(count))

        print("----------szie: ",size)
        print("------------self.loadlimit: ",self.loadlimit)
        print("----------count: ", count)
        i = 0
        try:
            while i < count:
                insertdata = resultvalues[i * self.loadlimit:(i + 1) * self.loadlimit]
                cursor.executemany(insertsql, insertdata)
                db.commit()
                logger.info("------------------insert-----------------------:  " + str(i))
                print("------------------insert-----------------------:  ", i)
                i += 1
        except:
            db.rollback()
        cursor.close()
        logger.info("#####################insert end####################")
        print("#####################insert end####################")
        global threadnum
        logger.info("threadnum--------------------------: " + str(threadnum))
        logger.info("filenum--------------------------: " + str(filenum))
        print("threadnum--------------------------: ",threadnum)
        print("filenum--------------------------: ", filenum)
        Lock.acquire()
        threadnum=threadnum+1
        logger.info(".................................after.......................")
        logger.info("threadnum--------------------------: " + str(threadnum))
        logger.info("filenum--------------------------: " + str(filenum))
        print(".................................after.......................")
        print("threadnum--------------------------: ", threadnum)
        print("filenum--------------------------: ", filenum)
        if threadnum>=filenum:
            logger.info(threadnum)
            logger.info("***********************real insert end***************************")
            logger.info("final threadnum--------------------------: " + str(threadnum))
            logger.info("final filenum--------------------------: " + str(filenum))
            logger.info("update............................ " + str(self.primaryid))

            print(threadnum)
            print("***********************real insert end***************************")
            print("final threadnum--------------------------: ", threadnum)
            print("final filenum--------------------------: ", filenum)
            print("update............................ ",self.primaryid)
            LoadDataStatus.objects.filter(id=self.primaryid).update(status='1',updatetime=timezone.now())
            threadnum=0
            self.pool.close()
        Lock.release()
        return

    def data_handler(self,excelpath,filenum):
        logger.info("----------------------insert file: " + excelpath)
        print("----------------------insert file: ", excelpath)
        # #录入数据
        # limit=10000
        self.insertorgtable(excelpath,filenum)

    def task(self,filelists,filenum):
        # 设定最大队列数和线程数
        q = Queue(maxsize=10)
        st = time.time()
        i = 0
        while i < len(filelists):
            t = threading.Thread(target=self.data_handler, args=(filelists[i],filenum,))
            q.put(t)
            if (q.full() == True) or (len(filelists)) == 0:
                thread_list = []
                while q.empty() == False:
                    t = q.get()
                    thread_list.append(t)
                    t.start()
                for t in thread_list:
                    t.join()
            i = i + 1
        while q.empty() == False:
            thread_list = []
            t = q.get()
            thread_list.append(t)
            t.start()
        for t in thread_list:
            t.join()
        logger.info("数据插入完成.==>> 耗时:{}'s:" + str(format(round(time.time() - st, 3))))
        print("数据插入完成.==>> 耗时:{}'s".format(round(time.time() - st, 3)))

    def expoertExcel2Db(self):
        logger.info("---------expoertExcel2Db-------------------")
        self.filelists=[]
        for root, dirs, files in os.walk(self.currentbasedir):
            print(root)  # 当前目录路径
            print(dirs)  # 当前路径下所有子目录
            print(files)  # 当前路径下所有非目录      子文件
        for file in files:
            excelpath = os.path.join(self.currentbasedir, file)
            docname = self.get_file_name(excelpath)
            logger.info("------------------------------------docname：" + docname)
            print("------------------------------------docname：", docname)
            self.filelists.append(excelpath)
        threadnum=0
        self.task(self.filelists,len(self.filelists))











