import argparse
import subprocess
import re
import os

### Sample usage:
# c:\Python27\python.exe C:\Users\fuhrm\PycharmProjects\mooseherding\miner.py --gitrepo file://C:/Users/fuhrm/argouml-svn.git --shafile C:\Users\fuhrm\Documents\doristest\argouml_sha1.txt --dorisoutputdir C:\Users\fuhrm\Documents\doristest\argouml_doris --resultsdir C:\users\fuhrm\mining_output\ --ifilter org::argouml::

parser = argparse.ArgumentParser(description='Process a GIT repo for data mining.')
parser.add_argument('--ifilter',
                    help='optional filter for prefix path of interfaces, e.g., org::mozilla::')
parser.add_argument('--uml',
                    help='optional flag to generate PlantUML output')
parser.add_argument('--gitrepo', required=True,
                    help='path of git repository (should be file://...)')
parser.add_argument('--shafile', required=True,
                    help='path of file containing list of sha1 keys')
parser.add_argument('--dorisoutputdir', required=True,
                    help='path where Doris stores its files')
parser.add_argument('--resultsdir', required=True,
                    help='path where to store final results (CSV files)')

args = parser.parse_args()

pharo_console = os.path.normpath('C:/Users/fuhrm/Documents/pharo6/pharo-vm/PharoConsole.exe')
pharo_image_path = os.path.normpath('C:/Users/fuhrm/Google Drive/moose_suite_6_0/')
pharo_image = os.path.normpath(pharo_image_path + '/Interface_Clients_CommandLineHandler.61.image')
miner_command = '"' + pharo_console + '" --headless "' + pharo_image + '" mooseminer '

if args.ifilter:
    assert isinstance(args.ifilter, str)
    miner_command += '--ifilter=' + args.ifilter

if args.uml:
    miner_command += ' --uml'

git_repo = args.gitrepo
sha_file = args.shafile
doris_output_dir = args.dorisoutputdir
results_dir = args.resultsdir

# should match "argouml-svn" in a path like "file://c:/Users/fuhrm/argouml-svn.git"
regex = r'.+\/(.+?).git'
m = re.search(regex, git_repo)
git_repo_master = m.group(1) + "_master"

# remove the 'file://' to get the local path
local_git_repo_path = git_repo[7:]

# Note: the 'churn' calculation requires a local repository (accessible via BASH)
# Calculate churn for each revision in the SHA1 file
print('---------------------------------------------------------------')
print('Calculating churn for each commit in ' + local_git_repo_path)
print('---------------------------------------------------------------')
with open(sha_file) as f:
    sha_list = f.readlines()
# remove whitespace characters like `\n` at the end of each line
sha_list = [x.strip() for x in sha_list]

for sha1 in sha_list:
    churn_results_file = os.path.join(results_dir, sha1 + '_churn')
    with open(churn_results_file, "w") as outfile:
        subprocess.call([r'C:\Python27\python.exe', r'c:\users\fuhrm\bin\git-churnlines', sha1],
                        cwd=local_git_repo_path, stdout=outfile)
        print('Created ' + churn_results_file)

# run Doris to create a set of directories (checkout) for each revision in the SHA1 file
# Example: java -Xmx3072m -jar c:\Users\fuhrm\workspace\doris\target\doris-1.0.0-jar-with-dependencies.jar -u file://c:/Users/fuhrm/argouml-svn.git -shafile argouml_sha1.txt
print('---------------------------------------------------------------')
print('Cloning commits with Doris ' + local_git_repo_path)
print('---------------------------------------------------------------')

subprocess.call(['java', '-Xmx3072m', '-jar',
                 r'c:\Users\fuhrm\workspace\doris\target\doris-1.0.0-jar-with-dependencies.jar',
                 '-u', git_repo,
                 '-t', doris_output_dir,
                 '-shafile', sha_file])

# run jdt2famix to create an MSE file for each commit directory (integer commit number in doris)
print('---------------------------------------------------------------')
print('Parsing Java files to build Famix (MSE) files')
print('---------------------------------------------------------------')

doris_master = os.path.join(doris_output_dir, git_repo_master)
FNULL = open(os.devnull, 'w')

# just get one level of dirs in the walk
for dir_name in os.listdir(doris_master):
    # commits are directories named with the integer of the commit number
    is_commit = re.search(r'^([0-9]+)$', dir_name)
    if is_commit:
        commit_number = is_commit.group(1)
        print ('Processing commit number ' + commit_number)
        subprocess.call([r'C:\jdt2famix-1.0.3\jdt2famix.cmd'], cwd=os.path.join(doris_master, dir_name), stdout=FNULL)
        # verify an MSE file was created
        mse_file = os.path.join(doris_master, dir_name, commit_number + '.mse')
        if os.path.isfile(mse_file):
            # run a MOOSE/Pharo script to analyse MSE file producing CSV output files
            # fix any UTF-8 nonsense, e.g., ArgoUML has bad encoding in Java
            mse_file_utf8 = mse_file + "_utf8.mse"
            print('About to convert: ' + mse_file + ' to ' + mse_file_utf8)
            with open(mse_file_utf8, "w") as outfile:
                return_code = subprocess.call('c:\\program files (x86)\\gnuwin32\\bin\\iconv.exe -f CP1252 -t UTF-8 '
                                              + mse_file, stdout=outfile)
            # Run the MOOSE processor
            print ('                                   .    ')
            print ('                                  .Z    ')
            print ('                                   O    ')
            print ('                                    ?   ')
            print ('Mining with Moose...                Z   ')
            print ('                                    Z   ')
            print (' ...... . ,.. .   .......  .. ,I77OOO7$.')
            print ('I?++++++++?+++??~:~:~I?I??????????ZZZI?.')
            print ('                                   .Z . ')
            print ('                                   .Z.  ')
            print ('                                   +,   ')
            print ('                                   Z    ')
            print ('                                  ..    ')
            print ('                                  Z     ')
            print('About to subprocess: ' + miner_command + ' ' + mse_file_utf8)
            return_code = subprocess.call(miner_command + ' ' + mse_file_utf8)
            print(return_code)
            os.remove(mse_file_utf8)

            # Move the results from Pharo (windows) stdout, stderr, puml and csv files generated
            print('---------------------------------------------------------------')
            print('Moving results files to ' + results_dir)
            print('---------------------------------------------------------------')
            os.rename(pharo_image_path + "/stdout",
                      os.path.join(results_dir, commit_number + "_stdout"))
            os.rename(pharo_image_path + "/stderr",
                      os.path.join(results_dir, commit_number + "_stderr"))
            os.rename(pharo_image_path + "/Interfaces.csv",
                      os.path.join(results_dir, commit_number + "_Interfaces.csv"))
            os.rename(pharo_image_path + "/ProtectedClients.csv",
                      os.path.join(results_dir, commit_number + "_ProtectedClients.csv"))
            os.rename(pharo_image_path + "/UnprotectedClients.csv",
                      os.path.join(results_dir, commit_number + "_UnprotectedClients.csv"))
            if os.path.isfile(pharo_image_path + "/modelUML.puml"):
                os.rename(pharo_image_path + "/modelUML.puml",
                          os.path.join(results_dir, commit_number + "_modelUML.puml"))

        else:
            print ("Could not find " + commit_number + ".mse in " + dir_name + " after jdt2famix execution.")
            exit(-1)

