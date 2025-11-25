# 🎭 EMOTION DETECTION - INTEGRATION GUIDE

**Date:** 19. November 2025
**Status:** Refactored and integrated with AIKI-HOME

---

## 🏗️ ARCHITECTURE

We have **TWO systems** working together:

### 1. AIKI-HOME Input Activity Monitor
**Location:** `/home/jovnna/aiki/aiki-home/src/monitoring/input_activity_monitor.py`

**Responsibility:** Actual hardware tracking
- ✅ Tracks keyboard events via `evdev`
- ✅ Tracks mouse events via `evdev`
- ✅ ADHD pattern detection (hyperfocus, distracted, normal)
- ✅ Sends metrics every 5 minutes to AIKI learning engine

**Runs as:** Async background service (systemd)

---

### 2. AIKI Emotion Detector
**Location:** `/home/jovnna/aiki/aiki_emotion_detection.py`

**Responsibility:** Emotion inference from data
- ✅ Text pattern analysis (regex + keywords)
- ✅ Consumes input metrics from AIKI-HOME monitor
- ✅ Combines signals for final emotion
- ✅ Provides tone recommendations for AIKI

**Used by:** `aiki_consciousness.py` during each interaction

---

## 🔗 HOW THEY INTEGRATE

```
┌─────────────────────────────────────────────┐
│ AIKI-HOME Input Activity Monitor           │
│ (src/monitoring/input_activity_monitor.py) │
│                                             │
│ Tracks:                                     │
│ - Keyboard events (evdev)                   │
│ - Mouse events (evdev)                      │
│ - ADHD patterns (hyperfocus/distracted)     │
└─────────────────┬───────────────────────────┘
                  │
                  │ Sends metrics every 5 min
                  ▼
┌─────────────────────────────────────────────┐
│ AIKI Learning Engine                        │
│ (aiki-home/src/ai/learning_engine.py)       │
│                                             │
│ Stores:                                     │
│ - Activity patterns                         │
│ - ADHD insights                             │
└─────────────────┬───────────────────────────┘
                  │
                  │ Can be queried
                  ▼
┌─────────────────────────────────────────────┐
│ AIKI Emotion Detector                       │
│ (aiki_emotion_detection.py)                 │
│                                             │
│ Analyzes:                                   │
│ - Text patterns (always)                    │
│ - Input metrics (if available)              │
│ - Combined signals                          │
└─────────────────┬───────────────────────────┘
                  │
                  │ Used during interaction
                  ▼
┌─────────────────────────────────────────────┐
│ AIKI Consciousness                          │
│ (aiki_consciousness.py)                     │
│                                             │
│ 1. Detects emotion from user message       │
│ 2. Adjusts tone based on emotion            │
│ 3. Generates response                       │
└─────────────────────────────────────────────┘
```

---

## 💻 USAGE

### Option 1: Text-Only (Current Default)

```python
from aiki_emotion_detection import EmotionDetector

detector = EmotionDetector()

# Detect from text only
result = detector.detect_combined("Fuck this, det fungerer ikke!")

print(result['primary_emotion'])  # → 'frustrated'
print(result['tone_adjustment'])   # → 'calm_and_helpful'
```

---

### Option 2: Text + Input Metrics (Future)

```python
# Get metrics from AIKI-HOME monitor
input_metrics = {
    'keystrokes_per_min': 150.0,   # From input_activity_monitor
    'mouse_moves_per_min': 45.2,
    'clicks_per_min': 3.1,
    'idle_seconds': 5,
    'pattern_type': 'hyperfocus'   # ADHD pattern
}

# Detect with combined signals
result = detector.detect_combined(
    text="La oss fortsette!",
    input_metrics=input_metrics
)

print(result['primary_emotion'])  # → 'focused'
print(result['input_metrics'])    # → Shows input data used
```

---

### Option 3: Update Metrics Separately

```python
# Update metrics from background process
detector.update_input_metrics({
    'keystrokes_per_min': 15.5,
    'pattern_type': 'normal',
    'idle_seconds': 120
})

# Later calls will use stored metrics
result = detector.detect_combined("Hva skjer her?")
# Will combine text + stored metrics
```

---

## 🔧 INTEGRATION STEPS (For Future)

### Step 1: Query AIKI-HOME Learning Engine

Add to `aiki_consciousness.py`:

```python
def _get_input_activity_metrics(self) -> Optional[Dict]:
    """Get latest input activity metrics from AIKI-HOME"""
    try:
        # Import AIKI-HOME learning engine
        import sys
        sys.path.append('/home/jovnna/aiki/aiki-home/src')
        from ai.learning_engine import get_learning_engine

        learning = get_learning_engine()

        # Get latest user behavior analysis
        latest = learning.get_latest_pattern('user_behavior', user_id='jovnna')

        if latest:
            return latest.get('metrics', {})
    except Exception as e:
        self.logger.debug(f"Could not get input metrics: {e}")

    return None
```

---

### Step 2: Pass Metrics to Emotion Detector

Update emotion detection call:

