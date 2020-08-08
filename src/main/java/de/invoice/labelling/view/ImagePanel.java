package de.invoice.labelling.view;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;

public class ImagePanel extends JPanel {
    private BufferedImage image;
    private Point offset = new Point();
    private double scale = 1.0;
    private double rotation = 0.0;

    public double getRotation() {
        return rotation;
    }

    public double getScale() {
        return scale;
    }

    public void moveImage(int x, int y) {
        offset = new Point(offset.x + x, offset.y + y);
        repaint();
    }

    public void rotateImage(double rotation) {
        this.rotation += rotation;
        repaint();
    }

    public void setImage(BufferedImage image) {
        this.image = image;

        Dimension imageSize = getSize(image);
        Dimension viewSize = getSize();

        offset = new Point();
        scale = scaleToFit(imageSize, viewSize);
        rotation = 0.0;
        repaint();
    }

    public void scaleImage(double scale) {
        this.scale += scale;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        if (image != null) {
            Dimension imageSize = getSize(image);
            Dimension scaledImageSize = scaleSize(imageSize, scale);
            Point centerOffset = center(scaledImageSize, getSize());

            Image scaledImage = image.getScaledInstance(scaledImageSize.width, scaledImageSize.height, Image.SCALE_DEFAULT);
            g.drawImage(scaledImage, centerOffset.x + offset.x, centerOffset.y + offset.y, this);
        }
    }

    private static Dimension getSize(BufferedImage image) {
        return new Dimension(image.getWidth(), image.getHeight());
    }

    private static Dimension scaleSize(Dimension size, double scale) {
        return new Dimension((int) (scale * size.width), (int) (scale * size.height));
    }

    private static Point center(Dimension inner, Dimension outer) {
        return new Point(centerOffset(inner.width, outer.width), centerOffset(inner.height, outer.height));
    }

    private static int centerOffset(int innerSize, int outerSize) {
        return (outerSize - innerSize) / 2;
    }

    private static double scaleToFit(Dimension current, Dimension target) {
        return Math.min(scaleFactor(current.width, target.width), scaleFactor(current.height, target.height));
    }

    private static double scaleFactor(double currentSize, double targetSize) {
        return targetSize / currentSize;
    }
}
