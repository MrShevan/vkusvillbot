import os
import io
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from PIL import Image
from barcode.writer import ImageWriter
from barcode import generate


def make_image(goods_images_path, idxs, synset, shelve_name):
    """ Max - 12 images """
    image_list = []

    for idx in idxs:
        image_path = os.path.join(goods_images_path, synset.iloc[idx].path)
        try:
            image = mpimg.imread(image_path)
        except:
            image = mpimg.imread('/app/vkusvillbot/data/default.jpg')

        image_list.append(image)

    # Plot Fig Settings
    if len(idxs) > 8:
        title_size = 28
        fig_size = (20, 60)
        plot_grid = (6, 2)

    elif len(idxs) > 4:
        title_size = 24
        fig_size = (20, 40)
        plot_grid = (4, 2)

    elif len(idxs) > 2:
        title_size = 20
        fig_size = (20, 20)
        plot_grid = (2, 2)

    elif len(idxs) > 1:
        title_size = 20
        fig_size = (10, 18)
        plot_grid = (2, 1)

    else:
        title_size = 20
        fig_size = (10, 10)
        plot_grid = (1, 1)

    fig = plt.figure(figsize=fig_size)

    for index, id in enumerate(idxs):
        ax = fig.add_subplot(*plot_grid, index + 1)
        ax.set_title(
            label=f'{synset.iloc[id]["Товар"]} \n' +
                  f'Вид: {synset.iloc[id]["РодительскяГруппаТоваров"]} \n' +
                  f'Штрихкод: {str(synset.iloc[id]["Штрихкод"])} \n' +
                  f'Номер полки: {str(synset.iloc[id][shelve_name])} \n',
            loc='left', fontdict={'fontsize': title_size})
        plt.xticks([])
        plt.yticks([])

        buf = io.BytesIO()
        plt.imshow(image_list[index])

    fig.savefig(buf, format='jpg')
    buf.seek(0)

    return buf.read()


def make_image_barcode(goods_images_path, idxs, synset, shelve_name):
    """ Max - 6 images """
    image_list = []

    for idx in idxs:
        image_path = os.path.join(goods_images_path, synset.iloc[idx].path)
        try:
            image = mpimg.imread(image_path)
        except:
            image = mpimg.imread('/app/vkusvillbot/data/default.jpg')

        image_list.append(image)

    # Plot Fig Settings
    if len(idxs) > 4:
        title_size = 22
        fig_size = (20, 60)
        plot_grid = (6, 2)

    elif len(idxs) > 2:
        title_size = 24
        fig_size = (20, 40)
        plot_grid = (4, 2)

    elif len(idxs) == 2:
        title_size = 20
        fig_size = (20, 20)
        plot_grid = (2, 2)

    else:
        title_size = 20
        fig_size = (20, 20)
        plot_grid = (1, 2)

    fig = plt.figure(figsize=fig_size)

    buf = io.BytesIO()

    for index, id in enumerate(idxs):
        # Описане с картинкой слева
        ax = fig.add_subplot(*plot_grid, 2 * index + 1)
        ax.set_title(
            label=f'{synset.iloc[id]["Товар"]} \n' +
                  f'Вид: {synset.iloc[id]["РодительскяГруппаТоваров"]} \n' +
                  f'Группа товаров: {str(synset.iloc[id]["ГруппаТоваров"])} \n' +
                  f'Номер полки: {str(synset.iloc[id][shelve_name])} \n',
            loc='left', fontdict={'fontsize': title_size})
        plt.xticks([])
        plt.yticks([])
        plt.imshow(image_list[index])

        # Штрихкод справа
        ax = fig.add_subplot(*plot_grid, 2 * index + 2)
        barcode = str(synset.iloc[id]["Штрихкод"])

        fp = io.BytesIO()
        if len(barcode) == 13:
            generate('EAN13', barcode, writer=ImageWriter(), output=fp)

        elif len(barcode) == 7:
            generate('EAN8', barcode, writer=ImageWriter(), output=fp)

        else:
            raise Exception('Barcode len 7 or 13')

        barcode_image = np.array(Image.open(fp))

        plt.xticks([])
        plt.yticks([])
        plt.imshow(barcode_image)

    fig.savefig(buf, format='jpg')
    buf.seek(0)

    return buf.read()
