import csv


def calculate_dashboard_metrics(file_path):
    """Return basic metrics for an uploaded CSV dashboard file."""
    metrics = {
        'row_count': 0,
        'columns': [],
    }

    if file_path.lower().endswith('.csv'):
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            metrics['columns'] = reader.fieldnames or []
            metrics['row_count'] = sum(1 for _ in reader)

    return metrics
