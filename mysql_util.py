import pymysql
import traceback
import sys

#测试连接数据库
# # 创建数据库的连接对象
# conn = pymysql.connect(host="localhost",database="notebook",user='root',password='123456',charset='utf8')
# # 创建游标对象
# cursor = conn.cursor()
# # 使用游标对象，执行sql语句
# # 增加
# sql_insert = "insert into articles (title,content,author,create_date) values ('测试标题','测试内容','测试作者','2023-08-20 23:14:39')"
# # 删除
# sql_delete = "delete from articles where title = '测试标题2'"
# # 修改/更新
# sql_update = "update articles set title = '测试标题2' where title = '测试标题'"
# # 查询
# sql_select = "select * from articles"
#
# try:
#     # result_insert = cursor.execute(sql_insert)# 增加
#     # result_delete = cursor.execute(sql_delete)# 删除
#     # result_update = cursor.execute(sql_update)# 修改/更新
#     result_select = cursor.execute(sql_select)# 查询
#     # print(result_insert) # 会输出操作的行数
#     # print(result_delete) # 会输出操作的行数
#     # print(result_update) # 会输出操作的行数
#     print(result_select) # 会输出操作的行数
#     # fetch这三种方法不同时出现，且仅在查询操作中使用
#     # print(cursor.fetchall()) # 会出查询的所有结果
#     # print(cursor.fetchone()) # 会输出一条查询的结果
#     # print(cursor.fetchmany(2)) # 传入参数会输出对应条数的查询结果
#     data = cursor.fetchall()
#     # print("查询结果为：\n %s " % data)
#     # print("查询结果为：\n {0}".format(data))
#     print(f"查询结果为：\n {data}")
#     conn.commit() # 提交操作，只要涉及增删改查就必须有commit，否则写不进数据库
# except:
#     print("操作失败！")
#     conn.rollback()
#
# #关闭游标
# cursor.close()
# #关闭连接
# conn.close()

class MysqlUtil():
    def __init__(self):
        host = '127.0.0.1'
        user = 'root'
        password = '123456'
        database = 'notebook'
        self.db = pymysql.connect(host=host, user=user, password=password, db=database)
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception:
            print("发生异常", Exception)
            self.db.rollback()
        finally:
            self.db.close()

    def fetchone(self, sql):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except:
            traceback.print_exc()
            self.db.rollback()
        finally:
            self.db.close()
        return result

    def fetchall(self, sql):
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
        except:
            info = sys.exc_info()
            print(info[0], ":", info[1])
            self.db.rollback()
        finally:
            self.db.close()
        return results

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            f = open("\log.txt", 'a')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
            self.db.rollback()
        finally:
            self.db.close()

    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        finally:
            self.db.close()