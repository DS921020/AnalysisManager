import json
from DataModel.models import Test, Role, Resource


def testdb(request):
    requestjson=json.loads(request.body)
    username=requestjson.get('username')
    usermobile = requestjson.get('usermobile')
    rolelist=Role.objects.filter(usermobile=usermobile).all()
    resourcedict={}
    for tmprole in rolelist:
        resource=Resource.objects.filter(roleid=tmprole.roleid).all()
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
                tmpresultlist=resourcedict.get(tmpresource.resourceparentid)
                flag=False
                for tmpdict in tmpresultlist:
                    if tmpdict.get('id')==tmpresource.resourceid:
                        flag=True
                        break
                if flag is True:
                    continue
                tmpresultlist.append(tmpresourcedict)
    resultlist=[]
    for k,v in resourcedict.items():
        tmpresultdict={}
        tmpparentresource = Resource.objects.filter(resourceparentid=k).first()
        tmpresultdict['id']=tmpparentresource.resourceparentid
        tmpresultdict['name'] = tmpparentresource.resourceparentname
        tmpresultdict['content'] = v
        resultlist.append(tmpresultdict)
    return 'ok'

