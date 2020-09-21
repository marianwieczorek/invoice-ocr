# Invoice OCR
# Preprocessing
## Normalization
* Normalize color channels to [0, 1]
* Crop to centered squared section
* Order colors asc by value
  * eg. (57, 188, 31) → (31, 57, 188)
  * or (57, 188, 31) → (31, 188)

# Labeling
TODO

# Classification
The neural net predicts rotation intervals. The intervals are growing in size starting from 0°. Interval classes are symmetric for positive and negative angles. Rotations in (-180°, -90°) and (90°, 180°) are merged into one single class.

Every class has the property: for every angle x in [a, b) with m = (a+b)/2, x-m is in (-a, a).

The algorithm calls the neural net multiple times to reduce the rotation iteratively.

## Distinct rotation intervals
1. [m0-r0, m0+r0), [m1-r1, m1+r1), ...
1. m0-r0 = 0°, mk-1+rk-1 = mk-rk
1. rk < mk-1+rk-1, rk-1 < rk

The last condition ensures that applying the algorithm multiple times results in decreasing indices. Therefore, the image rotation approaches the smallest interval.

## Overlapping rotation intervals
TODO

# Training
## Rotations
A range of rotations of a single image is used for training. However, if an image is rotated the size must decrease to avoid filling missing information. Since the original section is already a square, the size computes as:

### Relation between r and b
<code>r = sqrt(2)&middot;b/2 = sqrt(0.5)&middot;b</code>

### Relation between r, a, and &phi;
With <code>0 &leq; &phi; &leq; &pi;/4</code>,

<code>
r&middot;cos(&pi;/4 - &phi;) = a/2

r = a/(2&middot;cos(&pi;/4 - &phi;)
</code>

### Adding angles
<code>
cos(&pi;/4 - &phi;)

= cos(&pi;/4)&middot;cos(&phi;) + sin(&pi;/4)&middot;sin(&phi;)

= sqrt(0.5)&middot;(cos(&phi;) + sin(&phi;))
</code>

### Relation between b, a, and phi
b*sqrt(0.5) = a/(2*cos(π/4 - φ))
b*sqrt(0.5)*2*cos(π/4 - φ) = a
b*sqrt(0.5)*2*sqrt(0.5)*(cos(φ) + sin(φ)) = a
b = a/(cos(φ) + sin(φ))
