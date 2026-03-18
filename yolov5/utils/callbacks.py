"""
训练回调函数模块
包含：ReduceLROnPlateau, EarlyStopping, ModelEMA 等
(与 YOLOv2 版本基本相同，适用于通用训练流程)
"""

import torch
import torch.nn as nn
from copy import deepcopy
import math


class ReduceLROnPlateau:
    """当验证指标停止改善时降低学习率"""

    def __init__(self, optimizer, mode='min', factor=0.1, patience=5,
                 min_lr=1e-7, threshold=1e-4, verbose=True):
        self.optimizer = optimizer
        self.mode = mode
        self.factor = factor
        self.patience = patience
        self.min_lr = min_lr
        self.threshold = threshold
        self.verbose = verbose
        self.best = None
        self.num_bad_epochs = 0
        self.num_lr_reductions = 0
        self._last_lr = [group['lr'] for group in optimizer.param_groups]
        self._init_is_better()

    def _init_is_better(self):
        if self.mode == 'min':
            self.is_better = lambda a, best: a < best - self.threshold
        else:
            self.is_better = lambda a, best: a > best + self.threshold

    def step(self, metrics):
        current = float(metrics)
        reduced = False
        if self.best is None:
            self.best = current
            self.num_bad_epochs = 0
        elif self.is_better(current, self.best):
            self.best = current
            self.num_bad_epochs = 0
        else:
            self.num_bad_epochs += 1
        if self.num_bad_epochs >= self.patience:
            reduced = self._reduce_lr()
            self.num_bad_epochs = 0
        return reduced

    def _reduce_lr(self):
        reduced = False
        for i, param_group in enumerate(self.optimizer.param_groups):
            old_lr = param_group['lr']
            new_lr = max(old_lr * self.factor, self.min_lr)
            if old_lr > self.min_lr:
                param_group['lr'] = new_lr
                reduced = True
                self._last_lr[i] = new_lr
                if self.verbose:
                    print(f'  Reducing learning rate: {old_lr:.2e} -> {new_lr:.2e}')
        if reduced:
            self.num_lr_reductions += 1
        return reduced

    def get_last_lr(self):
        return self._last_lr

    def state_dict(self):
        return {
            'best': self.best,
            'num_bad_epochs': self.num_bad_epochs,
            'num_lr_reductions': self.num_lr_reductions,
            '_last_lr': self._last_lr
        }

    def load_state_dict(self, state_dict):
        self.best = state_dict['best']
        self.num_bad_epochs = state_dict['num_bad_epochs']
        self.num_lr_reductions = state_dict['num_lr_reductions']
        self._last_lr = state_dict['_last_lr']


class EarlyStopping:
    """早停机制"""

    def __init__(self, patience=10, mode='min', min_delta=0.0,
                 check_lr_reductions=False, max_lr_reductions=3, verbose=True):
        self.patience = patience
        self.mode = mode
        self.min_delta = min_delta
        self.check_lr_reductions = check_lr_reductions
        self.max_lr_reductions = max_lr_reductions
        self.verbose = verbose
        self.best = None
        self.counter = 0
        self.should_stop = False
        self._init_is_better()

    def _init_is_better(self):
        if self.mode == 'min':
            self.is_better = lambda a, best: a < best - self.min_delta
        else:
            self.is_better = lambda a, best: a > best + self.min_delta

    def reset(self):
        self.counter = 0

    def step(self, metrics, lr_reduced=False, num_lr_reductions=0):
        current = float(metrics)
        if self.check_lr_reductions:
            if lr_reduced:
                if self.best is not None and not self.is_better(current, self.best):
                    if num_lr_reductions >= self.max_lr_reductions:
                        self.should_stop = True
                        if self.verbose:
                            print(f'  Early stopping: {self.max_lr_reductions} LR reductions without improvement')
            if self.best is None or self.is_better(current, self.best):
                self.best = current
        else:
            if self.best is None:
                self.best = current
                self.counter = 0
            elif self.is_better(current, self.best):
                self.best = current
                self.counter = 0
            else:
                self.counter += 1
                if self.verbose and self.counter > 0:
                    print(f'  EarlyStopping counter: {self.counter}/{self.patience}')
                if self.counter >= self.patience:
                    self.should_stop = True
                    if self.verbose:
                        print(f'  Early stopping: No improvement for {self.patience} epochs')
        return self.should_stop

    def state_dict(self):
        return {'best': self.best, 'counter': self.counter, 'should_stop': self.should_stop}

    def load_state_dict(self, state_dict):
        self.best = state_dict['best']
        self.counter = state_dict['counter']
        self.should_stop = state_dict['should_stop']


class ModelEMA:
    """模型参数的指数移动平均"""

    def __init__(self, model, decay=0.9999, tau=2000, updates=0):
        self.ema = deepcopy(model).eval()
        self.updates = updates
        self.decay = decay
        self.tau = tau
        for p in self.ema.parameters():
            p.requires_grad_(False)

    def update(self, model):
        self.updates += 1
        d = self.decay * (1 - math.exp(-self.updates / self.tau))
        msd = model.state_dict()
        esd = self.ema.state_dict()
        for k, v in esd.items():
            if v.dtype.is_floating_point:
                v *= d
                v += (1 - d) * msd[k].detach()

    def state_dict(self):
        return {'ema': self.ema.state_dict(), 'updates': self.updates}

    def load_state_dict(self, state_dict):
        self.ema.load_state_dict(state_dict['ema'])
        self.updates = state_dict['updates']


class GradientAccumulator:
    """梯度累积器"""

    def __init__(self, accumulation_steps=1):
        self.accumulation_steps = accumulation_steps
        self.current_step = 0

    def backward(self, loss):
        scaled_loss = loss / self.accumulation_steps
        scaled_loss.backward()
        self.current_step += 1

    def should_step(self, batch_idx):
        return (batch_idx + 1) % self.accumulation_steps == 0

    def step(self, optimizer, scaler=None, grad_clip=0.0, model=None):
        if scaler is not None:
            if grad_clip > 0 and model is not None:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            scaler.step(optimizer)
            scaler.update()
        else:
            if grad_clip > 0 and model is not None:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()
        self.current_step = 0

    def get_effective_batch_size(self, batch_size):
        return batch_size * self.accumulation_steps


class WarmupScheduler:
    """学习率 Warmup 调度器"""

    def __init__(self, optimizer, warmup_epochs=3, warmup_bias_lr=0.1, warmup_momentum=0.8):
        self.optimizer = optimizer
        self.warmup_epochs = warmup_epochs
        self.warmup_bias_lr = warmup_bias_lr
        self.warmup_momentum = warmup_momentum
        self.base_lrs = [group['lr'] for group in optimizer.param_groups]
        self.base_momentum = optimizer.param_groups[0].get('momentum', 0.9)

    def step(self, epoch, batch_idx=0, num_batches=1):
        if epoch >= self.warmup_epochs:
            return
        progress = (epoch * num_batches + batch_idx) / (self.warmup_epochs * num_batches)
        for i, group in enumerate(self.optimizer.param_groups):
            group['lr'] = self.base_lrs[i] * progress
            if 'momentum' in group:
                group['momentum'] = self.warmup_momentum + \
                    (self.base_momentum - self.warmup_momentum) * progress
