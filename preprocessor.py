import re
import pandas as pd

def preprocess(data):
    # Ensure consistent space before AM/PM (fixing non-breaking space issue)
    data = data.replace("\u202F", " ")  # Normalize non-breaking space

    # Updated regex pattern to match date format correctly
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[apAP][mM]\s-\s'
    
    messages = re.split(pattern, data)[1:]  # Extract messages
    dates = re.findall(pattern, data)  # Extract timestamps

    # Ensure equal lengths to prevent mismatches
    if len(messages) != len(dates):
        raise ValueError("Mismatch between extracted messages and timestamps")

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date column
    df['message_date'] = df['message_date'].str.strip(' - ')
    df['date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p', errors='coerce')

    # Extract user & message using improved regex
    users, messages = [], []
    for message in df['user_message']:
        match = re.match(r'([^:]+):\s(.+)', message)
        if match:
            users.append(match.group(1).strip())  # User name
            messages.append(match.group(2).strip())  # Message content
        else:
            users.append('group_notification')  # System messages
            messages.append(message.strip())

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message', 'message_date'], inplace=True)

    # Extract time-based features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour_24'] = df['date'].dt.hour
    df['hour_12'] = df['date'].dt.strftime('%I').astype(int)
    df['minute'] = df['date'].dt.minute
    df['am_pm'] = df['date'].dt.strftime('%p')

    # Create period columns
    df['period_12hr'] = df['hour_12'].astype(str) + '-' + (df['hour_12'] + 1).astype(str) + ' ' + df['am_pm']
    df['period_24hr'] = df['hour_24'].astype(str).str.zfill(2) + '-' + (df['hour_24'] + 1).astype(str).str.zfill(2)

    return df
