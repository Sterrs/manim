from constants import RIGHT

from scene.graph_scene import GraphScene
from mobject.geometry import Dot, Polygon
from mobject.svg.tex_mobject import TextMobject
from mobject.value_tracker import ValueTracker
from animation.creation import ShowCreation, Write, Transform
from continual_animation.update import ContinualUpdate

class ModifiedValue(ValueTracker):
    """This can be used to track a function of other values, for use in a GeometryScene

    Should be instantiated through GeometryScene, unless you want to deal with
    the update attribute yourself.
    """
    def __init__(self, func, *inputs, **kwargs):
        """

        :param func should be a function that expects len(args) input values, and
                    outputs a single integer
        """
        self.inputs = inputs
        ValueTracker.__init__(self, value=func(*(i.get_value() for i in self.inputs)), **kwargs)
        self.continual_update = ContinualUpdate(self,
                                      lambda v: v.set_value(func(*(i.get_value() for i in v.inputs))))

#TODO: Wrapper classes to fix problems in geometry classes?
#TODO: Point class.
#FIXME: Probably shouldn't use coordinates?
class GeometryScene(GraphScene):
    """A Scene specifically for euclidean and coordinate geometry.

    Instructions for use:
     - Create a subclass of this class.
     - Let's say you want to create 3 points and draw a circle through them,
       and then move them about.
     - Create 6 Value() objects, for the coordinates of the 3 points.
     - Use self.new_point_from_coords(x, y) 3 times for 3 points
     - Use self.new_circle_from3p(p1, p2, p3) to create the circle
     - Use self.play(ApplyMethod(value.set_value, x)) to animate the circle

    You can add your own things with their own updaters if you want, such as
    a label which is always next_to() a point, or something specific.

    Note: Do not attempt to modify the objects directly, it probably won't work.

    This is ideal for Olympiad geometry questions.
    """
    def construct(self):
        GraphScene.construct(self)

    def modified_value(self, func, *inputs):
        """Create a value that depends on others

        inputs should be the values it depends on, and func should be the
        function to run to keep things up to date.
        """
        mv = ModifiedValue(func, *inputs)
        self.add(mv.continual_update)
        return mv

    def new_point_from_coords(self, x, y, label=None, animate=None, **kwargs): #TODO: *animate?
        """Create an point (Dot) from a pair of coordinates

        :param x Value() x-coordinate
        :param y Value() y-coordinate
        :param animate 2-tuple of (run_time, rate_func) for the ShowCreation

        Returns a Dot()
        """
        assert(isinstance(x, ValueTracker) and isinstance(y, ValueTracker),
               "Parameters must be ValueTracker objects.")
        point = Dot(self.coords_to_point(x.get_value(), y.get_value()), **kwargs)
        point_update = ContinualUpdate(point,
                                       lambda p: p.move_to(self.coords_to_point(x.get_value(),
                                                                                y.get_value())))
        if animate is not None:
            self.play(ShowCreation(point, run_time=animate[0], rate_func=animate[1]))
        else:
            self.add(point)
        self.add(point_update)

        if label is not None:
            label = TextMobject(label)
            label.match_color(point)
            label_update = ContinualUpdate(label, lambda l: l.next_to(point, RIGHT))
            if animate is not None:
                self.play(Write(label, run_time=animate[0]*2, rate_func=animate[1]))
            else:
                self.add(label)
            self.add(label_update)

        return point

    def new_polygon_from_points(self, *points, animate=None, **kwargs):
        """Create a Polygon from many points"""
        polygon = Polygon(*[p.get_arc_center() for p in points], **kwargs)
        polygon.update_dots = points

        def transform(poly):
            vertices = [p.get_arc_center() for p in poly.update_dots]
            Transform(poly, Polygon(*vertices)).update(1)

        polygon_update = ContinualUpdate(polygon, transform)
        if animate is not None:
            self.play(ShowCreation(polygon, run_time=animate[0], rate_func=animate[1]))
        else:
            self.add(polygon)
        self.add(polygon_update)
        return polygon

    def find_intersections(self, mob1, mob2):
        """Find the points where two Mobjects intersect

        Returns a list of points
        """
        pass
