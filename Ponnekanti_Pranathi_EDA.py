# TASK - 1

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

'''
customers = pd.read_csv("Customers.csv")
products = pd.read_csv("Products.csv")
transactions = pd.read_csv("Transactions.csv")

transactions_with_customers = pd.merge(transactions, customers, on="CustomerID", how="left")

merged_transactions = pd.merge(transactions_with_customers, products, on="ProductID", how="left")


# Since there are two Price columns, we can drop one
merged_transactions = merged_transactions.drop(columns=["Price_y"])

merged_transactions = merged_transactions.rename(columns={"Price_x": "Price"})

merged_transactions.to_csv("merged_transactions_updated.csv", index=False)

print(merged_transactions.head())
'''

# This data is formed after merging the Customers.csv, Products.csv and Transactions.csv for easy visualization
merged_transactions = pd.read_csv("merged_transactions_updated.csv")


# Pre-processing the data to avoid errors 


# 1. Unique Transaction ID Check
unique_transaction_ids = merged_transactions['TransactionID'].is_unique
print(f"TransactionID uniqueness check: {unique_transaction_ids}")

# 2. TotalValue is equal to Price * Quantity
merged_transactions['CalculatedTotalValue'] = merged_transactions['Price'] * merged_transactions['Quantity']

merged_transactions['TotalValue'] = merged_transactions['TotalValue'].round(2)
merged_transactions['CalculatedTotalValue'] = merged_transactions['CalculatedTotalValue'].round(2)

inconsistent_total_values = merged_transactions[merged_transactions['TotalValue'] != merged_transactions['CalculatedTotalValue']]

# Print the inconsistent rows
print("\nRows with Inconsistent TotalValue (Price * Quantity mismatch):")
print(inconsistent_total_values[['TransactionID', 'CustomerID', 'ProductID', 'Quantity', 'TotalValue', 'CalculatedTotalValue']])


'''
# 3. Check if TransactionDate is later than SignupDate
merged_transactions['TransactionDate'] = pd.to_datetime(merged_transactions['TransactionDate'], errors='coerce')
merged_transactions['SignupDate'] = pd.to_datetime(merged_transactions['SignupDate'], errors='coerce')

# Check if the conversion was successful
print(f"Converted TransactionDate to datetime: {merged_transactions['TransactionDate'].dtypes}")
print(f"Converted SignupDate to datetime: {merged_transactions['SignupDate'].dtypes}")

# Now strip time component if only date is needed
merged_transactions['TransactionDate'] = merged_transactions['TransactionDate'].dt.date
merged_transactions['SignupDate'] = merged_transactions['SignupDate'].dt.date

# Re-check where 'TransactionDate' is not later than 'SignupDate'
inconsistent_transactions = merged_transactions[merged_transactions['TransactionDate'] < merged_transactions['SignupDate']]

# Print the inconsistent rows
print("\nRows with TransactionDate not later than SignupDate:")
print(inconsistent_transactions[['TransactionID', 'CustomerID', 'ProductID', 'TransactionDate', 'SignupDate']])

merged_transactions_cleaned = merged_transactions[merged_transactions['TransactionDate'] >= merged_transactions['SignupDate']]

# Save the cleaned dataset to a new CSV file
merged_transactions_cleaned.to_csv("merged_transactions.csv", index=False)
print("\nInconsistent transactions have been removed and saved to 'merged_transactions_cleaned.csv'.")

'''

# 4. Region should be unique for each CustomerID
region_per_customer = merged_transactions.groupby('CustomerID')['Region'].nunique()
region_check = (region_per_customer == 1).all()
print(f"Region uniqueness check for each CustomerID: {region_check}")

# 5. Check if no two product names have the same ProductID
product_id_per_name = merged_transactions.groupby(['ProductName', 'Category', 'Price'])['ProductID'].nunique()
product_name_check = (product_id_per_name == 1).all()
non_unique_products = product_id_per_name[product_id_per_name > 1]
print(f"ProductID uniqueness check for each ProductName: {product_name_check}")
print("\nProduct Names with Non-Unique ProductIDs, Category, or Price:")
for details in non_unique_products.index:
    product_names = merged_transactions[
        (merged_transactions['ProductName'] == details[0]) &
        (merged_transactions['Category'] == details[1]) &
        (merged_transactions['Price'] == details[2])
    ]['ProductID'].unique()
    print(f"Product Name: {details[0]}, Category: {details[1]}, Price: {details[2]}, Product IDs: {product_names}")
    
# 6. Check if no two customers have the same CustomerID
customer_consistency_check = merged_transactions.groupby('CustomerID')[['CustomerName', 'Region', 'SignupDate']].nunique()
inconsistent_customers = customer_consistency_check[(customer_consistency_check > 1).any(axis=1)]
print(f"\nInconsistent CustomerIDs (CustomerName, Region, SignupDate mismatch):")
print(inconsistent_customers)

# Now the original Preprocessing starts
# 7. Checking for null values
null_values = merged_transactions.isnull().sum()
print("\nNull values in each column:")
print(null_values)

