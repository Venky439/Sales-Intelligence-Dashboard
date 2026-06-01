select count(*) from Orders;
select count(*) from orderdetails;
select count(*) from sales_target;
show tables;
select * from orderdetails;
select * from sales_target;
select * from orders;
select round(sum(Amount),2) AS Total_Sales From orderdetails;
select round(sum(Profit),2) AS Profit_Sales From orderdetails;
select round((sum(Profit)/sum(Amount))*100,2) AS Profit_Margin_Percentage From orderdetails;
select Category,round(sum(Profit),2) AS Profit From orderdetails group by Category order by Profit desc;
select Category,round(sum(Amount),2) AS Total_Sales,
                round(sum(Profit),2) AS Profit_Sales,
                round((sum(Profit)/sum(Amount))*100,2) AS Profit_Margin
                From orderdetails group by Category order by Profit_Margin;
# Montly Trend Analysis   
SELECT 
MONTH(o.`Order Date`) AS Month_Number,
ROUND(SUM(od.Amount),2) AS Total_Sales,
ROUND(SUM(od.Profit),2) AS Profit_Sales
FROM orders o
JOIN orderdetails od
ON o.`Order ID` = od.`Order ID`
GROUP BY MONTH(o.`Order Date`)
ORDER BY Month_Number;
# moth wise trend
select od.Category,
	   round(sum(od.Amount),2) AS Actual_Sales,
       round(sum(st.Target),2) AS Sales_Target,
       round(sum(od.Amount)- sum(st.Target),2) AS target_Difference
	   From orderdetails od join sales_target st 
	   on od.Category = st.Category 
       group by od.Category;
# State Wise Performance
select o.State,
               Round(sum(od.Amount),2) as Total_Sales,  
               round(sum(od.Profit),2) as Total_Profit,
               round((sum(Profit)/sum(Amount))*100,2) AS Profit_Margin 
               from orders o 
               join orderdetails od 
               on o.`Order ID` = od.`Order ID` 
               group by o.State 
               Order by Total_Sales desc;  
# So Now we want to highest sales but poor margins  
select o.State,
               Round(sum(od.Amount),2) as Total_Sales,  
               round(sum(od.Profit),2) as Total_Profit,
               round((sum(Profit)/sum(Amount))*100,2) AS Profit_Margin 
               from orders o 
               join orderdetails od 
               on o.`Order ID` = od.`Order ID` 
               group by o.State
               having sum(od.Amount) > 50000
               Order by Profit_Margin asc;   
# Customer Analysis
select CustomerName,
				    Round(sum(od.Amount),2) as Total_Spent,  
					round(sum(od.Profit),2) as Profit_Contribution,
                    count(distinct o.`Order ID`) AS Total_Orders
					from orders o 
					join orderdetails od 
                    on o.`Order ID` = od.`Order ID`
                    group  by CustomerName
                    order by total_Spent desc
                    limit 10;
#Customer Risk Segmentation
select CustomerName,
				    Round(sum(od.Amount),2) as Total_Spent,  
					round(sum(od.Profit),2) as Profit_Contribution,
                    round((sum(Profit)/sum(Amount))*100,2) AS Profit_Margin, 
                    count(distinct o.`Order ID`) AS Total_Orders
					from orders o 
					join orderdetails od 
                    on o.`Order ID` = od.`Order ID`
                    group  by CustomerName
                    having sum(od.Amount) > 5000
                    order by Profit_Margin asc
                    limit 10;
# Monthly Growth Analysis
select month(o.`Order Date`) as Month_Number,
Round(sum(od.Amount),2) as Monthly_Sales,
LAG(Round(sum(od.Amount),2))
over (order by MONTH(o.`Order Date`)) as Previous_Month_Sales
from orders o 
join orderdetails od 
on o.`Order ID` = od.`Order ID`
group by month(o.`Order Date`)
order by Month_Number;
#Rank to  the Customers
select o.CustomerName,
round(sum(od.Amount),2) AS Total_Sales,
rank() Over (order by sum(od.Amount) desc) AS Customer_Rank 
From orders o 
join orderdetails od 
on o.`Order ID` = od.`Order ID` 
group by Customername;

