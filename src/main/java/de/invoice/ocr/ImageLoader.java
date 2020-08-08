package de.invoice.ocr;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.Optional;

public class ImageLoader {
    public static Optional<BufferedImage> loadImage(final String pathToImageFile) {
        return FileUtils.existingFile(pathToImageFile).flatMap(ImageLoader::readFile);
    }

    private static Optional<BufferedImage> readFile(final File imageFile) {
        try {
            return Optional.ofNullable(ImageIO.read(imageFile));
        } catch (IOException e) {
            return Optional.empty();
        }
    }
}
