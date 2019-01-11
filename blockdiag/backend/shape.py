from shaape.arrowparser import ArrowParser
from shaape.background import Background
from shaape.backgroundparser import BackgroundParser
from shaape.cairobackend import CairoBackend
from shaape.cairoepsbackend import CairoEpsBackend
from shaape.cairopdfbackend import CairoPdfBackend
from shaape.cairosvgbackend import CairoSvgBackend
from shaape.drawable import Drawable
from shaape.drawingbackend import DrawingBackend
from shaape.nameparser import NameParser
from shaape.overlayparser import OverlayParser
from shaape.scalable import Scalable
from shaape.styleparser import StyleParser
from shaape.textparser import TextParser
from shaape.yamlparser import YamlParser
from shaape.parser import Parser


class KrokiShaape:
    def __init__(self, source, output_type="png", scale=1.0, width=None, height=None):
        self.__parsers = []
        self.__backends = []
        self.__source = source
        self.__original_source = source
        self.__outfile = '-'
        self.__enable_hashing = False
        self.__additional_source = str(scale) + str(width) + str(height)
        self.register_parser(YamlParser())
        self.register_parser(BackgroundParser())
        self.register_parser(TextParser())
        self.register_parser(OverlayParser())
        self.register_parser(ArrowParser())
        self.register_parser(NameParser())
        self.register_parser(StyleParser())
        backends = {
            'svg': CairoSvgBackend,
            'pdf': CairoPdfBackend,
            'eps': CairoEpsBackend,
            'png': CairoBackend
        }
        if output_type in backends:
            self.register_backend(backends[output_type](image_scale=scale, image_width=width, image_height=height))
        else:
            self.register_backend(CairoBackend(image_scale=scale, image_width=width, image_height=height))

    def original_source(self):
        return self.__original_source

    def register_parser(self, parser):
        if not isinstance(parser, Parser):
            raise TypeError
        self.__parsers.append(parser)
        return

    def register_backend(self, backend):
        if not isinstance(backend, DrawingBackend):
            raise TypeError
        self.__backends.append(backend)
        return

    def run(self):
        raw_data = self.__source
        objects = []
        for parser in self.__parsers:
            parser.run(raw_data, objects)
            raw_data = parser.parsed_data()
            objects = parser.objects()

        for backend in self.__backends:
            backend.run(objects, self.__outfile)

    def parsers(self):
        return self.__parsers

    def backends(self):
        return self.__backends


class Options(object):
    def __init__(self):
        self.output_type = 'png'
        self.scale = 1.0
        self.width = None
        self.height = None


def generate_shaape():
    opts = Options()
    raw_data = """
     +----------+
     | +--+     |
     | |b | a   +--+
     +-|--|-----+  |
       |  |        |
  +----|--|-----+  |
  |c   |  |  +--|--+
  |    |  |  |  |
  +----|--|-----+
       |  |  |
    <--|--|--+
       |  |
       +--+

options:
- "a": {fill:[[1, 0, 0, 0.5]]}
- "b": {fill:[[0, 1, 0, 0.5]]}
- "c": {fill:[[1, 1, 0, 0.5]]}
"""
    shaape = KrokiShaape(raw_data,
                         output_type=opts.output_type,
                         scale=opts.scale,
                         width=opts.width,
                         height=opts.height)

    drawable_objects = []
    for parser in shaape.parsers():
        print drawable_objects
        print raw_data
        print parser
        parser.run(raw_data, drawable_objects)
        raw_data = parser.parsed_data()
        drawable_objects = parser.objects()

    for backend in shaape.backends():
        sortable = lambda x: isinstance(x, Drawable)
        sortable_objects = filter(lambda x: sortable(x), drawable_objects)
        unsortable_objects = filter(lambda x: not sortable(x), drawable_objects)
        drawable_objects = sorted(sortable_objects, key=lambda x: x.min()) + unsortable_objects

        for drawable_object in drawable_objects:
            if isinstance(drawable_object, Background):
                if not backend.__user_canvas_size[0]:
                    if backend.__user_canvas_size[1]:
                        scale = backend.__user_canvas_size[1] / drawable_object.size()[1] * backend.__aspect_ratio
                    else:
                        scale = backend.__pixels_per_unit[0]
                    backend._canvas_size[0] = drawable_object.size()[0] * scale
                if not backend.__user_canvas_size[1]:
                    if backend.__user_canvas_size[0]:
                        scale = backend.__user_canvas_size[0] / drawable_object.size()[0] / backend.__aspect_ratio
                    else:
                        scale = backend.__pixels_per_unit[1]
                    backend._canvas_size[1] = drawable_object.size()[1] * scale
                backend.__global_scale = [backend._canvas_size[0] / drawable_object.size()[0],
                                          backend._canvas_size[1] / drawable_object.size()[1]]
                backend._scale = backend.__global_scale[0] / (backend.DEFAULT_PIXELS_PER_UNIT * backend.__aspect_ratio)

        for drawable_object in drawable_objects:
            if isinstance(drawable_object, Scalable):
                drawable_object.scale(backend.__global_scale)

        backend.create_canvas()
        backend.draw_objects(drawable_objects)
        print backend.__surfaces[-1].get_data()


if __name__ == "__main__":
    generate_shaape()
