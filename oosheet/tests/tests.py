# -*- coding: utf-8 -*-

"""
Each test must start with test_

clear() is called between each test.
Sheets Sheet1 and Sheet2 can be used for tests.

Following parameters can be passed to run_tests.py:

  --dev    Only tests with @dev decorator will be executed
  --stop   Errors are raised

If no errors are encountered, all tests will be merged to a test document to be
run as macro.

"""

def clear():
    S('a1').unprotect_sheet()
    S('a1:z100').delete()

def test_column_name_vs_index_conversion():
    assert S()._col_index('A') == 0
    assert S()._col_index('B') == 1
    assert S()._col_index('c') == 2 
    assert S()._col_index('Z') == 25
    assert S()._col_index('AA') == 26
    assert S()._col_index('AF') == 31

    assert S()._col_name(0) == 'A'
    assert S()._col_name(1) == 'B'
    assert S()._col_name(25) == 'Z'
    assert S()._col_name(26) == 'AA'
    assert S()._col_name(31) == 'AF'

def test_value():
    S('a1').value = 10

    assert S('a1').value == 10
    assert S('a1').formula == u'10'
    assert S('a1').string == u'10'

def test_string():
    S('a1').string = u'Hello'

    assert S('a1').string == u'Hello'
    assert S('a1').formula == u'Hello'
    assert S('a1').value == 0

    S('a1').string = u'10'
    assert S('a1').formula == u"'10"
    assert S('a1').value == 0

def test_formula():
    S('a1').value = 10
    S('a2').formula = '=a1+5'

    assert S('a2').value == 15
    assert S('a2').string == u'15'
    assert S('a2').formula == '=A1+5'

def test_date():
    S('a1').date = datetime(2010, 12, 17)

    assert S('a1').date == datetime(2010, 12, 17)
    S('a1').date += timedelta(5)
    assert S('a1').date == datetime(2010, 12, 22)
    assert '/' in S('a1').string

def test_date_only_sets_format_if_not_already_in_date_format():

    S().sheet.getCellRangeByName('Sheet1.A1').NumberFormat = 30
    S().sheet.getCellRangeByName('Sheet1.A2').NumberFormat = 38

    S('a1:a3').date = datetime(2011, 02, 20)

    # Check if formats have been preserved
    assert S('a1').string == '2/20/11'
    assert S('a2').string == 'Sunday, February 20, 2011'

    # Now format must have been set
    assert '/' in S('a3').string

def test_data_of_multiple_cells_can_be_changed():
    S('a1:g10').value = 5
    assert S('d5').value == 5
    S('a1:g10').set_value(6)
    assert S('c4').value == 6
    
    S('a1:g10').string = 'hello'
    assert S('e8').string == 'hello'
    S('a1:g10').set_string('world')
    assert S('f2').string == 'world'

    S('a1:g10').date = datetime(2011, 1, 20)
    assert S('e7').date == datetime(2011, 1, 20)
    S('a1:g10').set_date(datetime(2011, 1, 21))
    assert S('f4').date == datetime(2011, 1, 21)

    S('a1').value = 1
    S('a2:g5').formula = '=a1+3'
    assert S('b3').value == 4
    S('a2:g5').set_formula('=a1+5')
    assert S('b3').value == 6

    S('a1:h11').delete()
    S('b2:g10').value = 17
    assert S('a1').value == 0
    assert S('b1').value == 0
    assert S('a2').value == 0
    assert S('b2').value == 17
    assert S('g11').value == 0
    assert S('h10').value == 0
    assert S('h11').value == 0
    assert S('g10').value == 17

def test_selection_has_width_and_height():
    assert S('a1').width == 1
    assert S('a1').height == 1
    assert S('a2').width == 1
    assert S('a2').height == 1
    assert S('b3:c5').width == 2
    assert S('b3:c5').height == 3

