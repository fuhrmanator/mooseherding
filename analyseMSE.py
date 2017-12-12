import os
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Process some MSE files in the subdirectories.')
parser.add_argument('--ifilter',
                    help='optional filter for prefix path of interfaces, e.g., org::mozilla::')

args = parser.parse_args()

cwd = os.getcwd()
pharo_console = os.path.normpath('C:/Users/fuhrm/Documents/pharo6/pharo-vm/PharoConsole.exe')
pharo_image_path = os.path.normpath('C:/Users/fuhrm/Google Drive/moose_suite_6_0/')
pharo_image = os.path.normpath(pharo_image_path + '/Interface_Clients_CommandLineHandler.59.image')
#extreme filter below
#miner_command = '"' + pharo_console + '" --headless "' + pharo_image + '" mooseminer --ifilter=org::mozilla::javascript::commonjs::module::provider --uml '
#miner_command = '"' + pharo_console + '" --headless "' + pharo_image + '" mooseminer --ifilter=org::mozilla:: --uml '
#miner_command = '"' + pharo_console + '" --headless "' + pharo_image + '" mooseminer --uml '
#miner_command = '"' + pharo_console + '" --headless "' + pharo_image + '" mooseminer --ifilter=org::argouml:: '
miner_command = '"' + pharo_console + '" --headless "' + pharo_image + '" mooseminer '

if args.ifilter:
    assert isinstance(args.ifilter, str)
    miner_command += '--ifilter=' + args.ifilter

for root, dirs, files in os.walk(cwd):
    for my_file in files:
        if my_file.endswith(".mse"):
            fqpath_file = os.path.join(root, my_file)
            #print(os.path.join(root, my_file))
            # fix any UTF-8 nonsense, e.g., ArgoUML has bad encoding in Java
            fqpath_file_utf8 = fqpath_file + "_utf8.mse"
            print('About to convert: ' + fqpath_file + ' to ' + fqpath_file_utf8)
            with open(fqpath_file_utf8, "w") as outfile:
                return_code = subprocess.call('c:\\program files (x86)\\gnuwin32\\bin\\iconv.exe -f CP1252 -t UTF-8 ' + fqpath_file, stdout=outfile)
            print (return_code)
            print('About to subprocess: ' + miner_command + ' ' + fqpath_file_utf8)
            return_code = subprocess.call(miner_command + ' ' + fqpath_file_utf8)
            print(return_code)
            os.remove(fqpath_file_utf8)
            # rename the stdout, stderr, puml and csv files generated
            print('About to rename ' + os.path.normpath(pharo_image_path + '/stdout') + " to " + os.path.normpath(pharo_image_path + "/" + my_file + '_stdout.txt'))
            os.rename(pharo_image_path + "/stdout", pharo_image_path + "/" + my_file + "_stdout.txt")
            os.rename(pharo_image_path + "/stderr", pharo_image_path + "/" + my_file + "_stderr.txt")
            #os.rename(pharo_image_path + "/modelUML.puml", pharo_image_path + "/" + "modelUML_" + my_file + ".puml")
            os.rename(pharo_image_path + "/Interfaces.csv", pharo_image_path + "/" + "Interfaces_" + my_file + ".csv")
            os.rename(pharo_image_path + "/ProtectedClients.csv", pharo_image_path + "/" + "ProtectedClients_" + my_file + ".csv")
            os.rename(pharo_image_path + "/UnprotectedClients.csv", pharo_image_path + "/" + "UnprotectedClients_" + my_file + ".csv")
            #exit(0)  # debug once through
