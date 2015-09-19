#!/bin/bash
mkdir ./bin
ln -s `pwd`/bqmail.py `pwd`/bin/bqmail
ln -s `pwd`/searchDMC.py `pwd`/bin/searchDMC
ln -s `pwd`/updateCatalog.py `pwd`/bin/updateCatalog
ln -s `pwd`/bqmail_continue.py `pwd`/bin/bqmail_continue
if [ `uname` == "Darwin" ]; then
   echo "export PATH=`pwd`/bin:\$PATH" >> ~/.bash_profile
else
   echo "export PATH=`pwd`/bin:\$PATH" >> ~/.bashrc
fi
exec $SHELL -l
