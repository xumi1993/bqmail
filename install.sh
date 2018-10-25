#!/bin/bash
mkdir ./bin
rm -f ./bin/*
ln -s `pwd`/bqmail.py `pwd`/bin/bqmail
ln -s `pwd`/searchDMC.py `pwd`/bin/searchDMC
ln -s `pwd`/updateCatalog.py `pwd`/bin/updateCatalog
ln -s `pwd`/bqmail_conti.py `pwd`/bin/bqmail_conti
ln -s `pwd`/download_seed.py `pwd`/bin/download_seed
if [ `uname` == "Darwin" ]; then
   if grep "export PATH=`pwd`/bin:\$PATH" ~/.bash_profile
   then
      echo "BQMail was already installed."
   else
      echo "# BQMail" >> ~/.bash_profile
      echo "export PATH=`pwd`/bin:\$PATH" >> ~/.bash_profile
      echo "Successfully install the BQMail."
   fi
else
   if grep "export PATH=`pwd`/bin:\$PATH" ~/.bashrc
   then
      echo "BQMail was already installed."
   else
      echo "# BQMail" >> ~/.bashrc
      echo "export PATH=`pwd`/bin:\$PATH" >> ~/.bashrc
      echo "Successfully install the BQMail."
   fi
fi
exec $SHELL -l
