# rowdiff.py

Find differences between two sets of rows in two CSV files.

# Diff behavior

The diffs are **set**-oriented. Thus, if you have one CSV file with these contents:

```
id,user
0,mike
```

...and you compare it against this CSV file:

```
id,user
0,mike
1,mike
2,mike
3,mike
```

...and you are *only* looking at the "user" column, then the tool will report the rows as being
identical. To see the differences, you will want to add the "id" column to the list of columns to
inspect.

# Installation and requirements

This is just a single file Python 3 script. It *should* work on any version of Python 3 but I have
not extensively tested this.

# Usage

Basic usage of this script looks like this:

`python3 rowdiff.py FILE1 FILE2 [filtering options]`

Where FILE1 and FILE2 are both CSV files with the same set of columns.

The rest of the options are used for filtering and whittling down data to a more useful comparison
set.

By default, no columns are selected to compare. You need to specify which ones you want to select,
or you can select all of them by using the `-a` flag.

## Filtering options

* `-a, --all` - Compare all columns in both data sets.
* `-c, --column COL` - Add a column to the set of columns to compare. This option may be specified
  multiple times. Additionally, you may specify a number of comma-separated columns to group
  together.
* `-i, --ignore COL` - Used in conjunction with the `-a` flag, this will remove any columns from
  the comparison result.
* `-g, --group-by` - Groups differences by a given column. This is useful for checking which values
  have changed, been added, or been removed that have a common grouping value.
  * **NOTE** that you may currently only group by one column. This is planned for the future.
  * **NOTE** that group-by does not have aggregate column support (e.g. `id,user`). This is planned
    for the future.

## Examples

These examples use the files in the `examples/` directory in this repository. Note that the notation
`examples/ex0_{1,2}.csv` expands to `examples/ex0_1.csv examples/ex0_2.csv`, which is used to save
typing.

### Compare all columns between

Command:

`./rowdiff.py examples/ex0_{1,2}.csv -a`

Output:

```
= id ===========================================================================
+ 2
- 8
= company ======================================================================
+ 100
- 200
= user =========================================================================
+ jack
- scott
- john
```

### Compare all columns between two sets of rows, except for the "company" colunn

Command:

`./rowdiff.py examples/ex0_{1,2}.csv -a -i company`

Output:

```
= user =========================================================================
+ jack
- scott
- john
= id ===========================================================================
+ 2
- 8
```

### Compare differing values of "user" and "id" columns

Command:

`./rowdiff.py examples/ex0_{1,2}.csv -c user -c id`

Output:

```
= user =========================================================================
+ jack
- scott
- john
= id ===========================================================================
+ 2
- 8
```

### Compare all pairings of the "id" and "user" columns

Command:

`./rowdiff.py examples/ex0_{1,2}.csv -c id,user`

Output:

```
= id,user ======================================================================
+ ('5', 'jack')
+ ('2', 'jacob')
- ('5', 'john')
- ('8', 'scott')
```

### Compare all columns that have the same "id" value, but different "user" values

Command:

`./rowdiff.py examples/ex0_{1,2}.csv -g id -c user`

Output:

```
= user =========================================================================
id group 5
 + jack
 - john
```

### Compare which users in company 888 have been added or removed

Command:

`./rowdiff.py examples/ex0_{1,2}.csv -g company -c user`

Output:

```
company group 999
 + jack
 - john
company group 888
 + jacob
 - scott
```

### Compare users whose company has changed

Command:

`./rowdiff.py examples/ex0_{1,2}.csv -g user -c company`

Output:

```
= company ======================================================================
user group jacob
 + 888
user group yosef
 + 100
 - 200
```
