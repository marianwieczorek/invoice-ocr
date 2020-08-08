package de.invoice.ocr.processing;

import java.awt.*;
import java.awt.image.BufferedImage;

public class BlackWhiteProcessor {
    private final BufferedImage image;

    public BlackWhiteProcessor(final BufferedImage image) {
        this.image = image;
    }

    public void apply() {
        for (int x = 0; x < image.getWidth(); ++x) {
            for (int y = 0; y < image.getHeight(); ++y) {
                final Color currentColor = new Color(image.getRGB(x, y));
                final Color newColor = map(currentColor);
                image.setRGB(x, y, newColor.getRGB());
            }
        }
    }

    private static Color map(final Color color) {
        final float[] hsb = toHsb(color);
        return grayness(hsb) > 0.5 ? Color.white : Color.black;
    }

    private static float[] toHsb(final Color color) {
        return Color.RGBtoHSB(color.getRed(), color.getGreen(), color.getBlue(), null);
    }

    private static float grayness(final float[] hsb) {
        return hsb[2];
    }
}
