""" Plotting implementations for accessor to Pandas.DataFrame & multiple animated plots

Implementation of accessor to pass args and kwargs from accessor function to chart constructors.

Example:
    ``df.plot_animated()``
"""

import pandas as pd
from pandas.core.base import PandasObject
import typing
import matplotlib.pyplot as plt
from matplotlib.colors import Colormap
from matplotlib.animation import FuncAnimation
from .charts import (
    BarChartRace,
    BubbleChart,
    LineChart,
    ScatterChart,
    PieChart,
    BarChart,
)
from typing import Sequence
import datetime


def get_allowed_kinds() -> typing.List[str]:
    """ Get list of implemented charts

    Returns:
        typing.List[str]: List of implemented chart types
    """
    return ["race", "line", "scatter", "pie", "bar", "bubble"]


def verify_filename(filename: str) -> str:
    """ Check file name is accurate

    Args:
        filename (str): String for file name with extension

    Raises:
        ValueError: Provide filename with extensions
        ValueError: Specify a length > 0

    Returns:
        str: Verified file name
    """
    if len(filename) <= 0:
        raise ValueError("Specify filename")

    if (
        isinstance(filename, str)
        and "." not in filename
        or len(filename.split(".")[1]) <= 0
    ):
        raise ValueError("`filename` must be provided & have an extension")

    return filename


