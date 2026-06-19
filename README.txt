Quiltify: A program that recreates images by covering them with 8x8 patches

How to use:
in command prompt, in folder with quiltify.py (and python3 installed) and patches folder, run quiltify.py.
supply the path to the image to be quilted.

For example: "quiltify.py corpsejack-menace.jpg" will quilt the image corpsejack-menace.jpg

===

Additional arguments:

if you write "all" instead of the path to the image to be quilted,
all images in the folder containing quiltify will be quilted (except those with "quiltify" in their name).

further arguments are supplied by giving the argument name, a colon, and the desired value.
for instance, "quiltify.py corpsejack-menace.jpg quilted:true" will quilt the image corpsejack-menace.jpg,
with quilted set to true

---

List of arguments:

quilted: default false
whether the program just uses exact black and white patches or takes colors from that part of the image.
the program will be slower with quilted true

scale: default 1
the size the input image is scaled to before being quilted. choosing a value less than 1 will make
the program run faster, the patches more visible, and the resulting file smaller. not recommended to choose
a size greater than 1

bleach: default 0
only applicable when quilted is true. the amount of white/black mixed with the lighter and darker colors respectively,
to make them closer to white or black. for every integer amount, the lighter color is averaged with one more
pixel of white, and the darker color is averaged with one more pixel of black. how noticeable this is varies with
how many lighter than average and darker than average colors there are in the patch

contrast: default 0
only applicable when quilted is true. a difference vector is taken between the two colors, normalized, and added/subtracted
from each color times the value supplied.

similarity: default 0
the similarity method used to decide which patch is used among patches of the same brightness.
0: take sum of absolute difference between image and potential patch at each pixel
1: take sum of squared difference between image and potential patch at each pixel
2: randomly select potential patch
_: select the first patch in the array (the first patch alphabetically in patches/)

===

Advanced use:

further patches can be added/removed in patches folder. name (mostly) does not matter, just make 8x8 pngs.
the program scans patches for color #000000, so any other color will be treated as the light color.
program automatically inverts each patch, so don't include inverted versions of patches (will cause slowdown).
rotations of patches are necessary if desired.