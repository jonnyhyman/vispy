# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 2

"""
Simple demonstration of ImageVisual.
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy import visuals
from vispy.visuals.transforms import (AffineTransform, STTransform,
                                      arg_to_array, LogTransform, 
                                      PolarTransform, BaseTransform)
from image_visual import get_image

image = get_image()


class Canvas(vispy.app.Canvas):
    def __init__(self):
        vispy.app.Canvas.__init__(self, keys='interactive', size=(800, 800))

        self.images = [visuals.ImageVisual(image, method='impostor')
                       for i in range(4)]
        
        # Transform all images to a standard size / location (because
        # get_image() might return unexpected sizes)
        s = 100. / max(self.images[0].size)
        tx = 0.5 * (100 - (self.images[0].size[0] * s))
        ty = 0.5 * (100 - (self.images[0].size[1] * s))
        base_tr = STTransform(scale=(s, s), translate=(tx, ty))
        
        self.images[0].transform = (STTransform(scale=(30, 30),
                                                translate=(600, 600)) *
                                    SineTransform() *
                                    STTransform(scale=(0.1, 0.1),
                                                translate=(-5, -5)) *
                                    base_tr)

        tr = AffineTransform()
        tr.rotate(30, (0, 0, 1))
        tr.rotate(40, (0, 1, 0))
        tr.scale((3, 3))
        self.images[1].transform = (STTransform(translate=(200, 600)) *
                                    tr *
                                    STTransform(translate=(-50, -50)) *
                                    base_tr)

        self.images[2].transform = (STTransform(scale=(3, -150),
                                                translate=(200, 100)) *
                                    LogTransform((0, 2, 0)) *
                                    STTransform(scale=(1, -0.01),
                                                translate=(-50, 1.3)) *
                                    base_tr)

        self.images[3].transform = (STTransform(scale=(400, 400),
                                                translate=(600, 300)) *
                                    PolarTransform() *
                                    STTransform(scale=(np.pi/200, 0.005),
                                                translate=(-3*np.pi/4., 0.1)) *
                                    base_tr)

        self.show()

    def on_draw(self, ev):
        gloo.clear(color='black', depth=True)
        for img in self.images:
            img.draw()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for img in self.images:
            img.transforms.configure(canvas=self, viewport=vp)


# A simple custom Transform
class SineTransform(BaseTransform):
    """
    Add sine wave to y-value for wavy effect.
    """
    glsl_map = """
        vec4 sineTransform(vec4 pos) {
            return vec4(pos.x, pos.y + sin(pos.x), pos.z, 1);
        }"""

    glsl_imap = """
        vec4 sineTransform(vec4 pos) {
            return vec4(pos.x, pos.y - sin(pos.x), pos.z, 1);
        }"""

    Linear = False

    @arg_to_array
    def map(self, coords):
        ret = coords.copy()
        ret[..., 1] += np.sin(ret[..., 0])
        return ret

    @arg_to_array
    def imap(self, coords):
        ret = coords.copy()
        ret[..., 1] -= np.sin(ret[..., 0])
        return ret

    def inverse(self):
        return InvSineTransform()


class InvSineTransform(BaseTransform):
    glsl_map = SineTransform.glsl_imap
    glsl_imap = SineTransform.glsl_map

    Linear = False

    map = SineTransform.imap
    imap = SineTransform.map

    def inverse(self):
        return SineTransform()

if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
