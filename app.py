from OpenGL.GL import GL_COLOR_BUFFER_BIT, glClear, glClearColor
import glfw
import colorsys
from multiprocessing import Process, Queue
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

class ColourControls:
    def __init__(self):
        self.state = self.new_slider_state()

    def adjust(self, key, value):
        self.next_state(key, value)
        self.queue.put(self.rgb_colour_values())

    def next_state(self, key, value):
        self.state[key] = value
        if key in ['h', 's', 'v']:
            r, g, b = colorsys.hsv_to_rgb(*self.hsv_colour_values())
            self.state['r'] = int(r * 255)
            self.state['g'] = int(g * 255)
            self.state['b'] = int(b * 255)
        else:
            h, s, v = colorsys.rgb_to_hsv(*self.rgb_colour_values())
            self.state['h'] = int(h * 360)
            self.state['s'] = int(s * 100)
            self.state['v'] = int(v * 100)

    def hsv_colour_values(self):
        h_value, s_value, v_value = [self.state[k] for k in ['h', 's', 'v']]
        return [float(h_value) / 360.0, float(s_value) / 100.0, float(v_value) / 100.0]

    def rgb_colour_values(self):
        r_value, g_value, b_value = [self.state[k] for k in ['r', 'g', 'b']]
        return [float(r_value) / 255.0, float(g_value) / 255.0, float(b_value) / 255.0]

    def new_slider_state(_self):
        return {
                'r': 0,
                'g': 0,
                'b': 0,
                'h': 0,
                's': 0,
                'v': 0
                }

    def connect(self, queue):
        pass

class GUIColourControls(ColourControls):
    sliders = {}
    def connect(self, queue):
        self.queue = queue
        # suppress callbacks when we're automatically moving sliders
        self.is_auto_update = False

        app = QApplication([])

        window = QWidget()
        window.setWindowTitle('half_light controls')
        layout = QVBoxLayout()

        label = QLabel("Drag the sliders to change the colour.")

        for slider in self.state.keys():
            if slider == 'h':
                max = 360
            elif slider == 's':
                max = 100
            elif slider == 'v':
                max = 100
            else:
                max = 255
            self.sliders[slider] = self.create_slider(slider, max)
            widget = self.layout_with_label(self.sliders[slider], slider)
            layout.addWidget(widget)

        window.setLayout(layout)
        window.show()

        QApplication.exec()

    def layout_with_label(self, slider, slider_name):
        label = QLabel()
        label.setText(slider_name.upper())

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(slider)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_slider(self, key, max):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, max)
        slider.valueChanged.connect(lambda new_value: self.slider_value_changed(key, new_value))
        return slider

    def slider_value_changed(self, slider, new_value):
        if self.is_auto_update:
            return

        self.adjust(slider, new_value)

        self.is_auto_update = True
        for slider in self.state.keys():
            self.sliders[slider].setValue(self.state[slider])
        self.is_auto_update = False

class Viewport:
    def connect(self, queue):
        if not glfw.init():
            return

        window = glfw.create_window(640, 480, "half_light", None, None)
        if not window:
            glfw.terminate()
            return

        glfw.make_context_current(window)

        colour_values = [0.0, 0.0, 0.0]

        while not glfw.window_should_close(window):
            if not queue.empty():
                colour_values = queue.get()

            glClearColor(*colour_values, 1.0)
            glClear(GL_COLOR_BUFFER_BIT)
            glfw.swap_buffers(window)
            glfw.poll_events()

        glfw.terminate()

if __name__ == '__main__':
    colour_queue = Queue()

    viewport = Viewport()
    gui = GUIColourControls()

    gui_process = Process(target=gui.connect, args=(colour_queue, ))
    gui_process.start()

    render_process = Process(target=viewport.connect, args=(colour_queue,))
    render_process.start()

    gui_process.join()
    render_process.join()

