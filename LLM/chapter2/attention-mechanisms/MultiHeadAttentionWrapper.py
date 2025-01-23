import torch.nn as nn
import torch
import CausalAttention

class MultiHeadAttentionWrapper(nn.Module):
    def __init__(self, d_in, d_out, context_length,
                 dropout, num_heads, qkv_bias=False):
        super().__init__()
        self.heads = nn.ModuleList(
            [CausalAttention.CausalAttention(
                d_in, d_out, context_length, dropout, qkv_bias=qkv_bias
            )
            for _ in range(num_heads)]
        )

    # the results from each head are concatenated
    def forward(self, x):
        # We concatenate these context vector matrices along the column dimension.
        # If we have two attention heads and an embedding dimension of 2,
        # the final embedding dimension is 2 × 2 = 4.
        return torch.cat([head(x) for head in self.heads], dim=-1)

