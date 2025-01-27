# TASK - 2

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load merged_transactions_updates.csv and customersTest.csv
merged_transactions_updates = pd.read_csv('merged_transactions_updated.csv')
customers_test = pd.read_csv('customersTest.csv')

# Ensure 'TransactionDate' is in datetime format
if merged_transactions_updates['TransactionDate'].dtype != 'datetime64[ns]':
    merged_transactions_updates['TransactionDate'] = pd.to_datetime(merged_transactions_updates['TransactionDate'])

# Extract the month from TransactionDate (for trend analysis)
merged_transactions_updates['TransactionMonth'] = merged_transactions_updates['TransactionDate'].dt.month

# Check if 'Region' and other necessary columns are correctly loaded
print(merged_transactions_updates.columns)  # Verify if 'Region' is present in this DataFrame

# For training, use merged_transactions_updates where 'Region' and other info are available
region_product_sales = merged_transactions_updates.groupby(['Region', 'TransactionMonth', 'ProductName'])['Quantity'].sum().reset_index()

# Plot the sales data to understand trends
plt.figure(figsize=(10, 6))
sns.barplot(x=region_product_sales['ProductName'], y=region_product_sales['Quantity'], hue=region_product_sales['Region'], palette='Set1')
plt.title('Product Sales by Region and Month')
plt.xlabel('Product Name')
plt.ylabel('Quantity Sold')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Merge customer info with transactions for testing
merged_test_data = pd.merge(customers_test, merged_transactions_updates, on='CustomerID', how='left')

# Now let's proceed with generating lookalike recommendations based on 'Region' and 'TransactionMonth'

lookalike_recommendations = {}

for _, customer in customers_test.iterrows():
    # For each customer in the test set, find others from the same region and similar signup month
    region = customer['Region']
    signup_month = pd.to_datetime(customer['SignupDate']).month

    # Filter transactions by the same region and similar signup month
    potential_lookalikes = merged_transactions_updates[
        (merged_transactions_updates['Region'] == region) & 
        (merged_transactions_updates['TransactionMonth'] == signup_month)
    ]
    
    # Get unique customer IDs for lookalikes in the same region and month
    lookalikes = potential_lookalikes['CustomerID'].unique()
    
    # Calculate a simple similarity score based on the number of matching transactions
    lookalike_scores = {}
    for lookalike in lookalikes:
        common_transactions = merged_transactions_updates[
            (merged_transactions_updates['CustomerID'] == lookalike) & 
            (merged_transactions_updates['Region'] == region) & 
            (merged_transactions_updates['TransactionMonth'] == signup_month)
        ]
        score = common_transactions.shape[0]  # Number of transactions (can be adjusted)
        lookalike_scores[lookalike] = score

    # Sort and pick top 3 lookalikes
    sorted_lookalikes = sorted(lookalike_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    lookalike_recommendations[customer['CustomerID']] = sorted_lookalikes

# Save the lookalike recommendations to a CSV
lookalike_df = pd.DataFrame([
    {'CustomerID': key, 'Lookalikes': str(value)} for key, value in lookalike_recommendations.items()
])

lookalike_df.to_csv('Lookalike.csv', index=False)

print(lookalike_df.head())
