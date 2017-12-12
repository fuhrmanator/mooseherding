import argparse

import subprocess

parser = argparse.ArgumentParser(description='Process a GIT repo for data mining.')

parser.add_argument('--shafile', required=True,
                    help='path of file containing list of sha1 keys')

args = parser.parse_args()
sha_file = args.shafile

with open(sha_file) as f:
    sha_list = f.readlines()
# remove whitespace characters like `\n` at the end of each line
sha_list = [x.strip() for x in sha_list]

# for first one, calculate the number from the "TAIL" e.g. first parentless commit
# see https://stackoverflow.com/a/1007545/1168342
#     git rev-list --max-parents=0 HEAD
# I chose to leave off the --max-parents=0 as it ignores branched commits, which we use

subprocess.call(["git", "rev-list", "--count", sha_list[0]])

for i in range(len(sha_list)-1):
    subprocess.call(["git", "rev-list", "--count", sha_list[i] + ".." + sha_list[i+1]])
