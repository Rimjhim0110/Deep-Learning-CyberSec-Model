import pandas as pd

def read_log_file(file_path):
    # Read the .txt file into a list and convert it to a DataFrame
    with open(file_path, 'r') as f:
        log_entries = f.readlines()
    
    df = pd.DataFrame(log_entries, columns=['log'])

    # Regular expression pattern to extract features from the log
    log_pattern = (
        r'(?P<IP_Address>\S+) \S+ \S+ \[(?P<Time_Stamp>.*?)\] '
        r'"(?P<HTTP_Method>\w+) (?P<Requested_File_Path>.*?) '
        r'(?P<HTTP_Version>HTTP\/\d\.\d)" (?P<Status_Code>\d{3}) '
        r'(?P<Bytes_Received>\S*) "(?P<Referer_File_Path>.*?)" '
        r'"(?P<User_Agent>.*?)"'
    )

    df[['IP_Address', 'Time_Stamp', 'HTTP_Method', 'Requested_File_Path', 'HTTP_Version', 'Status_Code', 'Bytes_Received', 'Referer_File_Path', 'User_Agent']] = df['log'].str.extract(log_pattern)

    return df

def handle_missing_data(df):
    # Drop the rows with empty values
    df.dropna(axis=0, how='any', inplace=True)
    return df
