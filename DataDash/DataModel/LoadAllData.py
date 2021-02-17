#!/usr/bin/python
# -*- coding: UTF-8 -*-
import configparser
import threading
from queue import Queue

import django.utils.timezone as timezone

import pymysql
from dbutils.pooled_db import PooledDB
import time

from DataModel.models import LoadDataStatus
import logging

logger = logging.getLogger(__name__)
loadalldatathreadnum=0
Lock = threading.Lock()

class LoadAllData:
    host = ''
    user = ''
    password = ''
    database = ''
    port = ''
    db = None
    config = None
    pool = None
    limit=0
    cleantablename=''
    ortable=''
    queryortable=''
    queryortable1=''
    atomtablename=''
    primaryid=''

    def queryortablenum(self):
        db = self.pool.connection()
        cur = db.cursor()
        queryatomsubsql = "select count(1) from " + self.ortable + ";"
        cur.execute(queryatomsubsql)
        tmpresult = cur.fetchone()
        db.close()
        cur.close()
        return tmpresult

    def queryatomsub(self,db, companyid):
        cur = db.cursor()
        queryatomsubsql = "select atomsubindustry from " + self.atomtablename + " where compamyid=" + companyid + ";"
        cur.execute(queryatomsubsql)
        tmpresult = cur.fetchone()
        cur.close()
        return tmpresult

    def insertcleantabledatas(self,db,finalresultlist):
        cur = db.cursor()
        insertcleantablesql = "insert into " + self.cleantablename + " values( "
        strcleansize = len(finalresultlist[0])
        strcleancount = 0
        for strcleancount in range(strcleancount, strcleansize):
            insertcleantablesql += "%s" + ","
            strcleancount += 1
        insertcleantablesql = insertcleantablesql[0:len(insertcleantablesql) - 1]
        insertcleantablesql = insertcleantablesql + ")"
        cur.executemany(insertcleantablesql, finalresultlist)
        db.commit()
        cur.close()

    def data_handler(self,start,limitarraylen):
        logger.info("data_handler start....................")
        sqlthreetablequery = """select 
        										   o.prodate 			,
        										   o.proarea 			,
        										   o.procounty 			,
        										   o.compamyid 			,
        										   o.compamyname 		,
        										   o.compamylevel 		,
        										   o.cloudincome				,
        										   o.idcincome					,
        										   o.eduincome				,
        										   o.cloudmovieincome				,
        										   o.andjiangincome				,
        										   o.qianliyanincome				,
        										   o.cailinincome				    ,
        										   o.workmoblieincome				,
        										   o.dataprolanincome				,
        										   o.netprolanincome				,
        										   o.companyprolanincome				,
        										   o.comvoiceprolanincome				,
        										   o.imsprolanincome				,
        										   o.voiceprolanincome				,
        										   o.sibaiincome				,
        										   o.comduanincome				,
        										   o.comcaiincome				,
        										   o.itoincome				,
        										   o.andbussincome				,
        										   o.andbusstvincome			,
        										   o.commovieincome				,
        										   o.policeincome				,
        										   o.comvincome				,
        										   o.comvmincome				,
        										   o.comvduanincome				,
        										   o.otherincome				,
        										   t.compamyid ,
        										   t.cloudincome				,   
        										   t.idcincome					,					
        										   t.eduincome				,
        										   t.cloudmovieincome				,
        										   t.andjiangincome				,			  
        										   t.qianliyanincome				,
        										   t.cailinincome				    ,
        										   t.workmoblieincome				,
        										   t.dataprolanincome				,
        										   t.netprolanincome				,
        										   t.companyprolanincome				,
        										   t.comvoiceprolanincome				,
        										   t.imsprolanincome				,
        										   t.voiceprolanincome				,
        										   t.sibaiincome				,
        										   t.comduanincome				,
        										   t.comcaiincome				,
        										   t.itoincome				,
        										   t.andbussincome				,
        										   t.andbusstvincome			,
        										   t.commovieincome				,
        										   t.policeincome				,
        										   t.comvincome				,
        										   t.comvmincome				,
        										   t.comvduanincome				,
        										   t.otherincome,
        										   fcompamyid 			,
        										   fcloudincome				,
        										   fidcincome					,
        										   feduincome				,
        										   fcloudmovieincome				,
        										   fandjiangincome				,
        										   fqianliyanincome				,
        										   fcailinincome				    ,
        										   fworkmoblieincome				,
        										   fdataprolanincome				,
        										   fnetprolanincome				,
        										   fcompanyprolanincome				,
        										   fcomvoiceprolanincome				,
        										   fimsprolanincome				,
        										   fvoiceprolanincome				,
        										   fsibaiincome				,
        										   fcomduanincome				,
        										   fcomcaiincome				,
        										   fitoincome				,
        										   fandbussincome				,
        										   fandbusstvincome			,
        										   fcommovieincome				,
        										   fpoliceincome				,
        										   fcomvincome				,
        										   fcomvmincome				,
        										   fcomvduanincome				,
        										   fotherincome	from """ + self.ortable + """ o
                                                                    LEFT JOIN(
                                                                                select 
                                                                                             u.compamyid 			,

                                                                                           u.cloudincome				,

                                                                                           u.idcincome					,

                                                                                           u.eduincome				,

                                                                                           u.cloudmovieincome				,

                                                                                           u.andjiangincome				,

                                                                                           u.qianliyanincome				,

                                                                                           u.cailinincome				    ,

                                                                                           u.workmoblieincome				,

                                                                                           u.dataprolanincome				,

                                                                                           u.netprolanincome				,

                                                                                           u.companyprolanincome				,

                                                                                           u.comvoiceprolanincome				,

                                                                                           u.imsprolanincome				,

                                                                                           u.voiceprolanincome				,

                                                                                           u.sibaiincome				,

                                                                                           u.comduanincome				,

                                                                                           u.comcaiincome				,

                                                                                           u.itoincome				,

                                                                                           u.andbussincome				,

                                                                                           u.andbusstvincome			,

                                                                                           u.commovieincome				,

                                                                                           u.policeincome				,

                                                                                           u.comvincome				,

                                                                                           u.comvmincome				,

                                                                                           u.comvduanincome				,

                                                                                           u.otherincome,

                                                                                             f.compamyid 	as 		fcompamyid,

                                                                                           f.cloudincome		as 		fcloudincome		,

                                                                                           f.idcincome		 as fidcincome			,

                                                                                           f.eduincome as 	feduincome 			,

                                                                                           f.cloudmovieincome as 		fcloudmovieincome		,

                                                                                           f.andjiangincome	as 	fandjiangincome		,

                                                                                           f.qianliyanincome as fqianliyanincome				,

                                                                                           f.cailinincome	as 		fcailinincome	    ,

                                                                                           f.workmoblieincome as 	fworkmoblieincome			,

                                                                                           f.dataprolanincome	as	fdataprolanincome		,

                                                                                           f.netprolanincome	as	 fnetprolanincome		,

                                                                                           f.companyprolanincome as	 fcompanyprolanincome			,

                                                                                           f.comvoiceprolanincome as	fcomvoiceprolanincome			,

                                                                                           f.imsprolanincome as		fimsprolanincome		,

                                                                                           f.voiceprolanincome as	fvoiceprolanincome			,

                                                                                           f.sibaiincome as		fsibaiincome 		,

                                                                                           f.comduanincome as		fcomduanincome		,

                                                                                           f.comcaiincome as		fcomcaiincome		,

                                                                                           f.itoincome as fitoincome				,

                                                                                           f.andbussincome as	fandbussincome			,

                                                                                           f.andbusstvincome as	fandbusstvincome		,

                                                                                           f.commovieincome as	fcommovieincome			,

                                                                                           f.policeincome as	fpoliceincome			,

                                                                                           f.comvincome as	fcomvincome			,

                                                                                           f.comvmincome as		fcomvmincome		,

                                                                                           f.comvduanincome as fcomvduanincome				,

                                                                                           f.otherincome as	fotherincome
                                        from  """ + self.queryortable + """ u 	
                                        LEFT JOIN """ + self.queryortable1 + """ f
                                        on u.compamyid=f.compamyid
                                        ) t on t.compamyid = o.compamyid
                                        where 
                                                o.compamyid <>0 and o.compamyid is not null and o.compamyid<>-1
                                        ORDER BY
                                                o.compamyid
                                        limit """ + str(start) + "," + str(self.limit) + ";"
        logger.info("start=-------" + str(start))
        logger.info("limit=-------" + str(self.limit))
        print("start=-------", start)
        print("limit=-------", self.limit)
        db = self.pool.connection()
        cur = db.cursor()
        cur.execute(sqlthreetablequery)
        datasresultlist = cur.fetchall()
        tmpcount = 0
        finalresultlist = []
        for tmp in datasresultlist:
            logger.info("----------------------------" + str(tmpcount))
            print("----------------------------", tmpcount)
            print(tmp)
            atomsubindustry = self.queryatomsub(db,tmp[3])
            if atomsubindustry is None:
                tmpcount += 1
                continue
            finalresult = []
            for y in range(0, 6):
                finalresult.append(tmp[y])
            firstpos = 6
            midpos = firstpos + 27
            afterpos = firstpos + 27 + 27
            while afterpos < len(tmp):
                tmpfirs = tmp[firstpos]
                tmpmid = tmp[midpos]
                tmpafter = tmp[afterpos]
                firstpos = firstpos + 1
                midpos = firstpos + 27
                afterpos = firstpos + 27 + 27
                if tmpfirs is None:
                    tmpfirs = 0.0
                if tmpmid is None:
                    tmpmid = 0.0
                if tmpafter is None:
                    tmpafter = 0.0
                tmpresult = tmpfirs + tmpmid + tmpafter
                finalresult.append(tmpresult)
                finalresult.append(0.0)
            finalresult.append(atomsubindustry)
            tmpcount += 1
            finalresultlist.append(finalresult)
        if len(finalresultlist) > 0:
            logger.info("finalresultlist---------------------------------")
            print("finalresultlist---------------------------------", finalresultlist)
            self.insertcleantabledatas(db, finalresultlist)
        print("#####################insert end####################")
        logger.info("#####################insert end####################")
        global loadalldatathreadnum
        logger.info("loadalldatathreadnum--------------------------: " + str(loadalldatathreadnum))
        logger.info("limitarraylen--------------------------: " + str(limitarraylen))
        print("loadalldatathreadnum--------------------------: ", loadalldatathreadnum)
        print("limitarraylen--------------------------: ", limitarraylen)
        Lock.acquire()
        loadalldatathreadnum = loadalldatathreadnum + 1
        logger.info(".................................after.......................")
        logger.info("loadalldatathreadnum--------------------------: " + str(loadalldatathreadnum))
        logger.info("limitarraylen--------------------------: " + str(limitarraylen))
        print(".................................after.......................")
        print("loadalldatathreadnum--------------------------: ", loadalldatathreadnum)
        print("limitarraylen--------------------------: ", limitarraylen)
        if loadalldatathreadnum >= limitarraylen:
            logger.info(loadalldatathreadnum)
            logger.info("***********************real insert end***************************")
            logger.info("final threadnum--------------------------: " + str(loadalldatathreadnum))
            logger.info("final filenum--------------------------: " + str(limitarraylen))
            print(loadalldatathreadnum)
            print("***********************real insert end***************************")
            print("final threadnum--------------------------: ", loadalldatathreadnum)
            print("final filenum--------------------------: ", limitarraylen)
            LoadDataStatus.objects.filter(id=self.primaryid).update(status='1', updatetime=timezone.now())
        Lock.release()
        return

    def createcleantable(self,cleantablename):
        try:
            db = self.pool.connection()
            cur = db.cursor()
            droptablesql = "drop table if exists " + cleantablename + ";"
            cur.execute(droptablesql)
            createtablesql = "create table " + cleantablename + """(
                                               prodate 			VARCHAR(20),
                                               proarea 			VARCHAR(20),
                                               procounty 			VARCHAR(20),
                                               compamyid 			VARCHAR(40),
                                               compamyname 		VARCHAR(80),
                                               compamylevel 		VARCHAR(20),            
                                               cloudincome				float(20,6),
                                               cloudincrease				float(20,6),
                                               idcincome					float(20,6),
                                               idcincrease				float(20,6),
                                               eduincome				float(20,6),
                                               eduincrease				float(20,6),
                                               cloudmovieincome				float(20,6),
                                               cloudmovieincrease				float(20,6),
                                               andjiangincome				float(20,6),
                                               andjiangincrease				float(20,6),
                                               qianliyanincome				float(20,6),
                                               qianliyanincrease		    float(20,6),
                                               cailinincome				    float(20,6),
                                               cailinincrease				float(20,6),
                                               workmoblieincome				float(20,6),
                                               workmoblieincrease				float(20,6),
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
                                               comduanincome				float(20,6),
                                               comduanincrease				float(20,6),
                                               comcaiincome				float(20,6),
                                               comcaiincrease				float(20,6),
                                               itoincome				float(20,6),
                                               itoincrease				float(20,6),
                                               andbussincome				float(20,6),
                                               andbussincrease				float(20,6),
                                               andbusstvincome			float(20,6),
                                               andbusstvincrease				float(20,6),
                                               commovieincome				float(20,6),
                                               commovieincrease				float(20,6),
                                               policeincome				float(20,6),
                                               policeincrease				float(20,6),
                                               comvincome				float(20,6),
                                               comvincrease				float(20,6),
                                               comvmincome				float(20,6),
                                               comvmincrease				float(20,6),
                                               comvduanincome				float(20,6),
                                               comvduanincrease				float(20,6),
                                               otherincome				float(20,6),
                                               otherincrease				float(20,6),
                                               atomsubindustry       VARCHAR(20)
                                            )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
            cur.execute(createtablesql)
            createcleantableindex = "ALTER TABLE " + cleantablename + " ADD INDEX index_name(compamyid);"
            cur.execute(createcleantableindex)
            cur.close()
        except:
            db.rollback()
        db.close()
        cur.close()

    def task(self,limitarray,limitarraylen):
        # 设定最大队列数和线程数
        q = Queue(maxsize=10)
        st = time.time()
        i = 0
        while i < len(limitarray):
            t = threading.Thread(target=self.data_handler, args=(limitarray[i],limitarraylen,))
            q.put(t)
            if (q.full() == True) or (len(limitarray)) == 0:
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
        print("数据插入完成.==>> 耗时:{}'s".format(round(time.time() - st, 3)))


    def __init__(self,ortable,queryortable,queryortable1,
             atomtablename,cleantablename,datastatusid):
        config = configparser.ConfigParser()
        config.read('threadanalysis.conf')
        print(config['db']['host'])
        print(config['db']['user'])
        print(config['db']['database'])
        print(config['db']['port'])
        print(config['db']['password'])
        logger.info(config['db']['host'])
        logger.info(config['db']['user'])
        logger.info(config['db']['database'])
        logger.info(config['db']['port'])
        logger.info(config['db']['password'])

        self.host = config['db']['host']
        self.user = config['db']['user']
        self.password = config['db']['password']
        self.database = config['db']['database']
        self.port = int(config['db']['port'])
        self.limit = config['loadlimit']['limit']
        self.primaryid=datastatusid

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

        self.cleantablename=cleantablename
        self.ortable=ortable
        self.queryortable=queryortable
        self.queryortable1=queryortable1
        self.atomtablename=atomtablename

        logger.info("----------------------createcleantable--------------------------")
        self.createcleantable(cleantablename)

        ortablenum = self.queryortablenum()
        gap = ortablenum[0] / int(self.limit)
        limitarray = []
        firstgap = 0
        limitarray.append(firstgap)
        logger.info("----------------------limitarray loop--------------------------:" + str(len(limitarray)))
        while firstgap < ortablenum[0]:
            firstgap = firstgap + int(self.limit)
            limitarray.append(firstgap)
        logger.info("-------limitarray len---------:" + str(len(limitarray)))
        print("-------limitarray len---------:",len(limitarray))
        self.task(limitarray,len(limitarray))