import socket
import threading
import time
import sys
import json
import re
import mysql.connector
import datetime
import logging
import os
from common import function

sqlHost = function.getConfig('sql.conf', 'mysql', 'HOSTNAME')
sqlPort = function.getConfig('sql.conf', 'mysql', 'PORT')
sqlUser = function.getConfig('sql.conf', 'mysql', 'USERNAME')
sqlPasswd = function.getConfig('sql.conf', 'mysql', 'PASSWORD')
sqlDatabase = function.getConfig('sql.conf', 'mysql', 'DATABASE')
# 是否写入到MYSQL数据库,True写入,False不写入
isSql = True
# 每隔多少获取信息,并写入MYSQL数据中,单位秒 	 
time_sleep = 5


def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定ip和端口
        s.bind(('0.0.0.0', 9000))
        # 同时连接数量
        s.listen(10)
    # 如果监听错误就退出
    except socket.error as msg:
        _log(msg, 2)
        sys.exit(1)
    _log('Waiting connection...', 0)

    while 1:
        # 取得Soket信息以及M1的IP地址和端口
        conn, addr = s.accept()
        # 创建获取数据线程,get_data(conn,addr)
        t = threading.Thread(target=get_data, args=(conn, addr))
        t.start()


def get_data(conn, addr):
    get_msg = b'\xaaO\x01%F\x119\x8f\x0b\x00\x00\x00\x00\x00\x00\x00\x00\xb0\xf8\x93\x11dR\x007\x00\x00\x02{"type":5,"status":1}\xff#END#'
    _log('A new connection from {0}'.format(addr), 0)
    while 1:
        # 发送信息给M1
        conn.sendall(get_msg)
        # 取得M1发来的数据
        data = conn.recv(1024)

        if data:
            jsonData = parseJsonData(data)
            _log("Get M1 data: " + str(jsonData), 3)
            if jsonData is not None:
                print(jsonData)
                info_Humidity = cut(float(jsonData['humidity']), 1)  # 湿度
                info_Temperature = cut(float(jsonData['temperature']), 1)  # 温度
                info_PM25 = jsonData['value']  # PM2.5
                info_HCHO = cut(float(jsonData['hcho']) / 1000, 2)  # 甲醇
                if isSql:
                    mysql_insert(timestamp2(), info_Humidity, info_Temperature, info_PM25, info_HCHO)
        # 等待指定时间,单位秒
        time.sleep(time_sleep)


# 连接MYSQL
def mysql_conn():
    _log("MySql: Connecting...", 3)
    try:
        mydb = mysql.connector.connect(
            host=sqlHost,
            port=sqlPort,
            user=sqlUser,
            passwd=sqlPasswd,
            database=sqlDatabase,
            charset="utf8"
        )
        mycursor = mydb.cursor()
        _log("MySql: Is connected.", 3)
        # 如果m1表不存在,则自动创建
        sql = """
			create table if not exists m1(
			id int auto_increment primary key,
			time int,
			humidity float,
			temperature float,
			pm25 float,
			hcho float)
		"""
        mycursor.execute(sql)
        return mydb, mycursor
    except Exception as err:
        _log("MySql: Connection failed.", 2)


# 关闭MYSQL连接
def mysql_close(mydb, mycursor):
    if mycursor:
        mycursor.close()
    if mydb:
        mydb.close()


# 插入记录,依次是 时间戳,湿度,温度,PM2.5,甲醇
def mysql_insert(time, humidity, temperature, pm25, hcho):
    try:
        mydb, mycursor = mysql_conn()
        _log("MySql: Writing data...", 3)
        sql = "insert into m1(time,humidity,temperature,pm25,hcho) value (" + str(time) + "," + str(
            humidity) + "," + str(temperature) + "," + str(pm25) + "," + str(hcho) + ")"
        mycursor.execute(sql)
        mydb.commit()
        _log("MySql: Write data successfully.", 3)
    except Exception as e:
        _log("MySql: Failed to write data.", 2)
    mysql_close(mydb, mycursor)


# Json处理从M1取得的数据
def parseJsonData(data):
    pattern = r"(\{.*?\})"
    jsonStr = re.findall(pattern, str(data), re.M)
    l = len(jsonStr)
    if l > 0:
        return json.loads(jsonStr[l - 1])
    else:
        return None


# 获取时间戳,保留整数,1610608841
def timestamp2():
    timestamp = int(time.time())
    return timestamp


# 时间戳转为文本时间格式
def timestamp2string(timeStamp):
    d = datetime.datetime.fromtimestamp(timeStamp)
    str1 = d.strftime("%Y-%m-%d %H:%M:%S")
    # 2015-08-28 16:43:37'
    return str1


# 保留小数，不进行四舍五入,M1就是这样处理,个人觉得四舍五入更好...
def cut(num, c):
    str_num = str(num)
    return str(str_num[:str_num.index('.') + 1 + c])


def _log(str, level):
    # 创建logger实例并命名
    logger = logging.getLogger('PhicommM1 Server')
    # 设置logger的日志级别
    logger.setLevel(logging.DEBUG)
    # 判断当前日志对象中是否有处理器，如果没有，则添加处理器
    if not logger.handlers:
        # 添加控制台管理器(即控制台展示log内容）
        ls = logging.StreamHandler()
        ls.setLevel(logging.DEBUG)
        # 设置log的记录格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
        # 把格式添加到控制台管理器,即控制台打印日志
        ls.setFormatter(formatter)
        # 把控制台添加到logger
        logger.addHandler(ls)
        # 在项目目录下建一个logs目录，来存放log文件
        logdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        # 在logs目录下创建以日期开头的.log文件
        logfile = os.path.join(logdir, time.strftime('%Y-%m-%d') + '.log')
        # 添加log的文件处理器，并设置log的配置文件模式编码
        lf = logging.FileHandler(filename=logfile, encoding='utf8')
        # 设置log文件处理器记录的日志级别
        lf.setLevel(logging.DEBUG)
        # 设置日志记录的格式
        lf.setFormatter(formatter)
        # 把文件处理器添加到log
        logger.addHandler(lf)
    if level == 0:
        logger.info(str)
    elif level == 1:
        logger.warning(str)
    elif level == 2:
        logger.error(str)
    elif level == 3:
        logger.debug(str)


if __name__ == '__main__':
    socket_service()
