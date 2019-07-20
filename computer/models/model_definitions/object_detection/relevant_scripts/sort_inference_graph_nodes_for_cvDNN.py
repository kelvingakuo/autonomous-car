import tensorflow as tf
from tensorflow.tools.graph_transforms import TransformGraph

with tf.gfile.FastGFile("D:/CODE/DATA/car_updated/AUTONOMOUS-SELF-DRVING-CAR/project_restructured/computer/models/saved_models/object_detection/BEST_MODEL-SO_FAR/detector_wide_angle_fullTF_7000_steps/frozen_inference_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    graph_def = TransformGraph(graph_def, ['image_tensor'], ['detection_boxes', 'detection_classes', 'detection_scores', 'num_detections'], ['sort_by_execution_order'])
    with tf.gfile.FastGFile("D:/CODE/DATA/car_updated/AUTONOMOUS-SELF-DRVING-CAR/project_restructured/computer/models/saved_models/object_detection/BEST_MODEL-SO_FAR/detector_wide_angle_fullTF_7000_steps/sorted_frozen_inference_graph.pb", 'wb') as f:
        f.write(graph_def.SerializeToString())