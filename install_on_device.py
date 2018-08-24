#!/usr/bin/python2.7
import os
import subprocess

def do(cmd):
    subprocess.call(cmd, shell=True)

#do('wget https://pypi.python.org/packages/9d/05/6c661df990288634d81544fb46c6ba04a52700597f6246069145e1e98e43/PyRedPitaya-1.0.tar.gz')
do('git clone https://github.com/hermitdemschoenenleben/pyrp.git')
#do('tar -xf PyRedPitaya-1.0.tar.gz')
#os.chdir('PyRedPitaya-1.0')
os.chdir('pyrp')
do('python2.7 setup.py install')
do('apt-get install python-pip python-numpy')
do('wget https://bootstrap.pypa.io/ez_setup.py -O - | python')
do('pip2 install myhdl')
os.chdir('monitor')
do('make')
do('cp libmonitor.so /usr/lib/')

do('mkdir /jumps')