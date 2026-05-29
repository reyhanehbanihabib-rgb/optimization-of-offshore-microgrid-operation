"""Small plotting helpers used by the optimization notebooks."""

import matplotlib.pyplot as plt


def simple_plotter(
    x,
    y_series,
    display_legend=None,
    x_label=None,
    y_label=None,
    plot_title=None,
    shape=None,
    x_lim=None,
    y_lim=None,
    x_show=None,
    y_show=None,
    y_lines=None,
    scatter=False,
    dashed=None,
    **_,
):
    """Plot one or more series with the permissive API used in legacy notebooks."""
    fig, ax = plt.subplots(figsize=shape or (8, 4))
    dashed = set(dashed or [])

    for index, y_values in enumerate(y_series):
        style = "--" if index in dashed else "-"
        label = None
        if display_legend and index < len(display_legend):
            label = display_legend[index]
        if scatter:
            ax.scatter(x, y_values, label=label)
        else:
            ax.plot(x, y_values, style, label=label)

    if y_lines is not None:
        for value in y_lines:
            ax.axhline(value, color="0.5", linewidth=0.8, linestyle=":")

    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if plot_title:
        ax.set_title(plot_title)
    if x_lim is not None:
        ax.set_xlim(x_lim)
    if y_lim is not None:
        ax.set_ylim(y_lim)
    if x_show is not None:
        ax.set_xticks(x_show)
    if y_show is not None:
        ax.set_yticks(y_show)
    if display_legend:
        ax.legend()

    fig.tight_layout()
    return fig, ax
