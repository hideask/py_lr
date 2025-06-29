import pandas as pd
import os

def getFileNames(path, suffix):
    r_list = []
    path_list = os.listdir(path)
    for p in path_list:
        if os.path.splitext(p)[1] == suffix:
            r_list.append(p)

    return r_list
def getFileNames2(path, suffix):
    r_list = []
    path_list = os.listdir(path)
    for p in path_list:
        if p.endswith(suffix):
            r_list.append(p)

    return r_list

def add_field(len, name):
    name_col = []
    for i in range(len):
        name_col.append(name)
    return name_col


if __name__ == '__main__' :
    file_path = 'C:/Users/songjia/Downloads'
    files_list = getFileNames2(file_path, '.xls')
    print(files_list)
    df_all = []
    for file in files_list :
        df = pd.read_excel(file_path + '/' + file)
        name = file.split('-')[1]
        df['姓名'] = add_field(df.__len__(),name)
        print(df)
        df_all.append(df)


    df_merge = pd.concat(df_all,ignore_index=True)

    last_col = df_merge.columns[-1]
    df_merge = df_merge[[last_col] + df_merge.columns.drop([last_col]).tolist()]

    print(df_merge)
    # df_all = pd.DataFrame(df_all)
    df_merge.to_excel(file_path + '/merge.xls')