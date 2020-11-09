# notes_to_self

# Projects

## Research

### Getting into a new project

* What is the purpose of this new project? Is it clearly defined?
* What value is unlocked at v1? Can this value really be deployed? What second order effects might occur _after_ deployment (and what _blocks_ the value from being released)?
* What's the biggest uncertainty ahead? What does it cost to solve it, what value does it bring?
  * Try to derisk the biggest/most painful uncertainties soonest
* What single thing might give us 80% of the remaining answer? Probably avoid the edge cases (document, but don't focus on them)
  * Identify the most valuable deliverables (most-derisking, most-value-yielding) to rank opportunities
* Milestones - list some, note what each enables

## Strategy

* Prefer who/what/why/where/when objective questions
* Focus on understanding the levers for highest value delivery, check for shared agreement on these (ignore low-value stuff that's cool but won't enable beneficial change)
* Aim for frequent mini-retros to discuss "what did we learn? what shouldn't we repeat?"

# Definitions

* Billion in UK and USA is 10^9 (the "short billion"), unlike various parts of Europe. Milliard can be used in Europe to refer to 10^9.

# Python

## Wants

* Pandas better describe - colour the percentiles, not the counts/mean/std, include 5/95% in percentiles. Add dtype description and maybe memory, not how many columns were ignored too (stick on the end maybe?)

* Pandas better cut - give it some ranges and ask for nice labels and it'll form e.g. in scientific form (1M-500k ...) with open/closed labels, maybe special handling of e.g. 0, with formatting for currency and others

* Matplotlib label formatter - take int/float labels and convert to eg currency (2dp), human readable (e.g. 1M), optional leading symbol (e.g. £, $) or trailing text (e.g. pp.), with commas (e.g. "2,000") `friendly_label(dp=2, leading_text="", following_text="", with_commas=False, ints_if_possible=False)` and `human_readable(...)`

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

`utc=True` will set timezone (else no tz info). Lowest valid date we can parse is circa `pd.to_datetime('1677-09-22', utc=True)` (21st will raise a `OutOfBoundsDatetime` unless `errors="ignore"` passed, if this is passed then we get a string back in place! use `coerce` to get `NaT` for invalid times) - limitations: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timestamp-limitations . Error handling: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#invalid-data

### `cut`

Pandas is closed-right by default i.e. with `right=True` (default) then bins are `(b1, b2]` (exclusive/open of left, inclusive/closed of right: https://en.wikipedia.org/wiki/Bracket_(mathematics) ). https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.cut.html

### `merge`

Merging is the underlying operation, `df.join` is a shortcut into `merge`.  `join` merges keys on the left with the index on the right, it doesn't change the resulting index. Prefer `merge` to stay explicit and check to see if the `index` has changed.

`indicator=True` adds `_merge` column with indicators like `both`. `validate='many_to_one'` validates uniqueness on the right (or left or both), raising `MergeError` if not validated.

### `concatenate`

Has lots of options including to drop the index, `axis=1` for columnar concatenation and more.

### `reindex`

Apply a new index e.g. a series of ints to a non-contiguous existing `index`, `fill_na` defaults to `NaN`.

### `value_counts`

Probably add `dropna=False` every time _caveat_ this means we easily miss NaN values, the sanity_check is to count the results and check them against the size of the original column.

### `info`

`df.info(memory_usage="deep")` introspects each column and counts bytes used including strings - but this can be slow on many strings (e.g. millions of rows of strings might take 1 minute).

### `describe`

* `ser.describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99, 1])` add more percentiles.
* `df.describe().style.background_gradient(axis=0)`

### `read_csv`

`pd.read_csv(parse_dates=True)` will only parse index dates, instead use `parse_dates=['col1', 'col2']` to parse other cols.

### `str.contains`

Lightweight pattern match use to e.g. `df.columns.contains('somestring', ignorecase=True)` to find substring `somestring` in column names, returns a mask.

### formatting

`vc.apply(lambda v: f"{v*100:.0f}%")` turn a `value_counts` into percentages like "92%"

### display options

`pd.get_option('display.max_columns')` probably 20 and `max_rows` is 60. Use `pd.set_option('display.max_columns', 100)` for more cols in e.g. `.head()`. `pd.set_option('precision', 4)`. https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html#frequently-used-options

```
def show_all(many_rows, max_rows=999):
    """Show many rows rather than the typical small default"""
    from IPython.display import display
    with pd.option_context('display.max_rows', 999):
        display(many_rows) # display required else no output generated due to indentation
```

### selecting columns or rows with `filter`

Use `df.filter(regex='blah')` to find column names containing "blah", add `axis=0` to do the same filtering on row labels.

### Data processing tips

`query` with `NaN` rows is a pain, for text columns we could replace missing data with `-` and then that's another string-like thing for a query, this significantly simplifies the queries.

## matplotlib

### my style (?)

```
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x') # horizontal grid lines only
ax.legend(frameon=False)
```

### `subplot`

* `fig, ax = plt.subplots(constrained_layout=True)`
* `fig, axs = plt.subplots(figsize=(20, 12), nrows=2, gridspec_kw={'height_ratios': [2, 1]})` 

### Pandas `plot`

Marks with x and no lines: `.plot(marker='x', linestyle=' ', ax=ax)`

## Horiztonal lines

`ax.axhline(10, color='grey', linestyle='--')`

## Formatting axis

* `ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))`


### subplots

* `fig, axs = plt.subplots(ncols=2, figsize=(8, 6))`

### limits

#### symmetric limits (x and y have same range)

```
min_val = min(ax.get_xlim()[0], ax.get_ylim()[0])
max_val = min(ax.get_xlim()[1], ax.get_ylim()[1])
ax.set_xlim(xmin=min_val, xmax=max_val)
ax.set_ylim(ymin=min_val, ymax=max_val)
```

#### symmetric (y axis)

```
biggest = max(abs(ax.get_ylim()[0]), abs(ax.get_ylim()[1]))
ax.set_ylim(ymin=-biggest, ymax=biggest)
```

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

```
# add e.g. s for seconds labeling on tick label
locs =ax.get_yticks()
new_yticks=[f"{d}s" for d in locs]
ax.set_yticklabels(new_yticks); 
```

* "percentage point, pp" for percentage differences https://en.wikipedia.org/wiki/Percentage_point, possibly use "proportion" in the title and aim for "%" symbol on numeric axis

### axis ticks

* https://matplotlib.org/3.1.0/api/ticker_api.html
  * `FixedLocator` is good for equal indices e.g. week count 10, 11, 12
  * `MaxNLocator` guesses at a good start/end point for fixed intervals
  * https://jakevdp.github.io/PythonDataScienceHandbook/04.10-customizing-ticks.html examples

## IPython

* `ipython -i script.py` will end script in interactive mode, add `-i --` so that args following `script.py` don't get picked up by IPython

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

## Debugging

### `pdb`

In IPython `pdb.run("scipy.stats.power_divergence(o, axis=None, ddof=2, lambda_='log-likelihood')")` will invoke `pdb`, use `s` to step into the function, `n` for the next line, `p` to print state (use this to see that `f_exp` is calculated in an unexpected way, see Statistical tests below). `b _count` will set a breakpoint for the `_count` function inside `power_divergence`, run to it with `c`.


## Statistical tests

`scipy.stats.chi2_contingency(o)` on a 2D array calculates `e=scipy.stats.contingency.expected_freq(o)` internally. With a `2x2` table the `dof==1` so `correction` is used which adjusts `o`, then this calls through to `scipy.stats.power_divergence`. To use a G Test pass `lambda_="log-likelihood"` to `chi2_contingency`. To avoid the correction when debugging confirm that `scipy.stats.chi2_contingency(o, correction=False)` and `scipy.stats.power_divergence(o, e, axis=None, ddof=2)` are the same. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html .  To calculate an equivalent G Test manually use `scipy.stats.power_divergence(o, e, axis=None, ddof=2, lambda_='log-likelihood')`. _Note_ that `e` is calculated implicitly as the mean of the array inside `power_divergence` which is _not_ the same as calling `expected_freq`! Prefer to be explicit. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.power_divergence.html


## Getting to high code quality

### `flake8`

Lints and checks code, works in most IDEs and as a git commit hook. Can disable a line with annoying warnings using `  # NOQA` as the comment.

### `pylama`

Has more than `flake8`, not as widely supported (2020-05 not in Visual Code as a default linter).

### `black`

Highly opinionated, not necessarily "what you want" as some of the reformating is hard to read _but_ you also don't get a choice and that's a really good outcome!

### `bulwark`

Check dataframe cols as I go

### `watermark`

* https://github.com/rasbt/watermark

```
%load_ext watermark
%watermark -i -v -m -p pandas,numpy,matplotlib -g -b
# possible -iv for all imported pkg versions? try this...
```

# Dask

* (stupid niche) writing a custom distributed Agg `dd.Aggregation(name="sumsq", chunk=lambda s: s.aggregate(func=lambda x: np.sum(np.power(x, 2))), agg=lambda s: s.sum())` is a pain in the arse - this calculates a sum of squares on a grouped series


# Shell

## link

`ln -s other_folder_file .` link the other file into this folder.

## scripts

`set -euo` to fail most errors, unset variables or fails in a pipeline https://twitter.com/b0rk/status/1314345978963648524

# Video editing

* https://github.com/mifi/lossless-cut
