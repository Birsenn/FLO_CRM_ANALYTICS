import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

df_ = pd.read_csv("/Users/birsenbayat/Desktop/miuul/PythonProgrammingForDataScience/CRM_Analitigi/FLOMusteriSegmentasyonu/flo_data_20k.csv")
df = df_.copy()


df.head()

#First look at data

df.head(10)
df.columns
df.shape
df.describe().T
df.isnull().sum()
df.dtypes

#Omnichannel customers shop both online and offline platforms.
#We create new variables for the total number of purchases and spending of each customer.

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]

df.head()

#By examining the variable types, we convert the type of variables that express date to date.
df.dtypes
df["first_order_date"] = df["first_order_date"].apply(pd.to_datetime)
df["last_order_date"] = df["last_order_date"].apply(pd.to_datetime)
df["last_order_date_online"] = df["last_order_date_online"].apply(pd.to_datetime)
df["last_order_date_offline"] = df["last_order_date_offline"].apply(pd.to_datetime)

#Let's look at the distribution of the number of customers in the shopping channels, the total number of products purchased, and the total expenditures.
analysing = df.groupby("order_channel").agg({"master_id": "count",
                                 "order_num_total": "sum",
                                 "customer_value_total": "sum"})


#Let's list the top 10 customers with the most revenue.
df.sort_values(by="customer_value_total", ascending=False).head(10)

#Let's list the top 10 customers with the most orders.
df.sort_values(by="order_num_total", ascending=False).head(10)

#Let's functionalize the data preparation process.

def dataset_preparing(dataframe):
    dataframe.dropna(inplace=True)
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_online"] + dataframe["customer_value_total_ever_offline"]

    dataframe["first_order_date"] = dataframe["first_order_date"].apply(pd.to_datetime)
    dataframe["last_order_date"] = dataframe["last_order_date"].apply(pd.to_datetime)
    dataframe["last_order_date_online"] = dataframe["last_order_date_online"].apply(pd.to_datetime)
    dataframe["last_order_date_offline"] = dataframe["last_order_date_offline"].apply(pd.to_datetime)

    return dataframe

#using function for data preparation
df = df_.copy()
df.head()
dataset_preparing(df)

#Calculating RFM Metrics
#Step 1: We will define Recency, Frequency and Monetary.
#Step 2: We will assign the metrics you calculated to a variable named rfm.

df["last_order_date"].max() #we will find the last date ordered and decide on the analysis date.

today_date = dt.datetime(2021, 6, 2)

rfm = df.groupby("master_id").agg({"last_order_date": lambda x: (today_date - x.max()).days,
                                   "order_num_total": "sum",
                                   "customer_value_total": "sum"})

rfm.columns = ["recency", "frequency", "monetary"]
rfm.head()

#Calculation of RF Score
#Step 1: We will convert the Recency, Frequency and Monetary metrics to scores between 1-5 with the help of qcut.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels = [5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

#We will express recency_score and frequency_score as a single variable and save it as RF_SCORE.
rfm["RF_SCORE"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))
rfm.shape

#Definition of RF Score as Segments
#Step 1: We will make segment definitions for the generated RF scores.
#Step 2: We will convert the scores into segments with the help of the seg_map below.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)
rfm.head()
rfm.shape

#Action

#Step 1: Let's examine the recency, frequency and monetary averages of the segments.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#Step 2: With the help of RFM analysis, let's find the customers in the relevant profile for the 2 cases given below and save the customer IDs as csv.
#By presenting this csv file to the relevant units, we will ensure that work is done on these customers.

#a. FLO includes a new women's shoe brand. The product prices of the brand it includes are above the general customer preferences.
#For this reason, it is desired to contact the customers in the profile that will be interested in the promotion of the brand and product sales.
#Those who shop from loyal customers (champions, loyal_customers) and women are the customers to be contacted privately.
#Save the id numbers of these customers to the csv file.

rfm = rfm.reset_index()
rfm = rfm.merge(df[["master_id", "interested_in_categories_12"]], how = 'left')
rfm.head()
rfm.shape

deneme = rfm.loc[((rfm["segment"] == "champions") | (rfm["segment"] == "loyal_customers")) & (rfm["interested_in_categories_12"].str.contains("KADIN")), ["master_id"]]
deneme.shape
deneme.head()

deneme.to_csv("rfm_a.csv")

#b.Nearly 40% discount is planned for Men's and Children's products. Previously interested in categories related to this discount
#good customers but not to be lost customers who have not shopped for a long time, those who are asleep and new customers
#want to be specifically targeted. Save the ids of the customers in the appropriate profile to the csv file.

target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","hibernating","new_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK"))|(df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("indirim_hedef_müşteri_ids.csv", index=False)

#In this way, we have divided the customers into segments. By examining these segments in certain breakdowns, it is necessary to focus on which points 
#we can make the interpretation and reach the target audience customer. We can organize campaigns for the necessary segments, we can regain the necessary segments.
