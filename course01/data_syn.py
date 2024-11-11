from datetime import datetime

import cx_Oracle
import psycopg2

# 连接 Oracle 数据库
dsn = cx_Oracle.makedsn('192.168.26.10', '1521', service_name='gjjdev')
ora_conn = cx_Oracle.connect(user="HFNEW_HF", password="111111", dsn=dsn)
# 连接 PostgreSQL 数据库
pg_conn = psycopg2.connect(dbname="nportal", user="nportal2023", password="nportal2023", host="172.20.20.32", port='5588')

i = 0
# 创建游标
ora_cursor = ora_conn.cursor()
pg_cursor = pg_conn.cursor()

# 查询 Oracle 数据
# ora_cursor.execute("SELECT * FROM t_biz_param_main")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_main " +
#                         "(cslsh, ywmk, sfzccs, csdm, csmc, csms, csz, sxrq, shxrq, sfqy, slsj, slrbh, sfqtxg) " +
#                         "values " +
#                         "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row)
#     print(i + 1)
#     i += 1
#
# ora_cursor.execute("SELECT * FROM t_biz_param_main_bus")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_main_bus (ywdjh, ycslsh, czlx, ywmk, sfzccs, csdm, csmc, csms, csz, sxrq, shxrq, sfqy, slsj, slrbh, slrxm, sljg, ywssjg, ywsswd, ywzt, ywhj, xxly, ywzy, spbz, bjrq, lcbbh, shyy, shcj, bzxx, glyw, glcs) values"
#    +"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#                       , row)
#     print(i + 1)
#     i += 1

# ora_cursor.execute("SELECT * FROM t_biz_param_main_his")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_main_his (ywlsh, cslsh, ywmk, sfzccs, csdm, csmc, csms, csz, sxrq, shxrq, sfqy, slsj, slrbh, sfqtxg, bgywdjh) values"
#   +"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#                       , row)
#     print(i + 1)
#     i += 1

# ora_cursor.execute("SELECT * FROM t_biz_param_scope")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_scope (fzxlsh, fzxzlx, fzxdm, fzxms) values "
#    +"(%s, %s, %s, %s)", row)
#     print(i + 1)
#     i += 1

# ora_cursor.execute("SELECT * FROM t_biz_param_scope_relation")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_scope_relation (ywlsh, cslsh, fzxlsh, fzxz, fzxms) values "
#   +"(%s, %s, %s, %s, %s)", row)
#     print(i + 1)
#     i += 1

# ora_cursor.execute("SELECT * FROM t_biz_param_scope_relation_bus")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_scope_relation_bus (ywlsh, ywdjh, cslsh, fzxlsh, fzxz, fzxms, yywlsh) values"
#   + "(%s, %s, %s, %s, %s, %s, %s)", row)
#     print(i + 1)
#     i += 1

# ora_cursor.execute("SELECT * FROM t_biz_param_scope_relation_his")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_scope_relation_his (sjlsh, ywlsh, cslsh, fzxlsh, fzxz, fzxms) values"
#    +"(%s, %s, %s, %s, %s, %s)", row)
#     print(i + 1)
#     i += 1

# ora_cursor.execute("SELECT * FROM t_biz_param_scope_value")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_scope_value (ywlsh, fzxlsh, bds, ms) values "
#                       +"(%s, %s, %s, %s)", row)
#     print(i + 1)
#     i += 1
#
# ora_cursor.execute("SELECT * FROM t_biz_param_scope_value")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     pg_cursor.execute("insert into t_biz_param_scope_value (ywlsh, fzxlsh, bds, ms) values "
#                       +"(%s, %s, %s, %s)", row)
#     print(i + 1)
#     i += 1


# ora_cursor.execute("select t.aaa101,t.aaa100,t.aaa103,t.aaa102,t.pid,nvl(t.ver,0),0,null,null,null,sysdate,1,0,1,'hx',t.aae120,t.sn,t.zjbdm,t.rhzxdm,1,0 from aa10 t")
# data = ora_cursor.fetchall()
# # print(data)
#
# # 插入或更新 PostgreSQL 数据
# for row in data:
#     print(row)
#     pg_cursor.execute("insert into tadict (name,type,label,value,parentvalue,sort,authority,cssclass,cssstyle,remarks,createdate,createuser,"
#                       + "version,status,field01,field02,field03,field04,field05,system,newtype) "
#                       + "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#                       , row)
#
#     # (row['aaa101'], row['aaa100'], row['aaa103'], row['aaa102'], row['pid'], row['ver'], 0, None, None, None,
#     #  datetime.now(), 1,
#     #  0, 1, row['db'], row['aae120'], row['sn'], row['zjbdm'], row['rhzxdm'], 1, 0)
#     print(i + 1)
#     i += 1



ora_cursor.execute("SELECT * FROM t_policy_info")
data = ora_cursor.fetchall()
# print(data)

# 插入或更新 PostgreSQL 数据
for row in data:
    pg_cursor.execute("insert into t_policy_info " +
   "(ywlsh, dwjcblsx, dwjcblxx, grjcblsx, grjcblxx, grzfdkzcnx, grzfdkzged, lllx, xmdkzcnx, xmdkzgdkbl, yjcesx, yjcexx, zxll, grzfdkzgdkbl, djczgzgdked, last_update_time, jcjssx, jcjsxx, grzfdkygsr, dkjcys, zftqjcys)" +
   "values" +
  "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row)
    print(i + 1)
    i += 1

# 提交事务并关闭连接
pg_conn.commit()
pg_cursor.close()
pg_conn.close()

ora_cursor.close()
ora_conn.close()
