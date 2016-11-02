import sys
import math

from bokeh.charts import Bar, output_file, save
from bokeh.charts.attributes import CatAttr

if __name__ == '__main__':
    title, xlabel, ylabel, data_in, data_out = sys.argv[1:]

    with open(data_in, 'r') as f:
        lines = f.readlines()

    if lines[0].startswith("#"):
        xlabel, ylabel = [l.strip() for l in lines[0][1:].split(",")]
    else:
        xlabel, ylabel = "", ""

    rows = [line.split(",") for line in lines if not line.startswith("#")]
    data = [(label, float(value)) for label, value in rows if value.strip()]

    dataset = {
        'labels': [d[0] for d in data],
        'values': [d[1] for d in data]
    }

    bar = Bar(
        dataset,
        values='values',
        title=title.title(),
        label=CatAttr(columns=['labels'], sort=False),
        xlabel=xlabel,
        ylabel=ylabel,
        xgrid=False,
        ygrid=False,
        legend=None,
        tools=['save'],
        plot_width=3,
        plot_height=2,
        responsive=True
    )

    bar.xaxis.major_label_orientation = math.pi/2

    output_file(data_out)
    save(bar)
