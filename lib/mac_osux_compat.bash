#!/bin/bash

# See if this work can be finessed using a compatibility library.
# This is going to be really difficult, since only the GNU versions
# of the needed commands actually even provide a standard way to
# query the command to determine the version.

# Set this so that repetitive sourcing is avoided.  OO-Bash.
export LIB_MAC_OSUX_COMPAT=1

# Even if we are on a Mac OSuX system, life if further complicated by
# the fact that users may have (understandably) installed brew-installed
# GNU components into the execution path ahead of the brain-dead BSD
# versions supplied by Apple.

is_bsd_version() {
    # The BSD commands throw an exception when a '--version' is given
    # for any command, while most GNU commands actually report version
    # info.  Assume anything which responds to a version info request
    # with an error must be some brain-dead version supplied by Apple.

    # However, the GNU coreutils typically do not do this, so pre-check
    # with the path where they should be on a brew install
    { \
        readlink $( which ${1} | head -n1 ) \
            | grep -qe '^\/usr\/local\/Cellar\/coreutils\/' \
        || ${1} --version 2>/dev/null | grep -q GNU ; \
    } && return 1 || return 0
}

brew_installed() {
    # For any given command, see if we can find a GNU version which
    # has been brew-installed but not put into the path using the
    # standard name.

    { \
        which g${1} \
        || find /usr/local -name g${i} \( -type f -o -type l \) -perm +700 ; \
    } 2>/dev/null | head -n1 | grep -e '[^[:space:]]'

    false
}

function_exists() {
    type ${1} | grep -q 'shell function'
}

arglist_grep() {
    local grep_args=(${1})
    shift
   
    # Do this using a pipe to grep so we can simply pass the args.
    printf '%s\n' "${@}" | grep "${grep_args[@]}"
}

