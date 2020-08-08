/*
 * This Java source file was generated by the Gradle 'init' task.
 */
package de.invoice.ocr;

import de.invoice.ocr.data.DetectorConfig;
import de.invoice.ocr.processing.BlackWhiteProcessor;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class App {
    public static void main(String[] args) {

        // Load image file
        final String imageFilename = "asia_bites.jpg";
        final String pathToInputFile = FileUtils.pathToFile("invoices", imageFilename);
        final Optional<BufferedImage> image = ImageLoader.loadImage(pathToInputFile);

        // Preprocessing
        if (image.isPresent()) {
            final BlackWhiteProcessor bwProcessor = new BlackWhiteProcessor(image.get());
            bwProcessor.apply();
        }

        // Find segments
        final DetectorConfig detectorConfig = new DetectorConfig("tessdata", "deu");
        final Detector detector = new Detector(detectorConfig);
        final List<Rectangle> segmentList = image.flatMap(detector::findSegments).orElse(new ArrayList<>());

        // Print text
        final String result = image.flatMap(detector::detect).orElse("Something went wrong!");
        System.out.println(result);

        // Draw segments
        if (image.isPresent()) {
            final ImageDrawer drawer = new ImageDrawer(image.get());
            final String pathToOutputFile = FileUtils.pathToFile("invoices-out", imageFilename);
            segmentList.forEach(r -> drawer.draw(r, Color.red));
            ImageWriter.writeImage(pathToOutputFile, image.get());
        }
    }
}
