import matplotlib.pyplot as plt

from .. import config


INPUTS = config.INPUTS
FIG_DIR = INPUTS['files']['figures_dir']


def plot_helper(title='', xlabel='', ylabel='', legend=[], save=False):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(legend)
    if save:
        fig_saver(title, xlabel, ylabel)
        plt.close()


def fig_saver(title, xlabel, ylabel):
    fig_file = "{}{}".format(
        FIG_DIR,
        fig_filename(title, xlabel, ylabel)
    )
    plt.savefig(fig_file)


def fig_filename(title, xlabel, ylabel):
    return "{}_{}_{}.png".format(
        title,
        xlabel,
        ylabel
    ).lower().replace(' ', '_')


def bar_plot_helper(width, x, x_labels, bar_labels, heights):
    plt.figure(figsize=[10, 4.8])
    center_x_location = int(len(heights) / 2)
    for i in range(len(heights)):
        plt.bar(x + (i - center_x_location) * width, heights[i], width, label=bar_labels[i])


def bar_plot_formater(x, x_labels, title, xlabel, ylabel):
    plot_helper(title=title, xlabel=xlabel, ylabel=ylabel)
    plt.yscale('log')
    plt.xticks(ticks=x, labels=x_labels)
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.tight_layout()
    fig_saver(title, xlabel, ylabel)
    plt.close()
