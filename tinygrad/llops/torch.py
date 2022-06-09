import os
import torch
import numpy as np
from ..tensor import Function

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
class Buffer(torch.Tensor):
  custompad = lambda x,padding: torch.nn.functional.pad(x, [item for sublist in padding[::-1] for item in sublist])
  @staticmethod
  def fromCPU(data):
    return Buffer(torch.from_numpy(data).requires_grad_(False)).to(device)
  def toCPU(x):
    return x.cpu().numpy()
  def getdtype(self):
    return np.float32

# ************* unary+binary+reduce+movement ops *************

from tinygrad.llops.cpu import unary_op, binary_op, reduce_op, perm_axis, inner_slice, matmul

# ************* processing ops *************

def conv(x,w,ret,conv_args):
  # TODO: replace conv_args with stride and groups everywhere
  H, W, groups, rcout, cin, oy, ox, iy, ix, ys, xs, bs = conv_args
  ret[:] = torch.nn.functional.conv2d(x, w, stride=(ys,xs), groups=groups)
  return ret

def convdw(x,grad_output,dw,conv_args):
  H, W, groups, rcout, cin, oy, ox, iy, ix, ys, xs, bs = conv_args
  dw[:] = torch.nn.grad.conv2d_weight(x, dw.shape, grad_output, stride=(ys,xs), groups=groups)
  return dw

def convdx(w,grad_output,dx,conv_args):
  H, W, groups, rcout, cin, oy, ox, iy, ix, ys, xs, bs = conv_args
  dx[:] = torch.nn.grad.conv2d_input(dx.shape, w, grad_output, stride=(ys,xs), groups=groups)
  return dx