'''
Context Manager
E.g:
    open file
    connect a dataset
    process images or some big files
'''
'''
file = open('t_args.py', 'a')

#or we connect the dataset

try:
    file.write('\n#newline')

finally:
    file.close()
'''

'''
with 语句是 Python 中一种用于简化资源管理的语法结构，它提供了一种方便的方式来确保在使用完资源后能够正确地释放、关闭或清理这些资源。
with 语句也被称为上下文管理器，它适用于一些需要进行初始化和清理操作的场景，比如文件操作、数据库连接、线程锁等。

with 语句的主要作用包括以下几点：

自动资源管理： with 语句会自动在进入代码块之前调用上下文管理器的 __enter__() 方法，
        用于初始化和获取资源。在代码块执行完毕后，无论是否发生异常，都会自动调用上下文管理器的 __exit__() 方法，用于释放、关闭或清理资源。

异常处理： with 语句可以帮助处理异常，确保在发生异常时资源能够正确地释放。如果在 __exit__() 方法中正确地处理了异常，可以避免资源泄漏等问题。

简化代码： 使用 with 语句可以让代码更加简洁、可读和可维护。你不需要显式地调用资源的初始化和清理操作，而是让 Python 自动管理这些过程。
'''
class Processer:
    def __init__(self, filename):
        self.file = filename

    def __enter__(self):
        try:
            print(f'initialize {self.file}')
            self.fileobj = open(self.file)
            return self.fileobj
        except FileNotFoundError as e:
            self.fileobj = None
            print('file not exists')


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fileobj:
            self.fileobj.close()

with Processer('t_args1.py') as file:
    pass

# with open('t_args.py') as file:
#     file.write('\n#newline')


'''

contextmanager 是 Python 标准库中 contextlib 模块提供的一个装饰器，用于将一个普通的生成器函数转化为上下文管理器。
上下文管理器可以用来在 with 语句块中管理资源，如文件、数据库连接等，以确保在进入和退出代码块时能够正确地初始化和清理这些资源。

使用 contextmanager 装饰器可以避免你手动编写一个完整的上下文管理器类，从而简化代码并提高可读性。
'''
from contextlib import contextmanager

@contextmanager
def connect_database(url):
    obj = open(url,'r',encoding='utf-8')
    try:
        print('enter the obj')
        yield obj
    finally:
        print('exit the obj')
        obj.close()


with connect_database('t_args.py') as c:
    print(c.read())