def test_cell_contents_can_be_set_by_methods_which_can_be_cascaded():
    S('a1').set_value(1).drag_to('a5')
    assert S('a5').value == 5
    
    S('a1').set_string('hello').drag_to('a5')
    assert S('a5').string == 'hello'

    S('a1').value = 1
    S('a2').set_formula('=a1*2').drag_to('a5')
    assert S('a5').value == 16

    S('a1').set_date(datetime(2011, 1, 13)).drag_to('a5')
    assert S('a5').date == datetime(2011, 1, 17)

def test_drag_to():
    S('a1').value = 10
    S('a2').formula = '=a1+5'
    S('a2').drag_to('a3')

    assert S('a3').value == 20

def test_drag_to_with_cell_range():
    S('a1').value = 10
    S('a2').value = 20
    S('a3').value = 30

    S('a1:a3').drag_to('b3')

    assert S('b1').value == 11
    assert S('b2').value == 21
    assert S('b3').value == 31

def test_drag_calls_can_be_cascaded():
    S('a1').value = 1
    S('a1').drag_to('a5').drag_to('c5')
    assert S('c5').value == 7

def test_selector_handles_sheets():
    """This test requires english OpenOffice"""
    S('a1').value = 2
    S('Sheet2.a1').value = 5

    assert S('a1').value == 2
    assert S('Sheet2.a1').value == 5

    S('Sheet2.a2').value = 3
    S('Sheet2.a1:a2').drag_to('b2')

    assert S('Sheet2.b1').value == 6
    assert S('Sheet2.b2').value == 4

    S('Sheet2.a1:g10').delete()

def test_delete():
    S('a1').value = 1
    S('a1').delete()

    assert S('a1').value == 0
    assert S('a1').string == ''

    S('a1').value = 1
    S('a2').value = 1
    S('b1').value = 1
    S('b2').value = 1
    S('a1:b2').delete()

    assert S('a1').value == 0
    assert S('a1').string == ''
    assert S('a2').value == 0
    assert S('a2').string == ''
    assert S('b1').value == 0
    assert S('b1').string == ''
    assert S('b2').value == 0
    assert S('b2').string == ''

def test_last_rows_and_columns():
    assert S('a1:g10').first_row.selector.endswith('.A1:G1')
    assert S('a1:g10').last_row.selector.endswith('.A10:G10')
    assert S('a1:g10').first_column.selector.endswith('.A1:A10')
    assert S('a1:g10').last_column.selector.endswith('.G1:G10')

def test_insert_rows():
    S('a1').value = 10
    S('b2').formula = '=a1+5'

    S('b2').insert_row()

    assert S('b3').formula.lower() == '=a1+5'
    assert S('b2').value == 0
    assert S('b2').string == ''

def test_insert_row_expands_selector_and_can_be_cascaded():
    S('a1').value = 10
    S('a2').formula = '=a1+5'
    S('b1').value = 12

    S('a2').insert_row().drag_to('b3')

    assert S('b3').value == 17

def test_several_rows_can_be_inserted():
    S('a1').value = 11
    S('b2').formula = '=a1+5'

    result = S('b2').insert_rows(5)

    assert S('b7').formula.lower() == '=a1+5'

    result.value = 5

    assert S('b2').value == 5
    assert S('b4').value == 5
    assert S('b7').value == 5
    

def test_insert_column():
    S('a1').value = 10
    S('b2').formula = '=a1+5'

    S('b2').insert_column()

    assert S('c2').formula.lower() == '=a1+5'
    assert S('b2').value == 0
    assert S('b2').string == ''

def test_insert_column_expands_selector_and_can_be_cascaded():
    S('a1').value = 10
    S('b1').formula = '=a1+5'
    S('a2').value = 12

    S('b1').insert_column().drag_to('c2')

    assert S('c2').value == 17

def test_several_columns_can_be_inserted():
    S('a1').value = 11
    S('b2').formula = '=a1+5'

    result = S('b2').insert_columns(5)

    assert S('g2').formula.lower() == '=a1+5'

    result.value = 6

    assert S('b2').value == 6
    assert S('d2').value == 6
    assert S('g2').value == 6

def test_delete_rows():
    S('d5').value = 2
    S('a2').delete_rows()

    assert S('d4').value == 2

    S('a1:a3').delete_rows()

    assert S('d1').value == 2

