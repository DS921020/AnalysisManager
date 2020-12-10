import configparser
import json
import operator
from decimal import Decimal

import matplotlib
import matplotlib.pyplot as plt
import pymysql
from matplotlib.pylab import mpl
import xlwt
import django.utils.timezone as timezone

from DataModel.models import  AnalysisDataStatus

zhfont_kai = matplotlib.font_manager.FontProperties(fname="C:\Windows\Fonts\simkai.ttf")
zhfont_hei = matplotlib.font_manager.FontProperties(fname="C:\Windows\Fonts\simhei.ttf")
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus']=False

atomsdict={'sumcloudcount':'移动云','sumidccount':'idc','sumeducount':'和教育',
          "sumcloudmoviecount":"云视讯","sumandjiangcount":"和对讲",'sumqianliyancount':"千里眼",
          'sumcailincount':"集团彩铃","sumworkmobliecount":"工作手机","sumdataprolancount":"数据专线",
          "sumnetprolancount":"互联网专线","sumcompanyprolancount":"企业宽带","sumcomvoiceprolancount":"集团语音",
          "sumimsprolancount":"IMS","sumvoiceprolancount":"语音专线","sumsibaicount":"移动400",
          "sumcomduancount":"集团短信","sumcomcaicount":"集团彩信","sumitocount":"物联网",
          "sumandbusscount":"和商务直播","sumandbusstvcount":"和商务TV","sumcommoviecount":"企业视频彩铃",
          "sumpolicecount":"警务通","sumcomvcount":"集团V网","sumcomvmcount":"集团管家","sumcomvduancount":"集团短号通信录",
          "sumothercount":"其他产品"}

atomspdict={'移动云':'cloudincome','idc':'idcincome','和教育':'eduincome',
          "云视讯":"cloudmovieincome","和对讲":"andjiangincome",'千里眼':"qianliyanincome",
          '集团彩铃':"cailinincome","数据专线":"dataprolanincome",
          "互联网专线":"netprolanincome","企业宽带":"companyprolanincome","集团语音":"comvoiceprolanincome",
          "IMS":"imsprolanincome","语音专线":"voiceprolanincome","移动400":"sibaiincome",
          "集团短信":"comduanincome","集团彩信":"comcaiincome","物联网":"itoincome",
          "和商务直播":"andbussincome","和商务TV":"andbusstvincome","企业视频彩铃":"commovieincome",
          "警务通":"policeincome","集团V网":"comvincome"}

atomsbdict={'cloudincome':'移动云','idcincome':'idc','eduincome':'和教育',
          "cloudmovieincome":"云视讯","andjiangincome":"和对讲",'qianliyanincome':"千里眼",
          'cailinincome':"集团彩铃","dataprolanincome":"数据专线",
          "netprolanincome":"互联网专线","companyprolanincome":"企业宽带","comvoiceprolanincome":"集团语音",
          "imsprolanincome":"IMS","voiceprolanincome":"语音专线","sibaiincome":"移动400",
          "comduanincome":"集团短信","comcaiincome":"集团彩信","itoincome":"物联网",
          "andbussincome":"和商务直播","andbusstvincome":"和商务TV","commovieincome":"企业视频彩铃",
          "policeincome":"警务通","comvincome":"集团V网"}

