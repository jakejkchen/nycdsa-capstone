#!/bin/sh
bert-serving-start -num_worker=1 -model_dir ./bert_model/uncased_L-24_H-1024_A-16 -port 5555