"""
AIKI Traffic Intelligence Platform
===================================
Layer 5: Content Intelligence Pipeline

Deep packet inspection og innholdsanalyse:
- Video content analysis (thumbnails, metadata)
- Text sentiment analysis
- Toxicity detection
- Educational value scoring
- Engagement pattern detection
- Dark pattern identification

Bruker:
- NLP for tekstanalyse
- Image classification for thumbnails
- Metadata extraction fra video streams
"""

import hashlib
import json
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

import numpy as np


class ContentType(Enum):
    """Type innhold"""
    VIDEO_SHORT = auto()      # < 60 sek
    VIDEO_MEDIUM = auto()     # 1-10 min
    VIDEO_LONG = auto()       # > 10 min
    IMAGE = auto()
    TEXT_POST = auto()
    STORY = auto()
    LIVE_STREAM = auto()
    AUDIO = auto()
    GAME = auto()
    ADVERTISEMENT = auto()
    UNKNOWN = auto()


class ContentCategory(Enum):
    """Innholdskategori"""
    EDUCATIONAL = auto()
    ENTERTAINMENT = auto()
    NEWS = auto()
    SOCIAL = auto()
    SPORTS = auto()
    GAMING = auto()
    MUSIC = auto()
    COMEDY = auto()
    LIFESTYLE = auto()
    SHOPPING = auto()
    POLITICAL = auto()
    NSFW = auto()
    HARMFUL = auto()
    ADVERTISEMENT = auto()
    UNKNOWN = auto()


class EngagementTactic(Enum):
    """Dopamin-drivende engagement taktikker"""
    CLIFFHANGER = auto()          # "Wait for it..."
    COUNTDOWN = auto()            # Kunstig urgency
    LOOP_BAIT = auto()            # Designet for replay
    CONTROVERSY = auto()          # Rage bait
    FOMO = auto()                 # Fear of missing out
    SOCIAL_PROOF = auto()         # "Everyone is doing it"
    VARIABLE_REWARD = auto()      # Uforutsigbar belønning
    PERSONALIZATION = auto()      # "Just for you"
    AUTOPLAY = auto()             # Automatisk neste
    INFINITE_SCROLL = auto()      # Ingen naturlig stopp


class DarkPattern(Enum):
    """Manipulative UI/UX patterns"""
    HIDDEN_COSTS = auto()
    BAIT_SWITCH = auto()
    CONFIRM_SHAMING = auto()     # "No, I don't want to save money"
    DISGUISED_ADS = auto()
    FORCED_CONTINUITY = auto()
    FRIEND_SPAM = auto()
    PRIVACY_ZUCKERING = auto()
    ROACH_MOTEL = auto()         # Easy in, hard out
    TRICK_QUESTIONS = auto()
    NOTIFICATION_SPAM = auto()


@dataclass
class ContentAnalysis:
    """Resultat av innholdsanalyse"""
    content_id: str
    content_type: ContentType
    category: ContentCategory

    # Scores (0.0 - 1.0)
    educational_value: float = 0.0
    entertainment_value: float = 0.0
    toxicity_score: float = 0.0
    engagement_intensity: float = 0.0
    manipulation_score: float = 0.0

    # Detected patterns
    engagement_tactics: list[EngagementTactic] = field(default_factory=list)
    dark_patterns: list[DarkPattern] = field(default_factory=list)

    # Metadata
    duration: int = 0
    language: str = "unknown"
    has_captions: bool = False
    has_music: bool = False

    # Decision
    should_allow: bool = True
    should_inject_alternative: bool = False
    recommendation: str = ""


@dataclass
class TextAnalysisResult:
    """Resultat av tekstanalyse"""
    sentiment: float  # -1.0 (negativ) til 1.0 (positiv)
    toxicity: float  # 0.0 - 1.0
    educational_score: float  # 0.0 - 1.0
    engagement_bait_score: float  # 0.0 - 1.0
    language: str
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)