def plot(
    # Base constructor
    input_df: pd.DataFrame,
    filename: str = None,
    kind: str = "race",
    interpolate_period: bool = True,
    steps_per_period: int = 10,
    period_length: int = 500,
    period_fmt: str = "%d/%m/%Y",
    figsize: typing.Tuple[float, float] = (6.5, 3.5),
    title: str = None,
    fig: plt.figure = None,
    cmap: typing.Union[str, Colormap, typing.List[str]] = "dark24",
    tick_label_size: typing.Union[int, float] = 7,
    period_label: typing.Union[
        bool, typing.Dict[str, typing.Union[int, float, str]]
    ] = True,
    period_summary_func: typing.Callable = None,
    fixed_max: bool = False,
    dpi: float = 144,
    writer:str = None,
    enable_progress_bar: bool = False,
    # Bar chart
    orientation: str = "h",
    sort: str = "desc",
    label_bars: bool = True,
    bar_label_size: typing.Union[int, float] = 7,
    n_visible: int = None,
    fixed_order: typing.Union[bool, list] = False,
    perpendicular_bar_func: typing.Union[typing.Callable, str] = None,
    # Line Chart
    line_width: int = 2,
    label_events: typing.Dict[str, datetime.datetime] = None,
    fill_under_line_color: str = None,
    # Scatter Chart
    size: int = 2,
    # Bubble Chart
    x_data_label: str = None,
    y_data_label: str = None,
    size_data_label: typing.Union[int, str] = 2,
    color_data_label: str = "blue",
    **kwargs,
) -> typing.Union[ScatterChart, BarChartRace, LineChart, PieChart]:
    """
    Create animated charts with matplotlib and pandas

    Data must be in 'wide' format where each row represents a single time period and each 
    column represents a distinct category. Optionally, the index can label the time period.
    Bar height and location change linearly from one time period to the next.
    This is resource intensive - Start with just a few rows of data to test.

    Args:
        filename (str, optional): If a string, save animation to that filename location. Defaults to None.

        kind (str, optional): Type of chart to use. Defaults to "race".
            Supported kinds are: "race", "line", "scatter","pie","bar","bubble"

        interpolate_period (bool, optional): Whether to interpolate the period. Only valid for datetime or numeric indexes. Defaults to `True`.
            When set to `True`, for example, the two consecutive periods 2020-03-29 and 2020-03-30 would yield a new index of
                >>> df.plot_animated(interpolate_period=True,steps_per_period=4)
                    2020-03-29 00:00:00
                    2020-03-29 06:00:00
                    2020-03-29 12:00:00
                    2020-03-29 18:00:00
                    2020-03-30 00:00:00

        steps_per_period (int, optional): The number of steps to go from one time period to the next. Animation will interpolate between time periods. Defaults to 10.

        period_length (int, optional): Number of milliseconds to animate each period (row). Defaults to 500.

        period_fmt (str, optional):  Either a string with date directives or a new-style (Python 3.6+) formatted string.
            For a string with a date directive, find the complete list here https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

            String with date directives
            .. code-block::
                df.plot_animated(period_fmt='%B %d, %Y')
            Will change 2020/03/29 to March 29, 2020
        
            For new-style formatted string. Use curly braces and the variable `x`, 
            which will be passed the current period's index value.
            .. code-block::
                'Period {x:10.2f}'

            Date directives will only be used for datetime indexes. Defaults to "%d/%m/%Y".

        figsize (typing.Tuple[float, float], optional): matplotlib figure size in inches. Will be overridden if figure supplied to `fig`. Defaults to (6.5, 3.5).

        title (str, optional): Title of plot. Defaults to None.

        fig (plt.figure, optional): For greater control over the aesthetics, supply your own figure. Defaults to None.

        cmap (typing.Union[str, Colormap, typing.List[str]], optional): Provide string of colormap name, colormap instance, single color instance or list of colors as supported by https://matplotlib.org/2.0.2/api/colors_api.html. Defaults to "dark24".

        tick_label_size (typing.Union[int, float], optional): Size in points of tick labels. Defaults to 7.

        period_label (typing.Union[bool, typing.Dict[str, typing.Union[int, float, str]]], optional): If `True` or dict, use the index as a large text label on the axes whose value changes.
            Use a dictionary to supply the exact position of the period along with any valid parameters of the matplotlib `text` method.
            At a minimum, you must supply both 'x' and 'y' in axes coordinates
            .. code-block::
                custom_period_location = {
                    'x': .99,
                    'y': .8,
                    'ha': 'right',
                    'va': 'center'
                    }

                df.plot_animated(period_label=custom_period_location)
                
            If `False` - don't place label on axes. Defaults to True.

        period_summary_func (typing.Callable, optional):  Custom text added to the axes each period.
            Create a user-defined function that accepts two pandas Series of the current time period's values and ranks. It must return a dictionary containing at a minimum the keys "x", "y", and "s" which will be passed to the matplotlib `text` method. Defaults to None.
            .. code-block::
                def func(values):
                    total = values.sum()
                    s = f'Total Generation: {total}'
                    return {'x': .85, 'y': .2, 's': s, 'ha': 'right', 'size': 11}

                df.plot_animated(period_summary_func=func)

        dpi (float, optional): It is possible for some bars to be out of order momentarily during a transition since both height and location change linearly. Defaults to 144.

        writer (str, optional): Specify writer library, must be within list of available writers (`matplotlib.animation.writers.list()`) and `pillow` is not supported. Defaults to None.

        enable_progress_bar (bool,optional): Enable tqdm bar to show progress on generating animation, see more details at https://github.com/tqdm/tqdm. Defaults to False.

        sort (str, optional): 'asc' or 'desc'. Choose how to sort the bars. Use 'desc' to put largest bars on top and 'asc' to place largest bars on bottom. Defaults to "desc".

        label_bars (bool, optional): Whether to label the bars with their value on their right. Defaults to True.

        bar_label_size (typing.Union[int, float], optional): Size in points or relative size str of numeric labels just outside of the bars. Defaults to 7.

        n_visible (int, optional): Choose the maximum number of bars to display on the graph. By default, use all bars. New bars entering the race will appear from the edge of the axes. Defaults to None.

        fixed_order (typing.Union[bool, list], optional): When `False`, bar order changes every time period to correspond 
            with `sort`. When `True`, bars remained fixed according to their 
            final value corresponding with `sort`. Otherwise, provide a list 
            of the exact order of the categories for the entire duration. Defaults to False.

        fixed_max (bool, optional): Whether to fix the maximum value of the axis containing the values.
            When `False`, the axis for the values will have its maximum (xlim/ylim)
            just after the largest bar of the current time period. 
            The axis maximum will change along with the data.
            When True, the maximum axis value will remain constant for the 
            duration of the animation. For example, in a horizontal bar chart, 
            if the largest bar has a value of 100 for the first time period and 
            10,000 for the last time period. The xlim maximum will be 10,000 
            for each frame. Defaults to False.

        perpendicular_bar_func (typing.Union[typing.Callable, str], optional): Creates a single bar perpendicular to the main bars that spans the length of the axis. 
    
            Use either a string that the DataFrame `agg` method understands or a 
            user-defined function.
                
            DataFrame strings - 'mean', 'median', 'max', 'min', etc..

            The function is passed two pandas Series of the current time period's
            data and ranks. It must return a single value.
            .. code-block::
                def func(values):
                    return values.quantile(.75).
            
            Defaults to None.

        line_width (int, optional): Line width provided on line charts. Defaults to 2.

        label_events (typing.Dict[str,datetime.datetime],optional): Provide list of events to label with a vertical bar on line charts. Defaults to None.

            To be used with strptime or any datetime object

            Sample use:
            .. code-block::
                df.plot_animated(
                        kind='line',
                        filename='test.mp4',
                        label_events={
                            'Ruby Princess Disembark':datetime.strptime("19/03/2020", "%d/%m/%Y"),
                            'Lockdown':datetime.strptime("31/03/2020", "%d/%m/%Y")
                        },
                    )
        
        fill_under_line_color (str,optional): Color to show under line to create an area chart equivalent

            String passed must be in list of named colors by matplotlib https://matplotlib.org/3.1.1/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py
    
        size (int, optional): Size of scatter points on scatter charts. Defaults to 2.

        x_data_label (str,optional): For use with Scatter plots, label passed must be in level 0 column in multiindex

            Label passed all values will be used for the x-axis

        y_data_label (str,optional): For use with Scatter plots, label passed must be in level 0 column in multiindex

            Label passed all values will be used for the y-axis

        size_data_label (typing.Union[int,str],optional): For use with Scatter plots, label passed must be in level 0 column in multiindex. Defaults to 2.

            Label passed all values will be used for the size of each point on the plot.
            Otherwise a int can be passed for all points to be that size.

        color_data_label (str,optional): For use with Scatter plots, label passed must be in level 0 column in multiindex. Defaults. to "blue".

            Label passed all values will be used to create a colourmap for points.
            Otherwise a string can be passed of a named color by matplotlib for all points to be that color.
            
    Raises:
        ValueError: If chart type is not supported, raise error

    Returns:
        typing.Union[ScatterChart, BarChart, LineChart]: Return instance of chart type. Can be used with `pandas_alive.animate_multiple_plots` or `.save()`.
    """
    df = input_df.copy()
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    allowed_kinds = get_allowed_kinds()

    if kind not in allowed_kinds:
        allowed_kinds = "', '".join(allowed_kinds)
        raise ValueError("Allowed plot kinds are '%s'." % allowed_kinds)

    if kind == "race":
        bcr = BarChartRace(
            df,
            interpolate_period=interpolate_period,
            steps_per_period=steps_per_period,
            period_length=period_length,
            period_fmt=period_fmt,
            figsize=figsize,
            title=title,
            fig=fig,
            cmap=cmap,
            tick_label_size=tick_label_size,
            period_label=period_label,
            period_summary_func=period_summary_func,
            fixed_max=fixed_max,
            dpi=dpi,
            writer=writer,
            enable_progress_bar=enable_progress_bar,
            # Bar chart
            orientation=orientation,
            sort=sort,
            label_bars=label_bars,
            bar_label_size=bar_label_size,
            n_visible=n_visible,
            fixed_order=fixed_order,
            perpendicular_bar_func=perpendicular_bar_func,
            kwargs=kwargs,
        )
        if filename:
            bcr.save(verify_filename(filename))
        return bcr

    elif kind == "line":
        line_race = LineChart(
            df,
            interpolate_period=interpolate_period,
            steps_per_period=steps_per_period,
            period_length=period_length,
            period_fmt=period_fmt,
            figsize=figsize,
            title=title,
            fig=fig,
            cmap=cmap,
            tick_label_size=tick_label_size,
            period_label=period_label,
            period_summary_func=period_summary_func,
            fixed_max=fixed_max,
            dpi=dpi,
            writer=writer,
            enable_progress_bar=enable_progress_bar,
            line_width=line_width,
            label_events=label_events,
            fill_under_line_color=fill_under_line_color,
            kwargs=kwargs,
        )
        if filename:
            line_race.save(verify_filename(filename))
        return line_race
    elif kind == "scatter":
        animated_scatter = ScatterChart(
            df,
            interpolate_period=interpolate_period,
            steps_per_period=steps_per_period,
            period_length=period_length,
            period_fmt=period_fmt,
            figsize=figsize,
            title=title,
            fig=fig,
            cmap=cmap,
            tick_label_size=tick_label_size,
            period_label=period_label,
            period_summary_func=period_summary_func,
            fixed_max=fixed_max,
            dpi=dpi,
            writer=writer,
            enable_progress_bar=enable_progress_bar,
            size=size,
            kwargs=kwargs,
        )
        if filename:
            animated_scatter.save(verify_filename(filename))
        return animated_scatter
    elif kind == "pie":
        animated_pie = PieChart(
            df,
            interpolate_period=interpolate_period,
            steps_per_period=steps_per_period,
            period_length=period_length,
            period_fmt=period_fmt,
            figsize=figsize,
            title=title,
            fig=fig,
            cmap=cmap,
            tick_label_size=tick_label_size,
            period_label=period_label,
            period_summary_func=period_summary_func,
            fixed_max=fixed_max,
            dpi=dpi,
            writer=writer,
            enable_progress_bar=enable_progress_bar,
            kwargs=kwargs,
        )
        if filename:
            animated_pie.save(verify_filename(filename))
        return animated_pie
    elif kind == "bar":
        animated_bar = BarChart(
            df,
            interpolate_period=interpolate_period,
            steps_per_period=steps_per_period,
            period_length=period_length,
            period_fmt=period_fmt,
            figsize=figsize,
            title=title,
            fig=fig,
            cmap=cmap,
            tick_label_size=tick_label_size,
            period_label=period_label,
            period_summary_func=period_summary_func,
            fixed_max=fixed_max,
            dpi=dpi,
            writer=writer,
            enable_progress_bar=enable_progress_bar,
            kwargs=kwargs,
        )
        if filename:
            animated_bar.save(verify_filename(filename))
        return animated_bar
    elif kind == "bubble":
        animated_bubble = BubbleChart(
            df,
            interpolate_period=interpolate_period,
            steps_per_period=steps_per_period,
            period_length=period_length,
            period_fmt=period_fmt,
            figsize=figsize,
            title=title,
            fig=fig,
            cmap=cmap,
            tick_label_size=tick_label_size,
            period_label=period_label,
            period_summary_func=period_summary_func,
            fixed_max=fixed_max,
            dpi=dpi,
            writer=writer,
            enable_progress_bar=enable_progress_bar,
            x_data_label=x_data_label,
            y_data_label=y_data_label,
            size_data_label=size_data_label,
            color_data_label=color_data_label,
            kwargs=kwargs,
        )
        if filename:
            animated_bubble.save(verify_filename(filename))
        return animated_bubble


