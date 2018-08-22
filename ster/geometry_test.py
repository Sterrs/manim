from big_ol_pile_of_manim_imports import *

#TODO: Add this to big_ol_pile_of_manim_imports
from scene.geometry_scene import GeometryScene

class GeometryTest(GeometryScene):
    CONFIG = {
        "graph_origin": 0*LEFT,
        "x_min": -5,
        "x_max": 5,
        "y_min": -5,
        "y_max": 5,
        "x_axis_width": 6, # Ratio of x and y needs to be the same to look symmetrical
    }

    def construct(self, *args):
        # Setup the graph
        self.setup_axes(True)
        graph = self.get_graph(lambda x: x)
        graph_label = self.get_graph_label(graph, label="y=x", x_val=4)
        self.play(ShowCreation(graph), Write(graph_label))

        # These track the values of u and v
        u = ValueTracker(3)
        v = ValueTracker(2)
        neg_u = self.modified_value(lambda x: -x, u)
        neg_v = self.modified_value(lambda x: -x, v)


        # A little pattern that will be run each time to show off
        def go():
            self.play(ApplyMethod(u.set_value, -2, run_time=1), ApplyMethod(v.set_value, 3, run_time=1))
            self.play(ApplyMethod(u.set_value, 1, run_time=1), ApplyMethod(v.set_value, -2, run_time=1))
            self.play(ApplyMethod(u.set_value, 3, run_time=1), ApplyMethod(v.set_value, 2, run_time=1))


        # First dot
        dotA = self.new_point_from_coords(u, v, label="A")
        dotB = self.new_point_from_coords(v, u, label="B")
        go()
        dotC = self.new_point_from_coords(neg_v, u, label="C")
        dotD = self.new_point_from_coords(neg_v, neg_u, label="D")
        dotE = self.new_point_from_coords(v, neg_u, label="E")
        #go()

        polygon = self.new_polygon_from_points(dotA, dotB, dotC, dotD, dotE)

        # Animate again!
        go()

        self.wait(2)