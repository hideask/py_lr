import urllib.request
import re

# download the text file
# url = ("https://raw.githubusercontent.com/rasbt/"
#        "LLMs-from-scratch/main/ch02/01_main-chapter-code/"
#        "the-verdict.txt")
# fiele_path = "the-verdict.txt"
# urllib.request.urlretrieve(url, fiele_path)

with open("the-verdict.txt", encoding="utf-8") as f :
    raw_text = f.read()

print("Total number of characters:" , len(raw_text))
print(raw_text[:100])

# text = 'Hello, word. This is-- a test.'
# result = re.split(r'([,.:;?_!"()\']|--|\s)', text)
# result = [item for item in result if item.strip()]
# print(result)

preprocessed = re.split(r'([,.:;?_!"()\']|--|\s)', raw_text)
preprocessed = [item for item in preprocessed if item.strip()]
print(len(preprocessed))
print(preprocessed[:100])