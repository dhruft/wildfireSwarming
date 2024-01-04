import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

# Load the CSV file into a DataFrame
# Get the path of the directory containing the Python file
script_dir = os.path.dirname(__file__)

# # Construct the relative path to the CSV file
csv_file = os.path.join(script_dir, "..", "PFDP_Metric_Dataset_2016_Dhruva.csv")

data = pd.read_csv(csv_file, encoding="iso-8859-1")

# # Extract the values of HT_ft and DBH_inch columns
ht_values = data["Height_m"]
dbh_values = data["DBH_cm"]

maxX = 0
maxY = 0
minX = 10000
minY = 100000

for index, row in data.iterrows():
    
    maxX = max(maxX, row["Grid_X"])
    maxY = max(maxY, row["Grid_Y"])

    minX = min(minX, row["Grid_X"])
    minY = min(minY, row["Grid_Y"])

print(minX, minY)
print(maxX, maxY)


plt.figure(figsize=(10, 6))  # Set the figure size
plt.scatter(dbh_values, ht_values, color='blue', alpha=0.5)  # Scatter plot
plt.title("Scatter Plot of HT_ft vs DBH_inch")
plt.xlabel("DBH (inches)")
plt.ylabel("Height (feet)")
plt.grid(True)
plt.show()