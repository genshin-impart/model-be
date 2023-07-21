# -*- coding: utf-8 -*-
import sys

from api.model import apply_model, train_model, realtime_predict

if __name__ == '__main__':
    # ? DEBUG
    # print('sys.argv: ', sys.argv)
    if sys.argv[1] == 'apply':
        """应用模型 参数格式:
        sys.argv[1]: 'apply'
        sys.argv[2]: out_chunk_len
        sys.argv[3]: storage_path
        sys.argv[4]: data_path
        """
        apply_model(out_chunk_len=int(sys.argv[2]), storage_path=sys.argv[3], data_path=sys.argv[4])
    elif sys.argv[1] == 'train':
        """训练模型 参数格式:
        sys.argv[1]: 'train'
        sys.argv[2]: data_path
        sys.argv[3]: model_storage_path
        sys.argv[4]: name
        sys.argv[5]: description
        sys.argv[6]: in_chunk_len
        sys.argv[7]: out_chunk_len
        sys.argv[8]: learning_rate
        sys.argv[9]: batch_size
        sys.argv[10]: epochs
        """
        train_model(
            data_path=sys.argv[2],
            storage_path=sys.argv[3],
            name=str(sys.argv[4]),
            description=str(sys.argv[5]),
            in_chunk_len=int(sys.argv[6]),
            out_chunk_len=int(sys.argv[7]),
            learning_rate=float(sys.argv[8]),
            batch_size=int(sys.argv[9]),
            epochs=int(sys.argv[10])
        )
    else:
        """滚动预测 参数格式：
        sys.argv[1]: 'realtime'
        sys.argv[2]: storage_path
        sys.argv[3]: csv_path
        sys.argv[4]: in_chunk_len
        sys.argv[5]: out_chunk_len
        """
        realtime_predict(
            storage_path=sys.argv[2],
            csv_path=sys.argv[3],
            in_chunk_len=int(sys.argv[4]),
            out_chunk_len=int(sys.argv[5])
        )
