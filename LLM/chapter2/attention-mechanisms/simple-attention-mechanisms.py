import torch

inputs = torch.tensor(
    [[0.43, 0.15, 0.89],  # Your     (x^1)
     [0.55, 0.87, 0.66],  # journey  (x^2)
     [0.57, 0.85, 0.64],  # starts   (x^3)
     [0.22, 0.58, 0.33],  # with     (x^4)
     [0.77, 0.25, 0.10],  # one      (x^5)
     [0.05, 0.80, 0.55]]  # step     (x^6)
)
query = inputs[1]
attn_scores_2 = torch.empty(inputs.shape[0])
# print(attn_scores_2)
# print(inputs.shape[0])
for i, x_i in enumerate(inputs):
    # print(x_i, query)
    attn_scores_2[i] = torch.dot(x_i, query)
print(attn_scores_2)

attn_weight_2_tmp = attn_scores_2 / attn_scores_2.sum()
print("Attention weights:", attn_weight_2_tmp)
print("Sum:", attn_weight_2_tmp.sum())


def softmax_naive(x):
    return torch.exp(x) / torch.exp(x).sum()


attn_weight_2_naive = softmax_naive(attn_scores_2)
print("Attention weights:", attn_weight_2_naive)
print("Sum:", attn_weight_2_naive.sum())

attn_weight_2 = torch.softmax(attn_scores_2, dim=0)
print("Attention Weights:", attn_weight_2)
print("Sum:", attn_weight_2.sum())

query = inputs[1]
context_vec_2 = torch.zeros(query.shape)
for i, x_i in enumerate(inputs):
    print(attn_weight_2[i], x_i)
    print(attn_weight_2[i] * x_i)
    context_vec_2 += attn_weight_2[i] * x_i
    # print(context_vec_2)
print(context_vec_2)

# compute all context vectors
attn_scores = torch.empty(6, 6)
for i, x_i in enumerate(inputs):
    for j, x_j in enumerate(inputs):
        attn_scores[i, j] = torch.dot(x_i, x_j)
print(attn_scores)

# use matrix multiplication:
attn_scores = inputs @ inputs.T
print(attn_scores)

# normalize each row
attn_weights = torch.softmax(attn_scores, dim=1)
print(attn_weights)

# verify row sums
row_2_sum = sum([0.1385, 0.2379, 0.2333, 0.1240, 0.1082, 0.1581])
print("Row 2 sum:", row_2_sum)
print("All row sums:", attn_weights.sum(dim=1))

all_context_vecs = attn_weights @ inputs
print(inputs)
print(all_context_vecs)

# see that the previously calculated context_vec_2
# matches the second row in the previous tensor exactly
print("Previous 2nd context vector:", context_vec_2)

# compute query, key, and value
x_2 = inputs[1]
d_in = inputs.shape[1]
d_out = 2

torch.manual_seed(123)
W_query = torch.nn.Parameter(torch.rand(d_in, d_out), requires_grad=False)
W_key = torch.nn.Parameter(torch.rand(d_in, d_out), requires_grad=False)
W_value = torch.nn.Parameter(torch.rand(d_in, d_out), requires_grad=False)

query_2 = x_2 @ W_query
key_2 = x_2 @ W_key
value_2 = x_2 @ W_value
print(query_2)

# obtain all keys and values via matrix multiplication
keys = inputs @ W_key
values = inputs @ W_value
print("keys.shape:", keys.shape)
print("value_2.shape:", values.shape)

# compute the attention score w22.
keys_2 = keys[1]
attn_scores_22 = query_2.dot(keys_2)
print(attn_scores_22)

# compute all attention score via matrix multiplication
attn_scores_2 = query_2 @ keys.T
print(attn_scores_2)

# scale the attention scores
# the attention scores to the attention weights
d_k = keys.shape[-1]
attn_weights_2 = torch.softmax(attn_scores_2 / d_k ** 0.5, dim=-1)
print(attn_weights_2)

# compute the context vector as a weighted sum over the value vectors.
context_vec_2 = attn_weights_2 @ values
print(context_vec_2)

# use SelfAttention_v1 class
import SelfAttention_v1

torch.manual_seed(123)
sa_v1 = SelfAttention_v1.SelfAttention_v1(d_in, d_out)
print(sa_v1(inputs))
# print(context_vec_2)
# print(inputs)

# use SelfAttention_v2 class
import SelfAttention_v2

