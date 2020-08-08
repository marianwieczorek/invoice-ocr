package de.invoice.ocr;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.function.Consumer;

public class ImageWriter {
    public static void writeImage(final String pathToImageFile, final BufferedImage image) {
        FileUtils.newFile(pathToImageFile)
                .map(ImageWriter::createImageWriter)
                .ifPresent(writer -> writer.accept(image));
    }

    private static Consumer<BufferedImage> createImageWriter(final File outputFile) {
        return (image) -> writeImageToFile(image, outputFile);
    }

    private static void writeImageToFile(final BufferedImage image, final File outputFile) {
        try {
            ImageIO.write(image, FileUtils.fileExtension(outputFile), outputFile);
        } catch (IOException e) {
            // Fail silently.
        }
    }
}
