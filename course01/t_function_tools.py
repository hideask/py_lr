import random
import time
from functools import reduce
import operator as op
from functools import cache
from functools import lru_cache
from functools import cached_property
from functools import total_ordering
from functools import partial

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

#e.g. 1
class Dateset:
    def __init__(self):
        pass

    #运用到被反复调用的方法上面，可以提高性能
    @cached_property
    def get_obj(self):
        return 'consuming date'

#e.g. 2  缓存用例
class User:
    def __init__(self, base_info):
        self.base_info = base_info

        def __hash__():
            return hash(self.base_info[0])

@cache
def get_user_log(user: User):
    time.sleep(2)
    return f'result {user}'

#e.g. 3 total_ordering
'''
通过装饰器 @total_ordering，我们只需要定义 __eq__ 和 __lt__ 方法，
而其他比较操作（<=、>、>=）会自动从 __eq__ 和 __lt__ 推导生成。这大大简化了自定义类的比较操作的实现。
'''
@total_ordering
class Hero:
    def __init__(self, name, live=None, magic=None):
        self.name = name
        self.live = live or random.randint(0,100)
        self.magic = magic or random.randint(0,100)

    def __lt__(self, other):
        return self.live ,self.magic < other.live, other.magic

    def __eq__(self, other):
        return self.live ,self.magic == other.live, other.magic

li_bai = Hero('libai')
cao = Hero('cao')
hunter = Hero('deman-hunter')
master = Hero('blood-master')

print(li_bai >= cao)
print(Hero("li_bai", 10, 10) == Hero('caocao', 10, 10))



'''
Partial Function
    g(x,y) -> 
        h(y) = g(x,y) #  x with a constant value 
        
    偏函数是一个包装器，它用于将函数的一部分参数固定为特定的值，从而生成一个新的函数。
    这个新函数的签名（参数列表）是原始函数的一部分。偏函数的主要目的是减少代码重复和提高代码的可复用性。
    
    偏函数非常有用，特别是当你有一个通用函数，但需要在不同上下文中使用不同的默认参数时。
    通过创建偏函数，你可以将通用函数适应于特定的用例，而不需要在每个调用中重复传递相同的参数。这可以提高代码的可读性和可维护性
'''

def reset_user_base(base_info, user):
    user.base_info = base_info

reset_user_base('base-info', User('1'))
reset_user_base('base-info', User('2'))
reset_user_base('base-info', User('3'))
reset_user_base('base-info', User('4'))


reset_user_type_1 = partial(reset_user_base, base_info = 'base_info_type2')
u = User('1')

'''
使用时要指定参数名
'''
reset_user_type_1(user = u)
print(u.base_info)

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
    '''
    TypeError: unhashable type: 'list'
    
    reason：
    试图使用一个包含可变类型（比如列表）的对象作为字典的键时。字典的键必须是不可变的，因为字典的键是通过哈希函数进行散列的，
    可变对象无法哈希。
    
    可变对象无法哈希的主要原因是哈希表的设计和哈希算法的特性。在哈希表中，哈希函数将键映射到特定的存储位置，以便能够快速查找和访问数据。
    哈希表的性能取决于哈希函数的均匀性，即哈希函数应该能够将不同的键映射到不同的位置，以避免冲突。
    
    为了实现这种均匀性，哈希函数需要满足以下要求：
    
    稳定性： 相同的输入始终产生相同的哈希值。这是哈希查找的基本要求。
    
    均匀分布： 输入的微小变化应该导致哈希值的大变化。这确保了不同的键被映射到不同的存储位置。
    
    可变对象通常不满足这两个要求：
    
    不稳定性： 可变对象的值可以随时更改。如果一个可变对象的值在哈希表中被修改，那么哈希值也会发生变化。这违反了稳定性的要求，
    因为同一对象的哈希值在不同时间会不同。
    
    不均匀分布： 可变对象通常是通过引用来比较的，而不是通过值。这意味着两个相等的可变对象（即使它们的内容相同）可能具有不同的哈希值，
    因为它们在内存中的位置不同。这违反了均匀分布的要求。
    
    为了确保哈希表的一致性和性能，Python 中的哈希函数通常只允许不可变对象（如数字、字符串和元组）作为字典的键。
    这确保了字典的键在不变的情况下可以被正确地哈希，而不会导致数据不一致或性能下降。
    '''
    # print(matrix([10,9]))

    #测试对方法缓存
    # jack = User(['JACK',1,2])
    # print(get_user_log(jack))
    # print(get_user_log(jack))
    # print(get_user_log(jack))
    # print(get_user_log(jack))
    # print(get_user_log(jack))