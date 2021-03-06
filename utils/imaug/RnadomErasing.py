import tensorflow as tf


@tf.function
def random_erasing(img, mask, probability=0.5, sl=0.02, sh=0.4, r1=0.3, method='random'):

    """

    :param img:
    :param mask:
    :param probability: 擦除的概率
    :param sl: 擦除面积比率的下界
    :param sh: 擦除面积比率的上界
    :param r1: 擦除矩形长宽比
    :param method: 擦除部分填充方法： 'random', 'white', 'black'
    :return:
    """
    if tf.random.uniform([]) > probability:
        return img, mask

    img_width = img.shape[1]
    img_height = img.shape[0]
    img_channels = img.shape[2]

    area = img_height * img_width

    target_area = tf.random.uniform([], minval=sl, maxval=sh) * area
    aspect_ratio = tf.random.uniform([], minval=r1, maxval=1 / r1)
    h = tf.cast(tf.math.round(tf.math.sqrt(target_area * aspect_ratio)), tf.int32)
    w = tf.cast(tf.math.round(tf.math.sqrt(target_area / aspect_ratio)), tf.int32)

    while tf.constant(True, dtype=tf.bool):
        if h > img_height or w > img_height:
            target_area = tf.random.uniform([], minval=sl, maxval=sh) * area
            aspect_ratio = tf.random.uniform([], minval=r1, maxval=1 / r1)
            h = tf.cast(tf.math.round(tf.math.sqrt(target_area * aspect_ratio)), tf.int32)
            w = tf.cast(tf.math.round(tf.math.sqrt(target_area / aspect_ratio)), tf.int32)
        else:
            break

    x1 = tf.cond(img_height == h, lambda: 0,
                 lambda: tf.random.uniform([], minval=0, maxval=img_height - h, dtype=tf.int32))
    y1 = tf.cond(img_width == w, lambda: 0,
                 lambda: tf.random.uniform([], minval=0, maxval=img_width - w, dtype=tf.int32))

    part1 = tf.slice(img, [0, 0, 0], [x1, img_width, img_channels])  # first row
    part2 = tf.slice(img, [x1, 0, 0], [h, y1, img_channels])  # second row 1

    if method == 'black':
        part3 = tf.zeros((h, w, img_channels), dtype=tf.float32)  # second row 2
    elif method == 'white':
        part3 = tf.ones((h, w, img_channels), dtype=tf.float32)
    elif method == 'random':
        part3 = tf.random.uniform((h, w, img_channels), dtype=tf.float32)
    else:
        raise print('Wrong method parameter')

    part4 = tf.slice(img, [x1, y1 + w, 0], [h, img_width - y1 - w, img_channels])  # second row 3
    part5 = tf.slice(img, [x1 + h, 0, 0], [img_height - x1 - h, img_width, img_channels])  # third row

    middle_row = tf.concat([part2, part3, part4], axis=1)
    img = tf.concat([part1, middle_row, part5], axis=0)

    return img, mask
