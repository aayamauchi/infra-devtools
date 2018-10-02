#!/bin/bash

if [ -z "${LIB_BASH_PATH}" ] ; then
    if [[ "${0}" =~ \/ ]] ; then
        LIB_BASH_PATH="$( cd ${0%/*}/../lib ; echo ${PWD} )"
    else
        LIB_BASH_PATH="$( cd $( dirname $( which ${0} | head -n1 ) )/../lib ; echo ${PWD} )"
    fi
    export LIB_BASH_PATH
fi

# Unbelievable -- even 'uname' has a different arg list.
if [ "$( uname -s )" == Darwin -a -z "${LIB_MAC_OSUX_COMPAT}" ] ; then
    source ${LIB_BASH_PATH}/mac_osux_compat.bash
fi
