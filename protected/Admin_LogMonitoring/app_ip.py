import re
from collections import Counter
import csv
import pandas as pd
from matplotlib import pyplot as plt
from datetime import date

# Separate application with the --ADMIN FUNCTIONALITY LOG MONITORING-- from the main pharmacy application


def reader(filename):
    with open(filename) as f:
        log = f.read()
        regexp = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        IPAddress = re.findall(regexp, log)
        return IPAddress


def count(IPAddress):
    return Counter(IPAddress)


def write_csv(counter):
    with open('PharmacyFrequencyMonitoringIP.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        header = ['IP Address', ' FREQUENCY']

        writer.writerow(header)

        for item in counter:
            writer.writerow((item, counter[item]))


def ipgraph():
    data = pd.read_csv('PharmacyFrequencyMonitoringIP.csv')
    df = pd.DataFrame(data)
    X = list(df.iloc[:, 0])
    Y = list(df.iloc[:, 1])

    fig, ax = plt.subplots()
    labels = ax.get_xticklabels()
    plt.setp(labels, horizontalalignment='right')

    plt.barh(X, Y, color='c')
    plt.title("Frequency of logged IP Addresses")
    plt.xlabel("Frequency")
    plt.ylabel("IP Address")

    date_backup = date.today()
    print("-- Generated highest frequency of logged IP Addresses graph for Log Backup date", date_backup, "--")
    print("Message: Graph preview for", date_backup, "has been displayed")

    str_date_backup = str(date_backup).replace('-','.')
    countbackupfile = str_date_backup + ' - Pharmacy Log Backup.log'
    dateofgeneratedgraph = str_date_backup + ' - Frequency of top logged IP Addresses graph.png'

    plt.savefig(dateofgeneratedgraph)
    plt.show()


if __name__ == '__main__':
    date_backup = date.today()
    str_date_backup = str(date_backup).replace('-', '.')
    countbackupfile = str_date_backup + ' - Pharmacy Log Backup.log'
    write_csv(count(reader(countbackupfile)))
    ipgraph()