class TextAnalyzer:
    """
    Analyserer tekstinnhold

    Uten eksterne avhengigheter - bruker keyword-basert analyse
    Kan oppgraderes til transformer-modeller senere
    """

    # Toxic keywords (forenklet)
    TOXIC_PATTERNS = [
        r'\b(hate|kill|die|stupid|idiot|loser)\b',
        r'\b(slut|whore|bitch|fuck|shit)\b',
        # Add more as needed
    ]

    # Educational indicators
    EDUCATIONAL_KEYWORDS = [
        'learn', 'explain', 'how to', 'tutorial', 'science',
        'history', 'math', 'education', 'fact', 'study',
        'research', 'university', 'teacher', 'lesson',
        'lære', 'forklare', 'hvordan', 'vitenskap', 'historie'
    ]

    # Engagement bait patterns
    ENGAGEMENT_BAIT = [
        r'wait for it',
        r'you won\'t believe',
        r'watch till the end',
        r'this changed my life',
        r'gone wrong',
        r'not clickbait',
        r'\#fyp',
        r'\#viral',
        r'part \d+',
        r'follow for more',
    ]

    def analyze(self, text: str) -> TextAnalysisResult:
        """Analyser tekst"""
        text_lower = text.lower()

        # Toxicity
        toxicity = 0.0
        for pattern in self.TOXIC_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                toxicity += 0.3
        toxicity = min(1.0, toxicity)

        # Educational score
        edu_count = sum(1 for kw in self.EDUCATIONAL_KEYWORDS if kw in text_lower)
        educational = min(1.0, edu_count * 0.2)

        # Engagement bait
        bait_count = sum(1 for pattern in self.ENGAGEMENT_BAIT
                        if re.search(pattern, text_lower, re.IGNORECASE))
        engagement_bait = min(1.0, bait_count * 0.25)

        # Simple sentiment (positive vs negative word count)
        positive_words = ['good', 'great', 'love', 'amazing', 'best', 'happy',
                         'bra', 'flott', 'fantastisk', 'glad']
        negative_words = ['bad', 'worst', 'hate', 'terrible', 'awful',
                         'dårlig', 'forferdelig', 'hater']

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        total = pos_count + neg_count
        sentiment = (pos_count - neg_count) / total if total > 0 else 0.0

        # Language detection (simplified)
        norwegian_words = ['jeg', 'du', 'det', 'er', 'og', 'på', 'for', 'ikke']
        is_norwegian = sum(1 for w in norwegian_words if w in text_lower) > 2
        language = 'no' if is_norwegian else 'en'

        # Keywords extraction (top frequent words)
        words = re.findall(r'\b\w{4,}\b', text_lower)
        word_freq = defaultdict(int)
        for w in words:
            word_freq[w] += 1
        keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:10]

        return TextAnalysisResult(
            sentiment=sentiment,
            toxicity=toxicity,
            educational_score=educational,
            engagement_bait_score=engagement_bait,
            language=language,
            keywords=keywords
        )


class EngagementDetector:
    """
    Detekterer engagement-taktikker i innhold

    Analyserer:
    - Video metadata (looping, duration)
    - Beskrivelser og titler
    - UI patterns
    """

    def detect_tactics(self, metadata: dict, text: str) -> list[EngagementTactic]:
        """Detekter engagement-taktikker"""
        tactics = []
        text_lower = text.lower()

        # Cliffhanger
        cliffhanger_patterns = ['wait for it', 'watch till end', 'you\'ll never guess']
        if any(p in text_lower for p in cliffhanger_patterns):
            tactics.append(EngagementTactic.CLIFFHANGER)

        # Loop bait (korte videoer som looper naturlig)
        duration = metadata.get('duration', 0)
        if 0 < duration < 15:  # Under 15 sek
            tactics.append(EngagementTactic.LOOP_BAIT)

        # Controversy / rage bait
        controversy_patterns = ['unpopular opinion', 'hot take', 'fight me',
                               'debate', 'controversial']
        if any(p in text_lower for p in controversy_patterns):
            tactics.append(EngagementTactic.CONTROVERSY)

        # FOMO
        fomo_patterns = ['limited time', 'only today', 'don\'t miss',
                        'going fast', 'almost sold out']
        if any(p in text_lower for p in fomo_patterns):
            tactics.append(EngagementTactic.FOMO)

        # Social proof
        social_patterns = ['everyone is', 'trending', 'viral', 'millions of']
        if any(p in text_lower for p in social_patterns):
            tactics.append(EngagementTactic.SOCIAL_PROOF)

        # Part series (designed to keep watching)
        if re.search(r'part\s*\d+', text_lower):
            tactics.append(EngagementTactic.VARIABLE_REWARD)

        # Personalization markers
        if 'for you' in text_lower or 'fyp' in text_lower:
            tactics.append(EngagementTactic.PERSONALIZATION)

        return tactics

    def calculate_engagement_intensity(self, tactics: list[EngagementTactic],
                                        metadata: dict) -> float:
        """Beregn total engagement-intensitet"""
        base_score = len(tactics) * 0.15

        # Bonus for spesielt manipulative taktikker
        high_intensity = [
            EngagementTactic.CLIFFHANGER,
            EngagementTactic.LOOP_BAIT,
            EngagementTactic.CONTROVERSY
        ]
        for tactic in tactics:
            if tactic in high_intensity:
                base_score += 0.1

        # Korte videoer = høyere intensitet
        duration = metadata.get('duration', 60)
        if duration < 30:
            base_score += 0.2
        elif duration < 60:
            base_score += 0.1

        return min(1.0, base_score)