def test_delete_columns():
    S('f5').value = 2

    S('a2').delete_columns()

    assert S('e5').value == 2

    S('a1:d1').delete_columns()

    assert S('a5').value == 2

def test_copy_cut_and_paste():
    S('a1').value = 4
    S('a1').copy()
    S('b2').paste()

    assert S('a1').value == 4
    assert S('b2').value == 4

    S('a1').cut()
    S('c1').paste()

    assert S('a1').value == 0
    assert S('c1').value == 4

def test_copy_cut_and_paste_can_be_cascaded():
    S('a1').set_value(12).copy().set_value(15).shift_right().paste().shift_down().set_value(18).cut().shift_left().paste()
    assert S('a1').value == 15
    assert S('b1').value == 12
    assert S('b2').value == 0
    assert S('a2').value == 18

def test_delete():
    S('a1').value = 10
    S('a1').delete()
    assert S('a1').value == 0

    S('a1').string = 'hello'
    S('a1').delete()
    assert S('a1').string == ''

def test_undo_redo():
    S('a1').value = 1
    S('a1').value = 2
    S('a1').value = 3
    S('a1').value = 4
    S('a1').value = 5

    S().undo()
    assert S('a1').value == 4
    S().undo()
    S().undo()
    assert S('a1').value == 2
    S().redo()
    assert S('a1').value == 3
    S().redo()
    assert S('a1').value == 4
    S().undo()
    assert S('a1').value == 3

def test_save_as():
    filename = '/tmp/test_oosheet.ods'
    assert not os.path.exists(filename)
    S().save_as(filename)
    assert os.path.exists(filename)
    os.remove(filename)

def test_shift_until_works_for_single_cell_with_value_as_parameter():
    S('g10').string = 'total'

    assert str(S('g1').shift_down_until('total')).endswith('G10')
    assert str(S('g20').shift_up_until('total')).endswith('G10')
    assert str(S('a10').shift_right_until('total')).endswith('G10')
    assert str(S('z10').shift_left_until('total')).endswith('G10')

    S('g10').value = 18
    assert str(S('g1').shift_down_until(18)).endswith('G10')

    S('g10').value = 18.5
    assert str(S('g1').shift_down_until(18.5)).endswith('G10')

    date = datetime(2011, 1, 20)
    S('g10').date = date
    assert str(S('g1').shift_down_until(date)).endswith('G10')

def test_shift_until_works_with_conditions_for_one_dimension_selectors():
    date = datetime(2011, 1, 20)

    S('c10').string = 'total'
    S('d11').value = 19
    S('e12').value = 19.5
    S('f13').date = date
    S('c14').value = 20

    assert str(S('a1:z1').shift_down_until(column_c = 'total')).endswith('.A10:Z10')
    assert str(S('a1:z1').shift_down_until(column_d = 19)).endswith('.A11:Z11')
    assert str(S('a1:z1').shift_down_until(column_e = 19.5)).endswith('.A12:Z12')
    assert str(S('a1:z1').shift_down_until(column_f = date)).endswith('.A13:Z13')
    assert str(S('a1:z1').shift_down_until(column_c = 20)).endswith('.A14:Z14')

    assert str(S('a30:z30').shift_up_until(column_c = 'total')).endswith('.A10:Z10')
    assert str(S('a1:a30').shift_right_until(row_11 = 19)).endswith('.D1:D30')
    assert str(S('z1:z30').shift_left_until(row_12 = 19.5)).endswith('.E1:E30')

