# TASK - 3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score

data = pd.read_csv('merged_transactions_updated.csv')


# Counting transactions based on each CustomerID
customer_features = data.groupby('CustomerID').agg(
    total_spent=('CalculatedTotalValue', 'sum'),
    transaction_count=('TransactionID', 'count'),
    avg_transaction_value=('CalculatedTotalValue', 'mean')
).reset_index()

# Based on Region
customer_profile = data[['CustomerID', 'CustomerName', 'Region']].drop_duplicates()

# Merging region and customer transactions
customer_data = pd.merge(customer_profile, customer_features, on='CustomerID', how='left')

customer_data.fillna(0, inplace=True)


# For clustering
scaler = StandardScaler()
scaled_data = scaler.fit_transform(customer_data[['total_spent', 'transaction_count', 'avg_transaction_value']])

inertia = []
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_data)
    inertia.append(kmeans.inertia_)



optimal_k = 4
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
clusters = kmeans.fit_predict(scaled_data)

customer_data['Cluster'] = clusters

db_index = davies_bouldin_score(scaled_data, clusters)

print(f'Davies-Bouldin Index: {db_index}')

pca = PCA(n_components=2)
pca_components = pca.fit_transform(scaled_data)

plt.figure(figsize=(8, 6))
sns.scatterplot(x=pca_components[:, 0], y=pca_components[:, 1], hue=customer_data['Cluster'], palette='Set1', s=100)
plt.title(f'Customer Segments (K={optimal_k})')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend(title='Cluster')
plt.show()