torch.manual_seed(789)
sa_v2 = SelfAttention_v2.SelfAttention_v2(d_in, d_out)
print(sa_v2(inputs))

import SelfAttention_v1_v2

torch.manual_seed(789)
sa_v1_v2 = SelfAttention_v1_v2.SelfAttention_v1_v2(d_in, d_out)
print(sa_v1_v2(inputs))

# apply a causal attention mask
# step 1
querys = sa_v2.W_query(inputs)
keys = sa_v2.W_key(inputs)
attn_scores = querys @ keys.T
attn_weights = torch.softmax(attn_scores / keys.shape[-1] ** 0.5, dim=-1)
print(attn_weights)

# zero diagonal elements
# step 2
context_length = attn_scores.shape[0]
mask_simple = torch.tril(torch.ones(context_length, context_length))  # lower triangular matrix
print(mask_simple)

masked_simple = attn_weights * mask_simple
print(masked_simple)

# step = 3
row_sums = masked_simple.sum(dim=-1, keepdim=True)
masked_simple_norm = masked_simple / row_sums
print(masked_simple_norm)

# mask the attention scores with negative infinity values before applying the softmax function
mask = torch.triu(torch.ones(context_length, context_length) * float('-inf'), diagonal=1)  # upper triangular matrix
masked = attn_scores.masked_fill(mask.bool(), -torch.inf)
print(masked)

# apply the softmax function to these masked results.
attn_weights = torch.softmax(masked / keys.shape[-1] ** 0.5, dim=1)
print(attn_weights)

# test dropout()
torch.manual_seed(123)
# 1/（1 - 0.5） = 2
dropout = torch.nn.Dropout(0.5)
example = torch.ones(6, 6)
print(dropout(example))

# apply dropout to the attention weights matrix
torch.manual_seed(123)
print(dropout(attn_weights))

#
batch = torch.stack((inputs, inputs), dim=0)
print(batch)
print(batch.shape)

# test CausalAttention
import CausalAttention
torch.manual_seed(123)
context_length = batch.shape[1]
ca = CausalAttention.CausalAttention(d_in, d_out, context_length, dropout=0.0)
context_vecs = ca(batch)
print("context_vecs.shape:", context_vecs.shape)

# test MultiHeadAttentionWrapper
import MultiHeadAttentionWrapper
torch.manual_seed(123)
context_length = batch.shape[1]
d_in, d_out = 3, 2
mha = MultiHeadAttentionWrapper.MultiHeadAttentionWrapper(
    d_in, d_out, context_length, dropout=0.0, num_heads=2)
print(context_length)
print(batch)
context_vecs = mha(batch)
print(context_vecs)
print("context_vecs.shape:", context_vecs.shape)

# test MultiHeadAttention
import MultiHeadAttention
a = torch.tensor([[[[0.2745, 0.6584, 0.2775, 0.8573],
                    [0.8993, 0.0390, 0.9268, 0.7388],
                    [0.7179, 0.7058, 0.9156, 0.4340]],

                   [[0.0772, 0.3565, 0.1479, 0.5331],
                    [0.4066, 0.2318, 0.4545, 0.9737],
                    [0.4606, 0.5159, 0.4220, 0.5786]]]])
# print(a.transpose(2, 3))
print(a @ a.transpose(2, 3))

first_head = a[0, 0, :, :]
print(first_head)
first_res = first_head @ first_head.T
print("First head:\n", first_res)

second_head = a[0, 1, :, :]
second_res = second_head @ second_head.T
print("\nSecond head:\n", second_res)

torch.manual_seed(123)
print(batch.shape)
batch_size, context_length, d_in = batch.shape
d_out = 2
mha = MultiHeadAttention.MultiHeadAttention(
    d_in, d_out, context_length, dropout=0.0, num_heads=2)
context_vecs = mha(batch)
print(context_vecs)
print("context_vecs.shape:", context_vecs.shape)

torch.manual_seed(123)
linear_layer = torch.nn.Linear(inputs.shape[1], 768)
inputs = linear_layer(inputs.float())
batch = torch.stack((inputs, inputs), dim=0)
print(batch.shape)
batch_size, context_length, d_in = batch.shape
d_out = 768
mha = MultiHeadAttention.MultiHeadAttention(
    d_in, d_out, context_length, dropout=0.0, num_heads=12)
context_vecs = mha(batch)
print(context_vecs)
print("context_vecs.shape:", context_vecs.shape)

