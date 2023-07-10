![banner_resmi](https://github.com/Birsenn/FLO_CRM_ANALYTICS/blob/main/banner.png)

## RFM ile Müşteri Segmentasyonu
Online ayakkabı mağazası olan FLO, müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor. Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranışlardaki öbeklenmelere göre gruplar oluşturulacak.

## İşlem Basamakları
* Veri setinin hazırlanması <br/>
* RFM Metriklerinin Hesaplanması <br/>
* RF Skorunun Hesaplanması <br/>
* Belli segmentlere ait müşterilerin belirlenmesi <br/>

## BG-NBD ve Gamma-Gamma ile CLTV Tahmini
FLO satış ve pazarlama faaliyetleri için roadmap belirlemek istemektedir. Şirketin orta uzun vadeli plan yapabilmesi için var olan müşterilerin gelecekte şirkete sağlayacakları potansiyel değerin tahmin edilmesi gerekmektedir.

## İşlem Basamakları
* Veri setinin hazırlanması <br/>
* CLTV Veri Yapısının Oluşturulması <br/>
* BG/NBD, Gamma-Gamma Modellerinin Kurulması ve CLTV’nin Hesaplanması <br/>
* CLTV Değerine Göre Segmentlerin Oluşturulması <br/>

-------------------------------------------------------------------------------- <br/>

**Verilen özelliklerin kısa açıklamaları:** 

* **master_id:** Eşsiz müşteri numarası <br/>
* **order_channel:** Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile) <br/>
* **last_order_channel:** En son alışverişin yapıldığı kanal <br/>
* **first_order_date:** Müşterinin yaptığı ilk alışveriş tarihi <br/>
* **last_order_date:** Müşterinin yaptığı son alışveriş tarihi <br/>
* **last_order_date_online:** Müşterinin online platformda yaptığı son alışveriş tarihi <br/>
* **last_order_date_offline:** Müşterinin offline platformda yaptığı son alışveriş tarihi <br/>
* **order_num_total_ever_online:** Müşterinin online platformda yaptığı toplam alışveriş sayısı <br/>
* **order_num_total_ever_offline:** Müşterinin offline'da yaptığı toplam alışveriş sayısı <br/>
* **customer_value_total_ever_offline:** Müşterinin offline alışverişlerinde ödediği toplam ücret <br/>
* **customer_value_total_ever_online:** Müşterinin online alışverişlerinde ödediği toplam ücret <br/>
* **interested_in_categories_12:** Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi <br/>
