# -*- coding: utf-8 -*-

"""
make_markup.py
~~~~~~~~~~~~

Creates markup needed when adding journals to recently integrated rotation or to the DryadItemSummary.
 Edit the tuples and call render_itemsummary or render_recentlyintegrated to print markup to stdout

"""
__author__ = 'dan'

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
                    </xsl:when>"
    return markup


gms_journals = (
    ("GMS German Plastic, Reconstructive and Aesthetic Surgery", "http://www.egms.de/dynamic/de/journals/gpras/index.htm", "logo_gpras.png"),
    ("GMS Infectious Diseases", "http://www.egms.de/dynamic/en/journals/id/index.htm", "logo_id.png"),
    ("GMS Interdisciplinary Plastic and Reconstructive Surgery DGPW", "http://www.egms.de/dynamic/en/journals/iprs/", "logo_iprs_klein.png"),
    ("GMS Onkologische Rehabilitation und Sozialmedizin","http://www.egms.de/dynamic/en/journals/ors/index.htm", "logo_dgho.png"),
    ("GMS Zeitschrift für Medizinische Ausbildung","http://www.egms.de/dynamic/en/journals/zma/index.htm", "logo_gma_klein.png"),
    ("GMS Zeitschrift zur Förderung der Qualitätssicherung in medizinischen Laboratorien", "http://www.egms.de/dynamic/en/journals/lab/", "logo_lab.png")
)

jan27_journals = (
    ("Journal of Hymenoptera Research","http://www.pensoft.net/journals/jhr/","JHymenopRes.png"),
    ("Subterranean Biology","http://www.pensoft.net/journals/subtbiol/","SubterraneanBiol.png"),
)

feb20_journals = (
    ("Deutsche Entomologische Zeitschrift","http://www.pensoft.net/journals/dez/", "DEZ.png"),
)

bmc_journals = (
    ("BMC Ecology", "http://www.biomedcentral.com/bmcecol", "BMCEcology.png"),
    ("BMC Evolutionary Biology", "http://www.biomedcentral.com/bmcevolbiol", "BMCEvolBiology.png"),
)

apr2_journals = (
    ("Proceedings of the Royal Society B","http://rspb.royalsocietypublishing.org","ProceedingsB.png"),
    ("Scientific Data","http://www.nature.com/scientificdata/","ScientificData.png"),
)

elsevier_covers = (
    ("Basic and Applied Ecology","http://www.elsevier.com/locate/baae","baae.jpg"),
    ("Perspectives in Plant Ecology, Evolution and Systematics","http://www.elsevier.com/locate/ppees","ppees.jpg"),
    ("Flora - Morphology, Distribution, Functional Ecology of Plants","http://www.elsevier.com/locate/flora","flora.jpg"),
)

sep23_journals = (
    ("Ecological Applications", "http://www.esajournals.org/loi/ecap", "ecoApp.png"),
    ("Royal Society Open Science","http://royalsocietypublishing.org/royal-society-open-science","rsos.png"),
)

plos_journals = (
    ("PLOS Biology", "http://journals.plos.org/plosbiology/","plosbiology.jpg"),
    ("PLOS Computational Biology", "http://journals.plos.org/ploscompbiol/","ploscompbiol.jpg"),
    ("PLOS Genetics", "http://journals.plos.org/plosgenetics/","plosgenetics.jpg"),
    ("PLOS Medicine", "http://journals.plos.org/plosmedicine/","plosmedicine.jpg"),
    ("PLOS Neglected Tropical Diseases", "http://journals.plos.org/plosntds/","plosntds.jpg"),
    ("PLOS ONE", "http://www.plosone.org","plosone.jpg"),
    ("PLOS Pathogens", "http://journals.plos.org/plospathogens/","plospath.jpg"),
)

def render_recentlyintegrated(journal_name, cover_image):
    escaped = journal_name.replace(' ', '%5C+')
    lowercased= journal_name.lower().replace(' ', '%5C+')
    separator = "%5C%7C%5C%7C%5C%7C"
    markup = "\
        <!-- " + journal_name + " -->\n\
		  <a class=\"single-image-link\" href=\"/discover?field=prism.publicationName_filter&amp;query=&amp;fq=prism.publicationName_filter%3A" + lowercased + separator + escaped + "\">\
    <img class=\"pub-cover\" src=\"/themes/Mirage/images/recentlyIntegrated-" + cover_image + "\" alt=\"" + journal_name + "\" /></a>"
    return markup

recent_oct2014 = (
    ("Ecological Applications", "http://www.esajournals.org/loi/ecap", "ecoApp.png"),
    ("Royal Society Open Science","http://royalsocietypublishing.org/royal-society-open-science","rsos.png"),
)

for journal in plos_journals:
    print render_itemsummary(journal[0], journal[1], journal[2])

for journal in recent_oct2014:
    print render_recentlyintegrated(journal[0], journal[2])