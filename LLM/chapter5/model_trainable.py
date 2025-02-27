# 添加父目录到系统路径中

import sys
import os
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chapter4.model import GPTModel, GPTConfig
