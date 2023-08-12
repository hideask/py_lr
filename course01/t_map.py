import random
from icecream import ic

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


persons = [Person('test', random.randint(10, 20)) for _ in range(10)]

print(persons)

def add_age(p):
    p.age += 1
    return p.age
'''
map() 是一个内置函数，用于将一个函数应用于一个或多个序列（如列表、元组等）中的每个元素，
然后返回一个迭代器或可迭代对象，其中包含了将该函数应用于每个元素后的结果。
'''
r = map(add_age, persons)  #==> for p in persons: r = add_age(p)

print(next(r))
print(next(r))
print(next(r))

returned = filter(lambda n: n > 50,
                  map(lambda n: n ** 2,
                      map(lambda p:p.age, persons)))

ic(list(returned))