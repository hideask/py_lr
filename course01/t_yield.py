import datetime
import time
from collections import defaultdict

from icecream import ic

'''
yield是暂停函数，return是结束函数； 即yield返回值后继续执行函数体内代码，return返回值后不再执行函数体内代码
yield返回的是一个迭代器（yield本身是生成器-生成器是用来生成迭代器的）；return返回的是正常可迭代对象（list,set,dict等具有实际内存地址的存储对象）
共同点：return和yield都用来返回值；在一次性地返回所有值场景中return和yield的作用是一样的。

不同点：如果要返回的数据是通过for等循环生成的迭代器类型数据（如列表、元组），return只能在循环外部一次性地返回，yeild则可以在循环内部逐个元素返回。下边我们举例说明这个不同点。
'''
def count_words(filename):
    counts = defaultdict(int)

    time.sleep(1)

    return counts

'''
在实际应用中使用yield，可以在大批量处理时，不用等一次性返回数据，
避免处理过程中发生错误，导致所有的处理都失败。
使用yield可以在for循环中，逐个返回数据
'''
def get_all_results(files):
    '''
    此处使用（）和yield的效果一样，内部使用generator
    []同list的迭代一样
    :param files:
    :return:
    '''
    return (count_words(f) for f in files)
    # return [count_words(f) for f in files]

'''  results = []
    for f in files:
        # results.append(count_words(f))
        yield count_words(f)
    # return results
'''

def update_remote_db(k, v):
    pass

def collect_results(files):
    results = defaultdict(int)

    for c in get_all_results(files):
        print("get one {}".format(datetime.datetime.now()))
        for k, v in c:
            # print('get {} {}'.format(k,v))
            update_remote_db(k,v)
            results[k] += v

'''
自定义实现迭代器
迭代器的定义，使用 __iter__() 和 __next__() 方法来实现迭代器的行为。

在主程序中，首先创建了一个数据实例 data，
然后创建了一个迭代器 data_iterator 并使用 next() 函数来获取迭代器的值。
'''
class Data:
    def __init__(self,len):
        self.data = []
        self.len = len
        for i in range(len):
            self.data.append(i)

    def get_data(self,i):
        return self.data[i]

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < self.len:
            result = self.get_data(self.index)
            self.index += 1
            return result
        else:
            # 抛出异常，中断程序
            raise StopIteration


if __name__ == '__main__':
    files = ['some_file'] * 2

    print("get one {}".format(datetime.datetime.now()))
    collect_results(files)

    data = Data(3)
    # print(ic(data.data[1]))
    # print(data.get_data(2))
    data_iter = iter(data)
    print(next(data_iter))
    print(next(data_iter))
    print(next(data_iter))
