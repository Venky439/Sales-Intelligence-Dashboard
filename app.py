import streamlit as st
import pandas as pd
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import google.generativeai as genai

# Integrating the google gemini
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"])

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# Title
st.title("Sales Intelligence Dashboard")
st.write("AI Powered Analytics Dashboard")



#sales_target = "select * from sales_target"
#target_data = pd.read_csv("Sales target.csv")
#orders = pd.read_csv("List_of_Orders.csv")
#orderdetails = pd.read_csv("Order Details.csv")
# User Can Upload the file
st.sidebar.subheader("Upload Files")
orders_file = st.sidebar.file_uploader(
    "Upload Orders File",
    type=["csv"]
)

orderdetails_file = st.sidebar.file_uploader(
    "Upload Order Details File",
    type=["csv"]
)

target_file = st.sidebar.file_uploader(
    "Upload Target File",
    type=["csv"]
)

if (
    orders_file is not None
    and
    orderdetails_file is not None
    and
    target_file is not None
):

    orders = pd.read_csv(
        orders_file
    )

    orderdetails = pd.read_csv(
        orderdetails_file
    )

    target_data = pd.read_csv(
        target_file
    )

else:
    st.stop()


#data = data.loc[:, ~data.columns.duplicated()]
data = pd.merge(orders,orderdetails,on='Order ID')
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
    st.subheader("AI Executive Summary")

if st.button("Generate Executive Summary"):

    prompt = f"""
    You are a Senior Business Analyst.

    Total Sales = {total_sales}
    Total Profit = {total_profit}
    Total Orders = {total_orders}
    Profit Margin = {profit_margin}

    Top Sales Category = {high_sales}
    Lowest Sales Category = {low_sales}

    Create a management summary.
    Include:
    1. Key Findings
    2. Risks
    3. Recommendations
    """

    response = gemini_model.generate_content(prompt)

    st.success(response.text)

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
state_wise = filtered_data.groupby('State')['Amount'].sum().idxmax()
state_profit= filtered_data.groupby('State')['Profit'].sum().idxmax()
city_wise = filtered_data.groupby('City')['Amount'].sum().idxmax()
city_profit = filtered_data.groupby('City')['Profit'].sum().idxmax()
top_products = filtered_data.groupby('Sub-Category')['Amount'].sum().head(5)
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
#st.subheader("Top 5 Customers")
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

if st.button("Generate AI Recommendations"):

    prompt = f"""
    Category Performance:

    {target_vs_actual[['Category','Achievement %']].to_string()}

    Give recommendations for each category.

    Mention:
    - High Risk Categories
    - Improvement Areas
    - Growth Opportunities
    """

    response = gemini_model.generate_content(prompt)

    st.write(response.text)


# User Can ask the question
with tab4:

    st.subheader("AI Analytics Assistant")
    question = st.text_input(
        "Ask a business question"
    )

    if question:

        prompt = f"""
        You are a Senior Business Analyst.

        Sales Summary:
        Total Sales = {round(total_sales,2)}
        Total Profit = {round(total_profit,2)}
        Total Orders = {total_orders}
        Profit Margin = {round(profit_margin,2)}
        Top Sales Category = {high_sales}
        Top Profit Category = {high_profit}
        Lowest Sales Category = {low_sales}
        Lowest Profit Category = {low_profit}
        Top State Sales = {state_wise}
        Top State Profit = {state_profit}
        Top City Sales = {city_wise}
        Top City Profit = {city_profit}

        User Question:
        {question}

        Give a clear business answer.
        """

        response = gemini_model.generate_content(
            prompt
        )
        
        st.success(
            response.text
        )


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

# AI insights
if st.button("Generate AI Insights"):

    prompt = f"""
    Analyze this sales data.

    Total Sales: {total_sales}
    Total Profit: {total_profit}
    Profit Margin: {profit_margin}
    Top Category: {high_sales}
    Lowest Category: {low_sales}

    Give:
    1. Key Findings
    2. Risks
    3. Recommendations
    """

    response = gemini_model.generate_content(prompt)
    st.subheader("AI Executive Summary")
    st.write(response.text)


st.subheader("Management Report")
if st.button("Generate Management Report"):

    prompt = f"""
    Create a professional management report.

    Total Sales = {total_sales}
    Total Profit = {total_profit}
    Profit Margin = {profit_margin}
    Top Category = {high_sales}
    Lowest Category = {low_sales}

    Include:
    Executive Summary
    Sales Performance
    Risk Areas
    Recommendations
    """

    response = gemini_model.generate_content(prompt)
    st.text_area(
        "Management Report",
        response.text,
        height=400
    )



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
