import pandas as pd
import re

def preprocess(data):
    """
    Processes WhatsApp chat data and returns a structured DataFrame.
    
    Parameters:
        data (str): Raw text from the WhatsApp chat export.
    
    Returns:
        pd.DataFrame: Processed DataFrame with structured columns.
    """

    # Check if data is empty
    if not data.strip():
        raise ValueError("The uploaded file is empty. Please upload a valid chat file.")

    # Regular expression to extract timestamps, users, and messages
    pattern = r"(\d{1,2}[\/.-]\d{1,2}[\/.-]\d{2,4},? \d{1,2}:\d{2} ?(?:AM|PM)?) - ([^:]+): (.+)"


    messages = re.findall(pattern, data)

    if not messages:
        raise ValueError("No valid messages were found in the file. Please check the format.")

    # Creating DataFrame
    df = pd.DataFrame(messages, columns=['message_date', 'user', 'message'])

    # Convert the date column to datetime format
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format="%d/%m/%y, %H:%M", errors='coerce')

    except Exception as e:
        raise ValueError(f"Date parsing failed: {e}")

    # Drop rows where date conversion failed
    df = df.dropna(subset=['message_date'])
  

    # Add an 'only_date' column for daily timeline analysis
    df['only_date'] = df['message_date'].dt.strftime('%Y-%m-%d')  # Ensures correct format


    # Extract additional time-related features
    df['year'] = df['message_date'].dt.year
    df['month'] = df['message_date'].dt.month_name()
    df['month_num'] = df['message_date'].dt.month
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute

    # Create a time period column for heatmaps
    df['period_24hr'] = df['hour'].astype(str) + "-" + (df['hour'] + 1).astype(str)

    return df
