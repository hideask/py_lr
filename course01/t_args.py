'''
* 运算符：
在函数定义时，*args 用于接收不定数量的位置参数（可变位置参数）。这些参数将会被封装成一个元组。
在函数调用时，* 用于将一个可迭代对象（如列表、元组）解包成位置参数。
'''
def function(*args):
    for arg in args:
        print(arg)

function(1,2,3)
nums = [4,5,6]
function(*nums)

'''
** 运算符：
在函数定义时，**kwargs 用于接收不定数量的关键字参数（可变关键字参数）。这些参数将会被封装成一个字典。
在函数调用时，** 用于将一个字典解包成关键字参数。
'''
def function_1(**kwargs):

    for key,value in kwargs.items():
        print(key,value)

function_1(a=1, b=2)

my_dict = {'x':10,'y':20}
function_1(**my_dict)

'''
可以传任意类型的参数
'''
def function_2(*args, **kwargs):
    print(args)
    print(kwargs)

function_2(10,20,x=30,y=40)