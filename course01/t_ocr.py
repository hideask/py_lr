import requests
import json
import jsonpath

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 从json数据中根据start_row,start_col,end_row,end_col是否符合要求的单元格内容
def filter_by(td_info, start_row=None, start_col=None, end_row=None, end_col=None):
    params = locals()
    params.pop('td_info')
    for key in params:
        if params[key] is None:
            continue
        if td_info.get(key) != params[key]:
            return False
    return True

class CommonOcr(object):
    def __init__(self, img_path):
        self._img_path = img_path
    def recognize(self):
        # 替换为真实的URL
        url = 'http://129.2.2.61:10001/ai/service/v2/recognize/table'
        try:
            image = get_file_content(self._img_path)
            result = requests.post(url, data=image)
            return result.text
        except Exception as e:
            return e

if __name__ == "__main__":
    response = CommonOcr(r'F:/data/gd/pic-2.jpg')
    datajs = json.loads(response.recognize())

    s1 = jsonpath.jsonpath(datajs,"$..table_cells")  #获取所有cells
    print(s1[1])   #返回的所有列表
    # 使用filter()函数和lambda表达式过滤列表，获取指定范围内的单元格，并返回一个新列表，指定start_row、start_col、end_row、end_col参数
    filtered_list = list(filter(lambda x: filter_by(x, start_row=0, start_col=2, end_row=0, end_col=5), s1[1]))
    xm = filtered_list[0]['text']
    # 获取性别
    filtered_list = list(filter(lambda x: filter_by(x, start_row=0, start_col=7, end_row=0, end_col=8), s1[1]))
    xb = filtered_list[0]['text']
    filtered_list = list(filter(lambda x: filter_by(x, start_row=0, start_col=12, end_row=0, end_col=14), s1[1]))
    #社会保障号
    shbzh = filtered_list[0]['text']
    filtered_list = list(filter(lambda x: filter_by(x, start_row=1, start_col=2, end_row=1, end_col=5), s1[1]))
    # 出生年月
    csny = filtered_list[0]['text']
    filtered_list = list(filter(lambda x: filter_by(x, start_row=1, start_col=9, end_row=1, end_col=10), s1[1]))
    # 参加工作时间
    cjgzsj = filtered_list[0]['text']
    filtered_list = list(filter(lambda x: filter_by(x, start_row=1, start_col=13, end_row=1, end_col=14), s1[1]))
    # 申报日期
    sbrq = filtered_list[0]['text'].replace('\n','')
    filtered_list = list(filter(lambda x: filter_by(x, start_row=2, start_col=2, end_row=2, end_col=5), s1[1]))
    # 退休类别
    txlb = filtered_list[0]['text']
    filtered_list = list(filter(lambda x: filter_by(x, start_row=2, start_col=9, end_row=2, end_col=10), s1[1]))
    # 批准退休时间
    pztxsj = filtered_list[0]['text']
    filtered_list = list(filter(lambda x: filter_by(x, start_row=2, start_col=13, end_row=2, end_col=14), s1[1]))
    # 工作年限
    gznx = filtered_list[0]['text']
    #不计算工龄的在校学习时间
    filtered_list = list(filter(lambda x: filter_by(x, start_row=3, start_col=2, end_row=4, end_col=2), s1[1]))
    bjsgnzxxxsj = filtered_list[0]['text']
    #2014年10月前连续工龄
    filtered_list = list(filter(lambda x: filter_by(x, start_row=3, start_col=6, end_row=4, end_col=7), s1[1]))
    lxgn2014 = filtered_list[0]['text']
    #视同缴费年限
    filtered_list = list(filter(lambda x: filter_by(x, start_row=4, start_col=8, end_row=4, end_col=14), s1[1]))
    stjfnx = filtered_list[0]['text'].replace('\n','')
    #个人身份
    filtered_list = list(filter(lambda x: filter_by(x, start_row=5, start_col=6, end_row=5, end_col=7), s1[1]))
    grsf = filtered_list[0]['text'].replace('\n','')
    #用工形式
    filtered_list = list(filter(lambda x: filter_by(x, start_row=5, start_col=10, end_row=5, end_col=11), s1[1]))
    ygxs = filtered_list[0]['text'].replace('\n','')
    #是否领导
    filtered_list = list(filter(lambda x: filter_by(x, start_row=5, start_col=14, end_row=5, end_col=14), s1[1]))
    sfld = filtered_list[0]['text'].replace('\n','')
    #升降前享受待遇职务
    filtered_list = list(filter(lambda x: filter_by(x, start_row=6, start_col=6, end_row=6, end_col=7), s1[1]))
    sjqdyzw = filtered_list[0]['text'].replace('\n','')
    #升降前级别
    filtered_list = list(filter(lambda x: filter_by(x, start_row=6, start_col=10, end_row=6, end_col=11), s1[1]))
    sjqjb = filtered_list[0]['text']
    #升降前档次
    filtered_list = list(filter(lambda x: filter_by(x, start_row=6, start_col=14, end_row=6, end_col=14), s1[1]))
    sjqdc = filtered_list[0]['text']
    #股级干部标识
    filtered_list = list(filter(lambda x: filter_by(x, start_row=7, start_col=6, end_row=7, end_col=7), s1[1]))
    gjgbbs = filtered_list[0]['text']
    #警衔
    filtered_list = list(filter(lambda x: filter_by(x, start_row=7, start_col=10, end_row=7, end_col=11), s1[1]))
    jx = filtered_list[0]['text']
    #基本工资加发标识
    filtered_list = list(filter(lambda x: filter_by(x, start_row=7, start_col=14, end_row=7, end_col=14), s1[1]))
    jbgzjfbs = filtered_list[0]['text']
    #地区工资补贴
    filtered_list = list(filter(lambda x: filter_by(x, start_row=8, start_col=6, end_row=8, end_col=7), s1[1]))
    dqgzbt = filtered_list[0]['text']
    #升降后级别
    filtered_list = list(filter(lambda x: filter_by(x, start_row=8, start_col=10, end_row=8, end_col=11), s1[1]))
    sjhjb = filtered_list[0]['text']
    #升降后档次
    filtered_list = list(filter(lambda x: filter_by(x, start_row=8, start_col=14, end_row=8, end_col=14), s1[1]))
    sjhdc = filtered_list[0]['text']
    #退休个人身份
    filtered_list = list(filter(lambda x: filter_by(x, start_row=9, start_col=6, end_row=9, end_col=7), s1[1]))
    txgrsf = filtered_list[0]['text'].replace('\n','')
    #退休用工形式
    filtered_list = list(filter(lambda x: filter_by(x, start_row=9, start_col=10, end_row=9, end_col=11), s1[1]))
    txygxs = filtered_list[0]['text'].replace('\n','')
    #退休是否领导
    filtered_list = list(filter(lambda x: filter_by(x, start_row=9, start_col=14, end_row=9, end_col=14), s1[1]))
    txsfld = filtered_list[0]['text'].replace('\n','')
    #退休享受待遇职务
    filtered_list = list(filter(lambda x: filter_by(x, start_row=10, start_col=6, end_row=10, end_col=7), s1[1]))
    txdyzw = filtered_list[0]['text'].replace('\n','')
    #退休级别
    filtered_list = list(filter(lambda x: filter_by(x, start_row=10, start_col=10, end_row=10, end_col=11), s1[1]))
    txjb = filtered_list[0]['text']
    #退休档次
    filtered_list = list(filter(lambda x: filter_by(x, start_row=10, start_col=14, end_row=10, end_col=14), s1[1]))
    txdc = filtered_list[0]['text']
    #退休享受待遇职务
    filtered_list = list(filter(lambda x: filter_by(x, start_row=11, start_col=6, end_row=11, end_col=7), s1[1]))
    txdyzw = filtered_list[0]['text'].replace('\n','')
    #退休股级干部标识
    filtered_list = list(filter(lambda x: filter_by(x, start_row=11, start_col=10, end_row=11, end_col=11), s1[1]))
    txgjgbbs = filtered_list[0]['text']
    #退休警衔
    filtered_list = list(filter(lambda x: filter_by(x, start_row=11, start_col=14, end_row=11, end_col=14), s1[1]))
    txjx = filtered_list[0]['text']
    #常住地址
    filtered_list = list(filter(lambda x: filter_by(x, start_row=12, start_col=5, end_row=12, end_col=14), s1[1]))
    czdz = filtered_list[0]['text'].replace('\n','')
    #邮政编码
    filtered_list = list(filter(lambda x: filter_by(x, start_row=13, start_col=5, end_row=14, end_col=7), s1[1]))
    yzbm = filtered_list[0]['text']
    #固定电话
    filtered_list = list(filter(lambda x: filter_by(x, start_row=13, start_col=13, end_row=13, end_col=14), s1[1]))
    gddh = filtered_list[0]['text']
    #移动电话
    filtered_list = list(filter(lambda x: filter_by(x, start_row=14, start_col=13, end_row=14, end_col=14), s1[1]))
    yddh = filtered_list[0]['text']
    #领取账户信息
    filtered_list = list(filter(lambda x: filter_by(x, start_row=15, start_col=4, end_row=15, end_col=14), s1[1]))
    lqzhxx = filtered_list[0]['text'].replace('\n','')


    print(lqzhxx)
