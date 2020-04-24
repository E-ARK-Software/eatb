#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import string
import uuid

def randomword(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def get_unique_id():
    return uuid.uuid4().__str__()
