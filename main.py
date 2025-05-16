import argparse
import sys
from typing import List, Dict, Any, Callable, Optional, Union, TextIO


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate payroll reports from CSV data")
    parser.add_argument(
        "files", 
        nargs="+", 
        help="CSV files with employee data"
    )
    parser.add_argument(
        "--report", 
        required=True, 
        help="Report type to generate"
    )
    return parser.parse_args()


def read_csv(file_path: str) -> List[Dict[str, Any]]:
    result = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            header = file.readline().strip().split(',')
            for line in file:
                line = line.strip()
                if not line:
                    continue
                values = line.split(',')
                if len(values) != len(header):
                    continue
                    
                row_data = {header[i]: values[i] for i in range(len(header))}
                result.append(row_data)
                
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)
        
    return result


def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = data.copy()
    rate_column_names = ['hourly_rate', 'rate', 'salary']
    for column_name in rate_column_names:
        if column_name in normalized:
            normalized['hourly_rate'] = normalized[column_name]
            if column_name != 'hourly_rate':
                del normalized[column_name]
            break
    try:
        if 'hours_worked' in normalized:
            normalized['hours_worked'] = float(normalized['hours_worked'])
        if 'hourly_rate' in normalized:
            normalized['hourly_rate'] = float(normalized['hourly_rate'])
    except (ValueError, TypeError):
        pass
        
    return normalized


def calculate_payout(employee: Dict[str, Any]) -> float:
    try:
        hours = float(employee.get('hours_worked', 0))
        rate = float(employee.get('hourly_rate', 0))
        return hours * rate
    except (ValueError, TypeError):
        return 0.0


def generate_payout_report(employees: List[Dict[str, Any]]) -> None:
    print("PAYOUT REPORT")
    print("=" * 80)
    print(f"{'NAME':<30} {'EMAIL':<30} {'DEPARTMENT':<15} {'PAYOUT':<10}")
    print("-" * 80)
    
    total_payout = 0.0
    
    for employee in employees:
        name = employee.get('name', 'N/A')
        email = employee.get('email', 'N/A')
        department = employee.get('department', 'N/A')
        payout = calculate_payout(employee)
        total_payout += payout
        
        print(f"{name:<30} {email:<30} {department:<15} ${payout:<9.2f}")
    
    print("-" * 80)
    print(f"TOTAL PAYOUT: ${total_payout:.2f}")
    print("=" * 80)


class ReportFactory:
    _reports: Dict[str, Callable[[List[Dict[str, Any]]], None]] = {
        'payout': generate_payout_report
    }
    
    @classmethod
    def get_report_generator(cls, report_type: str) -> Optional[Callable]:
        return cls._reports.get(report_type.lower())
    
    @classmethod
    def register_report(cls, report_type: str, generator_func: Callable) -> None:
        cls._reports[report_type.lower()] = generator_func


def main() -> None:
    args = parse_arguments()
    report_generator = ReportFactory.get_report_generator(args.report)
    if not report_generator:
        print(f"Error: Unknown report type '{args.report}'")
        print(f"Available reports: {', '.join(ReportFactory._reports.keys())}")
        sys.exit(1)
    all_employees = []
    for file_path in args.files:
        employees = read_csv(file_path)
        all_employees.extend([normalize_data(employee) for employee in employees])
    report_generator(all_employees)


if __name__ == "__main__":
    main()