def test_shift_until_works_with_conditions_for_two_dimension_selectors():
    date = datetime(2011, 1, 20)

    S('c10').string = 'total'
    S('d11').value = 19
    S('e12').value = 19.5
    S('f13').date = date
    S('c14').value = 20

    assert str(S('a1:z2').shift_down_until(column_c = 'total')).endswith('.A9:Z10')
    assert str(S('a1:z2').shift_down_until(column_d = 19)).endswith('.A10:Z11')
    assert str(S('a1:z2').shift_down_until(column_e = 19.5)).endswith('.A11:Z12')
    assert str(S('a1:z2').shift_down_until(column_f = date)).endswith('.A12:Z13')
    assert str(S('a1:z4').shift_down_until(column_c = 20)).endswith('.A11:Z14')

    assert str(S('a20:z30').shift_up_until(column_c = 'total')).endswith('.A10:Z20')
    assert str(S('a1:c30').shift_right_until(row_11 = 19)).endswith('.B1:D30')
    assert str(S('x1:z30').shift_left_until(row_12 = 19.5)).endswith('.E1:G30')

def test_shift_until_handles_unicode_properly():
    S('c10').string = u'fué'
    assert str(S('a1:d1').shift_down_until(column_c = u'fué')).endswith('.A10:D10')

def test_shift_until_accepts_lambda_to_test_condition():
    S('f10').string = 'some stuff'
    S('g10').string = 'one string'
    S('h11').string = 'another string'
    S('h12').string = 'another stuff'

    assert str(S('a1:z1').shift_down_until(column_g_satisfies = lambda c: c.string.endswith('string'))).endswith('.A10:Z10')
    assert str(S('a1:z2').shift_down_until(column_h_satisfies = lambda c: c.string.startswith('another'))).endswith('.A10:Z11')
    assert str(S('a1:z2').shift_down_until(column_h_satisfies = lambda c: c.string.endswith('stuff'))).endswith('.A11:Z12')
    assert str(S('a1:a20').shift_right_until(row_10_satisfies = lambda c: c.string.endswith('string'))).endswith('.G1:G20')

def test_shift_until_accepts_none_for_empty_cell():
    S('a1').set_value(1).drag_to('g1').drag_to('g10')
    S('g10').delete()

    assert str(S('b1').shift_right_until(row_1 = None)).endswith('.H1')
    assert str(S('b1').shift_down_until(column_b = None)).endswith('.B11')
    assert str(S('b1:5').shift_down_until(column_c = None)).endswith('.B7:B11')
    assert str(S('b1:5').shift_right_until(row_2 = None)).endswith('.H1:H5')
    assert str(S('a2:z2').shift_down_until(column_f = None)).endswith('.A11:Z11')
    assert str(S('a2:z2').shift_down_until(column_g = None)).endswith('.A10:Z10')

def test_shift_right():
    S('a1').set_value(1).drag_to('a10').drag_to('f10')
    S('c1').set_value(100).drag_to('c10')

    S('b1:b5').shift_right().drag_to('d5')
    assert S('d3').value == 103

    S('a6:a10').shift_right(2).drag_to('d10')
    assert S('d7').value == 107

def test_shift_left():
    S('a1').set_value(1).drag_to('a10').drag_to('f10')
    S('c1').set_value(102).drag_to('c10')

    S('d1:d5').shift_left().drag_to('b5')
    assert S('b3').value == 103

    S('e6:e10').shift_left(2).drag_to('b10')
    assert S('b7').value == 107

def test_shift_down():
    S('a1').set_value(1).drag_to('a10').drag_to('g10')
    S('a4').set_value(100).drag_to('g4')

    S('a3:d3').shift_down().drag_to('d5')
    assert S('c5').value == 103

    S('e2:g2').shift_down(2).drag_to('g5')
    assert S('f5').value == 106

def test_shift_up():
    S('a1').set_value(1).drag_to('a10').drag_to('g10')
    S('a4').set_value(102).drag_to('g4')

    S('a5:d5').shift_up().drag_to('d3')
    assert S('c3').value == 103

    S('e6:g6').shift_up(2).drag_to('g3')
    assert S('f3').value == 106

def test_shifting_works_with_cell_contents():
    S('a1').set_value(10).shift_right().set_value(12).shift_down().set_value(15).shift_left().set_value(17)
    assert S('a2').value == 17

