#!/bin/bash
#copy this into PHP folder
OLD_opt_flag="-O2"
NEW_opt_flag="-O0"
OLD_prof_flag="-fprofile-generate"
NEW_prof_flag="--coverage"
CONT=""
NUM_THREADS="8"
RPATH="/tmp/"
TARGET="/var/www/html/wpxy/index.php"
PHP_PATH=""

if [[ $# != 4 ]]; then

	read -n 1 -p "Press Y/y to continue with default configuration or any other key to cancel: " CONT

	case $CONT in
		"Y")
		echo -e "\nStarting with default configuration...\n"
		;;
		"y")
		echo -e "\nStarting with default configuration...\n"
		;;
		*)
		echo -e "Exiting...\n Example of use: ./autogenerate.sh <num_threads> <Results_PATH_folder> <TARGET_php_file> "
		exit
		;;
	esac
else	
	NUM_THREADS="$1"
	RPATH="$2"
	TARGET="$3"
	ZEND_PATH =$4
fi

echo -e "Number of threads used for make:$NUM_THREADS\nResults folder path: $RPATH\nTARGET php file:$TARGET\n"

rm -r $RPATH/lcov_results
mkdir -p $RPATH/lcov_results/html

echo $RPATH/lcov_results/html
sleep 2
cd $PHP_PATH
pwd
#modify the Makefile to build sources with -O0 --coverage
sed "s/$OLD_opt_flag/$NEW_opt_flag/g" "Makefile" > Makefile.copy
cp Makefile.copy Makefile
sed "s/$OLD_prof_flag/$NEW_prof_flag/g" "Makefile" > Makefile.copy
cp Makefile.copy Makefile


#build with modofied Makefile
make clean
echo -e "Building. Please wait...\n"
make prof-gen -j $NUM_THREADS &> /dev/null
./sapi/cgi/php-cgi -T1000 $TARGET &> /dev/null


#gen graphics lcov - results in ~/Documents/lcov_prof
#lcov --directory $PHP_PATH/Zend/.libs/ --rc lcov_branch_coverage=1 --capture -o $RPATH/lcov_results/results.lcov
#genhtml --branch-coverage -o $RPATH/lcov_results/html $RPATH/lcov_results/results.lcov
rm Makefile.copy

#redo the initial config of Makefile
sed "s/$NEW_opt_flag/$OLD_opt_flag/g" "Makefile" > Makefile.copy
cp Makefile.copy Makefile
sed "s/$NEW_prof_flag/$OLD_prof_flag/g" "Makefile" > Makefile.copy
cp Makefile.copy Makefile

#rebuild with default flags
#make clean
#echo -e "Rebuilding to initial configuration. Please wait...\n"
#make -j $NUM_THREADS &> /dev/null
