import os
import io
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def make_goods_image(goods_images_path, idxs, synset):
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

    elif len(idxs) > 2:
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
                  f'Номер полки: {str(synset.iloc[id]["Номер полки"])} \n',
            loc='left', fontdict={'fontsize': title_size})
        plt.xticks([])
        plt.yticks([])

        buf = io.BytesIO()
        plt.imshow(image_list[index])

    fig.savefig(buf, format='jpg')
    buf.seek(0)

    return buf.read()
