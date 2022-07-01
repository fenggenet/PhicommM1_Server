import datetime
import pytz
from flask import Flask, jsonify, render_template,url_for
from sqlalchemy import create_engine

# 数据库配置变量
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'phicommm1'
USERNAME = 'PhicommM1'
PASSWORD = 'password'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
# 创建数据库引擎
engine = create_engine(DB_URI)

app = Flask(__name__)


@app.route('/')
def index():
    with engine.connect() as conn:
        rs = conn.execute('select * from m1 order by id DESC')
    row = rs.fetchone()
    return render_template(
        'index.html',
        info_time=timestamp2string(row.time),
        info_humidity=row.humidity,
        info_temperature=row.temperature,
        info_pm25=row.pm25,
        info_hcho=row.hcho
    )


@app.route('/getdata')
def getdata():
    with engine.connect() as conn:
        rs = conn.execute('select * from m1 order by id DESC')
    row = rs.fetchone()
    info_time = timestamp2string(row.time)
    info_humidity = str(row.humidity)
    info_temperature = str(row.temperature)
    info_pm25 = str(row.pm25)
    info_hcho = str(row.hcho)
    return jsonify(
        info_time=info_time,
        info_humidity=info_humidity,
        info_temperature=info_temperature,
        info_pm25=info_pm25,
        info_hcho=info_hcho
    )


# 时间戳转为文本时间格式
def timestamp2string(timestamp):
    _local_zone = pytz.timezone('Asia/Shanghai')
    d = datetime.datetime.fromtimestamp(timestamp,_local_zone)
    str1 = d.strftime("%Y-%m-%d %H:%M:%S")
    # 2022-06-29 16:43:37'
    return str1


# Json处理从M1取得的数据
def parsejsondata(data):
    pattern = r"(\{.*?\})"
    jsonstr = re.findall(pattern, str(data), re.M)
    l = len(jsonstr)
    if l > 0:
        return json.loads(jsonstr[l - 1])
    else:
        return None


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
