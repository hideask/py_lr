import torch.nn as nn
import torch
import SelfAttention_v2
class SelfAttention_v1_v2(nn.Module):
    def __init__(self, d_in, d_out):
        sa_v2 = SelfAttention_v2.SelfAttention_v2(d_in, d_out)
        super().__init__()
        self.W_query = sa_v2.get_W_query()
        self.W_key = sa_v2.get_W_Key()
        self.W_value = sa_v2.get_W_value()

    def forward(self, x):
        keys = self.W_key(x)
        queries = self.W_query(x)
        values = self.W_value(x)
        attn_scores = queries @ keys.T
        attn_weights = torch.softmax(
            attn_scores / keys.shape[-1]**0.5, dim=-1
        )
        context_vec = attn_weights @ values
        return context_vec

