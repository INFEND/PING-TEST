package com.xarkon.pingtest;

import org.junit.Test;
import static org.junit.Assert.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

/** UI-only source regression: accessible history summary retains its key fields. */
public class HistoryAccessibilitySourceTest {
    @Test public void historyCardsHaveAccessibleSummary() throws Exception {
        String source = new String(Files.readAllBytes(Paths.get("src/main/java/com/xarkon/pingtest/MainActivity.java")), StandardCharsets.UTF_8);
        assertTrue(source.contains("card.setContentDescription(o.optString(\"label\""));
        assertTrue(source.contains("+ lossLabel.getText() + \", \" + routeLabel"));
        assertTrue(source.contains("card.setFocusable(true)"));
        assertTrue(source.contains("card.setOnClickListener(v->historyDetails(o))"));
    }
}