def animate_multiple_plots(
    filename: str,
    plots: typing.List[typing.Union[BarChartRace, LineChart, PieChart, ScatterChart]],
    title: str = None,
    title_fontsize: typing.Union[int, float] = 16,
    dpi: int = 144,
    adjust_subplot_left: float = 0.15,
    adjust_subplot_right: float = 0.9,
    adjust_subplot_bottom: float = 0.1,
    adjust_subplot_top: float = 0.9,
    adjust_subplot_wspace: float = 0.2,
    adjust_subplot_hspace: float = 0.25,
):
    """ Plot multiple animated subplots with plt.subplots()

    Args:
        filename (str): Output file name with extension to rite to
        plots (typing.List[typing.Union[BarChart, LineChart]]): List of chart instances
        title (str, optional): Overall title for plots (suptitle). Defaults to None.
        title_fontsize (typing.Union[int, float], optional): Font size for suptitle. Defaults to 16.
        dpi (int, optional): Custom DPI to increase resolution. Defaults to 144.
        adjust_subplot_left (float, optional): the left side of the subplots of the figure. Defaults to 0.125.
        adjust_subplot_right (float, optional): the right side of the subplots of the figure. Defaults to 0.9.
        adjust_subplot_bottom (float, optional): the bottom of the subplots of the figure. Defaults to 0.1.
        adjust_subplot_top (float, optional): the top of the subplots of the figure. Defaults to 0.9.
        adjust_subplot_wspace (float, optional): the amount of width reserved for space between subplots, expressed as a fraction of the average axis width. Defaults to 0.2.
        adjust_subplot_hspace (float, optional): the amount of height reserved for space between subplots, expressed as a fraction of the average axis height. Defaults to 0.2.

    Raises:
        UserWarning: If Error found when plotting, prompt user to ensure indexs of plots are same length
    """

    def update_all_graphs(frame: int):
        """
        Function for updating all plots provided as a list via their respective `anim_func` method

        Args:
            frame (int): Frame to animate

        Raises:
            UserWarning: DataFrames apart of plots must have same length of index
        """
        for plot in plots:
            try:
                plot.anim_func(frame)
            except:
                raise UserWarning(
                    f"Ensure all plots share index length {[plot.get_frames() for plot in plots]}"
                )

    # Current just number of columns for number of plots
    # TODO add option for number of rows/columns
    # TODO Use gridspec?

    # Otherwise titles overlap and adjust_subplot does nothing
    from matplotlib import rcParams

    rcParams.update({"figure.autolayout": False})
    fig, axes = plt.subplots(len(plots))
    # fig, axes = plt.subplots(2,2)

    if title is not None:
        fig.suptitle(title)
    # fig.set_tight_layout(True)
    # Defaults from https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.subplots_adjust.html
    fig.subplots_adjust(
        left=adjust_subplot_left,
        right=adjust_subplot_right,
        bottom=adjust_subplot_bottom,
        top=adjust_subplot_top,
        wspace=adjust_subplot_wspace,
        hspace=adjust_subplot_hspace,
    )

    # fig = plt.figure()
    # spec = fig.add_gridspec()
    # fig.add_subplot(spec[0, 1])
    # Used for overlapping titles, supplot not considered so move down by 10%
    # https://stackoverflow.com/questions/8248467/matplotlib-tight-layout-doesnt-take-into-account-figure-suptitle
    # fig.tight_layout(rect=[0, 0, 1, 0.9])
    # fig.constrained_layout()
    # plt.rcParams["figure.constrained_layout.use"] = True
    # plt.subplots_adjust(top=0.85)
    # plt.subplots_adjust()
    # plt.rcParams.update({'figure.autolayout': True})

    for num, plot in enumerate(plots):
        axes[num] = plot.apply_style(axes[num])
        # plot.set_x_y_limits(plot.df,1,axes[num])
        if plot.fixed_max:
            # Hodgepodge way of fixing this, should refactor to contain all figures and axes
            # TODO plot.axes_format(self,ax) and pass current ax or desired ax
            if plot.__class__.__name__ == "BarChartRace" and plot.orientation == "h":
                axes[num].set_xlim(axes[num].get_xlim()[0], plot.df.values.max() * 1.1)
            elif plot.__class__.__name__ == "BarChartRace" and plot.orientation == "v":
                axes[num].set_ylim(axes[num].get_ylim()[0], plot.df.values.max() * 1.1)

        axes[num].set_title(plot.title)
        plot.ax = axes[num]

        plot.init_func()

    # fig.tight_layout()

    fps = 1000 / plots[0].period_length * plots[0].steps_per_period
    interval = plots[0].period_length / plots[0].steps_per_period
    anim = FuncAnimation(
        fig,
        update_all_graphs,
        min([max(plot.get_frames()) for plot in plots]),
        interval=interval,
    )

    extension = filename.split(".")[-1]
    # anim.save(filename, fps=fps, dpi=dpi, writer=plots[0].writer)
    if extension == "gif":
        anim.save(filename, fps=fps, dpi=dpi, writer="imagemagick")
    else:
        anim.save(filename, fps=fps, dpi=dpi)