def test_shifting_can_be_done_with_arithmetic_operations():
    assert str(S('a1') + (1, 0)).endswith('.B1')
    assert str(S('a1') + (0, 1)).endswith('.A2')
    assert str(S('a1') + (2, 3)).endswith('.C4')
    assert str(S('a1:b5') + (3, 4)).endswith('.D5:E9')

    assert str(S('b1') - (1, 0)).endswith('.A1')
    assert str(S('a2') - (0, 1)).endswith('.A1')
    assert str(S('c4') - (2, 3)).endswith('.A1')
    assert str(S('d5:e9') - (3, 4)).endswith('.A1:B5')

def test_difference_between_two_selectors_can_be_calculated_with_subtraction():
    assert S('b4') - S('b3') == (0, 1)
    assert S('b3') - S('b4') == (0, -1)
    assert S('c5') - S('a5') == (2, 0)
    assert S('a5') - S('c5') == (-2, 0)
    assert S('c5') - S('a2') == (2, 3)
    assert S('a2') - S('c5') == (-2, -3)
    assert S('c5:d6') - S('a2:b3') == (2, 3)

def test_selector_can_be_expanded():
    assert str(S('d4').grow_right()).endswith('.D4:E4')
    assert str(S('d4').grow_right(2)).endswith('.D4:F4')
    assert str(S('d4').grow_left()).endswith('.C4:D4')
    assert str(S('d4').grow_left(2)).endswith('.B4:D4')
    assert str(S('d4').grow_down()).endswith('.D4:D5')
    assert str(S('d4').grow_down(2)).endswith('.D4:D6')
    assert str(S('d4').grow_up()).endswith('.D3:D4')
    assert str(S('d4').grow_up(2)).endswith('.D2:D4')

    assert str(S('d4:e5').grow_right(2).grow_left(2).grow_down(2).grow_up(2)).endswith('.B2:G7')

def test_grow_until():
    S('a1').set_value(5).drag_to('a10').drag_to('g10')

    assert S('b3').grow_down_until(column_c = 15).selector.endswith('.B3:B9')
    assert S('b3').grow_down_until(column_d_satisfies = lambda s: s.value > 14).selector.endswith('.B3:B8')
    assert S('c4').grow_down_until(column_b = None).selector.endswith('.C4:C11')
    assert S('b2:d2').grow_down_until(column_a = 11).selector.endswith('.B2:D7')
    assert S('b2:b3').grow_down_until(column_a = 11).selector.endswith('.B2:B7')

    assert S('e9').grow_up_until(column_c = 8).selector.endswith('.E2:E9')
    assert S('e9:f10').grow_up_until(column_a_satisfies = lambda s: s.value < 6).selector.endswith('.E1:F10')

    assert S('a3:b4').grow_right_until(row_3_satisfies = lambda s: s.value > 11).selector.endswith('.A3:F4')

    assert S('f4:g5').grow_left_until(row_3_satisfies = lambda s:s.value < 9).selector.endswith('.B4:G5')    

def test_shrink_until():
    S('a1').set_value(5).drag_to('a10').drag_to('g10')

    assert S('b2:f9').shrink_down_until(column_f = 13).selector.endswith('.B2:F4')
    assert S('b2:f9').shrink_up_until(column_e_satisfies = lambda s: s.value > 13).selector.endswith('.B6:F9')
    assert S('b2:f9').shrink_left_until(row_9 = 16).selector.endswith('.D2:F9')
    assert S('b2:f9').shrink_right_until(row_9 = 16).selector.endswith('.B2:D9')

def test_selector_can_be_reduced():
    assert str(S('b2:g7').shrink_right()).endswith('.B2:F7')
    assert str(S('b2:g7').shrink_right(2)).endswith('.B2:E7')
    assert str(S('b2:g7').shrink_left()).endswith('.C2:G7')
    assert str(S('b2:g7').shrink_left(2)).endswith('.D2:G7')
    assert str(S('b2:g7').shrink_down()).endswith('.B2:G6')
    assert str(S('b2:g7').shrink_down(2)).endswith('.B2:G5')
    assert str(S('b2:g7').shrink_up()).endswith('.B3:G7')
    assert str(S('b2:g7').shrink_up(2)).endswith('.B4:G7')

    assert str(S('B2:G7').shrink_right(2).shrink_left(2).shrink_down(2).shrink_up(2)).endswith('.D4:E5')