class AnalysisData:
    host=''
    user=''
    password=''
    database=''
    port=''
    cleantablename=''
    atomtablename=''
    currentdir=''
    db=None,
    ordirpath=''
    id=''

    # 行业类型
    def atomclassfication(self):
        cur = self.db.cursor()
        queryclasssql = "select atomindustry from " + self.atomtablename + " group by atomindustry;"
        cur.execute(queryclasssql)
        atomclass = cur.fetchall()
        cur.close()
        return atomclass

    def atomclassficationlist(self,atomclass):
        cur = self.db.cursor()
        queryclasssql = "select atomsubindustry from " + self.atomtablename + " where atomindustry=" + "'" + atomclass[
            0] + "'" + " GROUP BY atomsubindustry;"
        cur.execute(queryclasssql)
        atomclasslist = cur.fetchall()
        cur.close()
        return atomclasslist

    def atomdata(self,atomdict,atomresultdict, ratomresultdict):
        cur = self.db.cursor()
        querysql = """select  
                            sum(case when cloudincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcloudcount,
                            sum(case when idcincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumidccount,
                            sum(case when eduincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumeducount,
                            sum(case when cloudmovieincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcloudmoviecount,
                            sum(case when andjiangincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumandjiangcount,
                            sum(case when qianliyanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumqianliyancount,
                            sum(case when cailinincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcailincount,
                            sum(case when workmoblieincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumworkmobliecount,
                            sum(case when dataprolanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumdataprolancount,
                            sum(case when netprolanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumnetprolancount,
                            sum(case when companyprolanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcompanyprolancount,
                            sum(case when comvoiceprolanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcomvoiceprolancount,
                            sum(case when imsprolanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumimsprolancount,
                            sum(case when voiceprolanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumvoiceprolancount,
                            sum(case when sibaiincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumsibaicount,
                            sum(case when comduanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcomduancount,
                            sum(case when comcaiincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcomcaicount,
                            sum(case when itoincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumitocount,
                            sum(case when andbussincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumandbusscount,
                            sum(case when andbusstvincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumandbusstvcount,
                            sum(case when commovieincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcommoviecount,
                            sum(case when policeincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumpolicecount, 
                            sum(case when comvincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcomvcount,
                            sum(case when comvmincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcomvmcount,
                            sum(case when comvduanincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumcomvduancount,
                            sum(case when otherincome>0.12 then 
                                        1
                                    ELSE
                                        0
                                    end
                            ) as sumothercount
                from """ + self.cleantablename + " where "
        atomdatadict = {}
        ratomdatadict = {}
        for item in atomdict:
            tmpsql = querysql
            atomdictlist = atomdict[item]
            concatstr = ""
            for tmp in atomdictlist:
                concatstr += "atomsubindustry=" + "'" + tmp[0] + "'" + " or "
            concatstr += " 0;"
            tmpsql = tmpsql + concatstr
            print(tmpsql)
            cur.execute(tmpsql)
            atomclass = cur.fetchall()
            col = cur.description
            atomdataeledict = {}
            pos = 0
            sumvel = Decimal(0)
            sumv = ""
            for tmp in col:
                if pos == 7 or pos == 11 or pos == 25:
                    pos += 1
                    continue
                elif pos == 22:
                    sumv = tmp
                    atomdataeledict[tmp] = atomclass[0][pos]
                    sumvel += Decimal(atomclass[0][pos])
                    pos += 1
                    continue
                elif pos == 23 or pos == 24:
                    atomdataeledict[sumv] += atomclass[0][pos]
                    sumvel += Decimal(atomclass[0][pos])
                    atomdataeledict[tmp] = Decimal(0)
                    pos += 1
                    continue
                else:
                    atomdataeledict[tmp] = atomclass[0][pos]
                    sumvel += Decimal(atomclass[0][pos])
                    pos += 1
            print(atomdataeledict)
            sorted_x = sorted(atomdataeledict.items(), key=operator.itemgetter(1), reverse=True)
            atomresultdict[item] = sorted_x[0:5]

            atomdataeledicttrate = {}
            c = 0
            for ritem in sorted_x:
                if c == 5:
                    break
                atomdataeledicttrate[ritem[0]] = ritem[1] / sumvel
                c += 1
            ratomresultdict[item] = atomdataeledicttrate
            print(ratomresultdict)

    def queryAveandSumandCount(self,industry):
        cur = self.db.cursor()
        # 计算产品均值，industry产品名称
        queryclasssql = "select AVG(" + industry + "),sum(" + industry + "),count(1) from " + self.cleantablename + " where " + industry + ">0;"
        cur.execute(queryclasssql)
        atomclass = cur.fetchone()
        average = atomclass[0]
        if average is None:
            return {}
        # 计算该产品每个子行业大于产品平均价值的产品数
        queryclasscount = "SELECT count(1),atomsubindustry from " + self.cleantablename + " where " + industry + ">" + str(
            average) + "GROUP BY atomsubindustry;"
        cur.execute(queryclasscount)
        atomclasslist = cur.fetchall()
        pro2industrydict = {}
        i = 0
        sumvel = 0
        for i in range(i, len(atomclasslist)):
            sumvel += atomclasslist[i][0]
            pro2industrydict[atomclasslist[i][1]] = atomclasslist[i][0]
        pro2industrydict['总计'] = sumvel
        cur.close()
        rsorted_x = sorted(pro2industrydict.items(), key=operator.itemgetter(1), reverse=True)
        topfiversorted_x = rsorted_x[0:7]
        return topfiversorted_x

    def querypro2industryfrequency(self,industry):
        cur = self.db.cursor()
        # 'select count(1) as counum,atomsubindustry FROM clean_industryincomeinfo where comvincome >0 GROUP BY atomsubindustry ORDER BY counum desc;'
        queryclasssql = "select count(1) as counum,atomsubindustry FROM " + self.cleantablename + " where " + industry + " >0 GROUP BY atomsubindustry ORDER BY counum desc;"
        cur.execute(queryclasssql)
        atomclasslist = cur.fetchall()
        pro2industrydict = {}
        i = 0
        sumvel = 0
        for i in range(i, len(atomclasslist)):
            pro2industrydict[atomclasslist[i][1]] = atomclasslist[i][0]
            sumvel += atomclasslist[i][0]
        pro2industrydict['总计'] = sumvel
        cur.close()
        rsorted_x = sorted(pro2industrydict.items(), key=operator.itemgetter(1), reverse=True)
        return rsorted_x[0:7]

    def writedatatoallexcelindustry(self,sortedindustrydicts, pro2industrydictresfrequency):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("allindustry")
        rownum = 0
        for item in sortedindustrydicts:
            print(item)
            sheet.write_merge(rownum, rownum + 3, 0, 0, atomsbdict.get(item))
            # sheet.write(rownum, 0,item)
            # sheet.write(rownum+1,0,item)
            colonum = 1
            for tmp in sortedindustrydicts.get(item):
                induname = tmp[0]
                sheet.write(rownum, colonum, induname)
                indudata = tmp[1]
                sheet.write(rownum + 1, colonum, indudata)
                colonum += 1
            colonum = 1
            for tmp1 in pro2industrydictresfrequency.get(item):
                induname1 = tmp1[0]
                indudataa1 = tmp1[1]
                sheet.write(rownum + 2, colonum, induname1)
                sheet.write(rownum + 3, colonum, indudataa1)
                colonum += 1
            rownum += 4
        filename = self.currentdir + "产品价值行业" + ".xls"
        workbook.save(filename)

    def writedatatoexcelindustry(self,sortedindustrydicts, sortedfindustrydicts, sortedallindustrydict):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("compare")
        sheet.write_merge(0, 1, 0, 0, '价值行业')
        sheet.write_merge(2, 3, 0, 0, '渗透行业')
        sheet.write_merge(4, 5, 0, 0, '热门行业')
        rownum = 0
        columnnum = 1
        ac = 0
        for columnnum in range(columnnum, len(sortedindustrydicts)):
            sheet.write(rownum, columnnum, sortedindustrydicts[ac][0])
            columnnum += 1
            ac += 1
        rownum += 1
        columnnum = 1
        ac = 0
        for columnnum in range(columnnum, len(sortedindustrydicts)):
            sheet.write(rownum, columnnum, sortedindustrydicts[ac][rownum])
            columnnum += 1
            ac += 1
        rownum += 1
        columnnum = 1
        ac = 0
        for columnnum in range(columnnum, len(sortedfindustrydicts)):
            sheet.write(rownum, columnnum, sortedfindustrydicts[ac][0])
            columnnum += 1
            ac += 1
        ac = 0
        rownum += 1
        columnnum = 1
        for columnnum in range(columnnum, len(sortedfindustrydicts)):
            sheet.write(rownum, columnnum, sortedfindustrydicts[ac][1])
            columnnum += 1
            ac += 1
        rownum += 1
        columnnum = 1
        ac = 0
        for columnnum in range(columnnum, len(sortedallindustrydict)):
            sheet.write(rownum, columnnum, sortedallindustrydict[ac][0])
            columnnum += 1
            ac += 1
        rownum += 1
        columnnum = 1
        ac = 0
        for columnnum in range(columnnum, len(sortedallindustrydict)):
            sheet.write(rownum, columnnum, sortedallindustrydict[ac][1])
            columnnum += 1
            ac += 1
        filename = self.currentdir + "价值渗透综合行业排名" + ".xls"
        workbook.save(filename)

    def convertjsontotable(self,pro2industrydictresvalue, pro2industrydictresfrequency):
        mvpdict={}
        mgpdict={}
        for itemvalue in pro2industrydictresvalue:
            key=atomsbdict.get(itemvalue)
            tmpdict={}
            pos=0
            sumvel=0
            for tmp in pro2industrydictresvalue.get(itemvalue):
                if pos==0:
                    sumvel=tmp[1]
                    tmpkey = tmp[0]
                    tmpvalue = tmp[1]
                    tmpdict[tmpkey] = tmpvalue
                    pos=pos+1
                    continue
                tmpkey=tmp[0]
                tmpvalue=round(tmp[1]/sumvel * 100,2)
                tmpdict[tmpkey]=tmpvalue
                pos = pos + 1
            mvpdict[key]=tmpdict

        for itemfrequency in pro2industrydictresfrequency:
            key2=atomsbdict.get(itemfrequency)
            tmpdict2 = {}
            pos2=0
            sumvel2 = 0
            for tmp2 in pro2industrydictresfrequency.get(itemfrequency):
                if pos2 == 0:
                    sumvel2 = tmp2[1]
                    tmpkey2 = tmp2[0]
                    tmpvalue2 = tmp2[1]
                    tmpdict2[tmpkey2] = tmpvalue2
                    pos2 = pos2 + 1
                    continue
                tmpkey2 = tmp2[0]
                tmpvalue2 = round(tmp2[1] / sumvel2 * 100,2)
                tmpdict2[tmpkey2] = tmpvalue2
                pos = pos + 1
            mgpdict[key2] = tmpdict2
        print("mvpdict:-----------",mvpdict)
        print("mgpdict:-----------", mgpdict)
        mvpdictjson=json.dumps(mvpdict,ensure_ascii=False)
        mgpdictjson = json.dumps(mgpdict,ensure_ascii=False)
        print("mvpdictjson:-----------", mvpdictjson)
        print("mgpdictjson:-----------", mgpdictjson)
        analysisDataStatus=AnalysisDataStatus.objects.filter(cleantablename=self.cleantablename,
                                       industrytablename=self.atomtablename,dirpath=self.ordirpath,status='0')
        if len(analysisDataStatus)>0:
            AnalysisDataStatus.objects.filter(id=self.id).update(mvpmsg=mvpdictjson,mgpmsg=mgpdictjson,updatetime=timezone.now())
        else:
            analysisDataStatusSave=AnalysisDataStatus(dirpath=self.ordirpath,cleantablename=self.cleantablename,
                                       industrytablename=self.atomtablename,mvpmsg=mvpdictjson,mgpmsg=mgpdictjson)
            analysisDataStatusSave.save()

    def convertindustryjsontotable(self,sortedindustrydicts, sortedfindustrydicts,sortedfindustrydictssum,sortedallindustrydictsum):
        industrydict={}
        industryfdict = {}
        for tmp in sortedindustrydicts:
            industrydict[tmp[0]]=round(tmp[1]/sortedfindustrydictssum*100,2)
        for tmp1 in sortedfindustrydicts:
            industryfdict[tmp1[0]]=round(tmp1[1]/sortedallindustrydictsum*100,2)
        print("industrydict:-----------", industrydict)
        print("industryfdict:-----------", industryfdict)
        mvidictjson = json.dumps(industrydict, ensure_ascii=False)
        mgidictjson = json.dumps(industryfdict, ensure_ascii=False)
        print("mgpdictjson:-----------", mvidictjson)
        print("mgidictjson:-----------", mgidictjson)
        inanalysisDataStatus = AnalysisDataStatus.objects.filter(cleantablename=self.cleantablename,
                                                              industrytablename=self.atomtablename,
                                                              dirpath=self.ordirpath, status='0')
        if len(inanalysisDataStatus) > 0:
            AnalysisDataStatus.objects.filter(id=self.id).update(mvimsg=mvidictjson, mgimsg=mgidictjson,
                                                                 updatetime=timezone.now())
        else:
            inanalysisDataStatusSave = AnalysisDataStatus(dirpath=self.ordirpath, cleantablename=self.cleantablename,
                                                        industrytablename=self.atomtablename, mvimsg=mvidictjson, mgimsg=mgidictjson)
            inanalysisDataStatusSave.save()

    def __init__(self,ordirpath,currentdir,cleantablneame,atomtablename,id):
        config = configparser.ConfigParser()
        config.read('allanalysisproperties.conf')
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
        self.cleantablename=cleantablneame
        self.atomtablename=atomtablename
        self.currentdir=currentdir
        self.ordirpath=ordirpath
        self.id=id
        self.db = pymysql.connect(host=self.host, user=self.user,
                             password=self.password, database=self.database, port=self.port)
        atomclass=self.atomclassfication()
        atomdict={}
        #挨个遍历industryincomeinfo表获取主行业下包含的子行业集合
        for atom in atomclass:
            atomdict[atom]=self.atomclassficationlist(atom)
        print(atomdict)
        atomresultdict = {}
        ratomresultdict = {}
        #计算每个主行业下每个产品价值大于12元出现的次数
        # 计算每个主行业下每个产品价值大于12元出现的次数
        self.atomdata(atomdict, atomresultdict, ratomresultdict)

        # 挨个遍历每个行业下的产品出现次数，以产品名称作为维度进行合并，形成产品-产品出现次数字典
        prodict = {}
        for item in atomresultdict.items():
            for tmp in item[1]:
                print(tmp)
                atomname = atomsdict.get(tmp[0][0])
                proname = atomspdict.get(atomname)
                if prodict.get(proname) is None:
                    prodict[proname] = 1
                else:
                    prodict[proname] += 1
        print(prodict)
        sortedprolist = sorted(prodict.items(), key=operator.itemgetter(1), reverse=True)
        print(sortedprolist)
        # 取出根据产品-产品次数排序之后的前九个产品
        # prolist = sortedprolist[0:9]
        prolist = sortedprolist
        pro2industrydictresvalue = {}
        # pro2industrydictresvalue字典是{产品：{子行业：子行业出现该产品个数（大于产品价值平均价值）}}
        for item in prolist:
            inname = item[0]
            pro2industrydictresvalue[inname] = self.queryAveandSumandCount(inname)
            print(inname)
            print(pro2industrydictresvalue[inname])

        # 从pro2industrydictresvalue（高价值）计算每个行业出现次数
        allindustrydict = {}
        industrydicts = {}
        for proitem in pro2industrydictresvalue:
            print(proitem)
            c = 0
            for c in range(c, len(pro2industrydictresvalue[proitem])):
                industryname = pro2industrydictresvalue[proitem][c][0]
                if industryname == '总计':
                    continue
                if industrydicts.get(industryname) is None:
                    industrydicts[industryname] = 1
                else:
                    industrydicts[industryname] += 1
                if allindustrydict.get(industryname) is None:
                    allindustrydict[industryname] = 1
                else:
                    allindustrydict[industryname] += 1
                c += 1
        print(industrydicts)
        sortedindustrydicts = sorted(industrydicts.items(), key=operator.itemgetter(1), reverse=True)
        print(sortedindustrydicts)

        # 统计每个产品价值>0的总数和不同子行业出现次数
        pro2industrydictresfrequency = {}
        for item in prolist:
            inname = item[0]
            pro2industrydictresfrequency[inname] = self.querypro2industryfrequency(inname)
            # print(inname)
            # print(pro2industrydictresfrequency[inname])

        # 产品维度，每个产品价值高的行业pro2industrydictresvalue---计算方式：
        # 1、从清洗表中根据主行业获取不同产品数，再根据产品名称合并，最终获取产品-产品出现次数字典：prodict
        # 2、根据产品字典，回清洗表查询该产品平均价值，并从表中查询大于平均价值的该产品条数，将这些产品条数按照子行业进行分组
        # 得到pro2industrydictresvalue字典是{产品：{子行业：子行业出现该产品个数（大于产品价值平均价值）}}价值高行业
        # 3、统计每个产品价值>0的总数，并按照不同子行业进行合并出现次数，pro2industrydictresfrequency渗透高行业
        # 字典是{产品：{子行业：子行业出现该产品个数（大于0）}}
        # 产品维度，每个产品渗透高的行业----计算方式：
        self.writedatatoallexcelindustry(pro2industrydictresvalue, pro2industrydictresfrequency)
        self.convertjsontotable(pro2industrydictresvalue, pro2industrydictresfrequency)
        findustrydicts = {}
        # 从pro2industrydictresfrequency（高渗透）计算每个行业出现次数
        for fyproitem in pro2industrydictresfrequency:
            print(fyproitem)
            d = 0
            for d in range(d, len(pro2industrydictresfrequency[fyproitem])):
                findustryname = pro2industrydictresfrequency[fyproitem][d][0]
                if findustryname == '总计':
                    continue
                if findustrydicts.get(findustryname) is None:
                    findustrydicts[findustryname] = 1
                else:
                    findustrydicts[findustryname] += 1
                if allindustrydict.get(findustryname) is None:
                    allindustrydict[findustryname] = 1
                else:
                    allindustrydict[findustryname] += 1
                d += 1
        print(findustrydicts)
        sortedfindustrydicts = sorted(findustrydicts.items(), key=operator.itemgetter(1), reverse=True)
        sortedallindustrydict = sorted(allindustrydict.items(), key=operator.itemgetter(1), reverse=True)
        print(sortedfindustrydicts)
        sortedfindustrydictssum=0
        sortedallindustrydictsum = 0
        for tmp in sortedfindustrydicts:
            sortedfindustrydictssum=sortedfindustrydictssum+tmp[1]
        for tmp1 in sortedallindustrydict:
            sortedallindustrydictsum = sortedallindustrydictsum + tmp1[1]
        self.convertindustryjsontotable(sortedindustrydicts[0:7], sortedfindustrydicts[0:7],sortedfindustrydictssum,sortedallindustrydictsum)
        # 通过高价值pro2industrydictresvalue中计算的行业次数，通过pro2industrydictresfrequency（高渗透）计算的行业和次数，取上述两者之和计算的热门行业
        self.writedatatoexcelindustry(sortedindustrydicts[0:7], sortedfindustrydicts[0:7], sortedallindustrydict[0:7])

        print("end end end")