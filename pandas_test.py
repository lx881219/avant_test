"""
Pandas Test:

Part 1)
 *  Make a new DataFrame with the data below:

rng = date_range('1/1/2011', periods=72, freq='H')
ts = Series(randn(len(rng)), index=rng)

 * Return a series where the absolute difference between a number and the next number in the series is less than .5


 * Plot and show a Histogram of the Series


 * Give me the rolling average of the series over the last 5 hours in a new column on a DataFrame


 * Change any negative numbers in the new rolling average column to 0


Part 2)

 * Take your DataFrame and put it into Excel.
        * Make the width of the columns 20
        * Hide the gridlines on the excel sheet



"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

rng = pd.date_range('1/1/2011', periods=72, freq='H')
values = [np.random.randn()]
while len(values) < len(rng):
    value = np.random.randn()
    if abs(values[-1]-value) < 0.5:
        values.append(value)
ts = pd.Series(values, index=rng)

# Create the DataFrame
df = pd.DataFrame(ts, columns = ['value'])

# Plot and show a Histogram of the Series
ts.plot(kind='hist')

# Give me the rolling average of the series over the last 5 hours in a new column on a DataFrame
data_mean = pd.rolling_mean(df['value'], window=5)
df['rolling_average'] = data_mean

#Change any negative numbers in the new rolling average column to 0
df['rolling_average'].apply(lambda x: 0 if x < 0 else x)

#part 2)
writer = pd.ExcelWriter('output.xlsx')
df.to_excel(writer, 'Sheet1')
worksheet = writer.sheets['Sheet1']

# Make the width of the columns 20
worksheet.set_column(0,2,20)

# Hide the gridlines on the excel sheet
worksheet.hide_gridlines

#save the file
writer.save()