# This step is highly repetitive -- get it done in a loop before trying
# to implement manually defined function work-arounds.
while read fn ; do
    if is_bsd_version ${fn} && ! function_exists ${fn} ; then
        eval $( echo BSD_${fn}=$( which ${fn} | head -n1 ) )
        if brew_path="$( brew_installed ${fn} )" ; then
            eval $( echo ${fn}\(\) { ${brew_path} \"\${@}\" \; } )
            export -f ${fn}
        fi
    else
        eval $( echo unset BSD_${fn} )
    fi
done < <( \
	grep -ve '#' <<-END_OF_CMD_LIST
		which
		stat
		chown
		chgrp
		chmod
		#date
		sed
	END_OF_CMD_LIST
)

if [ -n "${BSD_which}" ] ; then
    # Dumb.  I tend to use the '--skip-aliases' arg for this -- a lot --
    # which the BSD version does not support.

    which() {
        eval set -- $( arglist_grep "-v -- --skip-alias" "${@}" | sed -e 's/.*/"&"/;' )
        ${BSD_which} "${@}"
    }

    export -f which

fi

if [ -n "${BSD_stat}" ] ; then
    # Every. Single. Command.

    ret_val=0 cmd_out=

    stat() {
        local fix_mode=$( echo "${*}" | grep -e '%a' )

        # Why must the BSD versions of everything be so useless?
        #    sed -e 's/-c/-f/;s/%\([UG]\)/%S\l\1/g;s/%a/%p/;' \
        eval set -- $( \
            printf '"%s"\n' "${@/--format/-c}" | \
            sed -e 's/-c/-f/;s/%U/%Su/g;s/%G/%Sg/g;s/%a/%p/;' \
        )
        cmd_out=$( ${BSD_stat} "${@}" ) || ret_val=${?}

        if [ -n "${fix_mode}" ] ; then
            # For some absurd reason, the stat command returns a 6-digit
            # octal, with no built-in way to truncate it the the 4-digit
            # octal that anyone else in the world would expect.  Hope for
            # the best with this.

            echo "${cmd_out}" | sed -e 's/[0-7][0-7]\([0-7]\{4\}\)/\1/;'
        fi

        return ${ret_val}

    }

    export -f stat

fi

if [ -n "${BSD_chown}" ] ; then

    # The BSD chown won't take the '--reference' argument.
    # The BSD chown also won't allow '.' as a user/group separator.
    chown() {
        set -- "${@/./:}"
        if local ref=$( arglist_grep '-e ^--reference' "${@}" ) ; then
            eval set -- \
                $( stat -c'%U:%G' ${ref#--reference=} ) \
                $( arglist_grep '-ve ^--reference' "${@}" | sed -e 's/.*/"&"/;' )
            
        fi
        ${BSD_chown} "${@/./:}"
    }

    export -f chown

fi

if [ -n "${BSD_chgrp}" ] ; then

    # The BSD chgrp won't take the '--reference' argument.
    chgrp() {
        set -- "${@/./:}"
        if local ref=$( arglist_grep '-e ^--reference' "${@}" ) ; then
            eval set -- \
                $( stat -c'%g' ${ref#--reference=} ) \
                $( arglist_grep '-ve ^--reference' "${@}" | sed -e 's/.*/"&"/;' )
            
        fi
        ${BSD_chgrp} "${@}"
    }

    export -f chgrp

fi

if [ -n "${BSD_chmod}" ] ; then

    # The BSD chmod won't take the '--reference' argument.
    chmod() {
        if local ref=$( arglist_grep '-e ^--reference' "${@}" ) ; then
            eval set -- \
                $( stat -c'%a' ${ref#--reference=} ) \
                $( arglist_grep '-ve ^--reference' "${@}" | sed -e 's/.*/"&"/;' )
            
        fi
        ${BSD_chmod} "${@}"
    }

    export -f chmod

fi

if [ -n "${BSD_date}" ] ; then
    # The BSD version of the date command is essentially useless.  Not
    # even sure if it is possible to do something useful with this. May
    # just have to throw an exception.
    :
fi

if [ -n "${BSD_sed}" ] ; then
    # This one is a real killer.  There is no way I am going to write
    # sed script in BSD sed format just to support Mac OSuX.  But, how
    # to fix this without essentially reimplementing sed?  Try to at
    # least fix the things I know I do that BSD does not accept.  Also,
    # the stupid "-i" work-around.

    sed() {

        # Beyond the sed command syntax changes, the BSD sed is *really*
        # irritating in its refusal to do an in-place file edit without
        # creating a backup file.

        local inplace=
        local args=()

        while [ -n "${1}" ] ; do
            case "${1}" in
            -i*)
                if [ "${#1}" -eq 2 ] ; then
                    shift
                    if [ ${1:0:1} == - ] ; then
                        inplace=true
                        continue
                    else
                        args+=("--in-place=${1}")
                    fi
                else
                    args+=("${1}")
                fi
            ;;
            --in-place*)
                if [ ${1:10:1} == = ] ; then
                    args+=("${1}")
                else
                    inplace=true
                fi
            ;;
            -e*)
                # The '-e' is optional, but really should be present.
              
                local sed_script="${1#-e}"

                # This is so meta.
                if [ ${#sed_script} -eq 0 ] ; then
                    shift
                    sed_script="${1}"
                fi

                sed_script=$( \
                    echo "${sed_script}" \
                    | ${BSD_sed} -e '
                        s/\([^\;}]\)[[:space:]]*\}/\1\;}/g;
                        s/\([^\;}]\)[[:space:]]*$/\1\;/;
                    ' \
                )
                args+=(-e "${sed_script}")
            ;;
            *)
                args+=("${1}")
                if [ -z "${2}" -a -n "${inplace}" ] ; then
                    # This should be the filename.
                    inplace="${1}"
                fi
            ;;
            esac
            shift
        done

        if [ -n "${inplace}" ] ; then
            local tmp_out="$( mktemp )"
            if ${BSD_sed} "${args[@]}" > "${tmp_out}" ; then
                # Can't chown, but we should chgrp if we can.  Probably
                # should ignore errors attempting to do this -- the 'rm'
                # and 'mv' will fail if the user doesn't actually have
                # permission to do this.
                chgrp --reference="${inplace}" "${tmp_out}" &>/dev/null || :
                chmod --reference="${inplace}" "${tmp_out}"
                rm "${inplace}" && mv "${tmp_out}" "${inplace}"
            fi
        else
            ${BSD_sed} "${args[@]}"
        fi

    }

    export -f sed
fi
