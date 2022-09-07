# simple_svg_map_plotter

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
