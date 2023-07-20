# -*- coding: utf-8 -*-
import sys

from api.model import apply_model, train_model

if __name__ == '__main__':
    # ? DEBUG
    # print('sys.argv: ', sys.argv)
    if sys.argv[1] == 'apply':
        apply_model(out_chunk_len=int(sys.argv[2]), storage_path=sys.argv[3], data_path=sys.argv[4])
    else:
        pass