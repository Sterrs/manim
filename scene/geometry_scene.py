from constants import RIGHT

from scene.graph_scene import GraphScene
from mobject.geometry import Dot, Polygon, Circle
from mobject.svg.tex_mobject import TextMobject
from mobject.value_tracker import ValueTracker
from animation.creation import ShowCreation, Write, Transform
from continual_animation.update import ContinualUpdate

import math

# TODO: Before each commit, check that documentation is up-to-date
# TODO: Lots of assert()


class ModifiedValue(ValueTracker):
    """This can be used to track a function of other values, for use in a GeometryScene

    Should be instantiated through GeometryScene, unless you want to deal with
    the update attribute yourself.
    """
    def __init__(self, func, *inputs, **kwargs):
        """A value which updates automatically as its inputs do

        :param func should be a function that expects len(args) input values, and
                    outputs a single integer
        """
        self.inputs = inputs
        ValueTracker.__init__(self, value=func(*(i.get_value() for i in self.inputs)), **kwargs)
        self.continual_update = ContinualUpdate(self,
                                                lambda v: v.set_value(func(*(i.get_value() for i in v.inputs))))

class GeoObject:
    NULL = 0
    def __init__(self, **kwargs):
        # This is where all of the references (aka the objects) which this
        #  GeoObject depends on should be stored.
        self.references = {}
        # This tells the object what its definition was. Should be an integer >0
        self.TYPE = GeoObject.NULL
        #FIXME: \/
        # Make sure kwargs are the same after update...?
        self.kwargs = kwargs
        # Once the label is set, this should be a TextMobject
        self.label = None


# FIXME: What if it wasn't a visible point?
class GeoPoint(GeoObject, Dot):
    # Types:
    # references = [ValueTracker x, ValueTracker y]
    COORDS = 1

    # references = [GeoObject a, GeoObject b]
    INTERSECTION = 2

    def __init__(self, *args, **kwargs):
        GeoObject.__init__(self, **kwargs)
        Dot.__init__(self, *args, **kwargs)

    def get_point(self):
        return self.get_arc_center()


class GeoCircle(GeoObject, Circle):
    # Types:
    # references = [GeoPoint center, ValueTracker radius]
    CENTER_RADIUS = 1

    # references = [GeoPoint p1, GeoPoint p2, GeoPoint p3]
    POINTS = 2

    # references = [GeoPoint center, GeoPoint point]
    CENTER_POINT = 3

    def __init__(self, *args, **kwargs):
        GeoObject.__init__(self, **kwargs)
        Circle.__init__(self, *args, **kwargs)


