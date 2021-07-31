import pymysql

user = input("请输入名字：")    #与用户进行数据交互
pwd = input("请输入密码：")




connection = pymysql.connect(host='localhost',
                                     port=3306,
                                     user='root',
                                     password='root',
                                     db='shanxiyuan',
                                     charset='utf8',
                                     unix_socket='/tmp/mysql.sock'
                                     )  # 连接数据库

cursor = connection.cursor()
# 定义一个游标，用cursor在connection下建立游标
sql = "select * from user_name where name=%s and pwd=%s"
# 调用sql语句对数据库进行操作
ret = cursor.execute(sql, [user, pwd])
# execute返回值ret的影响是行数，如果是0，则是查询匹配结果为0行
print('返回=', ret)
# 查看返回值

cursor.close()  # 关闭游标
connection.close()  # 关闭连接

if ret:
    print("登录成功")
else:
    print("登录失败")

print('居然走不到这儿')

