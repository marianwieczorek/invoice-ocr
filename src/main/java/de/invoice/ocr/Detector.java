package de.invoice.ocr;

import de.invoice.ocr.data.DetectorConfig;
import net.sourceforge.tess4j.ITessAPI;
import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.util.List;
import java.util.Optional;

public class Detector {
    private final Tesseract tesseract;

    public Detector(final DetectorConfig config) {
        tesseract = new Tesseract();
        tesseract.setDatapath(config.getDataPath());
        tesseract.setLanguage(config.getLanguage());
    }

    public Optional<String> detect(final BufferedImage image) {
        try {
            return Optional.of(tesseract.doOCR(image));
        } catch (TesseractException e) {
            return Optional.empty();
        }
    }

    public Optional<List<Rectangle>> findSegments(final BufferedImage image) {
        try {
            return Optional.of(tesseract.getSegmentedRegions(image, ITessAPI.TessPageIteratorLevel.RIL_TEXTLINE));
        } catch (TesseractException e) {
            return Optional.empty();
        }
    }
}
