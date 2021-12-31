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
        regexp = r'[:]\s[A-Z]\d{7}[A-Z]'
        NRIC = re.findall(regexp, log)
        return NRIC


def count(NRIC):
    return Counter(NRIC)


def write_csv(counter):
    with open('PharmacyFrequencyMonitoringUsername.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        header = ['USERNAME (NRIC) ', ' FREQUENCY']

        writer.writerow(header)

        for item in counter:
            writer.writerow((item, counter[item]))


def NRICGraph():
    data = pd.read_csv('PharmacyFrequencyMonitoringUsername.csv')
    df = pd.DataFrame(data)
    X = list(df.iloc[:, 0])
    Y = list(df.iloc[:, 1])

    fig, ax = plt.subplots()
    labels = ax.get_xticklabels()
    plt.setp(labels, horizontalalignment='right')

    plt.barh(X, Y, color='c')
    plt.title("Frequency of logged Usernames")
    plt.xlabel("Frequency")
    plt.ylabel("Usernames")

    date_backup = date.today()
    print("-- Generated highest frequency of logged users graph for Log Backup date", date_backup, "--")
    print("Message: Graph preview for", date_backup, "has been displayed")

    str_date_backup = str(date_backup).replace('-','.')
    countbackupfile = str_date_backup + ' - Pharmacy Log Backup.log'
    dateofgeneratedgraph = str_date_backup + ' - Frequency of top logged users graph.png'

    plt.savefig(dateofgeneratedgraph)
    plt.show()


if __name__ == '__main__':
    date_backup = date.today()
    str_date_backup = str(date_backup).replace('-', '.')
    countbackupfile = str_date_backup + ' - Pharmacy Log Backup.log'
    write_csv(count(reader(countbackupfile)))
    NRICGraph()