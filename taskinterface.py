from flask import Flask,jsonify,request
import time,json
import hashlib
import flask
from lib import getip
import mysql
app=Flask(__name__)
@app.route('/mobilecdnapi',methods=['POST'])
def mobilecdnapi():
        string=''
        for i in flask.request.json['filelist']:
            #print i          
            string+=str(i['fileid'])+','+str(i['ftppath'])+','+str(i['md5'])+'|'
        configid=flask.request.json['configid']
        servicename=flask.request.json['servicename']
        version=flask.request.json['version']
        sumbitman=flask.request.json['sumbitman']
        sumbittime=time.strftime('%Y-%m-%d %H:%M:%S')
        code1=flask.request.json['code']
        
        if code1!= "mobilecdn":
            return jsonify({"msg":"invalidate code!!"})
        result=0
        msg={}
        for id in configid:
            sqlquery='select * from tasklists where configid="%s"'%id
            rows=mysql.mysqlquery(sqlquery)
            print len(rows)
            if len(rows)==0:
                sql='insert into tasklists(servicename,version,sumbitman,deploystatus,sumbittime,configid,filelists) values("%s","%s","%s","%s","%s","%s","%s")'%(servicename,version,sumbitman,"1",sumbittime,id,string)
                result=mysql.insert(sql)
                if result==1:
                    msg['status']=1
                else:
                    msg['status']=0
            else:
                sql='update tasklists set version="%s",deploystatus="%s",sumbittime="%s",filelists="%s"'%(version,"0",sumbittime,string)
                mysql.mysqlupdate(sql)
                msg['status']=1
        return jsonify(msg)
@app.route('/getstatus',methods=['POST'])
def getstatus():
    configid=flask.request.json['configid']
    allfiles=[]
    for id in configid:
        sql="select configid,deploystatus,filelists from tasklists where configid='%s'"%str(id)
        result=mysql.mysqlquery(sql)
        #if len(result)==0:     
        #    return jsonify({"status":1})
        files=[]
        for row in result:
            singlefile={}
            singlefile['configid']=row[0]
            singlefile['status']=row[1]
            for i in row[2].split('|'):
                file={}
                if len(i)==0:
                    pass
                else:
                    file['fileid']=i.split(',')[0]
                    file['filename']=i.split(',')[1]
                    file['md5']=i.split(',')[2]
                    files.append(file)
            singlefile['filelist']=files
            allfiles.append(singlefile)

    
    return jsonify({'allfiles':allfiles}) 
    
@app.route('/tasklists',methods=['POST'])
def tasklist():
    if request.method=='POST':
        servicename=request.form['servicename']
        version=request.form['version']
        sumbitman=request.form['sumbitman']
        sumbittime=time.strftime('%Y-%m-%d %H:%M:%S')
        m=hashlib.md5()
        m.update(version)
        md5str=m.hexdigest()
        querystring=md5str
        msg={}
        sql='insert into tasklists(servicename,version,sumbitman,deploystatus,sumbittime,querystring) values(%s,%s,%s,"%s","%s","%s")'%(servicename,version,sumbitman,"0",sumbittime,querystring)
        m=hashlib.md5()
        m.update(version)
        md5str=m.hexdigest()
        sqlquery='select * from tasklists where servicename=%s and version=%s'%(servicename,version) 
        value=mysql.mysqlquery(sqlquery)
        if len(value)==0:
            result=mysql.insert(sql)
            if result==1:
                msg['msg']="success" 
                msg['querystring']=md5str
                return jsonify(msg)
            else:
                msg['msg']="fail"  
                return jsonify(msg)
        else:
            msg['msg']="version exists!"
            return jsonify(msg)
@app.route('/querystatus/<querystring>')
def querystatus(querystring):
    msg={}
    m=hashlib.md5()
    m.update(querystring)
    md5str=m.hexdigest()
    version=md5str
    sql="select deploystatus from tasklists where querystring='%s'"%querystring
    #sql="update tasklists set deploystatus='%s' where version='%s'"%("1",version)
    res=mysql.mysqlquery(sql)
    for i in res:
        msg["status"]=i[0] 
    return jsonify(msg)
@app.route('/cdntaskstatus',methods=['POST'])
def cdntaskstatus():
    cdnurl=flask.request.json['url']
    status=flask.request.json['Status']
    starttime=flask.request.json['StartTime']
    endtime=flask.request.json['EndTime']
    dl2="http://dl2.jingoal.com"
    filename=cdnurl.split(dl2)[1]
    sqlcdn=""
    if status=="success":
        sqlupdatestatus='update tasklists set status="%s"'%'6'
        sqlcdn='update cdntasklists set status="%s" where filename="%s"'%('6',filename)
    else:
        sqlcdn='update cdntasklists set status="%s" where filename="%s"'%('7',filename)
        sqlupdatestatus='update tasklists set status="%s"'%'7'
    mysql.mysqlupdate(sqlcdn)
    sql="insert into taskstatus (cdnurl,status,starttime,endtime) values('%s','%s','%s','%s')"%(cdnurl,status,starttime,endtime)
    mysql.insert(sql)
    return ''
if __name__ == "__main__":
    ip=getip.getip()
    app.run(host=ip,port=6666,debug=True)
