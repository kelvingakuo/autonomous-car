import tensorflow as tf



rec = "train.record"

typ = "train"

k = 0

for record in tf.python_io.tf_record_iterator(rec):
		k = k + 1


print("Count of {} records: {}".format(typ, k))