##############################################################################
########### Class to add Animated plotting methods to Pandas DataFrame
##############################################################################
# Inspiration: https://github.com/PatrikHlobil/Pandas-Bokeh/blob/cb241ea570a0a2ea3d0c7055fbe79bbdd06cc712/pandas_bokeh/plot.py#L1759


class BasePlotMethods(PandasObject):
    """ For extending accessor to pandas DataFrame

    Args:
        PandasObject (PandasObject): Base Pandas Object
    """

    def __init__(self, data: typing.Union[pd.Series, pd.DataFrame]):
        """
        Initialise BasePlotMethods with parent data as either Series or DataFrame

        Args:
            data (typing.Union[pd.Series,pd.DataFrame]): Will take _parent attribute from DataFrame/Series
        """
        self._parent = data  # can be Series or DataFrame

    def __call__(self, *args, **kwargs):
        """
        If accessor hasn't been initialised raise error

        Raises:
            NotImplementedError: Error if accessor function has not been overridden
        """
        raise NotImplementedError


class AnimatedAccessor(BasePlotMethods):
    """ For including accessor on df, to enable `df.plot_animated()`

    Args:
        BasePlotMethods ([type]): BasePlotMethods within pandas
    """

    def __call__(self, *args, **kwargs):
        """
        Must be overriden to enable funcctionality
        
        Calls :func: pandas_alive.plotting.plot and returns instance of constructed chart
        """
        return plot(self.df, *args, **kwargs)

    @property
    def df(self) -> typing.Union[pd.Series, pd.DataFrame]:
        """
        Contains _parent DataFrame

        Returns:
            typing.Union[pd.Series,pd.DataFrame]: Parent DataFrame/Series
        """

        return self._parent

    def barh(self, x: str = None, y: str = None, **kwds):
        """ Make an animated horizontal bar plot.

        Args:
            x (str, optional): label or position. Defaults to DataFrame.index. Column to be used on categories.
            y (str, optional): label or position. Defaults to All numeric columns in DataFrame. Column to be plotted from the DataFrame

        Returns:
            BarChart: BarChart instance for use with multiple plots or .save()
        """

        return self(kind="barh", x=x, y=y, **kwds)
