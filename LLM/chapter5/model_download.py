# import urllib.request
# url = (
#     "https://raw.githubusercontent.com/rasbt/"
#     "LLMs-from-scratch/main/ch05/"
#     "01_main-chapter-code/gpt_download.py"
# )
# filename = url.split('/')[-1]
# urllib.request.urlretrieve(url, filename)

from .gpt_download import download_and_load_gpt2
settings, params = download_and_load_gpt2(
    model_size="124M", models_dir="gpt2"
)

print("Settings:", settings)
print("Parameter dictionary keys:", params.keys())

print(params["wte"])
print("Token embedding weight tensor dimensions:", params["wte"].shape)

model_configs = {
    "gpt2-small (124M)": {"emb_dim": 768, "n_layers": 12, "n_heads": 12},
    "gpt2-medium (355M)": {"emb_dim": 1024, "n_layers": 24, "n_heads": 16},
    "gpt2-large (774M)": {"emb_dim": 1280, "n_layers": 36, "n_heads": 20},
    "gpt2-xl (1558M)": {"emb_dim": 1600, "n_layers": 48, "n_heads": 25},
}

from .model_trainable import device, tokenizer, GPT_CONFIG_124M, GPTModel, generate, text_to_token_ids, token_ids_to_text
import torch
# use the original GPT-2 models params 
model_name = "gpt2-small (124M)"
NEW_CONFIG = GPT_CONFIG_124M.copy()
NEW_CONFIG.update(model_configs[model_name])
NEW_CONFIG.update({"context_length": 1024})
NEW_CONFIG.update({"qkv_bias": True})

# initialize a new GPTModel instance
gpt = GPTModel(NEW_CONFIG)
gpt.eval()

def assign(left, right):
    if left.shape != right.shape:
        raise ValueError(f"Shape mismatch. Left: {left.shape}, "
                          f"Right: {right.shape}"
        )
    return torch.nn.Parameter(torch.tensor(right))

# loads the weights from the params dictionary
# import numpy as np
# def load_weights_into_gpt(gpt, params):
#     gpt.pos_emb.weight = assign(gpt.pos_emb.weight, params['wpe'])
#     gpt.tok_emb.weight = assign(gpt.tok_emb.weight, params['wte'])

#     for b in range(len(params["blocks"])):
#         q_w, k_w, v_w = np.split(
#             (params["blocks"][b]["attn"]["c_attn"])["w"], 3, axis=-1)
#         gpt.trf_blocks[b].att.W_query.weight = assign(
#             gpt.trf_blocks[b].att.W_query.weight, q_w.T)
#         gpt.trf_blocks[b].att.W_key.weight = assign(
#             gpt.trf_blocks[b].att.W_key.weight, k_w.T)
#         gpt.trf_blocks[b].att.W_value.weight = assign(
#             gpt.trf_blocks[b].att.W_value.weight, v_w.T)

#         q_b, k_b, v_b = np.split(
#             (params["blocks"][b]["attn"]["c_attn"])["b"], 3, axis=-1)
#         gpt.trf_blocks[b].att.W_query.bias = assign(
#             gpt.trf_blocks[b].att.W_query.bias, q_b)
#         gpt.trf_blocks[b].att.W_key.bias = assign(
#             gpt.trf_blocks[b].att.W_key.bias, k_b)
#         gpt.trf_blocks[b].att.W_value.bias = assign(
#             gpt.trf_blocks[b].att.W_value.bias, v_b)

#         gpt.trf_blocks[b].att.out_proj.weight = assign(
#             gpt.trf_blocks[b].att.out_proj.weight,
#             params["blocks"][b]["attn"]["c_proj"]["w"].T
#         )
#         gpt.trf_blocks[b].att.out_proj.bias = assign(
#             gpt.trf_blocks[b].att.out_proj.bias,
#             params["blocks"][b]["attn"]["c_proj"]["b"]
#         )

#         gpt.trf_blocks[b].ff.layer[0].weight = assign(
#             gpt.trf_blocks[b].ff.layer[0].weight,
#             params["blocks"][b]["mlp"]["c_fc"]["w"].T
#         )
#         gpt.trf_blocks[b].ff.layer[0].bias = assign(
#             gpt.trf_blocks[b].ff.layer[0].bias,
#             params["blocks"][b]["mlp"]["c_fc"]["b"]
#         )
#         gpt.trf_blocks[b].ff.layer[2].weight = assign(
#             gpt.trf_blocks[b].ff.layer[2].weight,
#             params["blocks"][b]["mlp"]["c_proj"]["w"].T
#         )
#         gpt.trf_blocks[b].ff.layer[2].bias = assign(
#             gpt.trf_blocks[b].ff.layer[2].bias,
#             params["blocks"][b]["mlp"]["c_proj"]["b"]
#         )

