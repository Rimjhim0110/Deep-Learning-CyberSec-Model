import re

def mark_unusual_http_method(data):
    return 'Unusual HTTP Method' if data['Possible_Anomaly'] and data['HTTP_Method'] not in ['GET', 'POST'] else ''

def detect_unusual_traffic(data):
    data = data.sort_values('Time_Stamp', axis=1)
    data['Request_Count'] = data.groupby(['IP_Address', 'Time_Stamp']).cumcount() + 1
    return 'Unusual Traffic' if data['Request_Count'] > 15 and data['Anomaly_Type'] == '' else ''

def detect_sql_injection(row):
    patterns = {
        'Union-based SQL Injection; ': r'(\bUNION\b|\bSELECT\b|\bFROM\b|\bWHERE\b)\s*.*\bSELECT\b',
        'Error-based SQL Injection; ': r'\b(ORA-|MySQL error|SQL Server error|PostgreSQL ERROR)\b',
        'Time-based Blind SQL Injection; ': r'\b(SLEEP\s*\(\s*\d+\s*\)|WAITFOR\s+DELAY\s+\'\d+:\d+:\d+\')\b',
        'Boolean-based Blind SQL Injection; ': r'\b(TRUE\b|\bFALSE\b|\bAND\b|\bOR\b|\bNOT\b)',
        'Tautology-based SQL Injection; ': r'\b\d+\s*=\s*\d+\b',
    }
    return 'SQL Injection' if any(re.search(pattern, row['Requested_File_Path']) or re.search(pattern, row['User_Agent']) for pattern in patterns.values()) else ''

def detect_random_attacks(row):
    patterns = {
        'Access to Sensitive Files or Directories': r'/etc/passwd|\b/admin/config.php\b',
        'Directory Listing Attempts': r'/directory/',
        'Unauthorized Access Attempts': r'/login',
        'Open Redirect': r'\?redirect=http://malicious-site.com',
    }
    return 'Random Attack' if any(re.search(pattern, row['Requested_File_Path']) or re.search(pattern, row['User_Agent']) for pattern in patterns.values()) else ''

def label_data(df):
    """Label anomalies in the dataset."""  
    df['Possible_Anomaly'] = df['Status_Code'].astype(int).apply(lambda x: False if x < 300 else True)

    df['Anomaly_Type'] = df.apply(detect_random_attacks, axis=1)
    df['Anomaly_Type'] = df.apply(detect_sql_injection, axis=1)
    df['Anomaly_Type'] = df.apply(detect_unusual_traffic, axis=1)
    df['Anomaly_Type'] = df.apply(mark_unusual_http_method, axis=1)

    df['Anomaly_Type'].replace('', 'Valid Request', inplace=True)

    return df
