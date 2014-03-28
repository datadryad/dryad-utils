# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org>

# This script expects to read DOIs from standard input, one per line.
#
# It will try to resolve the DOI using dx.doi.org. If resolution fails,
# it will interpret it as a Dryad file DOI, will strip a trailing slash
# followed by at one or more digits, and interpret the rsult as a Dryad
# package DOI that is expected to resolve.
#
# DOIs that fail to resolve as files, but for which the package resolves,
# are reported as "fails". If the package fails too, that fact is reported
# alongside.

while read doi ; do
    pkgdoi=`echo "$doi" | sed -e 's/\/[0-9][0-9]*$//'`
    resp=`curl -L -H "Accept: text/x-bibliography" -s -w "%{http_code}" -o /dev/null http://dx.doi.org/"$doi"`
    if [ "$resp" -lt 400 ] ; then
        echo "$doi\tresolves"
    else 
        resp=`curl -L -H "Accept: text/x-bibliography" -s -w "%{http_code}" -o /dev/null http://dx.doi.org/"$pkgdoi"`
        if [ "$resp" -lt 400 ] ; then
            echo "$doi\tfails"
        else
            echo "$doi\tfails and package fails"
        fi
    fi
done
