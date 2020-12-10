from django.conf.urls import url
from django.urls import path,re_path
from DataModel import views
urlpatterns = [
    re_path(r'^test/(?P<m>[0-9]{2})/$', views.testroute),
    url(r'^uploadfile/',views.testupload),
    url(r'createtableandaddbasedata',views.CreateTableAndInsertBaseData),
    url(r'createtableandaddindustrydata', views.CreateTableAndInsertIndustry),
    url(r'queryanalysisstatustable',views.renderQueryAnalysisStatusHtml),
    url(r'showstaticsdetail', views.renderShowStaticsDetail),
    url(r'basedatainput', views.renderBaseHtml),
    url(r'queryAnalysisresult', views.renderAnalysisHtml),
    url(r'industrydatainput',views.renderIndustryHtml),
    url(r'querystatustable', views.renderQueryHtml),
    url(r'showstatics', views.renderindexcompare),
    url(r'querybasedatastatus', views.QueryBaseDataStatus),
    url(r'checkdir', views.QueryBaseDataDir),
    url(r'querystatus', views.QueryStatusPage),
    url(r'editstatus', views.EditStatus),
    url(r'deletestatus', views.DeleteStatus),
    url(r'exportlayinput.html', views.renderExportLayHtml),
    url(r'insureanalysislay.html', views.renderinsureanalysislayhtml),
    url(r'querytype', views.QueryByData),
    url(r'querydata', views.QueryData),
    url(r'exportdatatotables', views.ExportData2Tables),
    url(r'checkcleantable', views.CheckCleanExist),
    url(r'queryexportstatus', views.QueryExportStatus),
    url(r'analysisdata', views.AnysisData),
    url(r'queryanalysisstatus', views.QueryAnysisStatus),
    url(r'downloadfile', views.DownLoadAnalysisFile),
    url(r'ShowAllData', views.ShowAllData),
    url(r'ShowDetailData', views.ShowDetailData),
    url(r'GetMenu', views.GetMenu),
]