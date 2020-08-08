package de.invoice.labelling;

import de.invoice.labelling.view.WindowBuilder;

public class LabelApp {
    public static void main(String args[]) {
        WindowBuilder builder = new WindowBuilder();
        builder.setTitle("Labelling")
                .setSize(800, 600)
                .show();
    }
}
