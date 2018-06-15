
while read doi ; do
    pkgdoi=`echo "$doi" | sed -e 's/\/[0-9][.0-9]*$//'`
    resp=`curl -L -H "Accept: text/x-bibliography" -s -w "%{http_code}" -o /dev/null http://dx.doi.org/"$doi"`
    if [ "$resp" -lt 400 ] ; then
        echo -e "$doi\tresolves, updating"
	resp=`~/dryad-utils/doi_tool.py --doi=$doi --action=update`
	echo -e "$resp"
	echo ""
    else
	echo -e "$doi\tdoes not exist, creating"
        resp=`~/dryad-utils/doi_tool.py --doi=$doi --action=create`
	echo -e "$resp"
	echo ""
    fi
done
