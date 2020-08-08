package de.invoice.ocr.data;

public class DetectorConfig {
    private final String dataPath;
    private final String language;

    public DetectorConfig(final String dataPath, final String language) {
        this.dataPath = dataPath;
        this.language = language;
    }

    public String getDataPath() {
        return dataPath;
    }

    public String getLanguage() {
        return language;
    }
}
