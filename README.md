# notes_to_self

# Python

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
