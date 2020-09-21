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

Every class has the property: for every angle x in [a, b) with m = 0.5*(a+b), x-m is in (-a, a).

The algorithm calls the neural net multiple times to reduce the rotation iteratively.

## Distinct rotation intervals
* [m0-r0, m0+r0), [m1-r1, m1+r1), ...
* m0-r0 = 0°, mk-1+rk-1 = mk-rk
* rk < mk-1+rk-1, rk-1 < rk

The last condition ensures that applying the algorithm multiple times results in decreasing indices. Therefore, the image rotation approaches the smallest interval.

## Overlapping rotation intervals
TODO

# Training
## Rotations
A range of rotations of a single image is used for training. However, if an image is rotated the size must decrease to avoid filling missing information. Since the original section is already a square, the size computes as:

### Relation between r and b
r = sqrt(2)*b / 2 = sqrt(0.5)*b

### Relation between r, a, and phi
With 0 ≤ φ ≤ π/4
r*cos(π/4 - φ) = a/2
r = a/(2*cos(π/4 - φ)

### Adding angles
cos(π/4 - φ)
= cos(π/4)*cos(φ) + sin(π/4)*sin(φ)
= sqrt(0.5)*(cos(φ) + sin(φ))

### Relation between b, a, and phi
b*sqrt(0.5) = a/(2*cos(π/4 - φ))
b*sqrt(0.5)*2*cos(π/4 - φ) = a
b*sqrt(0.5)*2*sqrt(0.5)*(cos(φ) + sin(φ)) = a
b = a/(cos(φ) + sin(φ))
