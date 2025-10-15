#!/usr/local/bin bash
for v in .venv venv ; do
	if [[ -d $v ]] && [[ -e $v/bin/activate ]] ; then
		source $v/bin/activate
		break
	fi
done
planemo shed_update --check_diff --shed_target toolshed
