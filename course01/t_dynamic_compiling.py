a_sort = []
list_of_list = []
for i in range(100):
    a_sort.append(i)
    list_of_list.append(a_sort)

print(list_of_list)
print(list_of_list.__len__())

'''
展示python是一个动态编译的语言
'''
def decision_process(conditions, outs):
    base_string = f"if string.startswith('{conditions[0]}'): print('{outs[0]}')"
    for c, out in zip(conditions[1:],outs[1:]) :
        base_string += f"\n\telif string.startswith('{c}'): print('{out}')"

    return base_string

def create_func(conditions, outs):
    return f"""def complexit_if(string):
\t{decision_process(conditions,outs)}
    """

programming = create_func(['0','1','2'],['none', 'first', 'second'])

print(programming)

exec(programming)
exec("complexit_if('100123')")
exec("complexit_if('200123')")
exec("complexit_if('000123')")