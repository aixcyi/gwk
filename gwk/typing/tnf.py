# -*- coding: utf-8 -*-

from typing import Literal

from gwk.throwables import *

TNF = Literal[True, None, False]
"""
>>> branch = Wish()
>>> master = Wish(
>>>     merge_lang=True, merge_region=True
>>> )
>>> master += branch

在将branch合并到master时遵循以下策略：

- ``True`` 表示允许用branch覆盖master的信息；
- ``None`` 表示拒绝覆盖master的信息，哪怕二者不一致；
- ``False`` 表示当二者信息不一致时抛出异常。
"""


def check_tnf(obj, attr: str, new_value):
    """
    使用TNF策略校验与合并对象属性。

    TNF决策值应当存在该对象名为 "merge_{attr}" 的属性中，
    如果缺少这个属性，将会引发异常。

    :param obj: 目标对象（类实例）
    :param attr: 属性名称。
    :param new_value: 新的值。
    """
    old_value = getattr(obj, attr)
    policy = getattr(obj, 'merge_' + attr)

    if old_value == new_value:
        return

    if policy is True:
        setattr(obj, attr, new_value)
    elif policy is None:
        pass
    elif policy is False:
        raise MergingException(
            attr, old_value, new_value, type(obj).__name__
        )
