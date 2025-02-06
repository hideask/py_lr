import torch
import torch.nn as nn

GPT_CONFIG_124M = {
    "vocab_size": 50257,    # Vocabulary size
    "context_length": 1024, # Context length
    "emb_dim": 768,         # Embedding dimension
    "n_heads": 12,          # Number of heads in multi-head attention
    "n_layers": 12,         # Number of layers
    "drop_rate": 0.1,       # Dropout rate
    "qkv_bias": False       # Query-Key-Value bias
}

class DummyGPTModel(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.tok_emb = nn.Embedding(cfg["vocab_size"], cfg["emb_dim"])
        self.pos_emb = nn.Embedding(cfg["context_length"], cfg["emb_dim"])
        self.drop_emb = nn.Dropout(cfg["drop_rate"])
        self.trf_blocks = nn.Sequential(
            *[DummyTransformerBlock(cfg)
              for _ in range(cfg["n_layers"])
            ]
        )
        self.final_norm = DummyLayerNorm(cfg["emb_dim"])
        self.out_head = nn.Linear(
            cfg["emb_dim"], cfg["vocab_size"], bias=False
        )
    def forward(self, in_idx):
        batch_size, seq_len = in_idx.shape
        tok_embeds = self.tok_emb(in_idx)
        pos_embeds = self.pos_emb(
            torch.arange(seq_len, device=in_idx.device)
        )
        x = tok_embeds + pos_embeds
        x = self.drop_emb(x)
        x = self.trf_blocks(x)
        x = self.final_norm(x)
        logits = self.out_head(x)
        return logits

class DummyTransformerBlock(nn.Module):
    def __init__(self, cfg):
        super().__init__()

    def forward(self, x):
        return x

class DummyLayerNorm(nn.Module):
    def __init__(self, normalized_shape, eps=1e-5):
        super().__init__()

    def forward(self, x):
        return x

class LayerNorm(nn.Module):
    """
    This specific implementation of layer normalization operates on the last dimension of the input tensor x,
    which represents the embedding dimension (emb_dim).
    The variable eps is a small constant (epsilon) added to the variance to prevent division by zero during normalization.
    The scale and shift are two trainable parameters (of the same dimension as the input)
    that the LLM automatically adjusts during training if it is determined that doing so would improve the model’s performance
    on its training task. This allows the model to learn appropriate scaling and
    shifting that best suit the data it is processing.
    """
    def __init__(self, emb_dim):
        super().__init__()
        self.eps = 1e-5
        self.scale = nn.Parameter(torch.ones(emb_dim))
        self.shift = nn.Parameter(torch.zeros(emb_dim))

    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        # use an implementation detail by setting unbiased=False.
        # For those curious about what this means, in the variance calculation,
        # we divide by the number of inputs n in the variance formula
        # where the embedding dimension n is significantly large,
        # the difference between using n and n – 1 is practically negligible.
        # but the embedding demension n is small,
        # the deffrence between using n and n – 1 would be quiet noticeable.
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        norm_x = (x - mean) / torch.sqrt(var + self.eps)
        return self.scale * norm_x + self.shift

import tiktoken
if __name__ == "__main__":
    # tokenize a batch consisting of two text inputs for the GPT model
    # using the tiktoken tokenizer
    tokenizer = tiktoken.get_encoding("gpt2")
    batch = []
    txt1 = "Every effort moves you"
    txt2 = "Every day holds a"

    batch.append(torch.tensor(tokenizer.encode(txt1)))
    batch.append(torch.tensor(tokenizer.encode(txt2)))
    batch = torch.stack(batch, dim=0)
    print(batch)

    # initialize a new 124-million-parameter DummyGPTModel instance
    # and feed it the tokenized batch
    torch.manual_seed(123)
    model = DummyGPTModel(GPT_CONFIG_124M)
    logits = model(batch)
    print("Output shape:", logits.shape)
    print(logits)

    # a test of layer normalization where the six outputs of the layer,
    # also called activations, are normalized such that they have a 0 mean and
    # a variance of 1.
    torch.manual_seed(123)
    batch_example = torch.randn(2, 5)
    # ReLU , it simply thresholds negative inputs to 0, ensuring that a layer outputs only positive values,
    # which explains why the resulting layer output does not contain any negative values
    layer = nn.Sequential(nn.Linear(5, 6), nn.ReLU())
    out = layer(batch_example)
    print(out)
    print(out.shape)

    # The dim parameter specifies the dimension along which the calculation of the statistic
    # (here, mean or variance) should be performed in a tensor
    mean = out.mean(dim=-1, keepdim=True)
    var = out.var(dim=-1, keepdim=True)
    print("Mean:\n", mean)
    print("Variance:\n", var)

    out_norm = (out - mean) / torch.sqrt(var)
    mean = out_norm.mean(dim=-1, keepdim=True)
    var = out_norm.var(dim=-1, keepdim=True)
    print("Normalized layer outputs:\n", out_norm)
    print("Mean after normalization:\n", mean)
    print("Variance after normalization:\n", var)

    # turn off the scientific notation
    torch.set_printoptions(sci_mode=False)
    print("Mean:\n", mean)
    print("Variance:\n", var)

    # try the LayerNorm module in practice and apply it to the batch input.
    ln = LayerNorm(emb_dim=5)
    out_ln = ln(batch_example)
    mean = out_ln.mean(dim=-1, keepdim=True)
    var = out_ln.var(dim=-1, keepdim=True, unbiased=False)
    print("Mean:\n", mean)
    print("Variance:\n", var)

