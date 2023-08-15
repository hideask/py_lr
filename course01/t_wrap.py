

def memory(f):
    memory.cache = {}
    def _wrap(*args, **kwargs):
        if args in memory.cache:
            print('hit {}'.format(args))
            return memory.cache[args]
        else:
            r = f(args)
            memory.cache[args] = r
            return r
    return _wrap


def change_result_to_none(f):
    def _wrap(n):
        return None
    return _wrap

'''
执行函数时会触发什么操作
'''
def buttons(c):
    def button(f):
        def _wrap(*args,**kwargs):
            r = f(*args, **kwargs)
            print('press keyboard {}'.format(c))
            return r
        return _wrap
    return button

buttons_m = {
    c : buttons(c) for c in 'qwert'
}
# buttons = [buttons(c) for c in 'qwert']

'''
装饰器（Decorators）是 Python 中一种强大的编程工具，它们可以用来修改、扩展或包装函数或方法的行为。
装饰器通常用于在不修改原函数代码的情况下，添加一些额外的功能或逻辑。
它们提供了一种优雅的方式来重用和组合代码，使得代码更加模块化、可维护和可读。

装饰器的作用包括但不限于以下几个方面：

代码复用和模块化： 装饰器可以用来将一些通用的功能抽象出来，然后在多个函数或方法中重复使用，从而避免了代码冗余。

代码扩展和修改： 装饰器可以在不修改原函数代码的情况下，添加新的功能、行为或逻辑。例如，你可以用装饰器来添加日志记录、性能分析、输入验证等功能。

代码透明性： 装饰器可以使原函数保持原始的外部接口，不会对函数的调用方式产生影响，从而保持代码的透明性和一致性。

代码分离关注点： 装饰器将不同的关注点分离开，使得每个函数只关注特定的功能，从而提高代码的可维护性。

AOP（面向切面编程）： 装饰器类似于面向切面编程中的切面，可以在不同的地方插入代码，如前置操作、后置操作等。

装饰器是对函数的改变，如果不需要改变就把装饰器注释就行了
'''
# @change_result_to_none
# @memory
# buttons[0]
@buttons_m['w']
def fib(n):
    # n = n[0]
    return fib(n - 1) + fib(n - 2) if n >= 2 else 1


if __name__ == '__main__':
    # fib = memory(fib)
    # print(fib(10))
    # 简写
    print(fib(10))