import pandas as pd

data = pd.read_csv(r'Data\cleaned_data\processed_data.csv')

test_data = data.sample(20, random_state=42)

test_data = test_data.drop('Label', axis=1)

test_data.to_csv('Data/test_data_stream.csv', index=False)

print('Test Data Created Successfully!!')