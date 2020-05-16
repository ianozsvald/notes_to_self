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
                    help="show version (default: %(default)s)")

args = parser.parse_args()
print("Arguments provided:", args)
if args.version:
    print(f"Version: {__version__}")
```