def test_object_can_be_cloned():
    start = S('a1')
    end = S('a1').clone().shift_right()

    assert str(start).endswith('.A1')
    assert str(end).endswith('.B1')

def test_flatten():
    S('a1').value = 5
    S('a2').formula = '=a1+3'

    S('a2').flatten()
    S('a1').value = 10

    assert S('a2').value == 8

    S('a2').formula = '=a1+3'
    S('a2').drag_to('a10')
    
    S('a1:a10').flatten()
    S('a1').value = 0

    assert S('a2').value == 13
    assert S('a6').value == 25
    assert S('a10').value == 37

def test_flatten_works_with_string():
    S('a1').string = 'Hello World'
    S('a2').formula = u'=SUBSTITUTE(A1; "World"; "Moon")'

    S('a2').flatten()
    S('a1').string = 'asdf'

    assert S('a2').string == "Hello Moon"

def test_flatten_works_with_zero_formatted_as_string():
    S('a1').value = 0
    S('a2').value = 10
    S('a3').formula = '=a1+a2'
    S().sheet.getCellRangeByName('Sheet1.A1:A3').NumberFormat = 105 # $0.--

    string = S('a3').string
    S('a1').flatten()
    assert S('a3').string == string    
    

def test_protection():
    S('a1').unprotect()
    S('a2').protect()

    S('a1').unprotect_sheet()

    S('a1').value = 10
    S('a2').value = 15

    S('a2').protect_sheet()

    S('a1').value = 11
    
    S('a2').value = 12

    assert S('a1').value == 11 
    assert S('a2').value == 15

    S('a1').drag_to('a10')

    # cannot run over a protected cell
    
    assert S('a10').value == 0

    S('a2').unprotect_sheet()

    S('a2').value = 20

    assert S('a2').value == 20

    S('a1').set_value(1).drag_to('a10')

    assert S('a2').value == 2
    assert S('a10').value == 10

    S('Sheet2.a1').protect_sheet()
    
    S('Sheet1.a1').value = 17

    assert S('Sheet1.a1').value == 17

def test_protection_can_be_cascaded():

    S('a1').unprotect_sheet().unprotect().set_value(2)
    assert S('a1').value == 2

    S('b1').unprotect()
    S('a1').protect_sheet().protect().shift_right().set_value(3)
    assert S('b1').value == 3

def test_sheet_protection_supports_password():

    S('a1').unprotect()
    S('a2').value = 5
    
    S('a1').set_value(10).drag_to('a3')
    assert S('a2').value == 11
    
    S('a2').protect().protect_sheet("secretpassword")
    S('a1').set_value(20).drag_to('a3')
    assert S('a2').value == 11

    S('a2').unprotect_sheet()
    S('a1').set_value(30).drag_to('a3')
    assert S('a2').value == 11
    
    S('a2').unprotect_sheet("secretpassword")
    S('a1').set_value(40).drag_to('a3')
    assert S('a2').value == 41

def test_user_selection():
    S('a1').focus()
    assert S().selector == 'Sheet1.A1'

    S('b2:g10').focus()
    assert S().selector == 'Sheet1.B2:G10'

    S('Sheet2.b2:g10').focus()
    assert S().selector == 'Sheet2.B2:G10'

def test_format_as():
    S().sheet.getCellRangeByName('Sheet1.A1').NumberFormat = 38
    S('a1').date = datetime(2011, 03, 1)
    S('a2:3').date = datetime(2011, 03, 2)

    S('a2').format_as('a1')
    assert S('a2').string == 'Wednesday, March 02, 2011'

    S('a3').format_as(S('a1'))
    assert S('a3').string == 'Wednesday, March 02, 2011'

