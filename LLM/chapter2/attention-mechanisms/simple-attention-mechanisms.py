import torch
inputs = torch.tensor(
  [[0.43, 0.15, 0.89], # Your     (x^1)
   [0.55, 0.87, 0.66], # journey  (x^2)
   [0.57, 0.85, 0.64], # starts   (x^3)
   [0.22, 0.58, 0.33], # with     (x^4)
   [0.77, 0.25, 0.10], # one      (x^5)
   [0.05, 0.80, 0.55]] # step     (x^6)
)
query = inputs[1]
attn_scores_2 = torch.empty(inputs.shape[0])
#print(attn_scores_2)
#print(inputs.shape[0])
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
for i,x_i in enumerate(inputs):
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
W_key   = torch.nn.Parameter(torch.rand(d_in, d_out), requires_grad=False)
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
print(context_vec_2)
print(inputs)

# use SelfAttention_v2 class
import SelfAttention_v2
torch.manual_seed(123)
sa_v2 = SelfAttention_v2.SelfAttention_v2(d_in, d_out)
print(sa_v2(inputs))

import SelfAttention_v1_v2
torch.manual_seed(123)
sa_v1_v2 = SelfAttention_v1_v2.SelfAttention_v1_v2(d_in, d_out)
print(sa_v1_v2(inputs))
