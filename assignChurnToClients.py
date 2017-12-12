#
# Program to take output of git-churn and add it to the appropriate client CSV files
import argparse
import csv
import os


parser = argparse.ArgumentParser(description="Add (merge) churn data into client (protected and unprotected) CSV "
                                             "files .")

parser.add_argument('--resultsdir', required=True,
                    help='path where mining results (CSV and churn files) are located')
parser.add_argument('--churnfile', required=True,
                    help='File containing churn output (usually has an SHA1 in its name)')
parser.add_argument('--revision', required=True,
                    help='Integer specifying the revision number (created by Doris)')

args = parser.parse_args()
results_dir = args.resultsdir
churn_file = args.churnfile
revision = args.revision

protected_clients_csv = os.path.join(results_dir, revision + "_ProtectedClients.csv")
unprotected_clients_csv = os.path.join(results_dir, revision + "_UnprotectedClients.csv")
churn_file_tsv = os.path.join(results_dir, churn_file)


def readcsv(filename, delim):
    ifile = open(filename, "rU")
    reader = csv.reader(ifile, delimiter=delim)

    rownum = 0
    a = []

    for row in reader:
        a.append(row)
        rownum += 1

    ifile.close()
    return a


def merge_churn(client_list, churn_list):
    print "Merging clients..."
    for line in client_list:
        client_name_with_slashes = line[0].replace('::', '/') + ".java"
        # print "Searching for...", client_name_with_slashes
        found = False
        for sublist in churn_list:
            churn_entity = sublist[2]
            # churn entity name is 2th entity
            if client_name_with_slashes in churn_entity:
                found = True
                # calculate the churn and updated it in the client list
                line[3] = int(sublist[0]) + int(sublist[1])
                print line[3], line[0]
                break
        if not found:
            print "Didn't find '" + client_name_with_slashes + "' -- assuming values of 0 churn for this file. "
    return client_list


p_clients = readcsv(protected_clients_csv, ',')
u_clients = readcsv(unprotected_clients_csv, ',')
churn_entities = readcsv(churn_file_tsv, '\t')
# the last lines of churn_entities are a summary and not valid for data
for i in range(3):
    print "Removing line: ", churn_entities.pop(-1)

# add column for churn to clients
p_clients = [x + [0] for x in p_clients]
u_clients = [x + [0] for x in u_clients]

p_clients = merge_churn(p_clients, churn_entities)
u_clients = merge_churn(u_clients, churn_entities)

# write new CSV files with merged churn numbers