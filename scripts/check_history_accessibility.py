#!/usr/bin/env python3
"""Source regression for accessible history cards; run from repository root."""
from pathlib import Path

source = Path('app/src/main/java/com/xarkon/pingtest/MainActivity.java').read_text(encoding='utf-8')
checks = (
    'card.setContentDescription(o.optString("label"',
    '+ lossLabel.getText() + ", " + routeLabel',
    'card.setFocusable(true)',
    'card.setOnClickListener(v->historyDetails(o))',
    'card.setOnLongClickListener',
)
for check in checks:
    assert check in source, f'Missing history accessibility contract: {check}'
print('History accessibility UI regression: OK')
