# This is a sample Python script.
from datetime import datetime


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    print(datetime.now())
    strJson = {"msg": "身份证识别成功", "en.msg": "身份证识别成功", "code": "0", "succ": 1, "data": {"duration": "", "birthDay": "", "birthMonth": "", "address": "佳广州市白云区黄石东路333号", "gender": "", "nationality": "汉", "birthYear": "", "authority": "", "cardId": "440111199406037979", "name": "", "birth": "19940603"}, "client.doneCode": "1714189222056", "client.session.tracert": "4643628565677898", "cn.msg": "身份证识别成功", "client.doneCode.tracert": "4643628565677898", "server.doneCode": "app4.VmT20240428102348823C708", "errcode.uni": "BA-DEFAULT-0"}
    print(strJson["data"]["cardId"])
    print(str(strJson))
    str1 = '440111199406037979'
    print(str(strJson).index(str1))
    str2 = "440111199406037979"
    rst = (str1 == str2) | (1 == 2)
    flag = True
    flag1 = True
    print(rst)
    strs = ['1','2','3']
    print(strs.__len__())
    i = 0
    i += 1
    print(i)

    if flag:
        print("flag")
    elif:

    else:
        print("flag1")


    def all_values_in_set(lst, valid_set):
        return all(value in valid_set for value in lst)

        # 示例用法


    values = ['a', 'b', 'c', 'a', 'b']
    valid_values = {'a', 'b', 'c'}

    print(all_values_in_set(values, valid_values))  # 输出: True

    # 如果列表中包含不在集合中的值
    values_with_invalid = ['a', 'b', 'c', 'd', 'e']
    print(all_values_in_set(values_with_invalid, valid_values))  # 输出: False

    # 如果列表中包含不在集合中的值
    values_with_invalid = ['a', 'a']
    print(all_values_in_set(values_with_invalid, valid_values))  # 输出: False
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
