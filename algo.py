import datetime
import os
import sys

import django
import matplotlib
import requests

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime as dt

# MACD CALCULATION
# identifier = 'AAPL'

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject_PARSEC.settings')
    django.setup()


def algo(identifier: str, indicator: str):


    df = yf.download(identifier, start='2007-12-30', end='2008-12-30')
    plt.rcParams.update({'font.size': 7})
    df['EMA12'] = df.Close.ewm(span=12).mean()
    df['EMA26'] = df.Close.ewm(span=26).mean()

    df['MACD'] = df.EMA12 - df.EMA26
    df['signal'] = df.MACD.ewm(span=9).mean()

    # Simple Moving Average
    df['SMA'] = df.Close.rolling(10).mean()
    # plt.plot(df.SMA, label='SMA', color='yellow')
    # plt.savefig("myImagePDF_SMA.pdf", format="pdf", bbox_inches="tight")

    df[indicator]

    ########################################################################

    # Exponenential Moving Average
    # df['EMA'] = df.Close.ewm(span=10, min_periods=10).mean()
    # plt.plot(df.EMA, label='EMA', color='black')
    # plt.savefig("myImagePDF_EMA.pdf", format="pdf", bbox_inches="tight")

    ########################################################################

    # Average True Range
    # df['range'] = df['high'] - df['low']
    # df['atr_14'] = df['range'].rolling(14).mean()
    # plt.plot(df.EMA, label='ATR', color='orange')
    # plt.savefig("myImagePDF_ATR.pdf", format="pdf", bbox_inches="tight")

    ########################################################################

    # Relative Strengh Index
    # df['gain'] = df['diff'].clip(lower=0).round(2)
    # df['loss'] = df['diff'].clip(lower=0).abs().round(2)

    # Get initial Averages
    # df['avg_gain'] = df['gain'].rolling(10, min_periods=10).mean()[:10 + 1]
    # df['avg_loss'] = df['loss'].rolling(10, min_periods=10).mean()[:10 + 1]

    # Average Gains
    '''
    for i, row in enumerate(df['avg_gain'].iloc[10 + 1:]):
        df['avg_gain'].iloc[i + 10 + 1] = \
            (df['avg_gain'].iloc[i + 10] *
             (10 - 1) +
             df['gain'].iloc[i + 10 + 1]) \
            / 10
    # Average Losses
    for i, row in enumerate(df['avg_loss'].iloc[10 + 1:]):
        df['avg_loss'].iloc[i + 10 + 1] = \
            (df['avg_loss'].iloc[i + 10] *
             (10 - 1) +
             df['loss'].iloc[i + 10 + 1]) \
            / 10
    # Calculate RS Values
    df['rs'] = df['avg_gain'] / df['avg_loss']
    # Calculate RSI
    df['rsi'] = 100 - (100 / (1.0 + df['rs']))
    '''

    ########################################################################
    plt.plot(df.signal, label='signal', color='red')
    plt.plot(df.MACD, label='MACD', color='green')

    output = StringIO()
    plt.savefig(output, format="svg", bbox_inches="tight")



    plt.savefig("myImagePDF1.pdf", format="svg", bbox_inches="tight")

    Buy, Sell, = [], []

    for i in range(2, len(df)):
        if df.MACD.iloc[i] > df.signal.iloc[i] and df.MACD.iloc[i - 1] < df.signal.iloc[i - 1]:
            Buy.append(i)
        elif df.MACD.iloc[i] < df.signal.iloc[i] and df.MACD.iloc[i - 1] > df.signal.iloc[i - 1]:
            Sell.append(i)
    plt.figure(figsize=(12, 4))
    plt.scatter(df.iloc[Buy].index, df.iloc[Buy].Close, marker="^", color='green')
    plt.scatter(df.iloc[Sell].index, df.iloc[Sell].Close, marker="v", color='red')
    plt.plot(df.Close, label=identifier + 'Close', color='k')
    output = StringIO()
    plt.savefig(output, format="svg", bbox_inches="tight")
    plt.savefig("myImagePDF2.pdf", format="svg", bbox_inches="tight")
    print("saving Plot")

    Realbuys = [i for i in Buy]
    Realsells = [i + 1 for i in Sell]
    Buyprices = df.Open.iloc[Realbuys]
    indicat_buy = Buyprices[-1:]
    Sellprices = df.Open.iloc[Realsells]
    indicat_sell = Sellprices[-1:]

    '''
    a = indicat_buy.index[0]
    b = indicat_sell.index[0]
    print(a, b)
    if a > b:
        buy = True
        sell = False
        data = "TRADE ALGORITHM EMPFEHLUNG ZU : " + identifier + ": KAUFEN \n \n"
    elif b > a:
        sell = True
        buy = False
        data = "TRADE ALGORITHM EMPFEHLUNG ZU : " + identifier + ": VERKAUFEN \n \n"
    else:
        data = "Werte sind gleich, keine Empfehlung \n \n"
    return data
    '''

    fvalue = (((df.iloc[Sell].Close.reset_index(drop=True) / df.iloc[Buy].Close.reset_index(drop=True)).product() - 1) * 100)
    fvalue_without2 = ((df.iloc[Sell].Close[-1]) / (df.iloc[Buy].Close[0]))
    fvalue_without = (((((1000 / (df.iloc[Buy].Close[0])) * df.iloc[Sell].Close[-1]) / 1000) - 1) * 100)
    return df, output.getvalue(), fvalue, fvalue_without

