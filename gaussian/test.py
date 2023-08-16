import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
import pandas as pd

# Define the Matérn kernel with the desired smoothness parameter (nu)
nu = 2 # Smoothness parameter, adjust as needed
length_scale = 2 # Length scale parameter
noise_level = 0.5
kernel = Matern(length_scale=length_scale, nu=nu)

# True underlying function
# def true_function(x):
#     return np.sin(2 * np.pi * x)

# Simulated active learning loop
def active_learning(X_pool, y_pool, num_iterations, kernel):
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=noise_level)

    selected_X = []
    selected_y = []

    # Initialize with a random data point
    initial_index = np.random.choice(len(X_pool))
    selected_X.append(X_pool[initial_index])
    selected_y.append(y_pool[initial_index])

    # Remove initial point from candidate pool
    X_pool = np.delete(X_pool, initial_index)
    y_pool = np.delete(y_pool, initial_index)


    max_std = 0

    for _ in range(num_iterations - 1):
        # Select 10 random indices
        random_indices = np.random.choice(len(X_pool), size=10, replace=False)

        # Create x_available and y_available arrays
        x_available = X_pool[random_indices]
        y_available = y_pool[random_indices]
        #x_available = X_pool
        #y_available = y_pool

        gpr.fit(np.array(selected_X).reshape(-1, 1), np.array(selected_y))

        # Calculate the model's uncertainty for each candidate point
        stds = []
        for candidate_X in x_available:
            candidate_X = np.array([candidate_X])

            try:
                candidate_y, candidate_std = gpr.predict(candidate_X.reshape(-1, 1), return_std=True)
            except:
                continue

            max_std = max(candidate_std, max_std)

            stds.append(candidate_std)

        # Choose the point with the highest uncertainty reduction
        selected_index = np.argmax(stds)

        #print(f"SELECTEDDDD!! : {selected_X} - {cand}")

        # Add the selected data point to the training set
        selected_X.append(x_available[selected_index])
        selected_y.append(y_available[selected_index])

        # Remove the selected point from the pool
        X_pool = np.delete(X_pool, selected_index)
        y_pool = np.delete(y_pool, selected_index)

    print(max_std)

    return selected_X, selected_y

# Load the CSV file into a DataFrame
# Get the path of the directory containing the Python file
script_dir = os.path.dirname(__file__)

# # Construct the relative path to the CSV file
csv_file = os.path.join(script_dir, "..", "N1_trees_2018_for_Arun.csv")

data = pd.read_csv(csv_file, encoding="iso-8859-1")

# # Extract the values of HT_ft and DBH_inch columns
ht_values = data["HT_ft"]
dbh_values = data["DBH_inch"]

# Create a scatter plot
# plt.figure(figsize=(10, 6))  # Set the figure size
# plt.scatter(dbh_values, ht_values, color='blue', alpha=0.5)  # Scatter plot
# plt.title("Scatter Plot of HT_ft vs DBH_inch")
# plt.xlabel("DBH (inches)")
# plt.ylabel("Height (feet)")
# plt.grid(True)
# plt.show()


# Initial pool of candidate data points with noise
#X_pool = np.linspace(0, 1, 1000)  # Starting with a large candidate pool
#y_pool = true_function(X_pool) + np.random.normal(scale=0.1, size=X_pool.shape)  # Adding noise
#y_pool = true_function(X_pool)

X_pool = np.array(ht_values)
y_pool = np.array(dbh_values)

# Perform active learning
num_iterations = 100
selected_X, selected_y = active_learning(X_pool, y_pool, num_iterations, kernel)

# Create a test set to evaluate the model's predictions
X_test = np.linspace(0, 90, 1000)
# y_test = true_function(X_test)

# Fit the Gaussian Process model to the selected data points
#kernel = RBF(length_scale=0.1)

final_gpr = GaussianProcessRegressor(kernel=kernel, alpha=noise_level)
final_gpr.fit(np.array(selected_X).reshape(-1, 1), np.array(selected_y))

# Get the model's predictions and uncertainty for the test set
y_pred, y_std = final_gpr.predict(X_test.reshape(-1, 1), return_std=True)
y_std = 5*y_std
print(y_std)

# Plot the results
plt.figure(figsize=(10, 6))
#plt.plot(X_pool, true_function(X_pool), label='True Function')
plt.scatter(selected_X, selected_y, color='g', marker='x', label='Selected Data')
plt.plot(X_test, y_pred, color='b', label='GP Predictions')
plt.fill_between(X_test, y_pred - y_std, y_pred + y_std, alpha=0.3, color='b', label='Uncertainty')
plt.xlabel('Height')
plt.ylabel('DBH')
plt.legend()
plt.title('Active Learning with Gaussian Process Regression')
plt.show()