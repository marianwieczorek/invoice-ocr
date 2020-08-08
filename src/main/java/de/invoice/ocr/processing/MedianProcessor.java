package de.invoice.ocr.processing;

import java.awt.image.BufferedImage;

public class MedianProcessor {
    private final BufferedImage image;

    public MedianProcessor(final BufferedImage image) {
        this.image = image;
    }

    public void apply() {
        final int size = filterSize();
        final float[] filter = new float[size * size];
        for (int x = 0; x < image.getWidth() - size; ++x) {
            for (int y = 0; y < image.getHeight() - size; ++y) {

            }
        }
    }

    private int filterSize() {
        return (int) (0.05f * Math.min(image.getWidth(), image.getHeight()));
    }

    private static int indexOf(int x, int y, int width) {
        return y * width + x;
    }
}
