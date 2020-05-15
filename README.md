# notes_to_self

# Python

## Pandas

### `groupby`

Categoricals have a weird memory behaviour in 1.0 in `groupby`, must pass in `observed=True` on the `groupby` else it stalls and eats a lot of RAM: https://github.com/pandas-dev/pandas/issues/30552

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
