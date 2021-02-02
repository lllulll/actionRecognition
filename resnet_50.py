import tensorflow as tf
import tensorflow.contrib.slim as slim
import keras
def basic_Block(input,filter_num,index,is_training ):
   
    if index ==1 or index ==4 or index == 8 or index ==14:  #为了相加时的维度相同
       net = slim.conv3d(input, filter_num, [1,1,1],[1,1,1],activation_fn=None,padding='SAME')
       net = tf.layers.batch_normalization(net,training = is_training)
       net = tf.nn.relu(net)
       print(net.shape)
       net = slim.conv3d(net, filter_num, [3,3,3],[2,2,2],activation_fn=None,padding='SAME')
       net = tf.layers.batch_normalization(net, training = is_training)
       net = tf.nn.relu(net)
       print(net.shape)
       net = slim.conv3d(net, filter_num*4, [1,1,1],[1,1,1],activation_fn=None,padding='SAME')
       net = tf.layers.batch_normalization(net,training = is_training)
       net = tf.nn.relu(net)
       print("terribel:",net.shape)
       net_2 = slim.conv3d(input,filter_num*4,[1,1,1],[2,2,2],activation_fn=None,padding='SAME')
       net_2 = tf.layers.batch_normalization(net_2, training = is_training)
       print(net_2.shape)
       net = tf.add(net ,net_2)
    else:
       net = slim.conv3d(input, filter_num, [1,1,1],[1,1,1],activation_fn=None,padding='SAME')
       net = tf.layers.batch_normalization(net,training = is_training)
       net = tf.nn.relu(net)
       
       net = slim.conv3d(input, filter_num, [3,3,3],[1,1,1],activation_fn=None,padding='SAME')
       net = tf.layers.batch_normalization(net,training = is_training)
       net = tf.nn.relu(net)
    
       net = slim.conv3d(net, filter_num*4, [1,1,1],[1,1,1], activation_fn=None,padding='SAME')
       net = tf.layers.batch_normalization(net, training = is_training)
       net = tf.add(input, net)
        
    net = tf.nn.relu(net)
    return net
def C3D(input, num_classes, is_training, keep_prob ):
    with tf.variable_scope('C3D'):
        print(input.shape)
        net = slim.conv3d(input,64,[3,7,7],[2,2,2], activation_fn=None,padding='SAME', weights_regularizer=slim.l2_regularizer(0.0005))
        print("first_conv:",net.shape)
        net = tf.layers.batch_normalization(net, training = is_training)
        net = tf.nn.relu(net)
        net = slim.max_pool3d(net, kernel_size=[2, 2, 2], stride=[2, 2, 2], padding='SAME')
        print("after_max:",net.shape)
        net = basic_Block(net,64,1,is_training)
        net = basic_Block(net,64,2,is_training)
        net = basic_Block(net,64,3,is_training)
        #第一层残差块
        print("res_1:",net.shape)
        net = basic_Block(net,128,4,is_training)
        net = basic_Block(net,128,5,is_training)
        net = basic_Block(net,128,6,is_training)
        net = basic_Block(net,128,7,is_training)
        #第二层残差块
        print("res_2:",net.shape)
        net = basic_Block(net,256,8,is_training)
        net = basic_Block(net,256,9,is_training)
        net = basic_Block(net,256,10,is_training)
        net = basic_Block(net,256,11,is_training)
        net = basic_Block(net,256,12,is_training)
        net = basic_Block(net,256,13,is_training)
        #第三层残差块
        print("res_3:",net.shape)
        net = basic_Block(net,512,14,is_training)
        net = basic_Block(net,512,15,is_training)
        net = basic_Block(net,512,16,is_training)
        # 第四层残差块
        print("res_4:",net.shape)
        net = keras.layers.GlobalAveragePooling3D()(net)
        print("global_average:",net.shape)
        net = tf.reshape(net,[-1,2048])
        net = slim.fully_connected(net, 1000, weights_regularizer=slim.l2_regularizer(0.0005), \
                                   activation_fn=None)
        net = slim.dropout(net, keep_prob, scope='dropout1')
        out = slim.fully_connected(net, 101, weights_regularizer=slim.l2_regularizer(0.0005), \
                                   activation_fn=None, scope='out')

    return out