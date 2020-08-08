package de.invoice.labelling.view;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.util.LinkedHashMap;
import java.util.Map;

public class MenuBuilder {
    private final Map<String, Runnable> actions;

    public MenuBuilder() {
        actions = new LinkedHashMap<>();
    }

    public MenuBuilder addAction(String name, Runnable action) {
        actions.put(name, action);
        return this;
    }

    public JMenuBar build() {
        JMenuBar menuBar = new JMenuBar();
        JMenu fileMenu = new JMenu("File");
        menuBar.add(fileMenu);
        for (String name : actions.keySet()) {
            fileMenu.add(createItem(name));
        }
        return menuBar;
    }

    private JMenuItem createItem(String name) {
        JMenuItem item = new JMenuItem(name);
        Runnable action = actions.get(name);
        item.addActionListener((ActionEvent e) -> action.run());
        return item;
    }
}
