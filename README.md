# Invoice OCR
# Preprocessing
## Normalization
* Normalize color channels to [0, 1]
* Crop to centered squared section
* Order colors asc by value
  * eg. (57, 188, 31) &rarr; (31, 57, 188)
  * or (57, 188, 31) &rarr; (31, 188)

# Labeling
TODO

# Classification
The neural net predicts rotation intervals.
The intervals are growing in size starting from 0°.
Interval classes are symmetric for positive and negative angles.
Rotations in (-180°, -90°) and (90°, 180°) are merged into one single class.

Every class has the property: for every angle x in [a, b) with m = (a+b)/2, x-m is in (-a, a).

The algorithm calls the neural net multiple times to reduce the rotation iteratively.

## Distinct rotation intervals
1. [m0-r0, m0+r0), [m1-r1, m1+r1), ...
1. m0-r0 = 0°, mk-1+rk-1 = mk-rk
1. rk < mk-1+rk-1, rk-1 < rk

The last condition ensures that applying the algorithm multiple times results in decreasing indices.
Therefore, the image rotation approaches the smallest interval.

## Overlapping rotation intervals
TODO

# Training
## Rotations
For training a range of rotations for each image is used.
When an image is rotated the size must decrease to avoid filling missing information.
Since the original section is already a square, the size computes as:

### Relationship between r and b
<code>r = &Sqrt;2&middot;b/2 = &Sqrt;&half;&middot;b</code>

### Relationship between r, a, and &phi;
With <code>0 &leq; &phi; &leq; &pi;/4</code>,\
<code>r&middot;cos(&pi;/4-&phi;) = a/2</code>\
<code>r = a/(2&middot;cos(&pi;/4-&phi;))</code>

### Adding angles
<code>cos(&pi;/4-&phi;)</code>\
<code>= cos(&pi;/4)&middot;cos(&phi;)+sin(&pi;/4)&middot;sin(&phi;)</code>\
<code>= &Sqrt;&half;&middot;(cos(&phi;)+sin(&phi;))</code>

### Relationship between b, a, and &phi;
<code>b&middot;&Sqrt;&half; = a/(2&middot;cos(&pi;/4-&phi;))</code>\
<code>b&middot;&Sqrt;&half;&middot;2&middot;cos(&pi;/4-&phi;) = a</code>\
<code>b&middot;&Sqrt;&half;&middot;2&middot;&Sqrt;&half;&middot;(cos(&phi;)+sin(&phi;)) = a</code>\
<code>b = a/(cos(&phi;)+sin(&phi;))</code>

## Overfitting
In order to avoid overfitting, the colors of each training sample are changed randomly.

### Random tint
All colors are shifted by a constant hue.
This corresponds eg. to different lighting conditions.
<code>c&middot;(w-&sigma;&middot;r)</code>,
where c is a pixel color,
w is the color white,
r is a random color _per image_,
and sigma is the maximum tint amount.

### Noise
Random noise is added to each pixel.
This corresponds eg. to noise from the camera sensor.
<code>min{c+&sigma;&middot;r, w}</code>,
where c is a pixel color,
w is the color white,
r is a random color _per pixel_,
and sigma is the maximum noise amount.