# Dense Rank()
select o.CustomerName,
round(sum(od.Amount),2) AS Total_Sales,
dense_rank() Over (order by sum(od.Amount) desc) AS Dens_Rank 
From orders o 
join orderdetails od 
on o.`Order ID` = od.`Order ID` 
group by Customername;
# Row Numbering
select o.CustomerName,
round(sum(od.Amount),2) AS Total_Sales,
row_number() Over (order by sum(od.Amount) desc) AS Row_Num
From orders o 
join orderdetails od 
on o.`Order ID` = od.`Order ID` 
group by Customername;
# CTE Common Table Expression 
With Customer_Sales AS (
select o.CustomerName,
Round(sum(od.Amount),2) as Total_Sales
from orders o 
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by CustomerName
)
select * from Customer_sales order by Total_Sales desc;
#Customer above Average Sales
With Customer_Sales AS (
select o.CustomerName,
Round(sum(od.Amount),2) as Total_Sales
from orders o 
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by CustomerName
)
select * from Customer_sales where Total_Sales >
(
select avg(Total_Sales) from Customer_Sales 
);
# State Wise Customer Ranking
select o.State,o.CustomerName,
round(sum(od.Amount),2) as Total_Sales,
rank() over(
partition by o.State order by sum(od.Amount) desc 
) AS State_Rank
from orders o 
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by o.State,o.CustomerName;

# State Wise Top Costomers only
with Customer_Sales as(
select o.State,o.CustomerName,
round(sum(od.Amount),2) as Total_Sales
from orders o 
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by o.State,o.CustomerName
),
ranked_Customers as (
select *,rank() over (
partition by State order by Total_Sales desc
) as Customer_Rank 
from Customer_Sales
)
select * from ranked_Customers where Customer_Rank <=3;

# SQL VIEWS creating view for state wise sales
create view state_sales_summary as
select o.State,
round(sum(od.Amount),2) as Total_Sales,
round(sum(od.Profit),2) as Total_Profit,
round(
(sum(od.Profit)/sum(od.Amount))*100,2
) as Profit_Margin
from orders o
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by o.State;
# checking view
select * from state_sales_summary;

select o.CustomerName,round(sum(od.Amount),2) as total_sales,
case
    when round(sum(od.Amount),2) > 1000 Then 'High Sales'
    when round(sum(od.Amount),2) > 500 Then 'Medium Sales'
    else 'Low Sales'
end as Sales_Category
from orders o
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by CustomerName ;


# Stored Procedure
 delimiter //
 create procedure Get_State_Sales()
 begin
 select o.State,
round(sum(od.Amount),2) as Total_Sales,
round(sum(od.Profit),2) as Total_Profit
from orders o
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by o.State;
end //
delimiter ;
call Get_State_Sales();

# particular state sales
delimiter //
 create procedure Get_State_wise_Sales_summary(
 in State_name varchar(50))
 begin
 select o.State,
round(sum(od.Amount),2) as Total_Sales,
round(sum(od.Profit),2) as Total_Profit
from orders o
join orderdetails od
on o.`Order ID` = od.`Order ID`
where o.State = State_name
group by o.State;
end //
delimiter ;
# checking
call Get_State_wise_Sales_summary('Madhya Pradesh');

# Triggers
create table profit_alerts (
Alert_ID int auto_increment primary key,
CustomerName varchar(50),
Profit decimal(10,2),
Alert_Message varchar(255)
);

# Creating a trigger
delimiter //
create trigger negative_profit_alert
after insert
on orderdetails
for each row
begin 
if new.Profit < 0 Then
insert into profit_alerts
(CustomerName, profit, Alert_Message)

values
(
'Unknown Customer',
new.Profit,
'Negative profit transaction detected'
);
end if ;
end//
delimiter ;

