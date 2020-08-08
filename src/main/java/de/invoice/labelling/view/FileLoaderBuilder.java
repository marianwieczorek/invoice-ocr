package de.invoice.labelling.view;

import javax.swing.*;
import java.awt.*;
import java.io.File;
import java.io.FileFilter;
import java.util.List;
import java.util.*;
import java.util.function.Consumer;

public class FileLoaderBuilder {
    private final Consumer<List<File>> fileConsumer;
    private final Set<String> allowedExtensions = new HashSet<>();
    private Component parent;
    private File currentDirectory;

    public FileLoaderBuilder(Consumer<List<File>> fileConsumer) {
        this.fileConsumer = fileConsumer;
    }

    public FileLoaderBuilder addExtension(String extension) {
        allowedExtensions.add(extension);
        return this;
    }

    public FileLoaderBuilder withCurrentDirectory(File directory) {
        currentDirectory = directory;
        return this;
    }

    public FileLoaderBuilder withParent(Component parent) {
        this.parent = parent;
        return this;
    }

    public Runnable build() {
        return this::openDirectory;
    }

    private void openDirectory() {
        JFileChooser chooser = createDirectoryChooser();
        int result = chooser.showOpenDialog(parent);
        if (result == JFileChooser.APPROVE_OPTION) {
            File directory = chooser.getSelectedFile();
            fileConsumer.accept(getFilesOf(directory));
        }
    }

    private JFileChooser createDirectoryChooser() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setCurrentDirectory(currentDirectory);
        fileChooser.setFileHidingEnabled(true);
        fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        fileChooser.setMultiSelectionEnabled(false);
        return fileChooser;
    }

    private List<File> getFilesOf(File directory) {
        final FileFilter filter = (File file) -> {
            String name = file.getName().toLowerCase();
            return allowedExtensions.stream().anyMatch(name::endsWith);
        };
        return Optional.ofNullable(directory.listFiles(filter))
                .map(Arrays::asList)
                .orElse(Collections.emptyList());
    }

}
