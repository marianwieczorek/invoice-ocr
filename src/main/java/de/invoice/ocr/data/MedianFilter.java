package de.invoice.ocr.data;

import java.util.Arrays;

public class MedianFilter {
    private final float[] filterValues;
    private final int size;
    private int rowIndex;
    private int columnIndex;

    public MedianFilter(int size) {
        this.filterValues = new float[size * size];
        this.size = size;
        this.rowIndex = 0;
        this.columnIndex = 0;
    }

    public void updateRow(float[] row) {
        for (int i = 0; i < size; ++i) {
            filterValues[indexOf(i, columnIndex)] = row[i];
        }
        columnIndex = next(columnIndex);
    }

    public void updateColumn(float[] column) {
        for (int j = 0; j < size; ++j) {
            filterValues[indexOf(rowIndex, j)] = column[j];
        }
        rowIndex = next(rowIndex);
    }

    public float median() {
        float[] values = Arrays.copyOf(filterValues, filterValues.length);
        Arrays.sort(values);
        return values[values.length / 2];
    }

    private int indexOf(int i, int j) {
        return j * size + i;
    }

    private int next(int index) {
        ++index;
        if (index == size) {
            return 0;
        }
        return index;
    }
}
