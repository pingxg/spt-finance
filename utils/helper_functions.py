import inspect
import textwrap
from colorsys import hsv_to_rgb, rgb_to_hsv

import streamlit as st


def show_code(demo):
    """Showing the code of the demo."""
    show_code = st.sidebar.checkbox("Show code", True)
    if show_code:
        # Showing the code of the demo.
        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(demo)
        st.code(textwrap.dedent("".join(sourcelines[1:])))



def color_gradient(start_hex, finish_hex="#FFFFFF", n=10, alpha=1.0):
    """ returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    including the number sign ("#FFFFFF") """

    # Starting and ending colors in RGB form
    s = start_hex
    f = finish_hex
    # Convert hex colors to RGB
    start_rgb = tuple(int(s[i:i+2], 16) for i in (1, 3, 5))
    finish_rgb = tuple(int(f[i:i+2], 16) for i in (1, 3, 5))

    if n ==1:
        return [f"rgba({start_rgb[0]}, {start_rgb[1]}, {start_rgb[2]}, {alpha})"]
    # Convert RGB to HSV
    start_hsv = rgb_to_hsv(*start_rgb)
    finish_hsv = rgb_to_hsv(*finish_rgb)
    # Generate a list of HSV tuples between start and end
    hsv_tuples = [(start_hsv[0] + (i * (finish_hsv[0] - start_hsv[0]) / (n-1)),
                start_hsv[1] + (i * (finish_hsv[1] - start_hsv[1]) / (n-1)),
                start_hsv[2] + (i * (finish_hsv[2] - start_hsv[2]) / (n-1)))
                for i in range(n)]
    # Convert the HSV tuples to RGB tuples and scale to 0-255
    rgb_tuples = [(int(rgb[0]), int(rgb[1]), int(rgb[2])) for rgb in [hsv_to_rgb(*hsv) for hsv in hsv_tuples]]
    # Add the alpha value to the RGB tuples to create RGBA tuples
    rgba_tuples = [(rgb[0], rgb[1], rgb[2], alpha) for rgb in rgb_tuples]
    # Create a list of strings in the format "rgba(r, g, b, a)"
    return ["rgba({}, {}, {}, {})".format(rgba[0], rgba[1], rgba[2], rgba[3]) for rgba in rgba_tuples]