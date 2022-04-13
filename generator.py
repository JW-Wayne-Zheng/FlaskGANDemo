import tensorflow as tf
import tensorflow.keras.layers as L
import tensorflow_addons as tfa
from tensorflow.keras import Model

HEIGHT = 256
WIDTH = 256
CHANNELS = 3
BATCH_SIZE = 16
EPOCHS = 120
TRANSFORMER_BLOCKS = 6
GENERATOR_LR = 2e-4
DISCRIMINATOR_LR = 2e-4

conv_initializer = tf.random_normal_initializer(mean=0.0, stddev=0.02)
gamma_initializer = tf.keras.initializers.RandomNormal(mean=0.0, stddev=0.02)


def encoder_block(input_layer, filters, size=3, strides=2, apply_instancenorm=True, activation=L.ReLU(), name='block_x'):
    block = L.Conv2D(filters, size,
                     strides=strides,
                     padding='same',
                     use_bias=False,
                     kernel_initializer=conv_initializer,
                     name=f'encoder_{name}')(input_layer)

    if apply_instancenorm:
        block = tfa.layers.InstanceNormalization(
            gamma_initializer=gamma_initializer)(block)

    block = activation(block)

    return block


def transformer_block(input_layer, size=3, strides=1, name='block_x'):
    filters = input_layer.shape[-1]

    block = L.Conv2D(filters, size, strides=strides, padding='same', use_bias=False,
                     kernel_initializer=conv_initializer, name=f'transformer_{name}_1')(input_layer)
#     block = tfa.layers.InstanceNormalization(gamma_initializer=gamma_initializer)(block)
    block = L.ReLU()(block)

    block = L.Conv2D(filters, size, strides=strides, padding='same', use_bias=False,
                     kernel_initializer=conv_initializer, name=f'transformer_{name}_2')(block)
#     block = tfa.layers.InstanceNormalization(gamma_initializer=gamma_initializer)(block)

    block = L.Add()([block, input_layer])

    return block


def decoder_block(input_layer, filters, size=3, strides=2, apply_instancenorm=True, name='block_x'):
    block = L.Conv2DTranspose(filters, size,
                              strides=strides,
                              padding='same',
                              use_bias=False,
                              kernel_initializer=conv_initializer,
                              name=f'decoder_{name}')(input_layer)

    if apply_instancenorm:
        block = tfa.layers.InstanceNormalization(
            gamma_initializer=gamma_initializer)(block)

    block = L.ReLU()(block)

    return block

# Resized convolution


def decoder_rc_block(input_layer, filters, size=3, strides=1, apply_instancenorm=True, name='block_x'):
    block = tf.image.resize(images=input_layer, method='bilinear',
                            size=(input_layer.shape[1]*2, input_layer.shape[2]*2))

#     block = tf.pad(block, [[0, 0], [1, 1], [1, 1], [0, 0]], "SYMMETRIC") # Works only with GPU
#     block = L.Conv2D(filters, size, strides=strides, padding='valid', use_bias=False, # Works only with GPU
    block = L.Conv2D(filters, size,
                     strides=strides,
                     padding='same',
                     use_bias=False,
                     kernel_initializer=conv_initializer,
                     name=f'decoder_{name}')(block)

    if apply_instancenorm:
        block = tfa.layers.InstanceNormalization(
            gamma_initializer=gamma_initializer)(block)

    block = L.ReLU()(block)

    return block


def generator_fn(height=HEIGHT, width=WIDTH, channels=CHANNELS, transformer_blocks=TRANSFORMER_BLOCKS):
    OUTPUT_CHANNELS = 3
    inputs = L.Input(shape=[height, width, channels], name='input_image')

    # Encoder
    enc_1 = encoder_block(inputs, 64,  7, 1, apply_instancenorm=False,
                      activation=L.ReLU(), name='block_1')  # (bs, 256, 256, 64)
    enc_2 = encoder_block(enc_1, 128, 3, 2, apply_instancenorm=True,
                      activation=L.ReLU(), name='block_2')   # (bs, 128, 128, 128)
    enc_3 = encoder_block(enc_2, 256, 3, 2, apply_instancenorm=True,
                      activation=L.ReLU(), name='block_3')   # (bs, 64, 64, 256)

    # Transformer
    x = enc_3
    for n in range(transformer_blocks):
        # (bs, 64, 64, 256)
        x = transformer_block(x, 3, 1, name=f'block_{n+1}')

    # Decoder 
    x_skip = L.Concatenate(name='enc_dec_skip_1')(
        [x, enc_3])  # encoder - decoder skip connection

    dec_1 = decoder_block(x_skip, 128, 3, 2, apply_instancenorm=True,
                      name='block_1')  # (bs, 128, 128, 128)
    x_skip = L.Concatenate(name='enc_dec_skip_2')(
        [dec_1, enc_2])  # encoder - decoder skip connection

    # (bs, 256, 256, 64)   
    dec_2 = decoder_block(
        x_skip, 64,  3, 2, apply_instancenorm=True, name='block_2')
    x_skip = L.Concatenate(name='enc_dec_skip_3')(
        [dec_2, enc_1])  # encoder - decoder skip connection

    outputs = last = L.Conv2D(OUTPUT_CHANNELS, 7,
                          strides=1, padding='same',
                          kernel_initializer=conv_initializer,
                          use_bias=False,
                          activation='tanh',
                          name='decoder_output_block')(x_skip)  # (bs, 256, 256, 3)

    generator = Model(inputs, outputs)

    return generator