# Testing the Trigger
insert into orderdetails 
(`Order ID`,Amount, Profit, Quantity, Category, `Sub-Category`)
values
('Test123', 500, -100, 2,'Electronics','Phones');
 
# checking trigger working or not 
select * from  profit_alerts;

# Before Trigger to validate the amount
delimiter //
create trigger check_amount_before_insert
before insert
on orderdetails
for each row
begin
if new.Amount <=0 then
signal sqlstate'45000'
set message_text = 'Amount must be greater than zero';
end if;
end // 
delimiter ;

# Tesing
insert into orderdetails 
(`Order ID`,Amount, Profit, Quantity, Category, `Sub-Category`)
values
('Test123', -500, 100, 2,'Electronics','Phones');

# Audit table for Profit 
create table profit_audit (
Audit_ID int auto_increment primary key,
Order_ID varchar(50),
Old_Profit decimal(10,2),
New_Profit decimal(10,2),
updated_Time timestamp default current_timestamp
);
 delimiter //
 create trigger profit_update_audit
 after update
 on orderdetails
 for each row
 begin
 if Old.Profit <> new.Profit then
 insert into profit_audit
 (Order_ID, Old_Profit,New_Profit)
 values
 (
 New.`Order ID`,
 Old.Profit,
 new.Profit
 );
 end if;
 end // 
 delimiter ;
 
 # Testing
 Update orderdetails set Profit = 999
 Where `Order ID` = 'Test123';
 
 # Checking from audit table
 select * from profit_audit;

#Before audit
delimiter //
create trigger prevent_extreme_loss

before update
on orderdetails
for each row
begin
if New.Profit < -5000 then
signal sqlstate '45000'
set message_text = 'Profit cannot be less than -5000';
end if;
end //
delimiter ;

# Tesing 
update orderdetails
set Profit = -10000
where `Order ID` = 'TEST123';

# Subqueries
# customer sales whose sales are above average
select 
o.CustomerName,
round(sum(od.Amount),2) as Total_Sales
from orders o
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by CustomerName
having sum(od.Amount) >
(
select Avg(Customer_Total)
from (
select sum(Amount) as Customer_Total
from orderdetails od
join orders o 
on o.`Order ID` = od.`Order ID`
group by o.CustomerName
) as Avg_Table
);

# Customer whose sales are grearter than their state's average sale
select 
o.State,
o.CustomerName,
round(sum(od.Amount),2) As Customer_Sales
from orders o
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by o.CustomerName,o.State
having sum(od.Amount) >
(
select avg(State_Sales) 
from
(
select sum(od2.Amount) as State_Sales
from orders o2
join orderdetails od2
on o2.`Order ID` = od2.`Order ID`
where o2.State = o.State
group by o2.CustomerName
) as state_Avg
);

# Temporary table
create temporary table high_value_customers as 
select 
o.CustomerName,
round(sum(od.Amount),2) as Total_Sales
from orders o 
join orderdetails od
on o.`Order ID` = od.`Order ID`
group by o.CustomerName
Having sum(od.Amount) > 9000;
# Testing
select * from high_value_customers;

# Transactions
start transaction;
update orderdetails
set Profit = Profit + 100
where `Order ID` = 'Test123';
# Checking the Change
select * from orderdetails
where `Order ID` = 'Test123';
# Thats temperory to save "commit" Undo the change "rollback"

# Automating the Sales summary
# Enabling the event_sheduler ON
set global event_scheduler = on ;

create table daily_sales_summary (
Summary_Date date,
Total_Sales decimal(10,2),
Total_Profit decimal(10,2)
);
# Creating the event 
create event daily_sales_event
on schedule every 1 day
do 
insert into daily_sales_summary
select curdate(),
round(sum(Amount),2),
round(sum(Profit),2)
from orderdetails;
# Checking the events
show events ;
# checking the total
select * from daily_sales_summary;

