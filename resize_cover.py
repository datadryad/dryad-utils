# -*- coding: utf-8 -*-

"""
resize_cover.py
~~~~~~~~~~~~

Creates PNG images at 100x130 and a 160x200 of a journal cover image file passed as the first argument.
 The generated images maintain the original aspect ratio, and use a white background by default.  To use
 a different background color, specify it as the second argument.

 Requires pillow (up-to-date version of PIL)

The files are placed into the appropriate subdirectories of dryad-repo, so change DRYAD_REPO_ROOT if you're not me.

"""
import sys
from PIL import Image, ImageColor
from os.path import basename, splitext

__author__ = 'dan.leehr@nescent.org'


FRONT_COVER_DIMS = (100, 130)
PKG_COVER_DIMS = (160, 200)

DRYAD_REPO_ROOT =  "/Users/dan/Code/dryad-repo"

FRONT_OUTPUT_DIR = DRYAD_REPO_ROOT + "/dspace/modules/xmlui/src/main/webapp/themes/Mirage/images/"
PKG_OUTPUT_DIR = DRYAD_REPO_ROOT + "/dspace/modules/xmlui/src/main/webapp/themes/Dryad/images/coverimages/"

class CoverGenerator(object):
    def __init__(self, filename):
        self.filename = filename
        self.image = None
        self.resized = None
        self.dims = None
        self.output_filename = None
        self.bgcolor = "rgba(255,255,255,255)"

    def read_image(self):
        if self.image is None:
            self.image = Image.open(self.filename)
        return

    def generate_front_cover(self):
        """ Generate a cover image sized for the dryad homepage """
        self.read_image()
        self.dims = FRONT_COVER_DIMS
        return self.generate_cover()

    def generate_pkg_cover(self):
        """ Generate a cover image sized for the data package page """
        self.dims = PKG_COVER_DIMS
        return self.generate_cover()

    def calculate_aspect_preserved_size(self):
        widthratio = float(self.dims[0]) / float(self.image.size[0])
        heightratio = float(self.dims[1]) / float(self.image.size[1])

        ratio = min(widthratio, heightratio)
        self.aspect_preserved_size = (int(self.image.size[0] * ratio), int(self.image.size[1] * ratio))


    def generate_cover(self):
        """ Generate a cover image with the specified size """
        self.calculate_aspect_preserved_size()
        resized = self.image.copy().resize(self.aspect_preserved_size,Image.ANTIALIAS)
        # paste the resized into a new image
        color = ImageColor.getrgb(self.bgcolor)
        frame = Image.new(resized.mode, self.dims, color=color)
        box = ((self.dims[0] - resized.size[0])/2, (self.dims[1] - resized.size[1])/2)
        if resized.mode == 'RGBA':
            frame.paste(resized, box, resized)
        else:
            frame.paste(resized, box)
        self.resized = frame

    def write_cover(self):
        self.resized.save(self.output_filename, "PNG")

    def write_front_cover(self, output_filename):
        self.generate_front_cover()
        self.output_filename = output_filename
        self.write_cover()

    def write_pkg_cover(self, output_filename):
        self.generate_pkg_cover()
        self.output_filename = output_filename
        self.write_cover()

if __name__ == '__main__':
    filename = sys.argv[1]
    generator = CoverGenerator(filename)
    if len(sys.argv) > 2:
        generator.bgcolor = sys.argv[2]
    base = splitext(basename(filename))[0]
    generator.write_front_cover(FRONT_OUTPUT_DIR + "recentlyIntegrated-" + base + ".png")
    generator.write_pkg_cover(PKG_OUTPUT_DIR + base + ".png")

