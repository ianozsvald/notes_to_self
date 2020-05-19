# notes_to_self

# Python

## Pandas

### `groupby`

`gpby = df.groupby` generates a `groupby.generic.DataFrameGroupBy`. This has a `__len__`, `gpby.groups` shows the a dict of keys for the groups and the indices that match the rows.

`for group in gpby:` generates a tuple of `(name, subset_dataframe)`, the `subset_dataframe` has all the columns including the group keys. `.groups` generates this entire list of groups as a dict, index into it using e.g. `gpby.groups[('-', '-', 'Canada')]` to retrieve the indices (and use `df.loc[indices]`) to fetch the rows.  `gpby.get_group(('-',  '-',  'Canada'))` takes the keys and returns a `DataFrame` without the keys.

`gpby.transform` works on `Series` or `DataFrame` and returns a `Series` (?) that matches each input row pre-grouping. `gpby.apply` returns a result based on the grouped items.

`gpby` calls such as `mean` are delegated.

Categoricals have a non-obvious memory behaviour in 1.0 in `groupby`, must pass in `observed=True` on the `groupby` else it stalls and eats a lot of RAM: https://github.com/pandas-dev/pandas/issues/30552 It builds the cartesian product of all possible categorical groups with the default arguments which might take some time and RAM.

### `merge`

Merging is the underlying operation, `df.join` is a shortcut into `merge`.

### `concatenate`

Has lots of options including to drop the index, `axis=1` for columnar concatenation and more.

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

`python -m unittest` runs all tests with autodiscovery, `python -m unittest mymodule.myclass` finds `mymodule.py` and runs the tests in `myclass`.

There are some visual diffs but they're not brilliant. I don't think we can invoke `pdb` on failures without writing code?

### `pytest`

More mature than `unittest`, doesn't need the `unittest` methods for checking same/different code and catching expected exceptions is neater. Also has plugins, syntax colouring.

Typically we'd write `pytest` to execute it, there's something weird with being unable to find imported modules if `__init__.py` is (or maybe isn't) present, in which case `python -m pytest` does the job: https://stackoverflow.com/questions/41748464/pytest-cannot-import-module-while-python-can

`pytest --pdb` drops into the debugger on a failure. 


## Getting to high code quality

### `flake8`

Lints and checks code, works in most IDEs and as a git commit hook. Can disable a line with annoying warnings using `  # NOQA` as the comment.

### `pylama`

Has more than `flake8`, not as widely supported (2020-05 not in Visual Code as a default linter).

### `black`

Highly opinionated, not necessarily "what you want" as some of the reformating is hard to read _but_ you also don't get a choice and that's a really good outcome!
