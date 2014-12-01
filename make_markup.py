#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
make_markup.py
~~~~~~~~~~~~

Creates markup needed when adding journals to recently integrated rotation or to the DryadItemSummary.
 Edit the tuples and call render_itemsummary or render_recentlyintegrated to print markup to stdout

"""
__author__ = 'dan'

import argparse
import sys

def render_itemsummary(journal_name, journal_url, cover_image):
    markup = "\
        <xsl:when test='$journal-name = \"" + journal_name + "\"'>\n\
            <a target=\"_blank\">\n\
                <xsl:attribute name=\"href\">\n\
                    <xsl:choose>\n\
                        <xsl:when test=\"contains($article-doi,'doi:')\">\n\
                            <xsl:value-of\n\
                                    select=\"concat('http://dx.doi.org/', substring-after($article-doi, 'doi:'))\"/>\n\
                        </xsl:when>\n\
                        <xsl:otherwise>\n\
                            <xsl:value-of\n\
                                    select=\"string('" + journal_url + "')\"/>\n\
                        </xsl:otherwise>\n\
                    </xsl:choose>\n\
                </xsl:attribute>\n\
                <img class=\"pub-cover\" id=\"journal-logo\" src=\"/themes/Dryad/images/coverimages/" + cover_image + "\"\n\
                     alt=\"" + journal_name +" cover\"/>\n\
            </a>\n\
        </xsl:when>\n"
    return markup

def render_recentlyintegrated(journal_name, cover_image):
    escaped = journal_name.replace(' ', '%5C+')
    lowercased= journal_name.lower().replace(' ', '%5C+')
    separator = "%5C%7C%5C%7C%5C%7C"
    markup = "\
        <!-- " + journal_name + " -->\n\
		  <a class=\"single-image-link\" href=\"/discover?field=prism.publicationName_filter&amp;query=&amp;fq=prism.publicationName_filter%3A" + lowercased + separator + escaped + "\">\
<img class=\"pub-cover\" src=\"/themes/Mirage/images/recentlyIntegrated-" + cover_image + "\" alt=\"" + journal_name + "\" /></a>"
    return markup

# via http://stackoverflow.com/a/3637103
class DefaultHelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def main():
    parser = DefaultHelpParser(
        description='Generate Dryad XML markup for journal covers, using the provided name, link URL, and cover image',
        epilog='Journal name and URL should be enclosed in double quotes.\nImage files should exist in both coverimages and recentlyIntegrated versions. Use resize_cover.py for those.',
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('name', metavar='"Journal Name"', type=str)
    parser.add_argument('url', metavar='"http://website.com/"', type=str)
    parser.add_argument('image', metavar='"image-filename.png"', type=str)

    args = vars(parser.parse_args())
    print "Paste into dspace/modules/xmlui/src/main/webapp/themes/Mirage/Mirage.xsl"
    print "Update div#recently_integrated_journals, limit to 4"
    print " Begin Recently Integrated ".center(80,'=')
    print render_recentlyintegrated(args['name'], args['image'])
    print " End Recently Integrated ".center(80,'=')
    print ""
    print "Paste alphabetically into dspace/modules/xmlui/src/main/webapp/themes/Mirage/DryadItemSummary.xsl"
    print "Look for '<!-- this generates the linked journal image '"
    print " BEGIN DryadItemSummary.xsl ".center(80,'=')
    print render_itemsummary(args['name'], args['url'], args['image'])
    print " END DryadItemSummary.xsl ".center(80,'=')

if __name__ == '__main__':
    main()
