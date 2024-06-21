import matplotlib.pyplot as plt
import numpy as np
import dearpygui.dearpygui as dpg
from matplotlib.backends.backend_agg import FigureCanvasAgg

fig = plt.figure(figsize=(11.69, 8.26), dpi=100)
canvas = FigureCanvasAgg(fig)
ax = fig.gca()
canvas.draw()
buf = canvas.buffer_rgba()
image = np.asarray(buf)
image = image.astype(np.float32) / 255

with dpg.texture_registry():
    dpg.add_raw_texture(
        1169, 826, image, format=dpg.mvFormat_Float_rgba, id="texture_id"
    )

with dpg.window(label="MatPlotLib"):
    dpg.add_image("texture_id")

dpg.create_viewport(title='AutoFOSS Viz', width=800, height=500)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()