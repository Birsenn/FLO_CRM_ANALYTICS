df_ = pd.read_csv("/Users/birsenbayat/Desktop/miuul/PythonProgrammingForDataScience/CRM_Analitigi/FLOMusteriSegmentasyonu/flo_data_20k.csv")
df = df_.copy()

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

df.head()

#Veri setine genel bakış

df.head(10)
df.columns
df.shape
df.describe().T
df.isnull().sum()
df.dtypes

#Omnichannel müşteriler hem online'dan hemde offline platformlardan alışveriş yapmaktadır.
#Her bir müşterinin toplam alışveriş sayısı ve harcaması için yeni değişkenler oluşturuyoruz.

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]

df.head()

#Değişken tiplerini inceleyerek, tarih ifade eden değişkenlerin tipini date'e çeviriyoruz.
df.dtypes
df["first_order_date"] = df["first_order_date"].apply(pd.to_datetime)
df["last_order_date"] = df["last_order_date"].apply(pd.to_datetime)
df["last_order_date_online"] = df["last_order_date_online"].apply(pd.to_datetime)
df["last_order_date_offline"] = df["last_order_date_offline"].apply(pd.to_datetime)

#Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakalım.
analysing = df.groupby("order_channel").agg({"master_id": "count",
                                 "order_num_total": "sum",
                                 "customer_value_total": "sum"})


#En fazla kazancı getiren ilk 10 müşteriyi sıralayalım.
df.sort_values(by="customer_value_total", ascending=False).head(10)

#En fazla siparişi veren ilk 10 müşteriyi sıralayalım.
df.sort_values(by="order_num_total", ascending=False).head(10)

#Veri ön hazırlık sürecini fonksiyonlaştıralım.

def dataset_preparing(dataframe):
    dataframe.dropna(inplace=True)
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_online"] + dataframe["customer_value_total_ever_offline"]

    dataframe["first_order_date"] = dataframe["first_order_date"].apply(pd.to_datetime)
    dataframe["last_order_date"] = dataframe["last_order_date"].apply(pd.to_datetime)
    dataframe["last_order_date_online"] = dataframe["last_order_date_online"].apply(pd.to_datetime)
    dataframe["last_order_date_offline"] = dataframe["last_order_date_offline"].apply(pd.to_datetime)

    return dataframe

#deneme
df = df_.copy()
df.head()
dataset_preparing(df)

#RFM Metriklerinin Hesaplanması
#Adım 1: Recency, Frequency ve Monetary tanımlarını yapacağız.
#Adım 2: Hesapladığınız metrikleri rfm isimli bir değişkene atayacağız.

df["last_order_date"].max() #sipariş verilen son tarihi bulup analiz tarihine karar vereceğiz.

today_date = dt.datetime(2021, 6, 2)

rfm = df.groupby("master_id").agg({"last_order_date": lambda x: (today_date - x.max()).days,
                                   "order_num_total": "sum",
                                   "customer_value_total": "sum"})

rfm.columns = ["recency", "frequency", "monetary"]
rfm.head()

#RF Skorunun Hesaplanması
#Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çevireceğiz.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels = [5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

#recency_score ve frequency_score’u tek bir değişken olarak ifade edeceğiz ve RF_SCORE olarak kaydedeceğiz.
rfm["RF_SCORE"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))
rfm.shape

#RF Skorunun Segment Olarak Tanımlanması
#Adım 1: Oluşturulan RF skorları için segment tanımlamaları yapacağız.
#Adım 2: Aşağıdaki seg_map yardımı ile skorları segmentlere çevireceğiz.

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

#Aksiyon Zamanı !

#Adım 1: Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyelim.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#Adım 2: RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulalım ve müşteri id'lerini csv olarak kaydedelim.
#Bu csv dosyasını ilgili birimlere sunarak, bu müşterilerle ilgili çalışma yapılmasını sağlamış olacağız.

#a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri tercihlerinin üstünde.
#Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak iletişime geçmek isteniliyor.
#Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş yapan kişiler özel olarak iletişim kurulacak müşteriler.
#Bu müşterilerin id numaralarını csv dosyasına kaydediniz.

rfm = rfm.reset_index()
rfm = rfm.merge(df[["master_id", "interested_in_categories_12"]], how = 'left')
rfm.head()
rfm.shape

deneme = rfm.loc[((rfm["segment"] == "champions") | (rfm["segment"] == "loyal_customers")) & (rfm["interested_in_categories_12"].str.contains("KADIN")), ["master_id"]]
deneme.shape
deneme.head()

deneme.to_csv("rfm_a.csv")

#b. Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte
#iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni gelen müşteriler
#özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydediniz.

deneme2 = rfm.loc[((rfm["segment"] == "at_Risk") | (rfm["segment"] == "cant_loose") | (rfm["segment"] == "hibernating") | (rfm["segment"] == "new_customers")) & (rfm["interested_in_categories_12"].str.contains("ERKEK", "COCUK")), ["master_id"]]
deneme2.head()
deneme2.shape

deneme2.to_csv("rfm_b.csv")

#Böylelikle müşterileri segmentlere ayırmış olduk. Bu segmentleri belli kırılımlarda inceleyerek, hangi noktalara odaklanılması gerektiği
#yorumunu yapabiliriz ve hedef kitle müşteriye ulaşabiliriz. Gerekli segmentler için kampanyalar düzenleyebiliriz, gerekli segmentleri yeniden kazanabiliriz.










