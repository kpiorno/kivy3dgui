from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle

class MyPaintWidget(Widget):

    def __init__(self, **kargs):
        super().__init__(**kargs)
        with self.canvas:
            Color(0.9, 0.9, 0.9, 1)
            self.fbo_rect = Rectangle(size=self.size)  
            
            
    def on_size(self, *args):
        self.fbo_rect.size = self.size
        
    def on_touch_down(self, touch):
        
        color = (random(), 1, 1)
        with self.canvas:
            Color(*color, mode='hsv')
            d = 30.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            touch.ud['line'] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]


