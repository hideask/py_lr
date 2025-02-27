import pandas as pd

policy_data = pd.read_excel('F:/data/政策法规.xls', skiprows=[0, 1], sheet_name='综合查询导出数据列表')
headers_list = policy_data.columns.tolist()
print(headers_list)
# print(policy_data.head())
# print(policy_data[['标题', '资料内容']])

data = policy_data[['标题', '资料内容']]
data = data.iloc[0:]

for head in headers_list:
    if not head.startswith('Unnamed'):
        print(head)

for index,row in data.iterrows():
    filename = row[0].replace('/', ' ').replace('<', '“').replace('>', '”')
    print(filename)
    with open('F:/data/policy/' + filename + '.txt', 'w', encoding='utf-8') as file:
        # print(row[0])
        # print(row[1])
        # print('------------------------')
        # print('------------------------')
        file.write(row[0])
        file.write("\n")
        file.write(row[1])
        # print(len(row))