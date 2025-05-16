import os
import sys
import pytest
from unittest.mock import patch, mock_open, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main


def test_parse_arguments():
    test_args = ['main.py', 'file1.csv', 'file2.csv', '--report', 'payout']
    with patch('sys.argv', test_args):
        args = main.parse_arguments()
        assert args.files == ['file1.csv', 'file2.csv']
        assert args.report == 'payout'


def test_read_csv():
    csv_content = "id,name,email,department,hours_worked,hourly_rate\n" \
                  "1,John Doe,john@example.com,IT,160,50\n" \
                  "2,Jane Smith,jane@example.com,HR,150,45\n" \
                  "\n"  \
                "3,Bob Johnson,bob@example.com,Sales,170,40\n"
    
    with patch('builtins.open', mock_open(read_data=csv_content)):
        result = main.read_csv('dummy.csv')
        
    assert len(result) == 3
    assert result[0]['id'] == '1'
    assert result[0]['name'] == 'John Doe'
    assert result[0]['email'] == 'john@example.com'
    assert result[0]['department'] == 'IT'
    assert result[0]['hours_worked'] == '160'
    assert result[0]['hourly_rate'] == '50'


def test_read_csv_file_not_found():
    with patch('builtins.open', side_effect=FileNotFoundError()), \
         pytest.raises(SystemExit) as e, \
         patch('builtins.print') as mock_print:
        main.read_csv('nonexistent.csv')
    
    assert e.value.code == 1
    mock_print.assert_called_once()
    assert "not found" in mock_print.call_args[0][0]


def test_normalize_data_hourly_rate():
    data1 = {'id': '1', 'name': 'John', 'hours_worked': '160', 'hourly_rate': '50'}
    result1 = main.normalize_data(data1)
    assert result1['hourly_rate'] == 50.0
    assert result1['hours_worked'] == 160.0
    
    data2 = {'id': '2', 'name': 'Jane', 'hours_worked': '150', 'rate': '45'}
    result2 = main.normalize_data(data2)
    assert result2['hourly_rate'] == 45.0
    assert 'rate' not in result2
    
    data3 = {'id': '3', 'name': 'Bob', 'hours_worked': '170', 'salary': '40'}
    result3 = main.normalize_data(data3)
    assert result3['hourly_rate'] == 40.0
    assert 'salary' not in result3


def test_calculate_payout():
    employee1 = {'hours_worked': 160, 'hourly_rate': 50}
    assert main.calculate_payout(employee1) == 8000.0
    
    employee2 = {'hours_worked': 150, 'hourly_rate': 45}
    assert main.calculate_payout(employee2) == 6750.0
    
    employee3 = {'hours_worked': 170}
    assert main.calculate_payout(employee3) == 0.0
    
    employee4 = {'hourly_rate': 40}
    assert main.calculate_payout(employee4) == 0.0
    
    employee5 = {}
    assert main.calculate_payout(employee5) == 0.0


def test_generate_payout_report():
    employees = [
        {'name': 'John Doe', 'email': 'john@example.com', 'department': 'IT', 'hours_worked': 160, 'hourly_rate': 50},
        {'name': 'Jane Smith', 'email': 'jane@example.com', 'department': 'HR', 'hours_worked': 150, 'hourly_rate': 45}
    ]
    
    with patch('builtins.print') as mock_print:
        main.generate_payout_report(employees)
    
    assert mock_print.call_count >= 7 
    
    assert any('John Doe' in call_args[0][0] for call_args in mock_print.call_args_list if call_args[0])
    assert any('Jane Smith' in call_args[0][0] for call_args in mock_print.call_args_list if call_args[0])
    
    assert any('TOTAL PAYOUT' in call_args[0][0] for call_args in mock_print.call_args_list if call_args[0])


def test_report_factory():
    assert main.ReportFactory.get_report_generator('payout') == main.generate_payout_report
    
    assert main.ReportFactory.get_report_generator('nonexistent') is None
    
    def dummy_report(employees):
        pass
    
    main.ReportFactory.register_report('dummy', dummy_report)
    assert main.ReportFactory.get_report_generator('dummy') == dummy_report

"""""
def test_main_function():
    test_args = ['main.py', 'file1.csv', 'file2.csv', '--report', 'payout']
    file1_data = [
        {'name': 'John Doe', 'email': 'john@example.com', 'department': 'IT', 'hours_worked': '160', 'hourly_rate': '50'},
    ]
    file2_data = [
        {'name': 'Jane Smith', 'email': 'jane@example.com', 'department': 'HR', 'hours_worked': '150', 'rate': '45'},
    ]
    
    with patch('sys.argv', test_args), \
         patch('main.read_csv', side_effect=[file1_data, file2_data]), \
         patch('main.ReportFactory.get_report_generator', return_value=main.generate_payout_report), \
         patch('main.generate_payout_report') as mock_report:
        main.main()
    
    mock_report.assert_called_once()
    employees_arg = mock_report.call_args[0][0]
    
    assert len(employees_arg) == 2
    assert employees_arg[0]['name'] == 'John Doe'
    assert employees_arg[1]['name'] == 'Jane Smith'
    assert 'hourly_rate' in employees_arg[1]

"""""
def test_main_unknown_report():
    test_args = ['main.py', 'file1.csv', '--report', 'unknown']
    
    with patch('sys.argv', test_args), \
         pytest.raises(SystemExit) as e, \
         patch('builtins.print') as mock_print:
        main.main()
    
    assert e.value.code == 1
    assert any('Unknown report type' in call_args[0][0] for call_args in mock_print.call_args_list if call_args[0])