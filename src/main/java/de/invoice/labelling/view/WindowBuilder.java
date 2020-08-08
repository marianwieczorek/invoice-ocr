package de.invoice.labelling.view;

import javax.imageio.ImageIO;
import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseEvent;
import java.awt.event.MouseWheelEvent;
import java.awt.event.WindowEvent;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class WindowBuilder {
    private int width;
    private int height;
    private String title;

    public WindowBuilder() {
        this.width = 800;
        this.height = 600;
    }

    public WindowBuilder setTitle(String title) {
        this.title = title;
        return this;
    }

    public WindowBuilder setSize(int width, int height) {
        this.width = width;
        this.height = height;
        return this;
    }

    public void show() {
        JFrame frame = createFrame();
        ImagePanel imagePanel = createImagePanel();
        FileListModel fileListModel = new FileListModel();
        JList<String> fileListView = createFileListView(fileListModel);
        Runnable openAction = createOpenAction(frame, fileListModel);
        Runnable exitAction = createExitAction(frame);
        JMenuBar menuBar = createMenuBar(openAction, exitAction);

        frame.setJMenuBar(menuBar);
        frame.add(BorderLayout.LINE_START, fileListView);
        frame.add(BorderLayout.CENTER, imagePanel);
        frame.setVisible(true);

        connectFileListToImageView(fileListView, fileListModel, imagePanel);
    }

    private JFrame createFrame() {
        JFrame frame = new JFrame(title);
        frame.setSize(width, height);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        return frame;
    }

    private static ImagePanel createImagePanel() {
        ImagePanel imagePanel = new ImagePanel();

        MouseNavigationListener navigationListener = new MouseNavigationListener() {
            Point dragOrigin = new Point();
            boolean isDragged = false;

            @Override
            public void mousePressed(MouseEvent event) {
                isDragged = event.getButton() == MouseEvent.BUTTON1;
                if (isDragged) {
                    dragOrigin = event.getPoint();
                }
            }

            @Override
            public void mouseDragged(MouseEvent event) {
                if (isDragged) {
                    int x = event.getX() - dragOrigin.x;
                    int y = event.getY() - dragOrigin.y;
                    imagePanel.moveImage(x, y);
                    dragOrigin = event.getPoint();
                }
            }

            @Override
            public void mouseWheelMoved(MouseWheelEvent e) {
                imagePanel.scaleImage(-0.01 * e.getWheelRotation());
            }
        };

        imagePanel.addMouseListener(navigationListener);
        imagePanel.addMouseMotionListener(navigationListener);
        imagePanel.addMouseWheelListener(navigationListener);
        return imagePanel;
    }

    private static JList<String> createFileListView(FileListModel model) {
        JList<String> listView = new JList<>();
        listView.setModel(model);
        listView.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        return listView;
    }

    private static Runnable createOpenAction(Component parent, FileListModel listModel) {
        return () -> new FileLoaderBuilder(listModel::setFiles)
                .addExtension(".bmp")
                .addExtension(".gif")
                .addExtension(".png")
                .addExtension(".jpeg")
                .addExtension(".jpg")
                .withParent(parent)
                .withCurrentDirectory(listModel.getCurrentDirectory().orElse(null))
                .build().run();
    }

    private static Runnable createExitAction(Window window) {
        return () -> window.dispatchEvent(new WindowEvent(window, WindowEvent.WINDOW_CLOSING));
    }

    private static JMenuBar createMenuBar(Runnable openAction, Runnable exitAction) {
        return new MenuBuilder()
                .addAction("Open", openAction)
                .addAction("Exit", exitAction)
                .build();
    }

    private static void connectFileListToImageView(JList<String> fileListView, FileListModel fileListModel, ImagePanel imagePanel) {
        fileListView.addListSelectionListener(event -> {
            int index = fileListView.isSelectedIndex(event.getFirstIndex()) ? event.getFirstIndex() : event.getLastIndex();
            if (!event.getValueIsAdjusting() && fileListView.isSelectedIndex(index)) {
                File selectedFile = fileListModel.getFileAt(index);
                try {
                    BufferedImage image = ImageIO.read(selectedFile);
                    imagePanel.setImage(image);
                } catch (IOException e) {
                    // Do nothing.
                }
            }
        });
    }
}
