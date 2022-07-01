# 说明

Phicomm悟空M1官方服务器关闭,WIFI图标一直闪烁,最开始只是想写个监听9000端口的服务器,让它的WIFI图标不闪,后来写着写着就加上了把获取的数据保存到MYSQL,再后来,即然都保存到MYSQL了,干脆再写个前端吧.Python小白,代码比较乱.
# 安装必要环境
在Docker上创建Python容器,端口映射9000和5000的TCP端口,9000为M1监听端口,5000为前端访问端口.

然后在终端上安装下面模块:

`pip install Flask`

`pip install sqlalchemy`

`pip install pymysql`

`pip install mysql-connector`

`pip install pytz`

# 安装PhicommM1 Server

`cd /usr/local`

`git clone https://github.com/fenggenet/PhicommM1_Server.git`

# 修改MYSQL配置

###### -进入PhicommM1 Server目录

`cd PhicommM1_Server`

###### -修改You MySQL Host IP为你的MYSQL服务器地址

`sed -i 's/^HOSTNAME.*\+=.*/HOSTNAME = You MySQL Host IP/' common/sql.conf`

###### -修改You MySQL Host Prot为你的MYSQL服务器端口

`sed -i 's/^PORT.*\+=.*/PORT = You MySQL Host Prot/' common/sql.conf`

###### -修改You MySQL DataBase为你的MYSQL数据库名称

`sed -i 's/^DATABASE.*\+=.*/DATABASE = You MySQL DataBase/' common/sql.conf`

###### -修改You MySQL UserName为你的MYSQL服务器用户名

`sed -i 's/^USERNAME.*\+=.*/USERNAME = You MySQL UserName/' common/sql.conf`

###### -修改You MySQL Password为你的MYSQL服务器密码

`sed -i 's/^PASSWORD.*\+=.*/PASSWORD = You MySQL Password/' common/sql.conf`


# 运行

`chmod a+x ./run.sh`

# 前端截图
![image](https://github.com/fenggenet/PhicommM1_Server/blob/main/preview/M1.png)
# License
[GPL-3.0](./LICENSE)
