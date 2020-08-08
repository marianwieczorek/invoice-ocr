package de.invoice.ocr;

import java.awt.*;
import java.awt.image.BufferedImage;

public class ImageDrawer {
    private final BufferedImage image;

    public ImageDrawer(final BufferedImage image) {
        this.image = image;
    }

    public void draw(final Rectangle rectangle, final Color color) {
        final Graphics g = image.getGraphics();
        g.setColor(color);
        g.drawRect(rectangle.x, rectangle.y, rectangle.width, rectangle.height);
        g.dispose();
    }
}