class DarkPatternDetector:
    """
    Detekter manipulative UI/UX patterns i responses

    Analyserer HTML/JSON for kjente dark patterns
    """

    def detect_patterns(self, response_data: dict | str,
                        content_type: str) -> list[DarkPattern]:
        """Detekter dark patterns"""
        patterns = []

        if isinstance(response_data, str):
            data_str = response_data.lower()
        else:
            data_str = json.dumps(response_data).lower()

        # Disguised ads
        if '"sponsored"' in data_str or '"ad"' in data_str:
            if '"organic"' in data_str or 'looks like' in data_str:
                patterns.append(DarkPattern.DISGUISED_ADS)

        # Confirm shaming
        shame_patterns = [
            'no thanks, i don\'t want',
            'i\'ll stay',
            'maybe later',
            'no, i prefer'
        ]
        if any(p in data_str for p in shame_patterns):
            patterns.append(DarkPattern.CONFIRM_SHAMING)

        # Notification spam indicators
        if data_str.count('"notification"') > 5:
            patterns.append(DarkPattern.NOTIFICATION_SPAM)

        # Privacy zuckering
        privacy_patterns = [
            'share with friends',
            'let contacts know',
            'post to feed'
        ]
        if any(p in data_str for p in privacy_patterns):
            patterns.append(DarkPattern.PRIVACY_ZUCKERING)

        return patterns


class VideoMetadataExtractor:
    """
    Ekstraher metadata fra video streams og API responses
    """

    def extract_from_tiktok(self, video_data: dict) -> dict:
        """Ekstraher metadata fra TikTok video"""
        metadata = {
            'duration': 0,
            'width': 0,
            'height': 0,
            'has_music': False,
            'music_title': None,
            'author': None,
            'description': '',
            'hashtags': [],
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'is_ad': False
        }

        try:
            # Video info
            if 'video' in video_data:
                v = video_data['video']
                metadata['duration'] = v.get('duration', 0)
                metadata['width'] = v.get('width', 0)
                metadata['height'] = v.get('height', 0)

            # Music info
            if 'music' in video_data:
                metadata['has_music'] = True
                metadata['music_title'] = video_data['music'].get('title')

            # Author
            if 'author' in video_data:
                metadata['author'] = video_data['author'].get('uniqueId')

            # Description and hashtags
            desc = video_data.get('desc', '')
            metadata['description'] = desc
            metadata['hashtags'] = re.findall(r'#(\w+)', desc)

            # Stats
            if 'stats' in video_data:
                s = video_data['stats']
                metadata['likes'] = s.get('diggCount', 0)
                metadata['comments'] = s.get('commentCount', 0)
                metadata['shares'] = s.get('shareCount', 0)

            # Ad detection
            metadata['is_ad'] = video_data.get('isAd', False)

        except Exception:
            pass

        return metadata

    def extract_from_instagram(self, media_data: dict) -> dict:
        """Ekstraher metadata fra Instagram"""
        metadata = {
            'duration': 0,
            'media_type': 'unknown',
            'author': None,
            'caption': '',
            'hashtags': [],
            'likes': 0,
            'comments': 0,
            'is_ad': False
        }

        try:
            metadata['media_type'] = media_data.get('media_type', 'unknown')
            metadata['author'] = media_data.get('user', {}).get('username')

            caption = media_data.get('caption', {})
            if isinstance(caption, dict):
                metadata['caption'] = caption.get('text', '')
            else:
                metadata['caption'] = str(caption) if caption else ''

            metadata['hashtags'] = re.findall(r'#(\w+)', metadata['caption'])
            metadata['likes'] = media_data.get('like_count', 0)
            metadata['comments'] = media_data.get('comment_count', 0)

            if 'video_duration' in media_data:
                metadata['duration'] = media_data['video_duration']

            metadata['is_ad'] = media_data.get('is_paid_partnership', False)

        except Exception:
            pass

        return metadata


