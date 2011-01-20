
.. _using-oosheet:

=============
Using OOSheet
=============

Developing with OOSheet
=======================

There are two ways of using OOSheet. You can either make a python script that manipulates an instance of OpenOffice.org, or you can make python macros that will be executed directly by OO. Macros can be installed in a global path for all users and documents, in user's home directory for a single user or inside a document.

No matter what your choice is, the python code is the same and works in any of those environments. So, it's always best to start your development by manipulating an instance of Openoffice.org, so that you don't have to restart it to test your routines.

You must launch OpenOffice.org Spreadsheet allowing socket connections. To do so, use the following command line (in GNU/Linux):

    $ oocalc -accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"

Hello world
===========

After launching oocalc, in a python shell:

    >>> from oosheet import OOSheet as S
    >>> S().alert('Hello world')

This will confirm that everything is properly setup. A second hello world could be:

    >>> S('a1').string = 'Hello world'


Cells selectors
===============

OOSheet uses selectors to determine which cells you are working with. Each instance of OOSheet class receives a selector as parameter. Cell-independent methods, like alert(), do not require a selector.

Examples of possible selectors:

    >>> S('b2') # one single cell at first sheet
    >>> S('a1:10') # one column from a1 to A10 at first sheet
    >>> S('a1:a10') # same thing
    >>> S('a1:g1') # one row with six columns
    >>> S('a1:g7') # a 7x7 square with 49 cells
    >>> S('Sheet2.a2:3') # cells A2 and A3 in sheet named "Sheet2"

and so on. 

Data manipulation
=================

Each cell has three relevant attributes concerning its data: value, string and formula. Besides that, OOSheet adds the "date" attribute, that is just a wrapper around value to work with datetime.datetime objects. Setting one of these 4 attributes will modify all of them accordinly.

Value is always a float and is not seen by the user. String is the representation you see inside the cell. Formula is the one you see at the formula box on top of the spreadsheet and generates a value and string. Dates are represented as values internally, counting the number of days since 30/12/1899, but that is transparent to developers using OOSheet.

The following code illustrates how to deal with those types:

    >>> S('a1').value = 1
    >>> S('a1').value
    1.0
    >>> S('a1').string
    u'1'
    >>> S('a1').formula
    u'1'
    >>> S('a1').date
    datetime.datetime(1899, 12, 31, 0, 0)

    >>> S('a1').string = 'Hello world'
    >>> S('a1').value
    0.0
    >>> S('a1').formula
    u'Hello world'
    >>> S('a1').date
    datetime.datetime(1899, 12, 30, 0, 0)

    >>> S('a1').value = 1
    >>> S('a2').formula = '=a1+10'
    >>> S('a2').value
    11.0
    >>> S('a2').string
    u'11'
    >>> S('a2').formula
    u'=A1+10'
    >>> S('a2').date
    datetime.datetime(1900, 1, 10, 0, 0)

    >>> S('a1').date = datetime.datetime(2011, 01, 19)
    >>> S('a1').value
    40562.0
    >>> S('a1').string
    u'40562'
    >>> S('a1').formula
    u'40562'

    (Note that setting a date will not format the cell as date. Trying to guess a good date format will potencially mess with your formatting, so OOSheet leaves this to you.)

Alternatively, you can use set_value(), set_string(), set_formula() and set_date() methods:

    >>> S('a1').set_value(1)
    >>> S('a2').set_string('Hello')
    and so on

This is useful for cascading calls.

Simulating user events
======================

Several user events can be simulated. The code talks for itself:

    >>> S('a1').value = 1
    >>> S('a1').drag_to('a10')
    >>> S('a1:a10').drag_to('g10')
    (drag_to does an autofill, what you drag is not the cell itself but that little square in the bottom right corner)

    >>> S('a4').insert_row()
    >>> S('d1').insert_column()
    >>> S('a7').delete_rows()
    >>> S('g1').delete_columns()

    >>> S('a8:b8').cut()
    >>> S('a1:4').copy()
    >>> S('j5').paste()

    >>> S('j4').format_as('a2')
    (you won't see anything, unless you have previously formatted a2 manually. Try setting its background first)

    >>> S().undo()
    >>> S().redo()
    >>> S().save_as('/tmp/oosheet_sandbox.ods')
    >>> S().quit() # this will close OpenOffice.org


Cascading calls
===============

Most methods can be cascaded. For example:

    >>> S('a1').set_value(1).drag_to('a10').drag_to('g10')

This is because these methods returns OOSheet objects. Note that the selector is not necessarily preserved, sometimes it is modified. In the above example, set_value() does not change the selector, but drag_to('a10') expands the selector to ('a1:a10'), so the whole column is dragged to G10.

The cascading logic is so that the resulting selector should always be as you expect.

Moving selectors
================

Selectors can be moved. For example:

    >>> S('sheet1.a1:a10').shift_right()
    Sheet1.B1:B10

The result is an OOSheet object with selector Sheet1.B1:B10. The shift_* methods are useful for cascading calls:

    >>> S('a1').set_value(1).drag_to('a10').drag_to('g10') #just to setup
    >>> S('c1:c10').insert_column().shift_right(2).copy().shift_left(3).paste()

It's also possible to shift a selector up and down:

    >>> S('a1').shift_down(2)
    Sheet1.A3
    >>> S('a3:c5').shift_up()
    Sheet1.A2:C4

You can also shift the selector until a condition is satisfied. The shift_DIRECTION_until() methods are used for this:

    >>> S('f1').value = 15
    >>> S('a1').shift_right_until(15)
    Sheet1.F1

The above example will only work for single cell selectors. For other selectors, you have to specify where to look for a value:

    >>> S('g5').string = 'total'
    >>> S('a1:10).shift_right_until(row_5 = 'total')
    Sheet1.G1:G10
    >>> S('a1:z1').shift_down_until(column_g = 'total')
    Sheet.A5:Z5
    (Note that only one parameter is accepted)

For more complex conditions, you can use lambda functions:

    >>> S('g5').string = 'hello world'
    >>> S('a1:10').shift_down_until(column_g_satisfies = lambda s: s.string.endswith('world'))
    Sheet1.G1:G10

The "s" parameter in lambda function will be a 1 cell OOSheet object.

When looking for cells, you must specify a column if you're shifting up or down, and a row if right or left. If you specify a column, the row considered will be the last one if you're going down and the first one if you're going up, and vice-versa. 

Selectors can also be expanded or reduced:

    >>> S('a1:10').grow_right()
    Sheet1.A1:B10
    >>> S('a1:g1').grow_down(2)
    Sheet1.A1:G3
    >>> S('c3:d4').grow_left()
    Sheet1.B3:D4
    >>> S('a1:g10').shrink_down()
    Sheet1.A1:G9
    >>> S('a1:g10').shrink_left()
    Sheet1.B1:G10




