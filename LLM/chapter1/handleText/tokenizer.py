import re
from torch.utils.data import DataLoader

from LLM.chapter1.handleText.GPTDatasetV1 import GPTDatasetV1
from LLM.chapter1.handleText.SimpleTokenizerV1 import SimpleTokenizerV1
from LLM.chapter1.handleText.SimpleTokenizerV2 import SimpleTokenizerV2

# download the text file
# url = ("https://raw.githubusercontent.com/rasbt/"
#        "LLMs-from-scratch/main/ch02/01_main-chapter-code/"
#        "the-verdict.txt")
# fiele_path = "the-verdict.txt"
# urllib.request.urlretrieve(url, fiele_path)

with open("the-verdict.txt", encoding="utf-8") as f :
    raw_text = f.read()

# print("Total number of characters:" , len(raw_text))
# print(raw_text[:100])

# text = 'Hello, word. This is-- a test.'
# result = re.split(r'([,.:;?_!"()\']|--|\s)', text)
# result = [item for item in result if item.strip()]
# print(result)

# Tokenizing text
preprocessed = re.split(r'([,.:;?_!"()\']|--|\s)', raw_text)
preprocessed = [item for item in preprocessed if item.strip()]
# print(len(preprocessed))
# print(preprocessed[:100])

# Coverting tokens into token IDs.
all_words = sorted(set(preprocessed))
vocab_size = len(all_words)
# print(vocab_size)

vocab = {token: integer for integer, token in enumerate(all_words)}
# for i , item in enumerate(vocab.items()):
#     print(i, item)
#     if i >= 50:
#         break

tokenizer = SimpleTokenizerV1(vocab)
text = """"It's the last he painted, you know," 
       Mrs. Gisburn said with pardonable pride."""
ids = tokenizer.encode(text)
# print(ids)
# print(tokenizer.decode(ids))

text = "Hello, do you like tea?"
# print(tokenizer.encode(text))

all_tokens = sorted(list(set(preprocessed)))
# end of text , unknown
all_tokens.extend(["<|endoftext|>", "<|unk|>"])
vocab = {token:integer for integer, token in enumerate(all_tokens)}
# print(len(vocab.items()))

# for i,item in enumerate(list(vocab.items())[-5:]):
#     print(item)

text1 = "Hello, do you like tea?"
text2 = "In the sunlit terraces of the palace."
text = " <|endoftext|> ".join((text1, text2))
# print(text)

tokenizer = SimpleTokenizerV2(vocab)
# print(tokenizer.encode(text))
# print(tokenizer.decode(tokenizer.encode(text)))

# Byte pair encoding (BPE)
from importlib.metadata import version
import tiktoken
print("tiktoken version:", version("tiktoken"))
tokenizer = tiktoken.get_encoding("gpt2")
text = (
    "Hello, do you like tea? <|endoftext|> In the sunlit terraces"
     "of someunknownPlace."
)
integers = tokenizer.encode(text, allowed_special={"<|endoftext|>"})
print(integers)

# 50256 is <|endoftext|>
# 8812, 2114, 1659, 617, 34680, 27271, 13 is someunknownPlace
strings = tokenizer.decode(integers)
print(strings)

#Data sampling with a sliding window
with open("the-verdict.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

enc_text = tokenizer.encode(raw_text)
print(len(enc_text))

enc_sample = enc_text[50:]
context_size = 4
x = enc_sample[:context_size]
y = enc_sample[1:context_size + 1]
print(f"x: {x}")
print(f"y:      {y}")

# input ----> received output
for i in range(1, context_size + 1):
    context = enc_sample[:i]
    desired = enc_sample[i]
    print(context, "---->", desired)

for i in range(1, context_size + 1):
    context = enc_sample[:i]
    desired = enc_sample[i]
    print(tokenizer.decode(context), "---->", tokenizer.decode([desired]))


def create_dataloader_v1(txt, batch_size=4, max_length=256,
                         stride=128, shuffle=True, drop_Last=True,
                         num_workers=0):
    tokenizer = tiktoken.get_encoding("gpt2")
    dataset = GPTDatasetV1(txt, tokenizer, max_length, stride)
    dataloader = DataLoader(dataset,
                            batch_size=batch_size,
                            shuffle=shuffle,
                            drop_last=drop_Last,
                            num_workers=num_workers)
    return dataloader
dataloader = create_dataloader_v1(raw_text, batch_size=1,
                                              max_length=4, stride=1,
                                              shuffle=False)
data_iter = iter(dataloader)
first_batch = next(data_iter)
print(first_batch)

second_batch = next(data_iter)
print(second_batch)

dataloader = create_dataloader_v1(raw_text, batch_size=8,
                                  max_length=4, stride=4, shuffle=False)
data_iter = iter(dataloader)
inputs, targets = next(data_iter)
print("Inputs: \n", inputs)
print("\nTargets:\n", targets)

#Creating token embeddings
