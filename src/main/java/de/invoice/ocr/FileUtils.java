package de.invoice.ocr;

import java.io.File;
import java.nio.file.Paths;
import java.util.Optional;

public class FileUtils {
    public static String pathToFile(final String path, final String filename) {
        return Paths.get(path, filename).toString();
    }

    public static Optional<File> existingFile(final String pathToFile) {
        File file = new File(pathToFile);
        if (file.exists()) {
            return Optional.of(file);
        }
        return Optional.empty();
    }

    public static Optional<File> newFile(final String pathToFile) {
        return Optional.of(new File(pathToFile));
    }

    public static String fileExtension(final File file) {
        final String filename = file.getName();
        final int indexOfDot = filename.lastIndexOf('.');
        return filename.substring(indexOfDot + 1);
    }
}
