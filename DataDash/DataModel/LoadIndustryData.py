#!/usr/bin/python
# -*- coding: UTF-8 -*-
import configparser
import os
import pymysql
import xlrd
import re
import logging

logger = logging.getLogger(__name__)
class LoadIndustryData:
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

    def exportexcel(self, filepath, resultvalues, tablename):
        file = xlrd.open_workbook(filepath) #打开Excel文件
        print(file.sheet_names())
        # logger.info("file.sheet_names:"+file.sheet_names)
        sheet=file.sheet_by_index(0)
        posi = 0
        tmpresult = []
        for i in range(1,sheet.nrows):
            # print("i---------:",i)
            logger.info("i---------------:" + str(i))
            replace = ['--', None]
            result=[]
            j = 0
            for j in range(j,sheet.ncols):
                    cellvalue = file.sheet_by_index(0).cell(i,j).value
                    if file.sheet_by_index(0).cell(i,j).ctype==3:
                        cellvalue = xlrd.xldate_as_datetime(cellvalue,0)
                    if cellvalue in replace:
                        cellvalue=None
                    result.append(cellvalue)
                    j+=1
            tmpresult.append(tuple(result))
            posi = posi + 1
            if posi >= self.limit:
                logger.info("#########################push###################")
                logger.info("------i:" + str(i))
                self.db.ping(reconnect=True)
                cursor = self.db.cursor()
                try:
                    strsize = len(tmpresult[0])
                    logger.info("###############strsize###########:" + str(strsize))
                    strcount = 0
                    sql = ""
                    sql = "insert into " + tablename + "  values("
                    for strcount in range(strcount, strsize):
                        sql += "%s" + ","
                        strcount += 1
                    sql = sql[0:len(sql) - 1]
                    sql = sql + ")"
                    logger.info("----------sql:" + sql)
                    cursor.executemany(sql, tmpresult)
                    self.db.commit()
                except Exception as ex:
                    logger.info("eeeeeeeeee-----------------------------")
                    logger.info(ex)
                    self.db.rollback()
                cursor.close()
                self.db.close()
                tmpresult = []
                posi = 0
        if len(tmpresult) > 0:
            logger.info("#########################last push###################")
            self.db.ping(reconnect=True)
            cursor = self.db.cursor()
            try:
                strsize = len(tmpresult[0])
                logger.info("###############strsize###########:" + str(strsize))
                strcount = 0
                sql = ""
                sql = "insert into " + tablename + "  values("
                for strcount in range(strcount, strsize):
                    sql += "%s" + ","
                    strcount += 1
                sql = sql[0:len(sql) - 1]
                sql = sql + ")"
                logger.info("----------sql:" + sql)
                cursor.executemany(sql, tmpresult)
                self.db.commit()
            except Exception as ex:
                logger.info("eeeeeeeeee-----------------------------")
                logger.info(ex)
                self.db.rollback()
            cursor.close()
            self.db.close()


    def createcleantable(self,cleantablename):
        try:
            self.db.ping(reconnect=True)
            cur = self.db.cursor()
            droptablesql = "drop table if exists " + cleantablename + ";"
            cur.execute(droptablesql)
            createtablesql = "create table " + cleantablename + """(
                                               prodate 			VARCHAR(20),
                                               proarea 			VARCHAR(20),
                                               procounty 			VARCHAR(20),
                                               vetindustry 			VARCHAR(20),	
                                               atomindustry 			VARCHAR(20),	
                                               atomsubindustry 			VARCHAR(20),
                                               compamyid 			VARCHAR(40),
                                               compamyname 		VARCHAR(80),
                                               compamylevel 		VARCHAR(20),
                                               compamymanagernum 		VARCHAR(20),
                                               compamymanagername 		VARCHAR(40),
                                               compamymanagerrole 		VARCHAR(20),
                                               yearitincome				float(20,6),
                                               yearitincrease				float(20,6),
                                                yearitincome1				float(20,6),
                                               yearitincrease1				float(20,6),
                                                yearitincome2				float(20,6),
                                               yearitincrease2				float(20,6),
                                                yearcomincome				float(20,6),
                                               yearcomincrease				float(20,6),
                                                yearprolanincome				float(20,6),
                                               yearprolanincrease				float(20,6),
                                               yearsubprolanincome				float(20,6),
                                               yearsubprolanincrease				float(20,6),
                                               yeareduincome				float(20,6),
                                               yeareduincrease				float(20,6),
                                               yearimsincome				float(20,6),
                                               yearimsincrease				float(20,6),
                                               yearduancaiincome				float(20,6),
                                               yearduancaiincrease				float(20,6),
                                               yearduanincome				float(20,6),
                                               yearduanincrease				float(20,6),
                                                yearcaiincome				float(20,6),
                                               yearcaiincrease				float(20,6),
                                               yearcailinincome				float(20,6),
                                               yearcailinincrease				float(20,6),
                                               yearidcincome				float(20,6),
                                               yearidcincrease				float(20,6),
                                                yearitoincome				float(20,6),
                                               yearitoincrease				float(20,6),
                                                 yearictincome				float(20,6),
                                               yearictincrease				float(20,6),
                                               yearcloudincome				float(20,6),
                                               yearcloudincrease				float(20,6),
                                               yearvsanincome				float(20,6),
                                               yearvsanincrease				float(20,6),
                                               yearvincome				float(20,6),
                                               yearvincrease				float(20,6),
                                                 yearvmincome				float(20,6),
                                               yearvmincrease				float(20,6),
                                                 yearvduanincome				float(20,6),
                                               yearvduanincrease				float(20,6),
                                                yearandjiangincome				float(20,6),
                                               yearandjiangincrease				float(20,6),
                                                yearandshiincome				float(20,6),
                                               yearandshiincrease				float(20,6),
                                               yearpoliceincome				float(20,6),
                                               yearpoliceincrease				float(20,6),
                                                workphincome				float(20,6),
                                                otherprosincome				float(20,6),
                                                otherprosincrease				float(20,6),
                                                monthincome				float(20,6),
                                                monthincrease				float(20,6),
                                                monthitincome				float(20,6),
                                                monthitincrease				float(20,6),
                                                monthitincome1				float(20,6),
                                                monthitincrease1				float(20,6),
                                                monthitincome2				float(20,6),
                                                monthitincrease2				float(20,6),
                                                monthitincome3				float(20,6),
                                                monthitincrease3				float(20,6),
                                                monthprolanincome				float(20,6),
                                                monthprolanincrease				float(20,6),
                                                monthsubprolanincome				float(20,6),
                                               monthsubprolanincrease				float(20,6),
                                               montheduincome				float(20,6),
                                               montheduincrease				float(20,6),
                                                monthimsincome				float(20,6),
                                               monthimsincrease				float(20,6),
                                               monthduancaiincome				float(20,6),
                                               monthduancaiincrease				float(20,6),
                                               monthduanincome				float(20,6),
                                               monthduanincrease				float(20,6),
                                               monthcaiincome				float(20,6),
                                               monthcaiincrease				float(20,6),
                                               monthcailinincome				float(20,6),
                                               monthcailinincrease				float(20,6),
                                               monthidcincome				float(20,6),
                                               monthidcincrease				float(20,6),
                                               monthitoincome				float(20,6),
                                               monthitoincrease				float(20,6),
                                               monthictincome				float(20,6),
                                               monthictincrease				float(20,6),
                                               monthcloudincome				float(20,6),
                                               monthcloudincrease				float(20,6),
                                               monthvsanincome				float(20,6),
                                               monthvsanincrease				float(20,6),
                                               monthvincome				float(20,6),
                                               monthvincrease				float(20,6),
                                               monthvmincome				float(20,6),
                                               monthvmincrease				float(20,6),
                                               monthvduanincome				float(20,6),
                                               monthvduanincrease				float(20,6),
                                                monthandjiangincome				float(20,6),
                                               monthandjiangincrease				float(20,6),
                                               monthandshiincome				float(20,6),
                                               monthandshiincrease				float(20,6),
                                               monthpoliceincome				float(20,6),
                                               monthpoliceincrease				float(20,6),
                                               monthworkphincome				float(20,6),
                                               monthotherprosincome				float(20,6),
                                               monthotherprosincrease				float(20,6)
                                            )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
            cur.execute(createtablesql)
            createcleantableindex = "ALTER TABLE " + cleantablename + " ADD INDEX index_name(compamyid);"
            cur.execute(createcleantableindex)
            cur.close()
        except:
            self.db.rollback()
        cur.close()

    # def insertdata(self,datas, sql, limit):
    #     self.db.ping(reconnect=True)
    #     cursor = self.db.cursor()
    #     strsize = len(datas[0][0])
    #     logger.info("###############strsize###########:"+str(strsize))
    #     strcount = 0
    #     for strcount in range(strcount, strsize):
    #         sql += "%s" + ","
    #         strcount += 1
    #     sql = sql[0:len(sql) - 1]
    #     sql = sql + ")"
    #     logger.info("----------sql:"+sql)
    #     size=len(datas)
    #     logger.info("--------------size:"+str(size))
    #     i=0
    #     try:
    #         while i<size:
    #             insertdata = datas[i]
    #             cursor.executemany(sql, insertdata)
    #             self.db.commit()
    #             logger.info("------------------insert-----------------------:" + str(i))
    #             i=i+1
    #     except:
    #         self.db.rollback()
    #     cursor.close()
    #     self.db.close()

    # size = len(datas)
    # count = int(size / limit) + 1
    # logger.info("----------count:"+str(count))
    # print("----------count:", count)
    # i = 0
    # try:
    #     while i < count:
    #         insertdata = datas[i * limit:(i + 1) * limit]
    #         cursor.executemany(sql, insertdata)
    #         self.db.commit()
    #         logger.info("------------------insert-----------------------:\n"+str(i))
    #         print("------------------insert-----------------------:\n", i)
    #         i += 1
    # except:
    #     self.db.rollback()
    # cursor.close()
    # self.db.close()

    def __init__(self,currentbasedir,tablename,filename):
        currentdir = os.getcwd()
        config = configparser.ConfigParser()
        config.read('insertproperties.conf')
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
        self.db = pymysql.connect(host=self.host, user=self.user,
                             password=self.password, database=self.database, port=self.port)

        self.limit = int(config['data']['limitnum'])
        self.tablename = tablename
        self.databasedir = config['data']['dirnamne']
        self.filename = filename

        try:
            # currentbasedir = currentbasedir + filename
            currentbasedir = os.path.join(currentbasedir, filename)
            logger.info("createcleantable---------------------------")
            self.createcleantable(tablename)
            resultvalues = []
            print("==============read excel================")
            logger.info("==============read excel================")

            self.exportexcel(currentbasedir, resultvalues, self.tablename)
            # print("----------------resultvalues", resultvalues)
            logger.info("==============end================&&&&&&&&&&&&")

            # #currentbasedir = currentbasedir + filename
            # currentbasedir=os.path.join(currentbasedir,filename)
            # resultvalues = []
            # print("==============read excel================")
            # logger.info("==============read excel================")
            # self.exportexcel(currentbasedir, resultvalues)
            # # print("----------------resultvalues", resultvalues)
            # logger.info("==============resultvalues================"+str(len(resultvalues)))
            # sql = "insert into " + tablename + "  values("
            # # sql = "insert into product_info values("
            # logger.info("createcleantable---------------------------")
            # self.createcleantable(tablename)
            # logger.info("insert---------------------------")
            # self.insertdata(resultvalues, sql, self.limit)
        except Exception as ex:
            print("Exception: %s" % ex)
            logger.info("Exception:............")
            logger.info(ex)