#         gpt.trf_blocks[b].norm1.scale = assign(
#             gpt.trf_blocks[b].norm1.scale,
#             params["blocks"][b]["ln_1"]["g"]
#         )
#         gpt.trf_blocks[b].norm1.shift = assign(
#             gpt.trf_blocks[b].norm1.shift,
#             params["blocks"][b]["ln_1"]["b"]
#         )
#         gpt.trf_blocks[b].norm2.scale = assign(
#             gpt.trf_blocks[b].norm2.scale,
#             params["blocks"][b]["ln_2"]["g"]
#         )
#         gpt.trf_blocks[b].norm2.shift = assign(
#             gpt.trf_blocks[b].norm2.shift,
#             params["blocks"][b]["ln_2"]["b"] 
#         )
    
#     gpt.final_norm.scale = assign(gpt.final_norm.scale, params["g"])
#     gpt.final_norm.shift = assign(gpt.final_norm.shift, params["b"])
#     gpt.out_head.weight = assign(gpt.out_head.weight, params["wte"])

import numpy as np

def load_weights_into_gpt(gpt, params):
    gpt.pos_emb.weight = assign(gpt.pos_emb.weight, params['wpe'])
    gpt.tok_emb.weight = assign(gpt.tok_emb.weight, params['wte'])

    for b in range(len(params["blocks"])):
        q_w, k_w, v_w = np.split(
            (params["blocks"][b]["attn"]["c_attn"])["w"], 3, axis=-1)
        gpt.trf_blocks[b].att.W_query.weight = assign(
            gpt.trf_blocks[b].att.W_query.weight, q_w.T)
        gpt.trf_blocks[b].att.W_key.weight = assign(
            gpt.trf_blocks[b].att.W_key.weight, k_w.T)
        gpt.trf_blocks[b].att.W_value.weight = assign(
            gpt.trf_blocks[b].att.W_value.weight, v_w.T)

        q_b, k_b, v_b = np.split(
            (params["blocks"][b]["attn"]["c_attn"])["b"], 3, axis=-1)
        gpt.trf_blocks[b].att.W_query.bias = assign(
            gpt.trf_blocks[b].att.W_query.bias, q_b)
        gpt.trf_blocks[b].att.W_key.bias = assign(
            gpt.trf_blocks[b].att.W_key.bias, k_b)
        gpt.trf_blocks[b].att.W_value.bias = assign(
            gpt.trf_blocks[b].att.W_value.bias, v_b)

        gpt.trf_blocks[b].att.out_proj.weight = assign(
            gpt.trf_blocks[b].att.out_proj.weight, 
            params["blocks"][b]["attn"]["c_proj"]["w"].T)
        gpt.trf_blocks[b].att.out_proj.bias = assign(
            gpt.trf_blocks[b].att.out_proj.bias, 
            params["blocks"][b]["attn"]["c_proj"]["b"])

        gpt.trf_blocks[b].ff.layers[0].weight = assign(
            gpt.trf_blocks[b].ff.layers[0].weight, 
            params["blocks"][b]["mlp"]["c_fc"]["w"].T)
        gpt.trf_blocks[b].ff.layers[0].bias = assign(
            gpt.trf_blocks[b].ff.layers[0].bias, 
            params["blocks"][b]["mlp"]["c_fc"]["b"])
        gpt.trf_blocks[b].ff.layers[2].weight = assign(
            gpt.trf_blocks[b].ff.layers[2].weight, 
            params["blocks"][b]["mlp"]["c_proj"]["w"].T)
        gpt.trf_blocks[b].ff.layers[2].bias = assign(
            gpt.trf_blocks[b].ff.layers[2].bias, 
            params["blocks"][b]["mlp"]["c_proj"]["b"])

        gpt.trf_blocks[b].norm1.scale = assign(
            gpt.trf_blocks[b].norm1.scale, 
            params["blocks"][b]["ln_1"]["g"])
        gpt.trf_blocks[b].norm1.shift = assign(
            gpt.trf_blocks[b].norm1.shift, 
            params["blocks"][b]["ln_1"]["b"])
        gpt.trf_blocks[b].norm2.scale = assign(
            gpt.trf_blocks[b].norm2.scale, 
            params["blocks"][b]["ln_2"]["g"])
        gpt.trf_blocks[b].norm2.shift = assign(
            gpt.trf_blocks[b].norm2.shift, 
            params["blocks"][b]["ln_2"]["b"])

    gpt.final_norm.scale = assign(gpt.final_norm.scale, params["g"])
    gpt.final_norm.shift = assign(gpt.final_norm.shift, params["b"])
    gpt.out_head.weight = assign(gpt.out_head.weight, params["wte"])

load_weights_into_gpt(gpt, params)
gpt.to(device)

torch.manual_seed(12)
token_ids = generate(
    model=gpt,
    idx=text_to_token_ids("Every effort moves you", tokenizer).to(device),
    max_new_tokens=25,
    context_size=NEW_CONFIG["context_length"],
    top_k=50,
    temperature=1.5,
)
print("Output text 1:\n", token_ids_to_text(token_ids, tokenizer))