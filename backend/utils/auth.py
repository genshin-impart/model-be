# -*- coding: utf-8 -*-
import os

from models import User


def get_user(username: str):
    """在 User 表中查找查找用户名为 username 的用户

    Args:
        username (str): 用户名

    Returns:
        _type_: 用户对象
    """
    user = User.query.filter_by(username=username).first()
    return user