class ContentScorer:
    """
    Beregner helhetlig content score for beslutninger
    """

    # Vekter for ulike faktorer
    WEIGHTS = {
        'educational': 0.3,
        'toxicity': -0.4,
        'engagement_manipulation': -0.2,
        'dark_patterns': -0.1
    }

    # Thresholds
    ALLOW_THRESHOLD = 0.3
    INJECT_THRESHOLD = 0.1

    def calculate_score(self, analysis: ContentAnalysis) -> float:
        """
        Beregn total score for innhold

        Høyere = bedre innhold
        Lavere = mer problematisk
        """
        score = 0.5  # Baseline

        score += analysis.educational_value * self.WEIGHTS['educational']
        score += analysis.toxicity_score * self.WEIGHTS['toxicity']
        score += analysis.engagement_intensity * self.WEIGHTS['engagement_manipulation']

        # Dark patterns penalty
        dark_penalty = len(analysis.dark_patterns) * 0.05
        score -= dark_penalty

        return max(0.0, min(1.0, score))

    def make_decision(self, analysis: ContentAnalysis) -> tuple[bool, bool, str]:
        """
        Ta beslutning om innhold

        Returns: (should_allow, should_inject_alternative, recommendation)
        """
        score = self.calculate_score(analysis)

        if score >= self.ALLOW_THRESHOLD:
            return True, False, "Innhold er akseptabelt"

        if score >= self.INJECT_THRESHOLD:
            return True, True, "Innhold tillatt, men anbefaler alternativ"

        return False, True, "Innhold bør blokkeres, vis alternativ"