def algo_SMA(identifier: str):
    df = yf.download(identifier, start='2022-01-01', end='2022-11-28')
    plt.rcParams.update({'font.size': 7})
    sma_period: int = 10
    df['sma_10'] = df['close'].rolling(sma_period).mean()
    plt.plot(df, label='time', color='red')


def sendmail(identifier, data, recipient):
    '''
    fromaddr = "parsec.algoservices@gmail.com"
    recipients = [recipient]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = "PARSEC DAILY ::: FOR - " + identifier

    body = data
    msg.attach(MIMEText(body, 'plain'))
    filename = "myImagePDF2.pdf"
    attachment = open(filename, "rb")
    body2 = '\n \n Disclaimer: Dies ist eine Marketingmitteilung. Die Anlage in Finanzinstrumenten ist Marktrisiken ' \
            'unterworfen. Frühere Wertentwicklungen bzw. Prognosen sind keine verlässlichen Indikatoren für zukünftige ' \
            'Ergebnisse. Die steuerliche Behandlung hängt von den persönlichen Verhältnissen des jeweiligen Kunden ab und ' \
            'kann künftigen Änderungen unterworfen sein. PARSEC ALGO TRADING REC. weist ausdrücklich darauf hin, ' \
            'dass diese Unterlage ausschließlich für den persönlichen Gebrauch und nur zur Information dienen soll. Eine ' \
            'Veröffentlichung, Vervielfältigung oder Weitergabe ist ohne die Zustimmung untersagt. Der Inhalt dieser ' \
            'Unterlage stellt nicht auf die individuellen Bedürfnisse einzelner Anleger ab (gewünschter Ertrag, ' \
            'steuerliche Situation, Risikobereitschaft etc.), sondern ist genereller Natur und basiert auf dem neuesten ' \
            'Wissensstand der mit der Erstellung betrauten Personen zu Redaktionsschluss. Diese Unterlage ist weder ein ' \
            'Angebot noch eine Einladung zur Angebotsstellung zum Kauf oder Verkauf von Wertpapieren. Die erforderlichen ' \
            'Angaben sind offenlegungspflichtig gemäß § 25 Mediengesetz '

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)

    filename = "myImagePDF1.pdf"
    attachment = open(filename, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)

    msg.attach(MIMEText(body2, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "irvdfuopxcjgngfq")
    text = msg.as_string()
    server.sendmail(fromaddr, recipients, text)
    server.quit()
'''


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Bitte einen Identifier angeben')
    else:
        from parsec.models import Client

        ident = sys.argv[1]
        algo(ident)


        # for c in Client.objects.all():
        #   sendmail(ident, res, c.email)
