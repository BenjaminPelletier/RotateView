import math

import numpy as np
import quaternion
np.set_printoptions(formatter={'all': lambda x: '%.3f' % x})

# The following demo assumes (without loss of generality) the following right-handed coordinate system:
#  +X: horizontal axis of the screen, left to right
#  +Y: vertical axis of the screen, bottom to top
#  +Z: axis perpendicular to the screen pointing toward the viewer

# Define the orientation of the view using the quaternion `q`
q0 = np.quaternion(1, 0, 0, 0)

# Check where the X and Y axes of the view are pointing
x_axis = np.array([1, 0, 0])
y_axis = np.array([0, 1, 0])
x0 = quaternion.rotate_vectors(q0, x_axis)
y0 = quaternion.rotate_vectors(q0, y_axis)
print('Originally, x-axis is {} and y-axis is {}'.format(x0, y0))

RADIANS_PER_PIXEL = math.pi / 800  # Rotate the view 180 degrees every 800 pixels of drag
def q_drag(pixels_right: float, pixels_up: float) -> np.quaternion:
  """Compute rotational transformation due to small mouse drag.
  For each horizontal pixel the user drags their mouse to the right, rotate a fixed angle about the +Y axis.
  For each vertical pixel the user drags their mouse up, rotate a fixed angle about the -X axis.
  """
  q_horizontal = quaternion.from_rotation_vector(np.array([0, math.sin(RADIANS_PER_PIXEL * pixels_right), 0]))
  q_vertical = quaternion.from_rotation_vector(np.array([-math.sin(RADIANS_PER_PIXEL * pixels_up), 0, 0]))
  return q_horizontal * q_vertical

# Demonstrate that dragging right rotates the X axis into the screen (-Z)
x_drag_right = quaternion.rotate_vectors(q_drag(10, 0) * q0, x_axis)
print('After dragging right 10 pixels, the X-axis points toward {}'.format(x_drag_right))

# Demonstrate that dragging down rotates the Y axis out of the screen (+Z)
y_drag_down = quaternion.rotate_vectors(q_drag(0, -10) * q0, y_axis)
print('After dragging down 10 pixels, the Y-axis points toward {}'.format(y_drag_down))

# Simulate dragging the mouse in circles to rotate the view
DRAG_RADIUS = 20  # pixels
CURSOR_MOVEMENT_DISTANCE = 0.1  # pixels between checks for whether the cursor position is different than before
dtheta = CURSOR_MOVEMENT_DISTANCE / DRAG_RADIUS
N_CIRCLES = 10  # circles of dragging
q = q0  # Start at original orientation
for circle in range(N_CIRCLES):
  # Start the mouse cursor in the middle of a screen with notional pixel origin (0, 0)
  last_pixel_u = 0
  last_pixel_v = DRAG_RADIUS
  theta = 0
  while theta < 2 * math.pi:
    new_pixel_u = round(DRAG_RADIUS * math.sin(theta))
    new_pixel_v = round(DRAG_RADIUS * math.cos(theta))
    # Check if the cursor position has changed
    if new_pixel_u != last_pixel_u or new_pixel_v != last_pixel_v:
      # Cursor position has changed; rotate the view accordingly
      q = q_drag(new_pixel_u - last_pixel_u, new_pixel_v - last_pixel_v) * q
      last_pixel_u = new_pixel_u
      last_pixel_v = new_pixel_v
    theta += dtheta  # move the subpixel location of the cursor
  # Take a look at where the X and Y axes of the view are pointing
  xc = quaternion.rotate_vectors(q, x_axis)
  yc = quaternion.rotate_vectors(q, y_axis)
  print('After {} circles of the mouse, x-axis is {} and y-axis is {}'.format(circle + 1, xc, yc))

print('Note in the above that the tip of the X axis is moving upward while the tip of the Y axis is moving leftward.  That means the view is yawing with each circle of the mouse.')
