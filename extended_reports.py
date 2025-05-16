import sys
from typing import List, Dict, Any
import main


def generate_department_summary_report(employees: List[Dict[str, Any]]) -> None:
    departments = {}
    for employee in employees:
        department = employee.get('department', 'Unknown')
        if department not in departments:
            departments[department] = {
                'count': 0,
                'total_hours': 0,
                'total_payout': 0,
                'avg_rate': 0
            }
        
        departments[department]['count'] += 1
        departments[department]['total_hours'] += employee.get('hours_worked', 0)
        departments[department]['total_payout'] += main.calculate_payout(employee)
    
    for dept, stats in departments.items():
        if stats['total_hours'] > 0:
            stats['avg_rate'] = stats['total_payout'] / stats['total_hours']
    
    print("DEPARTMENT SUMMARY REPORT")
    print("=" * 80)
    print(f"{'DEPARTMENT':<20} {'EMPLOYEES':<10} {'TOTAL HOURS':<15} {'AVG RATE':<10} {'TOTAL PAYOUT':<15}")
    print("-" * 80)
    
    grand_total_payout = 0
    for dept, stats in sorted(departments.items()):
        print(f"{dept:<20} {stats['count']:<10} {stats['total_hours']:<15.1f} "
              f"${stats['avg_rate']:<9.2f} ${stats['total_payout']:<14.2f}")
        grand_total_payout += stats['total_payout']
    
    print("-" * 80)
    print(f"GRAND TOTAL PAYOUT: ${grand_total_payout:.2f}")
    print("=" * 80)


def register_additional_reports():
    main.ReportFactory.register_report('department', generate_department_summary_report)


if __name__ == "__main__":
    register_additional_reports()
    
    main.main()