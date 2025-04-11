def detect_frequent_locations(df):
    df['hour'] = df['timestamp'].dt.hour
    night = df[(df['hour'] >= 22) | (df['hour'] < 6)]  # Home
    day = df[(df['hour'] >= 9) & (df['hour'] < 18)]   # Work

    home = night.groupby(['latitude', 'longitude']).size().idxmax()
    work = day.groupby(['latitude', 'longitude']).size().idxmax()

    return {'home': home, 'work': work}
