import tensorflow as tf
import numpy as np
import resnet_50
import data_process
def model():
    TRAIN_LOG_DIR = 'Log_resnet/train/'
    TRAIN_CHECK_POINT = 'train.ckpt-51'
    TEST_LOG_DIR = 'Log_test_resnet_50/'
    TEST_LIST_PATH = 'test.list'
    BATCH_SIZE = 1
    NUM_CLASSES = 101
    CROP_SZIE = 112
    CHANNEL_NUM = 3
    CLIP_LENGTH = 16
    EPOCH_NUM = 50
    test_num = data_process.get_test_num(TEST_LIST_PATH)
    test_video_indices = range(test_num)
    with tf.Graph().as_default():
        batch_clips = tf.placeholder(tf.float32, [BATCH_SIZE, CLIP_LENGTH, CROP_SZIE, CROP_SZIE, CHANNEL_NUM], name='X')
        batch_labels = tf.placeholder(tf.int32, [BATCH_SIZE, NUM_CLASSES], name='Y')
        is_training = tf.placeholder(tf.bool)
        keep_prob = tf.placeholder(tf.float32)
        logits = resnet_50.C3D(batch_clips, NUM_CLASSES,is_training,keep_prob)
        accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(logits, 1), tf.argmax(batch_labels, 1)), np.float32))
        k = tf.argmax(logits, 1)
        restorer = tf.train.Saver()
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        with tf.Session(config=config) as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(tf.local_variables_initializer())
            restorer.restore(sess, TRAIN_CHECK_POINT)
            accuracy_epoch = 0
            batch_index = 0
            step = 0
            for i in range(1):
                step = step+1
                # if i % 10 == 0:
                #    print('Testing %d of %d'%(i + 1, test_num // BATCH_SIZE))
                batch_data, batch_index = data_process.get_batches(TEST_LIST_PATH, NUM_CLASSES, batch_index,
                                                                  test_video_indices, BATCH_SIZE)
                accuracy_out,k_out= sess.run([accuracy,k],feed_dict={batch_clips: batch_data['clips'],
                                                         batch_labels: batch_data['labels'],is_training:False,keep_prob:1})
        print(k_out)
        return k_out
            #print('Test accuracy is %.5f' % (accuracy_epoch / (test_num // BATCH_SIZE)))
