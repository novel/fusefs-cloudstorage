#!/bin/sh
#
# Basic tests to make sure our filesystem supports
# basic UNIX shell operations such as mkdir, rm, cp etc
#
# Assummes that test filesystem is mounted under `pwd`/test
#

MOUNTPOINT="`pwd`/test"

RSTRING_GEN="uuidgen | sed 's|-||g'"
UNIXTIME="date '+%s'"

TESTS="container_ops object_ops"

test_container_ops() {
	echo "== test container operations"
	dirname=`eval ${RSTRING_GEN}`

	echo -n "* creating container... "
	mkdir ${dirname}
	echo "ok"
	echo -n "* removing container... "
	rmdir ${dirname}
	echo "ok"

}

test_object_ops() {
	echo "== test object operations"

	echo -n "* preparing container... "
	dirname=`eval ${RSTRING_GEN}`
	mkdir ${dirname}
	echo "ok"
	
	echo -n "* generating test file... "
	tmpfile_name=`eval ${RSTRING_GEN}`
	tmpfile="/tmp/${tmpfile_name}"
	uname -a > ${tmpfile}
	hostname >> ${tmpfile}
	date >> ${tmpfile}
	echo "ok"

	echo -n "* copying in test file to the storage... "
	cp ${tmpfile} ${dirname}
	echo "ok"

	echo -n "* testing if files are idential... "
	cmp ${tmpfile} ${dirname}/${tmpfile_name}
	if test $? -eq 0; then
		echo "ok"
	else
		echo "FAIL"
	fi

	echo -n "* removing test file..."
	rm ${tmpfile}
	echo "ok"
}

run_tests() {
	echo "starting tests @ ${MOUNTPOINT}"
	cd ${MOUNTPOINT}
	for testname in ${TESTS}; do
		test_func="test_${testname}"
		start_time=`eval ${UNIXTIME}`
		$test_func
		end_time=`eval ${UNIXTIME}`
		
		total_time=`expr ${end_time} - ${start_time}`
		echo "== ${testname}: ${total_time} seconds"
	done
}

run_tests
