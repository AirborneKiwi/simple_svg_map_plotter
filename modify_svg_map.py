"""
This script can plot numeric data from a simple csv table into an existing svg-file.
It used the headers of the csv file and will look for a path in the svg-file with a matching id.
Afterwards it uses the data value to set the fill color of the path corresponding to a chosen colormap.
The chosen colorbar is then simply made visible within the svg-file. Therefore, it has to be part of the svg-file already.

Each row in the data will be saved to a separate modified svg-file.

Arguments:
    -h
        Display this help message^^

    -s <svgfile>, --svgfile <svgfile>
        Default "EMN.svg". The filename of the svg-file that shall be used as a template.

    -d <datafile>, --datafile <datafile>
        Default "ExampleData.csv". The filename of the data file that shall be plotted.

    -a <yourtitle>, --axistitle <yourtitle>
        Default "Please add a title to the colorbar!". The title for the colorbar.

    --cmap <yourcmap>
        Default "RdYlGn". The seaborn colormap of your choice.
        Within the svg-file EMN.svg, there are the following colormaps included:
            - RdYlGn
            - crest
            - coolwarm
            - Spectral
            - icefire
            - vlag
            - Blues
            - YlOrBr
            - seagreen
            - flare

    --reversed
        Default False. If set to True, the colormap will be reversed.
"""

#!/usr/bin/python
import sys
import getopt

import pandas as pd
import numpy as np
import regex as re
from bs4 import BeautifulSoup
import seaborn as sns

def modify_svg_map(svg_filename: str, df: pd.DataFrame, colorbar_title: str, cmap: str = 'RdYlGn', reverse: bool = False, suffix:str ='') -> None:
    with open(svg_filename, 'r') as f:
        data = f.read()

    # Passing the stored data inside the beautifulsoup parser, storing the returned object
    Bs_data = BeautifulSoup(data, "xml")


    # Calculate the limits of the data and normalize the data to 0 to 1
    mins = df.min().min()
    maxs = df.max().max()
    df_norm = df.subtract(mins, axis=0).div(maxs - mins, axis=0)

    # Look for the colorbar and make it visible
    if reverse:
        colorbar = Bs_data.find('image', {'id': f'{cmap}_reversed'})
    else:
        colorbar = Bs_data.find('image', {'id': cmap})

    style = colorbar.get('style')
    result = re.search(r'(.*display:)none(;.*)', style)
    if result is None:
        if re.match(r'.*display:inline;.*', style) is not None:
            # Already visible->Nothing to do
            pass
    else:
        new_style = f'{result.group(1)}inline{result.group(2)}'
        colorbar['style'] = new_style

    # Scale the colorbar
    for i, v in zip(range(11), np.linspace(mins, maxs, num=11)):
        T_ytick = Bs_data.find('text', {'id': f'T_ytick_{i}'})
        T_ytick['contents'] = f'{v:.1f}'
        T_ytick.string = f'{v:.1f}'

    # Set the colorbar title
    T_colorbar_title = Bs_data.find('text', {'id': 'colorbar_title'})
    T_colorbar_title['contents'] = colorbar_title
    T_colorbar_title.string = colorbar_title

    # get the seaborn color palette
    palette = sns.color_palette(cmap, as_cmap=True)
    if reverse:
        palette = palette.reversed()

    def get_color_as_hex(color):
        return f'#{int(color[0] * 255 + 0.5):02x}{int(color[1] * 255 + 0.5):02x}{int(color[2] * 255 + 0.5):02x}'

    def f(v):
        return get_color_as_hex(palette(v))

    # replace all data values with their corresponding color
    df_colors = df_norm.applymap(f)

    for index, row in df_colors.iterrows():  # iterate over all rows and plot them to individual svg-files
        for id in row.index:  # iterate over all data headers
            # find the svg-path that fits the data header
            data_id = id.replace('ü', 'ue').replace(' ', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ß', 'ss')
            path = Bs_data.find('path', {'id': data_id})

            if path is None:
                path = Bs_data.find('path', {'inkscape:label': data_id})

            if path is None:
                raise Exception(f'The column "{data_id}" could not be found as an id in the svg')

            # replace the fill color with the new value
            style = path.get('style')
            result = re.search(r'(.*fill:)#[a-z0-9]+(;.*)', style)
            new_fill_color = row[id]
            new_style = f'{result.group(1)}{new_fill_color}{result.group(2)}'
            path['style'] = new_style

        # Save the modified svg file
        new_svg_filename = svg_filename[:svg_filename.rfind('.')] + suffix

        print(f'Saving row {index} to {new_svg_filename}.{index}.svg')
        with open(f'{new_svg_filename}.{index}.svg', 'w') as f:
            s = Bs_data.prettify()
            # remove the added whitespaces within the text elements
            s = re.sub(r'(<svg:text .*)[\n\r]\s*(.*)[\n\r]\s*(<\/svg:text>)', '\\1\\2\\3', s)
            f.write(s)


def main(argv):
    data_filename = 'ExampleData.csv'
    svg_filename = 'EMN.svg'
    axistitle = 'Please add a title to the colorbar!'
    cmap = 'RdYlGn'
    reverse = False

    try:
        opts, args = getopt.getopt(argv, '"hs:d:a:', ['svgfile=', 'datafile=', 'axistitle=', 'cmap=', 'reverse'])
    except getopt.GetoptError:
        print(__doc__)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(__doc__)
            sys.exit()
        elif opt in ("-s", "--svgfile"):
            svg_filename = arg
        elif opt in ("-d", "--datafile"):
            data_filename = arg
        elif opt in ("-a", "--axistitle"):
            axistitle = arg
        elif opt in ("--cmap"):
            cmap = arg
        elif opt in ("--reverse"):
            reverse = arg

    print(f'The svg-file is {svg_filename}')
    print(f'The data file is {data_filename}')
    print(f'The axis title is {axistitle}')
    print(f'The colormap is {cmap}{" reversed" if reverse else ""}')

    df = pd.read_csv(data_filename)
    print('The following data has been read:')
    print(df)

    print('\nModifying passed svg file with the data from the csv file and saving each line to an individual svg-file')
    modify_svg_map(svg_filename, df, colorbar_title=axistitle, cmap=cmap, reverse=reverse, suffix='_' + data_filename[:data_filename.rfind('.')])
    print('All saved.')


if __name__ == '__main__':
    main(sys.argv[1:])
