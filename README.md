# notes_to_self

# Projects

## Research

### Getting into a new project

* What's the biggest uncertainty ahead? What does it cost to solve it, what value does it bring?
* What single thing might give us 80% of the remaining answer? Probably avoid the edge cases (document, but don't focus on them)

## Strategy

* prefer who/what/why/where/when objective questions
* focus on understanding the levers for highest value delivery, check for shared agreement on these (ignore low-value stuff that's cool but won't enable beneficial change)

# Python

## Wants

* Pandas better describe - colour the percentiles, not the counts/mean/std, include 5/95% in percentiles. Add dtype description and maybe memory, not how many columns were ignored too (stick on the end maybe?)

## Pandas

### `groupby`

`gpby = df.groupby` generates a `groupby.generic.DataFrameGroupBy`. This has a `__len__`, `gpby.groups` shows the a dict of keys for the groups and the indices that match the rows.

`for group in gpby:` generates a tuple of `(name, subset_dataframe)`, the `subset_dataframe` has all the columns including the group keys. `.groups` generates this entire list of groups as a dict, index into it using e.g. `gpby.groups[('-', '-', 'Canada')]` to retrieve the indices (and use `df.loc[indices]`) to fetch the rows.  `gpby.get_group(('-',  '-',  'Canada'))` takes the keys and returns a `DataFrame` without the keys.

`gpby.transform` works on `Series` or `DataFrame` and returns a `Series` (?) that matches each input row pre-grouping. `gpby.apply` returns a result based on the grouped items.

`gpby` calls such as `mean` are delegated.

`groupby` on a timeseries (e.g. day index) won't care about missing items (e.g. missing days), using `resample` for date times with a `fillna` is probably more sensible.

Categoricals have a non-obvious memory behaviour in 1.0 in `groupby`, must pass in `observed=True` on the `groupby` else it stalls and eats a lot of RAM: https://github.com/pandas-dev/pandas/issues/30552 It builds the cartesian product of all possible categorical groups with the default arguments which might take some time and RAM.

### `crosstab`

`normalize` can take `"index"`/`0` (note not `"rows"`), `"columns"`/`1` or `"all"`/`True`, default is `False`.

### `pd.to_datetime`

`utc=True` will set timezone (else no tz info). Lowest valid date we can parse is circa `pd.to_datetime('1677-09-22', utc=True)` (21st will raise a `OutOfBoundsDatetime` unless `errors="ignore"` passed, if this is passed then we get a string back in place!) - limitations: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timestamp-limitations . Error handling: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#invalid-data

### `merge`

Merging is the underlying operation, `df.join` is a shortcut into `merge`.  `join` merges keys on the left with the index on the right, it doesn't change the resulting index. Prefer `merge` to stay explicit.

`indicator=True` adds `_merge` column with indicators like `both`. `validate='many_to_one'` validates uniqueness on the right (or left or both), raising `MergeError` if not validated.

### `concatenate`

Has lots of options including to drop the index, `axis=1` for columnar concatenation and more.

### `reindex`

Apply a new index e.g. a series of ints to a non-contiguous existing `index`, `fill_na` defaults to `NaN`.

### `value_counts`

Probably add `dropna=False` every time (IMHO this should be the default).

### `info`

`df.info(memory_usage="deep")` introspects each column and counts bytes used including strings - but this can be slow on many strings (e.g. millions of rows of strings might take 1 minute).

### `describe`

* `ser.describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99, 1])` add more percentiles.
* `df.describe().style.background_gradient(axis=0)`

### `read_csv`

`pd.read_csv(parse_dates=True)` will only parse index dates, instead use `parse_dates=['col1', 'col2']` to parse other cols.

### display options

`pd.get_option('display.max_columns')` probably 20 and `max_rows` is 60. Use `pd.set_option('display.max_columns', 100)` for more cols in e.g. `.head()`. `pd.set_option('precision', 4)`. https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html#frequently-used-options

### Data processing tips

`query` with `NaN` rows is a pain, for text columns we could replace missing data with `-` and then that's another string-like thing for a query, this significantly simplifies the queries.

## matplotlib

### `subplot`

`fig, ax = plt.subplots()`

### Pandas `plot`

Marks with x and no lines: `.plot(marker='x', linestyle=' ', ax=ax)`


### subplots

* `fig, axs = plt.subplots(ncols=2, figsize=(8, 6))`

### axis labels

```
import matplotlib as mpl
def set_commas(ax, on_x_axis=True):
    """Add commas to e.g. 1,000,000 on axis labels"""
    axis = ax.get_xaxis()
    if not on_x_axis:
        axis = ax.get_yaxis()
    axis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
```

## Argument parsing

### `argparse`

```
parser = argparse.ArgumentParser(description=__doc__) # read __doc__ attribute
parser.add_argument('-i', '--input_filename', type=str, nargs="?",
                    help='csv from someone'
                    ' (default: %(default)s))', # help msg 2 over lines with default
                    default=input_filename) # some default
parser.add_argument('-v', '--version', action="store_true",
                    help="show version")

args = parser.parse_args()
print("Arguments provided:", args)
if args.version:
    print(f"Version: {__version__}")
```

When argument parsing it might make sense to check for the presence of specified files and to `sys.exit(1)` with a message if they're missing. `argparse` can also stream `stdin` in place of named files for piped input.

## Testing

### `unittest`

`python -m unittest` runs all tests with autodiscovery, `python -m unittest mymodule.MyClass` finds `mymodule.py` and runs the tests in `MyClass`.

There are some visual diffs but they're not brilliant. I don't think we can invoke `pdb` on failures without writing code?

### `pytest`

More mature than `unittest`, doesn't need the `unittest` methods for checking same/different code and catching expected exceptions is neater. Also has plugins, syntax colouring.

Typically we'd write `pytest` to execute it, there's something weird with being unable to find imported modules if `__init__.py` is (or maybe isn't) present, in which case `python -m pytest` does the job: https://stackoverflow.com/questions/41748464/pytest-cannot-import-module-while-python-can

`pytest --pdb` drops into the debugger on a failure. 

### `coverage`

`$ coverage run -m unittest test_all.py` (or e.g. `discover` to discover all test files) writes an sqlite3 `.coverage` datafile, `$ coverage report html` generates `./htmlcov/` and `firefox htmlcov/index.html` opens the html report. Notes: https://coverage.readthedocs.io/en/coverage-5.1/

## Profiling

### `ipython_memory_usage`

`import ipython_memory_usage; #%ipython_memory_usage_start` for cell by cell memory analysis


## Getting to high code quality

### `flake8`

Lints and checks code, works in most IDEs and as a git commit hook. Can disable a line with annoying warnings using `  # NOQA` as the comment.

### `pylama`

Has more than `flake8`, not as widely supported (2020-05 not in Visual Code as a default linter).

### `black`

Highly opinionated, not necessarily "what you want" as some of the reformating is hard to read _but_ you also don't get a choice and that's a really good outcome!

### `engarde`

Check dataframe cols as I go

### `watermark`

* https://github.com/rasbt/watermark

```
%load_ext watermark
%watermark -i -v -m -p pandas,numpy,matplotlib -g -b
# possible -iv for all imported pkg versions? try this...
```