class ContentIntelligenceEngine:
    """
    HOVED-ENGINE for content intelligence

    Koordinerer alle analysemoduler og gir helhetlig vurdering
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Sub-modules
        self.text_analyzer = TextAnalyzer()
        self.engagement_detector = EngagementDetector()
        self.dark_pattern_detector = DarkPatternDetector()
        self.metadata_extractor = VideoMetadataExtractor()
        self.scorer = ContentScorer()

        # Cache
        self._analysis_cache: dict[str, ContentAnalysis] = {}

        # Stats
        self.stats = {
            'total_analyzed': 0,
            'blocked': 0,
            'injected': 0,
            'allowed': 0
        }

        # Database
        self._init_db()

    def _init_db(self):
        db_path = self.data_dir / "content_intelligence.db"
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS content_analysis (
                    content_id TEXT PRIMARY KEY,
                    analysis_time REAL,
                    content_type TEXT,
                    category TEXT,
                    educational_value REAL,
                    toxicity_score REAL,
                    engagement_intensity REAL,
                    manipulation_score REAL,
                    final_score REAL,
                    decision TEXT,
                    metadata JSON
                );

                CREATE TABLE IF NOT EXISTS blocked_content (
                    content_id TEXT PRIMARY KEY,
                    blocked_at REAL,
                    reason TEXT,
                    source_app TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_analysis_time
                ON content_analysis(analysis_time);
            """)

    def analyze_content(self, content_id: str, content_data: dict,
                        source_app: str = "unknown") -> ContentAnalysis:
        """
        Analyser innhold og ta beslutning

        Args:
            content_id: Unik ID for innhold
            content_data: Rå data fra API
            source_app: Kilde-app (tiktok, instagram, etc)

        Returns: ContentAnalysis med beslutning
        """
        # Sjekk cache
        if content_id in self._analysis_cache:
            return self._analysis_cache[content_id]

        self.stats['total_analyzed'] += 1

        # Ekstraher metadata basert på kilde
        if source_app == 'tiktok':
            metadata = self.metadata_extractor.extract_from_tiktok(content_data)
        elif source_app == 'instagram':
            metadata = self.metadata_extractor.extract_from_instagram(content_data)
        else:
            metadata = content_data

        # Bestem content type
        duration = metadata.get('duration', 0)
        if duration > 0:
            if duration < 60:
                content_type = ContentType.VIDEO_SHORT
            elif duration < 600:
                content_type = ContentType.VIDEO_MEDIUM
            else:
                content_type = ContentType.VIDEO_LONG
        else:
            content_type = ContentType.UNKNOWN

        # Analyser tekst (description/caption)
        text = metadata.get('description', '') or metadata.get('caption', '')
        text_analysis = self.text_analyzer.analyze(text)

        # Detekter engagement tactics
        tactics = self.engagement_detector.detect_tactics(metadata, text)
        engagement_intensity = self.engagement_detector.calculate_engagement_intensity(
            tactics, metadata
        )

        # Detekter dark patterns
        dark_patterns = self.dark_pattern_detector.detect_patterns(
            content_data, 'json'
        )

        # Bestem kategori
        if metadata.get('is_ad'):
            category = ContentCategory.ADVERTISEMENT
        elif text_analysis.educational_score > 0.5:
            category = ContentCategory.EDUCATIONAL
        elif text_analysis.toxicity > 0.5:
            category = ContentCategory.HARMFUL
        else:
            category = ContentCategory.ENTERTAINMENT

        # Bygg analyse
        analysis = ContentAnalysis(
            content_id=content_id,
            content_type=content_type,
            category=category,
            educational_value=text_analysis.educational_score,
            entertainment_value=1.0 - text_analysis.educational_score,
            toxicity_score=text_analysis.toxicity,
            engagement_intensity=engagement_intensity,
            manipulation_score=len(dark_patterns) * 0.2,
            engagement_tactics=tactics,
            dark_patterns=dark_patterns,
            duration=duration,
            language=text_analysis.language,
            has_music=metadata.get('has_music', False)
        )

        # Ta beslutning
        should_allow, should_inject, recommendation = self.scorer.make_decision(analysis)
        analysis.should_allow = should_allow
        analysis.should_inject_alternative = should_inject
        analysis.recommendation = recommendation

        # Oppdater stats
        if not should_allow:
            self.stats['blocked'] += 1
        elif should_inject:
            self.stats['injected'] += 1
        else:
            self.stats['allowed'] += 1

        # Cache og lagre
        self._analysis_cache[content_id] = analysis
        self._save_analysis(analysis)

        return analysis

    def _save_analysis(self, analysis: ContentAnalysis):
        """Lagre analyse til database"""
        db_path = self.data_dir / "content_intelligence.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO content_analysis
                (content_id, analysis_time, content_type, category,
                 educational_value, toxicity_score, engagement_intensity,
                 manipulation_score, final_score, decision, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.content_id,
                time.time(),
                analysis.content_type.name,
                analysis.category.name,
                analysis.educational_value,
                analysis.toxicity_score,
                analysis.engagement_intensity,
                analysis.manipulation_score,
                self.scorer.calculate_score(analysis),
                'allow' if analysis.should_allow else 'block',
                json.dumps({
                    'tactics': [t.name for t in analysis.engagement_tactics],
                    'dark_patterns': [p.name for p in analysis.dark_patterns]
                })
            ))

    def analyze_feed(self, feed_data: list[dict], source_app: str) -> list[ContentAnalysis]:
        """Analyser hele feed"""
        results = []
        for item in feed_data:
            content_id = item.get('id') or item.get('awemeId') or str(hash(str(item)))
            analysis = self.analyze_content(content_id, item, source_app)
            results.append(analysis)
        return results

    def get_feed_summary(self, analyses: list[ContentAnalysis]) -> dict:
        """Lag sammendrag av feed-analyse"""
        if not analyses:
            return {'total': 0}

        return {
            'total': len(analyses),
            'blocked': sum(1 for a in analyses if not a.should_allow),
            'inject_recommended': sum(1 for a in analyses if a.should_inject_alternative),
            'avg_educational': sum(a.educational_value for a in analyses) / len(analyses),
            'avg_toxicity': sum(a.toxicity_score for a in analyses) / len(analyses),
            'avg_engagement': sum(a.engagement_intensity for a in analyses) / len(analyses),
            'tactics_found': list(set(
                t.name for a in analyses for t in a.engagement_tactics
            )),
            'dark_patterns_found': list(set(
                p.name for a in analyses for p in a.dark_patterns
            ))
        }

    def get_stats(self) -> dict:
        """Hent statistikk"""
        return {
            **self.stats,
            'cache_size': len(self._analysis_cache)
        }


# Factory function
def create_content_intelligence(data_dir: str = "/home/jovnna/aiki/data/proxy") -> ContentIntelligenceEngine:
    """Opprett content intelligence engine"""
    return ContentIntelligenceEngine(Path(data_dir))
