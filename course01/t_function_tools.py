from functools import reduce, lru_cache, cached_property
import operator as op
from functools import cache

'''
reduce 函数是 Python 内置的一个高阶函数，位于 functools 模块中。它用于对一个序列（例如列表或元组）中的元素进行累积操作，从而将序列中的所有元素通过指定的二元函数进行逐步合并。

reduce 函数的语法如下：
functools.reduce(function, iterable[, initializer])
其中：

function 是一个二元函数（接受两个参数）或可调用对象，用于对序列中的元素进行合并操作。
iterable 是一个可迭代对象，包含需要进行累积操作的元素。
initializer 是可选的初始值，如果提供了初始值，则累积操作从初始值开始；如果没有提供初始值，则累积操作从序列的第一个元素开始。
reduce 函数的工作过程如下：

使用 function 对序列中的前两个元素进行操作，得到一个结果。
将上一步的结果与序列中的下一个元素进行操作，得到新的结果。
重复上一步，直到处理完所有元素，得到最终的累积结果。

'''

'''
operator 模块提供了一组用于执行常见操作的函数，这些函数通常用于对数据进行操作，例如比较、计算等。以下是一些常用的 operator 模块函数：

operator.add(a, b)：返回 a 和 b 的和。
operator.sub(a, b)：返回 a 减去 b 的结果。
operator.mul(a, b)：返回 a 和 b 的乘积。
operator.truediv(a, b)：返回 a 除以 b 的结果（浮点数除法）。
operator.floordiv(a, b)：返回 a 除以 b 的结果（整数除法）。
operator.mod(a, b)：返回 a 对 b 取模的结果。
operator.eq(a, b)：检查 a 是否等于 b，返回布尔值。
operator.ne(a, b)：检查 a 是否不等于 b，返回布尔值。
operator.lt(a, b)：检查 a 是否小于 b，返回布尔值。
operator.le(a, b)：检查 a 是否小于等于 b，返回布尔值。
operator.gt(a, b)：检查 a 是否大于 b，返回布尔值。
operator.ge(a, b)：检查 a 是否大于等于 b，返回布尔值。
以及其他更多操作函数
'''

some_lists = [
    [1,2],
    [3,4],
    [5,6,7,8,9,10.9,10.23,10.22],
    [112.3,134,55]
]

some_sets = (
    {1,2,3},
    {'node2'},
    {'node3'},
    {'ids'}
)

some_files = [
    'file_01',
    'file_02',
    'file_03',
    'file_04',
    'file_05',
    'file_06',
    'file_07',
    'file_08',
    'file_09',
    'file_10',
    'file_11'
]

some_numbers = [1,2,3,4,5,5,99]
whole_list = []

#常见写法
# for a_list in some_lists:
#     whole_list.append(a_list)
def merge(nested):
    """
    :param nested: a list which contains a lots of lists
    :return: a single list , which concat the lists
    """
    # whole_list = reduce(lambda a,b: a + b, nested)
    type_op = {
        list : op.add,
        int  : op.add,
        float: op.add,
        set  : op.or_,
        str  : op.add,
        dict : op.add

    }

    # if nested and len(nested) > 0: 同效果
    if nested:
        element = nested[0]
        print(reduce(type_op[type(element)], nested))
    else:
        print(nested)


# @cache
@lru_cache(maxsize=2**10)
def fib(n):
    return fib(n - 1) + fib(n - 2) if n >= 2 else 1

@cache
def matrix(position):
    x, y = position
    if x >= 1 and y >= 1:
        return matrix((x - 1, y - 1)) + matrix((x - 1, y)) + matrix((x, y - 1))
    else:
        return x,y

class Dateset:
    def __init__(self):
        pass

    #运用到被反复调用的方法上面，可以提高性能
    @cached_property
    def get_obj(self):
        return 'consuming date'


if __name__ == '__main__':
    # merge(some_lists)
    # merge(some_sets)
    # merge(some_files)
    # merge(some_numbers)
    # merge([])
    # merge(None)
    # print(fib(50))
    #
    # print(matrix((10,9)))
    print(matrix([10,9]))