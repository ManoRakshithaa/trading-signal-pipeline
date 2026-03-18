import json, sys

with open('output.json') as f:
    data = json.load(f)

assert data['status'] == 'success', f"Expected success, got {data['status']}"
assert data['rows_processed'] == 9996, f"Expected 9996, got {data['rows_processed']}"
assert 'value' in data, 'Missing signal_rate value'

print('All checks passed!')
print(f"Signal rate: {data['value']}")
print(f"Rows processed: {data['rows_processed']}")
