# Inspiration is from Doris project (Java) and this stackoverflow answer: https://stackoverflow.com/a/14091182/1168342
import argparse
import shutil
import subprocess
import os
import re
from multiprocessing.pool import ThreadPool
import time
import datetime

JDT_COMMAND = r'C:\jdt2famix-1.0.3\jdt2famix.cmd'
DEVNULL = open(os.devnull, 'w')


# function to run as separate process in a ThreadPool, https://stackoverflow.com/a/26783779/1168342
def extract_revision(git_repo_dir_local, sha1_local, destination, i, n):
    print "({i}/{n}) Extracting revision {rev}".format(i=i, n=n, rev=sha1_local)
    #  mkdir -p archive/$rev
    repo_name_local = os.path.split(git_repo_dir_local)[1]
    revision_dir = os.path.join(destination, repo_name_local + "_master", sha1_local)
    os.mkdir(revision_dir)
    #subprocess.check_output(["mkdir", revision_dir])
    #  git archive $rev | (cd archive/$rev; tar x)
    # extract_process = subprocess.Popen(["tar", "x"], cwd=revision_dir,
    #                                    stdin=subprocess.PIPE).stdin
    # arch_process = subprocess.Popen(["git", "archive", sha1_local],
    #                                 cwd=git_repo_dir_local,
    #                                 stdout=extract_process)
    #arch_process.wait()

    # Optimize, https://stackoverflow.com/a/46942812/1168342
    my_env = os.environ.copy()
    my_env["GIT_INDEX_FILE"] = revision_dir + "/.git"
    extract_process = subprocess.Popen(["git", "--work-tree=" + revision_dir, "checkout", sha1_local, "--", "."],
                                       cwd=git_repo_dir_local, env=my_env, stdout=DEVNULL)
    extract_process.wait()

    # Parse the Java files to create the MSE file
    # print ('Parsing revision ' + sha1_local + " for FAMIX...")
    subprocess.call([JDT_COMMAND], cwd=revision_dir, stdout=DEVNULL)
    # verify an MSE file was created
    mse_file = os.path.join(revision_dir, sha1_local + '.mse')
    if os.path.isfile(mse_file):
        # success
        # print ("Created " + mse_file)
        # move the MSE file
        mse_moved_file = os.path.join(destination, repo_name_local + "_master", sha1_local + ".mse")
        shutil.move(mse_file, mse_moved_file)
        # print ("Moved to " + mse_moved_file)
    else:
        # FAMIX failed
        print ("FAMIX parse failed for revision " + sha1_local)
    # clean up the extracted files directory
    shutil.rmtree(revision_dir)


parser = argparse.ArgumentParser(description='Extract the revisions of a GIT repo to separate directories for data mining.')

parser.add_argument('--sha1file', required=False,
                    help='path of file containing list of sha1 keys of revisions to extract')

parser.add_argument('--destination', required=True,
                    help='path of existing directory where commits should be extracted')

parser.add_argument('--tempwork', required=True,
                    help='path of temporary working directory where git repo will be cloned and manipulated')

parser.add_argument('--url', required=True,
                    help='path of git repo from which commits should be extracted')

args = parser.parse_args()
sha1_file = args.sha1file

sha1_list = None

if sha1_file is not None:
    with open(sha1_file) as f:
        sha1_list = f.readlines()
    # remove whitespace characters like `\n` at the end of each line
    sha1_list = [x.strip() for x in sha1_list]

print "Cloning repo at " + args.url + "..."
PIPE = subprocess.PIPE
process = subprocess.Popen(["git", "clone", args.url],
                           cwd=args.tempwork, stdout=PIPE, stderr=PIPE)

clone_output, clone_err_output = process.communicate()

# print("Clone output: ")
# print("'" + clone_output + "'")
# print("Clone err output: ")
# print("'" + clone_err_output + "'")

if 'fatal' in clone_err_output:
    print ("Clone failed. Exiting")
    exit(-1)

regex = r"Cloning into '(.+)'"
m = re.search(regex, clone_err_output)
repo_name = m.group(1)
git_repo_dir = os.path.join(args.tempwork, repo_name)

print ("Repo name = '" + repo_name + "' at " + git_repo_dir)

# create the root of the revision subdirs
subprocess.check_output(["mkdir", os.path.join(args.destination, repo_name + "_master")])


# Find git repo path $PROJECT_NAME
# TODO for each revision (starting at beginning?)
#   TODO : git reset --hard $SHA1
#   TODO : Copy dir to args.destination + revnumber/

# WHOA! It can work with 'worktree' command...
# https://stackoverflow.com/questions/40811177/how-to-extract-all-files-of-any-commit-to-a-folder-archive-from-a-git-repository

if sha1_list is None:
    process = subprocess.Popen(["git", "rev-list", "master"],
                               cwd=git_repo_dir, stdout=PIPE, stderr=PIPE)
    sha1_list, sha_list_err_output = process.communicate()
    # remove whitespace characters like `\n` at the end of each line
    # sha_list = [x.strip() for x in sha_list]

# print "Sha1_List"
# print shlen(a1_lis)


# git rev-list master | while read rev; do
#  echo creating archive for $rev
#  mkdir -p archive/$rev
#  git archive $rev | (cd archive/$rev; tar x)
# done


the_lines = sha1_list.splitlines()
n_lines = len(the_lines)
count = 0

num = 1  # set to the number of workers you want (it defaults to the cpu count of your machine)
tp = ThreadPool(num)

print "Processing {n} revision directories with {m} threads...".format(n=n_lines, m=num)
start_t = time.localtime()
for sha1 in the_lines:
    count = count + 1
    tp.apply_async(extract_revision, (git_repo_dir, sha1, args.destination, count, n_lines))
    # if count == 6:
    #     break

tp.close()
tp.join()

end_t = time.localtime()
time_diff = (time.mktime(end_t) - time.mktime(start_t))

print "Time difference: {diff} seconds".format(diff=time_diff)

# worktree is slow, and can't really be split into sub processes (paralellized)
#     subprocess.call(["git", "worktree", "add", os.path.join(args.destination, sha1), sha1],
#                     cwd=git_repo_dir)
