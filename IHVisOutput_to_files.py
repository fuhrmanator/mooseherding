# -*- coding: utf-8 -*-
import os


def get_files(dir, f):
    basedir = dir
    subdirs = []
    for fname in os.listdir(dir):
        fileName = os.path.join(basedir, fname)
        if os.path.isfile(fileName):
            if fileName.endswith(".txt"):
                f.write(fileName.encode('utf-8')+"\n")
                print fileName.encode('utf-8')
        elif os.path.isdir(fileName):
            subdirs.append(fileName)
    for subdir in subdirs:
        get_files(subdir, f)


savedfile = open("IHVisOutput.txt",'w')
get_files(unicode('C:/Users/fuhrm/Google Drive/Recherche/Maîtrise recherche Lahmar Elyes/Elyes Lahmar Projet recherche/Mesures des projets/IHVis output'), savedfile)
savedfile.close()
