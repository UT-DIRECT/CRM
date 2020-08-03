import matplotlib.pyplot as plt

from src.config import INPUTS


def plot_helper(fig_dir, title='', xlabel='', ylabel='', legend=[], save=False):
    plt.title(title)
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.legend(legend)
    if save:
        fig_saver(fig_dir, title, xlabel, ylabel)
        plt.close()


def fig_saver(fig_dir, title, xlabel, ylabel):
    fig_file = "{}{}".format(
        fig_dir,
        fig_filename(title, xlabel, ylabel)
    )
    plt.savefig(fig_file)


def fig_filename(title, xlabel, ylabel):
    filename = ''
    if len(title) > 0:
        filename = '{}_{}_{}.png'.format(
            title,
            xlabel,
            ylabel
        ).lower().replace(' ', '_')
    else:
        filename = '{}_{}.png'.format(
            xlabel,
            ylabel
        ).lower().replace(' ', '_')
    return filename


def bar_plot_helper(width, x, x_labels, bar_labels, heights):
    plt.figure(figsize=[10, 4.8])
    center_x_location = int(len(heights) / 2)
    for i in range(len(heights)):
        if i == 0:
            alpha = 1
        else:
            alpha = 0.5
        plt.bar(x + (i - center_x_location) * width, heights[i], width, label=bar_labels[i], alpha=alpha)


def bar_plot_formater(fig_dir, x, x_labels, title, xlabel, ylabel):
    plot_helper(fig_dir, title=title, xlabel=xlabel, ylabel=ylabel)
    plt.yscale('log')
    plt.xticks(ticks=x, labels=x_labels)
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.tight_layout()
    fig_saver(fig_dir, title, xlabel, ylabel)
    plt.close()