```python
# In process_input()
detected_emotion = None
if self.emotion_detector:
    # Try to get input metrics
    input_metrics = self._get_input_activity_metrics()

    # Detect with combined signals
    detected_emotion = self.emotion_detector.detect_combined(
        user_message,
        input_metrics=input_metrics
    )
```

---

### Step 3: Start AIKI-HOME Monitor (If Not Running)

```bash
# Check if running
systemctl status aiki-health-daemon

# Start if needed
cd /home/jovnna/aiki/aiki-home
python3 src/monitoring/input_activity_monitor.py
```

---

## 📊 METRICS FORMAT

From AIKI-HOME `input_activity_monitor.py`:

```python
{
    'category': 'user_behavior',
    'pattern_type': 'hyperfocus' | 'distracted' | 'normal',
    'confidence': 0.0-1.0,
    'timestamp': '2025-11-19T12:30:00',
    'metrics': {
        'keystrokes_per_min': 150.0,
        'mouse_moves_per_min': 45.2,
        'clicks_per_min': 3.1,
        'idle_seconds': 5.0
    },
    'session_totals': {
        'keystrokes': 12500,
        'mouse_moves': 5430,
        'clicks': 234,
        'session_duration': 3600.0  # seconds
    },
    'adhd_insights': 'Jovnna er i hyperfokus! 150 tastetrykk/min...',
    'user_id': 'jovnna'
}
```

---

## 🎯 EMOTION ADJUSTMENT RULES

### Based on Input Metrics:

**Hyperfocus (>100 keys/min):**
```python
final_scores['focused'] += 0.3
final_scores['excited'] += 0.2
```

**Slow Typing (<20 keys/min):**
```python
final_scores['tired'] += 0.2
final_scores['confused'] += 0.1
```

**ADHD Pattern = 'distracted':**
```python
final_scores['frustrated'] += 0.2
final_scores['tired'] += 0.2
```

**Long Idle (>5 min):**
```python
final_scores['anxious'] += 0.2
final_scores['confused'] += 0.1
```

---

## 📝 TESTING

### Test 1: Text-Only
```bash
python3.11 aiki_emotion_detection.py
```

Expected output:
```
Text: "Fuck this shit, det fungerer fremdeles ikke!"
Emotion: FRUSTRATED
Confidence: 0.30
```

---

### Test 2: With Input Metrics
```python
from aiki_emotion_detection import EmotionDetector

detector = EmotionDetector()

result = detector.detect_combined(
    "Hva skjer her?",
    input_metrics={
        'keystrokes_per_min': 15.5,
        'pattern_type': 'normal',
        'idle_seconds': 120
    }
)

assert result['primary_emotion'] == 'confused'
assert result['input_metrics'] is not None
```

---

### Test 3: Full Integration
```bash
# Start AIKI consciousness with emotion detection
python3.11 aiki_consciousness.py
```

Expected:
```
🎭 Detected emotion: FRUSTRATED (0.60)
   Tone: calm_and_helpful
   Recommendation: Be calm and solution-focused
```

---

## 🔒 PRIVACY

**AIKI-HOME Input Monitor:**
- ❌ Does NOT log actual keystrokes (what you type)
- ✅ Only logs PATTERNS (speed, rhythm, timing)
- ✅ All data anonymized and aggregated
- ✅ Stored locally (no cloud)

**Purpose:** Learn ADHD patterns for better accountability, not surveillance.

---

## 🚀 FUTURE ENHANCEMENTS

### Phase 1: Real-Time Integration (Pending)
- [ ] Connect emotion detector to AIKI-HOME learning engine
- [ ] Query latest input metrics during each interaction
- [ ] Test combined emotion detection

### Phase 2: Proactive Emotion Tracking (Planned)
- [ ] AIKI detects emotion BEFORE user asks
- [ ] "I notice you seem frustrated - want to talk about it?"
- [ ] Automatic tone adjustment without user input

### Phase 3: Long-Term Emotion Trends (Future)
- [ ] Track emotion history over weeks
- [ ] Identify patterns: "You're usually frustrated on Monday mornings"
- [ ] Predictive interventions: "Based on your pattern, you might need a break soon"

---

## 📦 FILES

**Core Components:**
- `aiki_emotion_detection.py` - Emotion detection logic
- `aiki-home/src/monitoring/input_activity_monitor.py` - Actual tracking
- `aiki-home/src/ai/learning_engine.py` - Data storage

**Integration:**
- `aiki_consciousness.py` - Uses emotion detector
- `aiki_config.py` - EMOTION_CONFIG settings

**Documentation:**
- `EMOTION_DETECTION_INTEGRATION.md` - This file
- `IMPLEMENTATION_SUMMARY.md` - Overall progress

---

## ✅ STATUS

**Current:**
- ✅ Duplicate trackers removed
- ✅ Emotion detector refactored
- ✅ Text-based detection working
- ✅ Input metrics integration ready
- ✅ Tests passing

**Next:**
- [ ] Connect to AIKI-HOME learning engine
- [ ] Test real-time integration
- [ ] Deploy to production

---

**Made with 🎭 by AIKI + Claude Code**
**Date:** 19. November 2025
**Version:** 2.0 (Integrated)