# 8. Checking for consistency in date columns (TransactionDate, SignupDate)
print("\nChecking consistency of date columns:")
date_columns = ['TransactionDate', 'SignupDate']
for column in date_columns:
    if merged_transactions[column].dtype != 'datetime64[ns]':
        print(f"Converting {column} to datetime format...")
        merged_transactions[column] = pd.to_datetime(merged_transactions[column])

# 9. Duplicates in the dataset
duplicates_check = merged_transactions.duplicated().sum()
print(f"\nNumber of duplicate rows: {duplicates_check}")

# 10. ProductPrice and Quantity are non-negative
negative_price_quantity_check = (merged_transactions['Price'] >= 0).all() and (merged_transactions['Quantity'] >= 0).all()
print(f"\nPrice and Quantity non-negative check: {negative_price_quantity_check}")

# 11. TotalValue is non-negative
negative_total_value_check = (merged_transactions['TotalValue'] >= 0).all()
print(f"TotalValue non-negative check: {negative_total_value_check}")



# For extracting the business insights

# 1. Categorizing by region and plotting the regions with the most transactions
region_sales = merged_transactions.groupby('Region')['TransactionID'].count().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x=region_sales.index, y=region_sales.values, palette='viridis')
plt.title('Transactions by Region (High to Low)', fontsize=14)
plt.xlabel('Region', fontsize=12)
plt.ylabel('Number of Transactions', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Grouping products by quantity sold and plotting the products with the highest sales
product_sales = merged_transactions.groupby('ProductName')['Quantity'].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x=product_sales.index, y=product_sales.values, palette='plasma')
plt.title('Products Sold by Quantity (High to Low)', fontsize=14)
plt.xlabel('Product Name', fontsize=12)
plt.ylabel('Quantity Sold', fontsize=12)
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()


# 3. Grouping categories by total quantity sold and plotting the categories with the highest sales
category_sales = merged_transactions.groupby('Category')['Quantity'].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x=category_sales.index, y=category_sales.values, palette='inferno')
plt.title('Sales by Category (High to Low)', fontsize=14)
plt.xlabel('Category', fontsize=12)
plt.ylabel('Total Quantity Sold', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 4 Transaction Time
if merged_transactions['TransactionDate'].dtype != 'datetime64[ns]':
    print("Converting TransactionDate to datetime format...")
    merged_transactions['TransactionDate'] = pd.to_datetime(merged_transactions['TransactionDate'])

merged_transactions['TransactionTime'] = merged_transactions['TransactionDate'].dt.time
merged_transactions['TransactionHour'] = merged_transactions['TransactionDate'].dt.hour

transactions_by_hour = merged_transactions.groupby('TransactionHour')['TransactionID'].count()

plt.figure(figsize=(10, 6))
sns.barplot(x=transactions_by_hour.index, y=transactions_by_hour.values, palette='coolwarm')
plt.title('Transactions by Hour of the Day', fontsize=14)
plt.xlabel('Hour of the Day (24-hour format)', fontsize=12)
plt.ylabel('Number of Transactions', fontsize=12)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# 5 Transaction Month
if merged_transactions['TransactionDate'].dtype != 'datetime64[ns]':
    print("Converting TransactionDate to datetime format...")
    merged_transactions['TransactionDate'] = pd.to_datetime(merged_transactions['TransactionDate'])

merged_transactions['TransactionMonth'] = merged_transactions['TransactionDate'].dt.month

transactions_by_month = merged_transactions.groupby('TransactionMonth')['TransactionID'].count()

transactions_by_month = transactions_by_month.sort_index()

plt.figure(figsize=(10, 6))
sns.barplot(x=transactions_by_month.index, y=transactions_by_month.values, palette='crest')
plt.title('Transactions by Month of the Year', fontsize=14)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Number of Transactions', fontsize=12)
plt.xticks(ticks=range(12), labels=['January', 'February', 'March', 'April', 'May', 'June', 
                                    'July', 'August', 'September', 'October', 'November', 'December'], rotation=45)
plt.tight_layout()
plt.show()




# 6 Grouping by CustomerID and counting the number of transactions of each customer
top_customers = (
    merged_transactions.groupby('CustomerID')
    .agg(TransactionCount=('TransactionID', 'count'))  
    .reset_index()
    .sort_values(by='TransactionCount', ascending=False)  
    .head(15)  
)

if 'CustomerName' in merged_transactions.columns:
    top_customers = top_customers.merge(
        merged_transactions[['CustomerID', 'CustomerName']].drop_duplicates(),
        on='CustomerID',
        how='left'
    )

# Plotting the top 15 customers
plt.figure(figsize=(12, 8))
sns.barplot(
    data=top_customers,
    y='CustomerName' if 'CustomerName' in top_customers.columns else 'CustomerID',
    x='TransactionCount',
    palette='viridis'
)
plt.title('Top 15 Customers Based on Number of Transactions', fontsize=16)
plt.xlabel('Number of Transactions', fontsize=14)
plt.ylabel('Customer', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.show()
