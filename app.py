import streamlit as st
import pandas as pd
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Title
st.title("Sales Intelligence Dashboard")
st.write("AI Powered Analytics Dashboard")

#sales_target = "select * from sales_target"
target_data = pd.read_csv("Sales target.csv")
orders = pd.read_csv("List_of_Orders.csv")
orderdetails = pd.read_csv("Order Details.csv")
#data = data.loc[:, ~data.columns.duplicated()]
data = pd.merge(orders,orderdetails,on='Order ID')
#data = data.loc[:, ~data.columns.duplicated()]
filtered_data = data.copy()

# Multi Filter Category
selected_categories = st.sidebar.multiselect(
"Select Category",
filtered_data['Category'].unique(),
default=filtered_data['Category'].unique()    
)

filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]

# State filter
selected_state = st.sidebar.selectbox(
"Select State",
['All']+list(filtered_data['State'].unique())    
)     

if selected_state != 'All':
    filtered_data = filtered_data[filtered_data['State'] == selected_state]

# City filter
selected_city = st.sidebar.selectbox(
"Select City",
['All']+list(filtered_data['City'].unique())    
) 

if selected_city != 'All':
    filtered_data = filtered_data[filtered_data['City'] == selected_city]
    

# Date filter
filtered_data['Order Date'] = pd.to_datetime(filtered_data['Order Date'],dayfirst=True)
st.sidebar.subheader("Date Filter")
start_date = st.sidebar.date_input(
"Start Date",
filtered_data['Order Date'].min()    
)

end_date = st.sidebar.date_input(
"End Date",
filtered_data['Order Date'].max()    
)

filtered_data = filtered_data[
(filtered_data['Order Date'] >= 
pd.to_datetime(start_date))
&
(filtered_data['Order Date'] <= 
pd.to_datetime(end_date))                              
]

#Feature wngineering
filtered_data['Performance'] = filtered_data['Profit'].apply(
    lambda x: 'Loss' if x < 0 else 'Profit'
)

# Merging sales_target and orders with Month column
filtered_data['Month'] = filtered_data['Order Date'].dt.strftime('%b-%y')
st.dataframe(filtered_data)
# Target vs Actual
target_data.rename(
columns={'Month of Order Date':'Month'},
inplace=True    
)

monthly_actual = filtered_data.groupby(['Month','Category'])['Amount'].sum().reset_index()
target_vs_actual = pd.merge(monthly_actual,target_data,on=['Month','Category'])
target_vs_actual['Achievement %'] = round((target_vs_actual['Amount'] / target_vs_actual['Target']),2) * 100
st.write("Target vs Actual Table")
st.dataframe(target_vs_actual)

# Setting Tabs
tab1, tab2, tab3, tab4 = st.tabs([
"Overview",
"Sales Analysis",
"Forecasting",
"AI Assistant"    
])

# KPI's
total_sales = filtered_data['Amount'].sum()
total_profit = filtered_data['Profit'].sum()
total_orders = filtered_data['Order ID'].nunique()
profit_margin = (
total_profit / total_sales
) * 100


# Inserting the data into the tabs


# KPI Cards
with tab1:

    st.subheader("Business Overview")


    col1,col2,col3,col4 = st.columns(4)

    col1.metric(
        "Total Sales",
        round(total_sales,2)
    )

    col2.metric(
        "Total Profit",
        round(total_profit,2)
    )

    col3.metric(
        "Total Orders",
        total_orders
    )

    col4.metric(
        "Profit Margin %",
        round(profit_margin,2)
    )


# Chart
sub_category_sales = filtered_data.groupby(
'Sub-Category'
)['Amount'].sum()

fig, ax = plt.subplots()
sub_category_sales.plot(
kind='bar',
ax=ax
)

plt.title("Sub Category Wise Sales")
plt.xlabel("Sub-Category")
plt.ylabel("Sales")
#st.pyplot(fig)

# Trend Chart
filtered_data['Order Date'] = pd.to_datetime(filtered_data['Order Date'])
monthly_sales = filtered_data.groupby(filtered_data['Order Date'].dt.month)['Amount'].sum()
fig2, ax2 = plt.subplots()
monthly_sales.plot(kind='line',
marker = 'o',
ax = ax2                   
)
plt.title("Monthly sales Trend")
plt.xlabel('Month')
plt.ylabel("Sales")
#st.pyplot(fig2)

top_category = filtered_data.groupby('Sub-Category')['Amount'].sum().idxmax()
top_sales_category = filtered_data.groupby('Sub-Category')['Amount'].sum().max()
high_profit_category = filtered_data.groupby('Sub-Category')['Profit'].sum().max()
highest_profit = filtered_data.groupby('Sub-Category')['Profit'].sum().idxmax()
lowest_category = filtered_data.groupby('Sub-Category')['Amount'].sum().idxmin()
low_sales_category = filtered_data.groupby('Sub-Category')['Amount'].sum().min()
low_profit_category = filtered_data.groupby('Sub-Category')['Profit'].sum().min()
low_profit = filtered_data.groupby('Category')['Profit'].sum().idxmin()
low_sales = filtered_data.groupby('Category')['Amount'].sum().idxmin()
high_sales = filtered_data.groupby('Category')['Amount'].sum().idxmax()
high_profit = filtered_data.groupby('Category')['Profit'].sum().idxmax()

