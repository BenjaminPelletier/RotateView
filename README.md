# Consequences of rotating a 3D view using Euler angle rotations corresponding with mouse movements

## Purpose

In Artec v Creality, a case alleging that Creality copied software from Artec,  [an expert testimony](https://storage.courtlistener.com/recap/gov.uscourts.nyed.477736/gov.uscourts.nyed.477736.26.4.pdf) states:

> The most plausible explanation for the observed misbehavior is that at least some source code was copied from Artec Studio into Magic Wand and CR Studio.

The "observed misbehavior" referenced is:

> when a user drags an object in a circular path, returning to the origin of the dragging motion, the object rotates nearly, but not quite, back to the original orientation. Rather than returning exactly back to its original orientation as it should, the object’s orientation has essentially “drifted” slightly during the click-and-drag action. If the circular click-and-drag action is performed only once, the “drift” is small, and it is likely most users would not notice it. However, if the circular click-and-drag action is performed repeatedly, the “drift” accumulates each time, and after many such repeated actions, the object’s orientation will have changed noticeably.

This repository demonstrates that this behavior is the likely outcome of a particular intuitive design choice.

## 3D user interface

Most user interfaces for working with 3D objects must enable the user to change their point of view relative to the 3D objects.  The human actions most commonly used to perform this task are clicking and dragging a mouse or touching and dragging a finger across a touchscreen/touchpad.  In either case, two dimensional motion must result in rotation of the frame of reference ("view") relative to the object.

### Euler angles

When choosing how to translate two dimensional motion into rotation, a developer is likely to consider a simple case and determine how to achieve that case first.  For example, the developer may assume dragging "down" on the screen should correspond with the movement that would be observed if there was a slot machine lever sticking out of the 3D object and the user had grabbed that lever and pulled it down.  In this case, dragging "down" should rotate the object about the horizontal axis of the screen.  To visualize this, stick your right thumb out to the right and curl your fingers back toward yourself -- your fingers are rotating about the horizontal axis of the screen.  The most intuitive algorithm for accomplishing this task is to apply a rotation about the horizontal screen axis to the view, proportional to the number of pixels the cursor was dragged (either via mouse or finger).  The same logic applies when dragging horizontally, only the axis of rotation should be the vertical screen axis in that case rather than the horizontal screen axis.

Pseudocode expressing the idea above might look something like this:

```python
def rotate_view(horizontal_drag_pixels, vertical_drag_pixels):
    # Define how fast the view should rotate -- in this case, 180 degrees per 800 pixels of dragging
    k = radians(180 / 800)

    # Rotation due to the user dragging horizontally
    R_horizontal = make_axis_angle_rotation(y_axis, horizontal_drag_pixels * k)

    # Rotation due to the user dragging vertically
    R_vertical = make_axis_angle_rotation(x_axis, vertical_drag_pixels * k)

    # Apply rotations to view
    global view
    view = view * R_horizontal * R_vertical
```

This approach can be summarized as rotating the view according to Euler angle rotations based on the user dragging a cursor across the screen.

### Other approaches

There are certainly other approaches a developer may take when translating two dimensional user input into view rotation.  For instance, when there is a well-defined "up" (for instance, if the scene includes a plane that represents the ground), a desirable characteristic is often to make sure the view is always pointing "up" -- that is, the bottom edge of the view is always parallel to the ground plane.  The above approach does not achieve this goal as the view is allowed to "roll" if appropriate user input is provided.  In these cases with well-defined "up", an intuitive solution is to "orbit" the object being viewed, and the user input controls the [azimuth and elevation/altitude](https://en.wikipedia.org/wiki/Horizontal_coordinate_system) of the "camera".  Dragging, in this case, increases or decreases the azimuth angle or elevation angle.

However, this is not typically an intuitive approach when "up" is not known.  For instance, if it is unknown whether the scene's ground plane is the XY plane or the XZ plane, assuming the ground plane is XZ when it is actually XY will result in frustrating (but not entirely unusable) view rotation behavior.

## Misbehavior

One of the many [documented problems](https://moble.github.io/spherical_functions/#euler-angles) with Euler angles is that they are order-dependent.  That is, we will obtain a different (but very similar) orientation if we rotate epsilon about X and then epsilon about Y rather than rotating epsilon about Y first and then epsilon about X.  This matters because the combination of many of these small Euler angle movements results in surprising behavior when dragging.  [`rotate_demo.py`](rotate_demo.py) in this repository simulates a circular cursor movement rotating a view using the Euler angles approach described above.  The result is that the view does not return to its original orientation after each circle, but rather experiences a predominant counter-clockwise yaw that increases with each circle.  This is the output from the script:

```
Originally, x-axis is [1.000 0.000 0.000] and y-axis is [0.000 1.000 0.000]
After dragging right 10 pixels, the X-axis points toward [0.999 0.000 -0.039]
After dragging down 10 pixels, the Y-axis points toward [0.000 0.999 0.039]
After 1 circles of the mouse, x-axis is [1.000 0.019 -0.002] and y-axis is [-0.019 1.000 0.000]
After 2 circles of the mouse, x-axis is [0.999 0.039 -0.003] and y-axis is [-0.039 0.999 0.000]
After 3 circles of the mouse, x-axis is [0.998 0.058 -0.005] and y-axis is [-0.058 0.998 0.000]
After 4 circles of the mouse, x-axis is [0.997 0.078 -0.006] and y-axis is [-0.078 0.997 0.000]
After 5 circles of the mouse, x-axis is [0.995 0.097 -0.008] and y-axis is [-0.097 0.995 0.000]
After 6 circles of the mouse, x-axis is [0.993 0.116 -0.009] and y-axis is [-0.116 0.993 0.001]
After 7 circles of the mouse, x-axis is [0.991 0.136 -0.011] and y-axis is [-0.136 0.991 0.001]
After 8 circles of the mouse, x-axis is [0.988 0.155 -0.012] and y-axis is [-0.155 0.988 0.001]
After 9 circles of the mouse, x-axis is [0.985 0.174 -0.014] and y-axis is [-0.174 0.985 0.001]
After 10 circles of the mouse, x-axis is [0.981 0.193 -0.015] and y-axis is [-0.193 0.981 0.001]
Note in the above that the tip of the X axis is moving upward while the tip of the Y axis is moving leftward.  That means the view is yawing with each circle of the mouse.
```

This appears to be the bug described by the expert testimony when he says:
 
 > it would be virtually impossible for this particular bug to occur in all three applications by coincidence.

As of April 20, 2022, another instance of "this particular bug" can be observed in the [OnShape CAD software](https://www.onshape.com/) -- right-click and drag circles while in the part editor and observe the part yaw with each circle.

## Author's background

My name is Benjamin Pelletier, and I can be reached by creating an issue in this repository.  I backed Creality's Kickstarter campaign for the scanner hardware dependent on the software in question.  I occasionally write software, including [Cube of Atlantis](https://www.droidgamers.com/2011/08/24/hidden-gem-cube-of-atlantis-puzzle-game-unique-frustrating-and-fun/), a puzzle game for Android where cube rotations were determined from user input using an algorithm very similar to that described in the Euler angles above.  My coauthor and I were very aware of the yaw behavior caused by repeated circular drags, and that mechanism is actually involved in some of the levels in that game.
