from __future__ import annotations
import napari
import numpy as np
import warnings
from skimage import io
from magicgui import magicgui
from pathlib import Path
from typing import Optional
import cv2


class CameraSetter:
    """A context manager to adjust viewer camera settings before rendering."""

    def __init__(self, viewer):
        self.viewer = viewer
        # get initial settings
        self.center = viewer.camera.center
        self.zoom = viewer.camera.zoom
        self.angles = viewer.camera.angles

        self.input_canvas_size = viewer.window.qt_viewer.canvas.size

        extent = viewer._sliced_extent_world[:, -2:]
        scene_size = (extent[1] - extent[0]) / viewer.window.qt_viewer.canvas.pixel_scale  # adjust for pixel scaling
        grid_size = list(viewer.grid.actual_shape(len(viewer.layers)))

        # Adjust grid_size if necessary
        if len(scene_size) > len(grid_size):
            grid_size = [1] * (len(scene_size) - len(grid_size)) + grid_size

        # calculate target size i.e the size the canvas should be to fit the whole scene
        self.target_size = tuple((scene_size[::-1] * grid_size[::-1]).astype(int))
        self.center = viewer.camera.center
        self.zoom = viewer.camera.zoom
        self.angles = viewer.camera.angles

    # copied from viewer.reset_view and modified without padding
    def _center_on_canvas(self):
        """Reset the camera view."""
        extent = self.viewer._sliced_extent_world
        scene_size = extent[1] - extent[0]
        corner = extent[0]
        grid_size = list(self.viewer.grid.actual_shape(len(self.viewer.layers)))
        if len(scene_size) > len(grid_size):
            grid_size = [1] * (len(scene_size) - len(grid_size)) + grid_size
        size = np.multiply(scene_size, grid_size)
        center = np.add(corner, np.divide(size, 2))[-self.viewer.dims.ndisplay :]
        center = [0] * (self.viewer.dims.ndisplay - len(center)) + list(center)
        self.viewer.camera.center = center

        if np.max(size) == 0:
            self.viewer.camera.zoom = np.min(self.viewer._canvas_size)
        else:
            scale = np.array(size[-2:])
            scale[np.isclose(scale, 0)] = 1
            self.viewer.camera.zoom = 1 * np.min(np.array(self.viewer._canvas_size) / scale)
        self.viewer.camera.angles = (0, 0, 90)

    def __enter__(self):
        """Set up the viewer for rendering."""
        self.viewer.window.qt_viewer.canvas.size = self.target_size
        self._center_on_canvas()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset the viewer after rendering."""
        self.viewer.window.qt_viewer.canvas.size = self.input_canvas_size
        self.viewer.camera.center = self.center
        self.viewer.camera.zoom = self.zoom
        self.viewer.camera.angles = self.angles

def get_choices(gui):
    """Return the choices for the axis dropdown."""
    viewer: napari.Viewer
    viewer = napari.current_viewer()
    choices = []
    for i, axis in enumerate(viewer.dims.axis_labels[:-2]):
        if axis is not None:
            choices.append(axis)
    return choices

@magicgui(call_button="save as tiff", directory={"mode": "d", "label": "Choose a directory"}, axis={"choices": get_choices})
def render_as_rgb(viewer: napari.Viewer, axis: Optional[int], directory=Path(), name: str = "out"):
    """Render the viewer for a single timepoint."""
    if viewer is None:
        raise ValueError("No active napari viewer. Open a napari viewer before running this function.")

    axis = int(axis) if axis is not None else None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with CameraSetter(viewer):
            if axis is not None:
                rgb = []
                for i in range(viewer.dims.range[axis][1].astype(int)):
                    viewer.dims.set_current_step(axis, i)
                    rendered_img = viewer.window.qt_viewer.canvas.render(alpha=False)
                    rgb.append(rendered_img)
                rendered_img = np.stack(rgb)
            else:
                rendered_img = viewer.window.qt_viewer.canvas.render(alpha=False)

    outpath = directory.joinpath(f"{name}.tif").as_posix()
    io.imsave(outpath, rendered_img)