# AI Business OInsights
st.subheader("AI business Insights")

st.success(
f"Top performing Sub-Category is{top_category} with Sales of {round(high_profit_category),2}"    
)
st.warning(
f"{lowest_category} has lowest profit performance"   
)

# Anomaly Alerts
filtered_data['Z_Score'] = zscore(filtered_data['Profit'])
Anomalies = filtered_data[filtered_data['Z_Score'].abs() > 3]
st.subheader("Anomaly Alerts")
st.write(
Anomalies[[
'Order ID',
'Amount',
'Profit',
'Z_Score'    
]]
)

# Top 5 Customers
top_customers = filtered_data.groupby('CustomerName')['Amount'].sum().sort_values(ascending=False).head(5)   
st.subheader("Top 5 Customers")
#st.bar_chart(top_customers)

# Forecast Prediction
monthly_Sales = filtered_data.groupby(filtered_data['Order Date'].dt.month)['Amount'].sum().reset_index()
X = monthly_Sales[['Order Date']]
y = monthly_Sales['Amount']
model = LinearRegression()
model.fit(X,y)
future_month = [[13]]
prediction = model.predict(future_month)
st.subheader("Sales Forecast")
st.success(f"Predicted Sales for next month: {round(prediction[0],2)}")
# Visualization 
fig3, ax3 = plt.subplots() 
plt.plot(
monthly_Sales['Order Date'],
monthly_Sales['Amount'],
marker='o'    
)
plt.scatter(
13,
prediction,
s=100    
)
plt.title("Sales Forecast")
plt.xlabel("Month")
plt.ylabel("Sales")
#st.pyplot(fig3)
with tab3:
    st.subheader("Sales Forecasting")
    st.pyplot(fig3)

# Actual Sales vs Target Sales
fig4, ax4 = plt.subplots(figsize=(10,5))
ax4.bar(
target_vs_actual['Category'],
target_vs_actual['Amount'],
label='Actual_Sales'    
)
ax4.bar(
target_vs_actual['Category'],
target_vs_actual['Target'],
alpha=0.5,   
label='Target'
)
plt.title(" Actual vs Target Sales")
plt.xlabel('Category')
plt.ylabel('Sales')
plt.legend()
#st.pyplot(fig4)


# Checking Target missed data
target_vs_actual['Status'] = (target_vs_actual['Achievement %'] >= 100)

missed_targets = target_vs_actual[target_vs_actual['Status']==False]
st.subheader("Target Missed Alerts")
st.dataframe(missed_targets)

# Alerting if any loss occurs
if len(missed_targets) > 0:
    st.warning("Some Categories missed the targets")
else:
    st.success("All targets achieved")    

def generate_recommendation(row):
    if row['Achievement %'] < 80:
        return "High Risk - Immediate Attention Needed"
    elif row['Achievement %'] < 100:
        return "Needs Improvement"
    else:
        return "Performing Well"

# Recommendation Analysis
target_vs_actual['Recommendation'] = target_vs_actual.apply(
generate_recommendation,
axis=1    
)

st.subheader("AI Recommendations")
st.dataframe(
target_vs_actual[
['Category',
'Achievement %',
'Recommendation']    
]    
)  

# User Can ask the question
with tab4:
    st.subheader("AI Analytics Assistant")
    question = st.text_input("Ask a business question")


    if "highest sales" in question.lower():
       st.success(f"{high_sales} has highest sales")
    elif "highest profit" in question.lower():
       st.success(f"{high_profit} has highest profit")
    elif "lowest sales" in question.lower():
       st.warning(f"{low_sales} has lowest Sales")
    elif "lowest profit" in question.lower():
       st.warning(f"{low_profit} has lowest profit")   
    else:
       st.error("Question not understand")     


# Loss making orders
loss_data = filtered_data[filtered_data['Performance'] == 'Loss']
st.subheader("Loss Making Orders")
st.dataframe(loss_data)

# Alerts
if total_profit < 0:
    st.error("Business is in Loss")
else:
    st.success("Business is in Profit")    

# Top Loss Products
top_loss_products = loss_data.groupby('Sub-Category')['Profit'].sum().sort_values().head(10)
st.write("Top Loss Making Products")
st.dataframe(top_loss_products)
fig5, ax5 = plt.subplots()
top_loss_products.plot(
kind='bar',ax=ax5)

plt.title("Top Loss Making Products")
plt.xlabel("Sub-Category")
plt.ylabel("Loss")
#st.pyplot(fig5)


# Assigning Tabs
with tab2:
    st.subheader("Sales Analysis")
    st.pyplot(fig)
    st.pyplot(fig2)
    st.pyplot(fig4)
    st.pyplot(fig5)
    st.bar_chart(top_customers)


csv = filtered_data.to_csv(index=False)
st.download_button(
label="Download CSV Report",
data = csv,
file_name="Sales_report.csv",
mime="text/csv"    
) 

# Target vs Actual file
csv2 = target_vs_actual.to_csv(index=False)
st.download_button(
label="Download Target CSV Report",
data = csv2,
file_name="Target_report.csv",
mime="text/csv"    
)    