def test_data_array():
    S('a1').value = 1
    S('a2').formula = '=a1 * 2'
    S('b1').formula = '=a1 * 1.5'
    S('a2').drag_to('a7')
    S('b1').drag_to('b7')
    S('b1:b7').drag_to('d7')

    assert len(S('a1:7').data_array) == 7
    assert len(S('a1:7').data_array[1]) == 1
    assert S('a1:7').data_array[2] == (4,)
    assert len(S('a1:c7').data_array[1]) == 3
    assert S('a1:d7').data_array[5][1] == 48

def test_iterator():
    for cell in S('a1:10'):
        cell.value = 31

    for cell in S('b1:c10'):
        cell.value = 32

    assert S('a1').value == 31
    assert S('a2').value == 31
    assert S('a3').value == 31
    assert S('a4').value == 31
    assert S('a9').value == 31
    assert S('a10').value == 31

    assert S('b1').value == 32
    assert S('b2').value == 32
    assert S('b3').value == 32
    assert S('b4').value == 32
    assert S('b9').value == 32
    assert S('b10').value == 32
    
    assert S('c1').value == 32
    assert S('c2').value == 32
    assert S('c3').value == 32
    assert S('c4').value == 32
    assert S('c9').value == 32
    assert S('c10').value == 32

def test_iterator_as_cells():
    for cell in S('b1:c10').cells:
        cell.value = 32

    assert S('b1').value == 32
    assert S('c10').value == 32

    for cell in S('b1:c10').cells:
        cell.value = 33

    assert S('b1').value == 33
    assert S('c10').value == 33

def test_iterator_rows():
    i = 10
    for row in S('a2:d10').rows:
        row.value = i
        i += 1

    assert S('a2').value == 10
    assert S('b2').value == 10
    assert S('c2').value == 10
    assert S('d2').value == 10

    assert S('a3').value == 11
    assert S('d3').value == 11

    assert S('a9').value == 17
    assert S('d9').value == 17

    assert S('a10').value == 18
    assert S('d10').value == 18

    assert S('a1').value == 0
    assert S('a11').value == 0

def test_iterator_columns():
    i = 10
    for col in S('b2:d10').columns:
        col.value = i
        i += 1

    assert S('b2').value == 10
    assert S('b3').value == 10
    assert S('b9').value == 10
    assert S('b10').value == 10

    assert S('c2').value == 11
    assert S('c10').value == 11

    assert S('d2').value == 12
    assert S('d10').value == 12

    assert S('a2').value == 0
    assert S('e2').value == 0
    assert S('a11').value == 0
    assert S('e11').value == 0

def test_dispatch():
    S('a1').value = 10
    S('a2').formula = '=a1+5'

    OODoc().dispatch('AutomaticCalculation', False)

    try:
        S('a1').value = 11
        assert S('a2').value == 15 #automatic calculation is off

        S().dispatch('calculate')

        assert S('a2').value == 16

    finally:
    
        OODoc().dispatch('AutomaticCalculation', True)

def test_find():
    vals = 'there are several cells with single words in it'.split()
    for i, cell in enumerate(S('a1:d8').cells):
        cell.string = vals[i%len(vals)]

    result = S('a1:g10').find('words')
    result = [ cell for cell in S('a1:g10').find('words') ]

    assert len(result) == 3
    assert str(result[0]).endswith('.A7')
    assert str(result[1]).endswith('.B8')
    assert str(result[2]).endswith('.D1')


def test_find_accepts_function_as_query():
    vals = 'there are several cells with single words in it'.split()
    for i, cell in enumerate(S('a1:d8').cells):
        cell.string = vals[i%len(vals)]

    result = [ cell for cell in S('a1:g10').find(lambda c: 'l' in c.string) ]

    assert len(result) == 11
    assert str(result[0]).endswith('.A3')
    assert str(result[1]).endswith('.A4')
    assert str(result[2]).endswith('.A6')
    assert str(result[3]).endswith('.B4')
    assert str(result[4]).endswith('.B5')
    assert str(result[5]).endswith('.B7')
    assert str(result[6]).endswith('.C5')
    assert str(result[7]).endswith('.C6')
    assert str(result[8]).endswith('.C8')
    assert str(result[9]).endswith('.D6')
    assert str(result[10]).endswith('.D7')

