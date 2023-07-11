#BUSINESS PROBLEM

#FLO is one of the biggest shoes and clothing company wants to determine roadmap for sales and marketing.
#The potential value that existing customers will provide to the company in the future so that the company can make
#a medium-long-term plan needs to be estimated.

#Data preparation

df_ = pd.read_csv("/Users/birsenbayat/Desktop/miuul/PythonProgrammingForDataScience/CRM_Analitigi/FLOCLTVPrediction/flo_data_20k.csv")
df = df_.copy()

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
pd.set_option('display.max_columns', None)
pd.set_option("display.width", 500)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

#Define the outlier_thresholds and replace_with_thresholds functions needed to suppress outliers

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return round(low_limit), round(up_limit)

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    # dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

#if "order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline",
#"customer_value_total_ever_online" columns have outliers, suppress them

df.describe().T

replace_with_thresholds(df, "order_num_total_ever_online")
replace_with_thresholds(df, "order_num_total_ever_offline")
replace_with_thresholds(df, "customer_value_total_ever_offline")
replace_with_thresholds(df, "customer_value_total_ever_online")

#when we look at the data describe, we saw that there was outliers because max and std values changed

#Omnichannel means that customers shop from both online and offline platforms.
#We will create new variables for the total number of purchases and spend of each customer

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]


#We will examine the variable types and convert the type of variables that express dates to date.

df.dtypes
df["first_order_date"] = df["first_order_date"].apply(pd.to_datetime)
df["last_order_date"] = df["last_order_date"].apply(pd.to_datetime)
df["last_order_date_online"] = df["last_order_date_online"].apply(pd.to_datetime)
df["last_order_date_offline"] = df["last_order_date_offline"].apply(pd.to_datetime)

#Creating the CLTV Data Structure

df["last_order_date"].max()
today_date = dt.datetime(2021, 6, 1)

df["recency"] = (df["last_order_date"] - df["first_order_date"]).dt.days

cltv = df.groupby("master_id").agg({"recency": "sum",
                                    "first_order_date": lambda x: (today_date - x).dt.days,
                                    "order_num_total": "sum",
                                    "customer_value_total": "sum"})

cltv.columns =["recency_cltv_weekly", "T_weekly", "frequency", "monetary_cltv_avg"]

cltv["recency_cltv_weekly"] = cltv["recency_cltv_weekly"] / 7
cltv["T_weekly"] = cltv["T_weekly"] / 7
cltv["monetary_cltv_avg"] = cltv["monetary_cltv_avg"] / cltv["frequency"]
cltv = cltv[cltv["frequency"]>1]
cltv.head()
cltv.shape


#Creating of BG/NBD, Gamma-Gamma Models and Calculation of CLTV
#Fit BG/NBD model

bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv["frequency"],
        cltv["recency_cltv_weekly"],
        cltv["T_weekly"])

#We will estimate expected purchases from customers within 3 months and add exp_sales_3_month to cltv dataframe
cltv["expected_purc_3_month"] = bgf.conditional_expected_number_of_purchases_up_to_time(12,
                                                        cltv["frequency"],
                                                        cltv["recency_cltv_weekly"],
                                                        cltv["T_weekly"])

#We will estimate expected purchases from customers within 6 months and add exp_sales_6_month to cltv dataframe
cltv["expected_purc_6_month"] = bgf.conditional_expected_number_of_purchases_up_to_time(24,
                                                        cltv["frequency"],
                                                        cltv["recency_cltv_weekly"],
                                                        cltv["T_weekly"])


#Fit Gamma-Gamma model. We will estimate the average value of the customers and add it to the cltv dataframe as exp_average_value.
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv['frequency'], cltv["monetary_cltv_avg"])

cltv["expected_average_value"] = ggf.conditional_expected_average_profit(cltv['frequency'],
                                                                             cltv["monetary_cltv_avg"])

#Calculating cltv for 6 month and adding cltv dataframe
CLTV = ggf.customer_lifetime_value(bgf,
                                   cltv['frequency'],
                                   cltv["recency_cltv_weekly"],
                                   cltv["T_weekly"],
                                   cltv["monetary_cltv_avg"],
                                   time=6,  # 6 aylık
                                   freq="W",  # T'nin frekans bilgisi.
                                   discount_rate=0.01)

CLTV = CLTV.reset_index()
CLTV.head()

cltv_final = cltv.merge(CLTV, on="master_id", how="left")
cltv_final.sort_values(by="clv", ascending=False).head(20)


#Creating Segments by CLTV Value

cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])


#comment: action recommendations for next 6 month
#The recency and age of the #A segment are lower than the other segments, and the frequencies are higher.
#Besides, the number of transactions it will make in 6 months and the average benefit it will bring seems higher.
#For this segment, which seems to provide the company with an average of 362,316 and a total of 1806505,089 revenues in a 6-month period,
#We can offer special campaigns that will increase the #purchasing rate, mentioning that there are special campaigns via e-mail and
#appealing to the customer, We need to take actions that will make you feel special and encourage shopping.

#B segment also goes close to the A segment. However, the C segment is not in a bad place in terms of shopping frequency and the benefit
#it will bring. Regular reminders can be made in order not to disturb the shopping routine, so as not to lose the C segment and preserve
#the situation. Categories of interest can be analyzed and information can be given in that direction.