# TODO: GeoPoint like ValueTracker, not like Dot
# TODO: Move all the "new" functions into GeoObject classes
# FIXME: Probably shouldn't use coordinates?
# FIXME too; coordinates & points & all sorts!!
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

    'animate' keyword arguments should be 2-tuples of (run_time, rate_func) to be
    passed to the animation classes.

    Note: Do not attempt to modify the objects directly, it probably won't work.

    This is ideal for Olympiad geometry questions.
    """
    def distance_between(self, p1, p2):
        if isinstance(p1, GeoPoint) and isinstance(p2, GeoPoint):
            x, y = self.point_to_coords(p1.get_point())
            a, b = self.point_to_coords(p2.get_point())
        else:
            x, y = self.point_to_coords(p1)
            a, b = self.point_to_coords(p2)
        return math.sqrt((x-a)**2 + (y-b)**2)

    def modified_value(self, func, *inputs):
        """Create a value that depends on others

        inputs should be the values it depends on, and func should be the
        function to run to keep things up to date.
        """
        mv = ModifiedValue(func, *inputs)
        self.add(mv.continual_update)
        return mv

    def new_point_from_coords(self, x, y, label=None, animate=None, **kwargs):
        """Create an point (Dot) from a pair of coordinates

        :param x Value() x-coordinate
        :param y Value() y-coordinate
        :param animate See GeometryScene documentation

        Returns a GeoPoint()
        """
        assert isinstance(x, ValueTracker) and isinstance(y, ValueTracker), "Parameters must be ValueTracker objects."
        point = GeoPoint(self.coords_to_point(x.get_value(), y.get_value()), **kwargs)
        point.type = GeoPoint.COORDS
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
            point.label = label
            label.match_color(point)

            def transform(l):
                l.next_to(point, RIGHT)
                l.match_color(point)

            label_update = ContinualUpdate(label, transform)
            if animate is not None:
                self.play(Write(label, run_time=animate[0]*2, rate_func=animate[1]))
            else:
                self.add(label)
            self.add(label_update)

        return point

    def new_circle_from_center_and_radius(self, center, radius, animate=None, **kwargs):
        """Create a circle from a Point at its center and its radius

        :param center A GeoPoint to set as the center
        :param radius A ValueTracker or ModifiedValue to use as the radius
        :param animate See GeometryScene documentation
        """
        circle = GeoCircle(radius=3/5*radius.get_value(), *kwargs)
        circle.type = GeoCircle.CENTER_RADIUS
        circle.references["center"] = center
        circle.references["radius"] = radius
        circle.move_arc_center_to(center.get_point())

        def transform(circ):
            new = Circle(radius=3/5*circ.references["radius"].get_value()) # , **circ.kwargs)
            new.move_arc_center_to(circ.references["center"].get_point())
            Transform(circ, new).update(1)

        circle_update = ContinualUpdate(circle, transform)
        if animate is not None:
            self.play(ShowCreation(circle, run_time=animate[0], rate_func=animate[1]))
        else:
            self.add(circle)
        self.add(circle_update)

        return circle

    def new_circle_from_center_and_point(self, center, point, animate=None, **kwargs):
        radius = ValueTracker(self.distance_between(center, point))

        def update_radius(radius):
            c = radius.circle_center
            p = radius.circle_point
            radius.set_value(self.distance_between(c, p))

        radius.circle_center = center
        radius.circle_point = point
        radius_update = ContinualUpdate(radius, update_radius)
        self.add(radius_update)

        circle = self.new_circle_from_center_and_radius(center, radius, animate=animate, **kwargs)
        circle.type = GeoCircle.CENTER_POINT
        return circle

    def new_circle_from_points(self, p1, p2, p3):
        """Create a circle from 3 non-collinear points"""
        def find_center(p1, p2, p3):
            x1, y1 = self.point_to_coords(p1.get_point())
            x2, y2 = self.point_to_coords(p2.get_point())
            x3, y3 = self.point_to_coords(p3.get_point())
            x, y = 0, 0
            # Find center & radius
            if x1 == x2:
                y = (y1 + y2)/2
                x = (y3 - y2)*((y2+y3)/2 - y) / (x3 - x2) + (x2+x3)/2
            elif x2 == x3:
                y = (y2 + y3)/2
                x = (y2 - y1) * ((y1 + y2) / 2 - y) / (x2 - x1) + (x1 + x2) / 2
            else:
                ma = (y2 - y1) / (x2 - x1)
                mb = (y3 - y2) / (x3 - x2)
                assert ma != mb, "The points must not be collinear!"
                x = (ma * mb * (y1 - y3) + mb * (x1 + x2) - ma * (x2 + x3)) / (2 * (mb - ma))
                if y3 == y2:
                    y = (-1 / ma) * (x - (x1 + x2) / 2) + (y1 + y2) / 2
                else:
                    y = (-1/mb)*(x-(x2+x3)/2) + (y2+y3)/2
            return self.coords_to_point(x, y)
        center = GeoPoint(find_center(p1, p2, p3))
        center.references["p1"] = p1
        center.references["p2"] = p2
        center.references["p3"] = p3
        center_update = ContinualUpdate(center,
                                        lambda c: c.move_to(find_center(c.references["p1"],
                                                                        c.references["p2"],
                                                                        c.references["p3"])))
        self.add(center_update)
        # Call new_circle_from_center_and_point
        circle = self.new_circle_from_center_and_point(center, p1)
        circle.type = GeoCircle.POINTS
        return circle

    # TODO: GeoPolygon
    def new_polygon_from_points(self, *points, animate=None, **kwargs):
        """Create a Polygon from many points"""
        polygon = Polygon(*[p.get_point() for p in points], **kwargs)
        polygon.update_dots = points

        def transform(poly):
            vertices = [p.get_point() for p in poly.update_dots]
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
