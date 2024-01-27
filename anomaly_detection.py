import re

def mark_unusual_http_method(data):
    return 'Unusual HTTP Method' if data['Possible Anomaly'] and data['HTTP Method'] not in ['GET', 'POST'] else ''

def detect_unusual_traffic(data):
    data = data.sort_values('Time Stamp')
    data['Request Count'] = data.groupby(['IP Address', 'Time Stamp']).cumcount() + 1
    return 'Unusual Traffic' if data['Request Count'] > 15 and data['Anomaly Type'] == '' else ''

def detect_sql_injection(row):
    patterns = {
        'Union-based SQL Injection; ': r'(\bUNION\b|\bSELECT\b|\bFROM\b|\bWHERE\b)\s*.*\bSELECT\b',
        'Error-based SQL Injection; ': r'\b(ORA-|MySQL error|SQL Server error|PostgreSQL ERROR)\b',
        'Time-based Blind SQL Injection; ': r'\b(SLEEP\s*\(\s*\d+\s*\)|WAITFOR\s+DELAY\s+\'\d+:\d+:\d+\')\b',
        'Boolean-based Blind SQL Injection; ': r'\b(TRUE\b|\bFALSE\b|\bAND\b|\bOR\b|\bNOT\b)',
        'Tautology-based SQL Injection; ': r'\b\d+\s*=\s*\d+\b',
    }
    return 'SQL Injection' if any(re.search(pattern, row['Requested File Path']) or re.search(pattern, row['User Agent']) for pattern in patterns.values()) else ''

def detect_random_attacks(row):
    patterns = {
        'Access to Sensitive Files or Directories': r'/etc/passwd|\b/admin/config.php\b',
        'Directory Listing Attempts': r'/directory/',
        'Unauthorized Access Attempts': r'/login',
        'Open Redirect': r'\?redirect=http://malicious-site.com',
    }
    return 'Random Attack' if any(re.search(pattern, row['Requested File Path']) or re.search(pattern, row['User Agent']) for pattern in patterns.values()) else ''

def label_data(df):
    """Label anomalies in the dataset."""    
    df['Anomaly Type'] = df.apply(detect_random_attacks, axis=1)
    df['Anomaly Type'] = df.apply(detect_sql_injection, axis=1)
    df['Anomaly Type'] = df.apply(detect_unusual_traffic, axis=1)
    df['Anomaly Type'] = df.apply(mark_unusual_http_method, axis=1)

    df['Anomaly Type'].replace('', 'Valid Request', inplace=True)

    return df
