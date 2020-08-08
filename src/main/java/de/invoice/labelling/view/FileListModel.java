package de.invoice.labelling.view;

import javax.swing.*;
import javax.swing.event.ListDataEvent;
import javax.swing.event.ListDataListener;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

public class FileListModel implements ListModel<String> {
    private final List<File> files;
    private final List<ListDataListener> listeners;

    public FileListModel() {
        files = new ArrayList<>();
        listeners = new ArrayList<>();
    }

    @Override
    public void addListDataListener(ListDataListener listener) {
        listeners.add(listener);
    }

    public void clear() {
        int oldSize = getSize();
        files.clear();

        if (oldSize > 0) {
            ListDataEvent event = new ListDataEvent(this, ListDataEvent.INTERVAL_REMOVED, 0, oldSize - 1);
            listeners.forEach(listener -> listener.intervalRemoved(event));
        }
    }

    public Optional<File> getCurrentDirectory() {
        return files.stream().map(File::getParentFile).filter(Objects::nonNull).findAny();
    }

    @Override
    public String getElementAt(int index) {
        return getFileAt(index).getName();
    }

    public File getFileAt(int index) {
        return files.get(index);
    }

    @Override
    public int getSize() {
        return files.size();
    }

    @Override
    public void removeListDataListener(ListDataListener listener) {
        listeners.remove(listener);
    }

    public void setFiles(List<File> files) {
        clear();
        this.files.addAll(files);

        if (getSize() > 0) {
            ListDataEvent event = new ListDataEvent(this, ListDataEvent.INTERVAL_ADDED, 0, getSize() - 1);
            listeners.forEach(listener -> listener.intervalAdded(event));
        }
    }
}
