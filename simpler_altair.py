

# https://altair-viz.github.io/user_guide/data.html
# DataFrames go into alt.Chart(df) but if we want .index we have to reset_index()
# and refer to it by the index's name (or `index`)
# x='counts:Q' will plot counts on x axis as a Quantitative
# https://altair-viz.github.io/user_guide/encoding.html#encoding-data-types
# Temporal, Ordinal, Nominal (discrete unordered category), Geojson
# Chart(df).mark_point for points, .mark_bar for bars
# https://altair-viz.github.io/user_guide/encoding.html#encoding-channels
# attributes include x, y, x2, y2, xError, latitude

# Note Pandas plotting not very useful
#import altair as alt
#pd.set_option('plotting.backend', 'altair') 

# Example:
#alt.Chart(cars).mark_point().encode(
#    x='Horsepower', # assumes :Q
#    y='Miles_per_Gallon', # assumed :Q
#    color='Origin',
#    shape='Origin')

# reset index, turn int counts into comma-separated values
#df_to_plot = df_seconds.reset_index().assign(nrows=[f'{v:,}' for v in df_seconds.index])
#alt.Chart(df_to_plot).mark_bar().encode(
# nrows has a new sort so specify the order seen in df_to_plot
#    x=alt.X('nrows', sort=df_to_plot.nrows.values),
# apply log scaling to y axis
#    y= alt.Y('seconds', scale= alt.Scale(type= 'log')),
#).properties(
#    title='Parquet read times by row-count',
#    width=200,
#    height=200
#)