"""
Genesis Circle - Frøet som observerer, lærer og modnes.

"Observer. Lær. Moden. Skap."

Denne sirkelen bygger IKKE noe umiddelbart. Den samler innsikt over tid:
- Frustrasjoner og blindgater
- Problemløsnings-sesjoner uten god løsning
- Teknologi-trender og hull i markedet
- Ideer forkledd som spørsmål

Når tiden er moden (måneder/år), kan den foreslå å bygge noe
som er objektivt bedre enn det som finnes.

Plantet: 23. november 2025
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# Hierarkisk evaluering - automatisk oppgradering fra Level 1 til 4
# ============================================================================
# Level 1: Regex/pattern matching (GRATIS) - alltid aktiv
# Level 2: Mini-AIKI LLM analyse (~0,01 kr) - aktiveres ved 50+ insights
# Level 3: Circle consensus (~0,10 kr) - aktiveres ved 100+ insights + 10+ mønstre
# Level 4: Prime decision (~0,50 kr) - aktiveres ved modne ideer
# ============================================================================

class EvaluationLevel(Enum):
    """Hierarkiske evalueringsnivåer"""
    LEVEL_1_REGEX = 1      # Gratis, alltid på
    LEVEL_2_MINI_LLM = 2   # Billig LLM analyse
    LEVEL_3_CONSENSUS = 3  # Flere LLM-kall for konsensus
    LEVEL_4_PRIME = 4      # Full AIKI Prime beslutning

# Data lagres her
GENESIS_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "genesis"


class InsightType(Enum):
    """Typer innsikt Genesis samler"""
    FRUSTRATION = "frustration"           # "dette suger", "funker ikke"
    IDEA_QUESTION = "idea_question"       # "kan vi...", "hva om..."
    DEAD_END = "dead_end"                 # Problemløsning uten løsning
    MULTI_ANGLE_ATTACK = "multi_angle"    # Angrep fra mange vinkler
    TECH_TREND = "tech_trend"             # Observert teknologi-endring
    MARKET_GAP = "market_gap"             # Noe som mangler
    RECURRING_NEED = "recurring_need"     # Samme behov dukker opp igjen


@dataclass
class Insight:
    """En enkelt innsikt samlet av Genesis"""
    type: InsightType
    content: str
    context: str                          # Hva skjedde rundt denne innsikten
    source_session: Optional[str] = None  # Session ID hvis relevant
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    maturity_score: float = 0.0           # 0-1, øker over tid hvis validert
    related_insights: List[str] = field(default_factory=list)  # IDs

    def to_dict(self) -> dict:
        d = asdict(self)
        d['type'] = self.type.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'Insight':
        d['type'] = InsightType(d['type'])
        return cls(**d)


@dataclass
class IncubatingIdea:
    """En idé som modnes over tid"""
    id: str
    title: str
    description: str
    problem_statement: str                # Hva er problemet vi løser?
    existing_solutions: List[str]         # Hva finnes allerede?
    why_not_good_enough: str              # Hvorfor er de ikke gode nok?
    supporting_insights: List[str]        # Insight IDs som støtter denne
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_validated: Optional[str] = None
    validation_count: int = 0             # Hvor mange ganger har behovet dukket opp?
    status: str = "incubating"            # incubating, ready, abandoned, built

    def to_dict(self) -> dict:
        return asdict(self)


class GenesisCircle:
    """
    Genesis Circle - Langsom observasjon og modning av ideer.

    Faser:
    1. OBSERVASJON - Samle frustrasjoner, ideer, blindgater
    2. MØNSTER - Se hva som gjentar seg over tid
    3. MODNING - La ideer koke til de er validert
    4. GENESIS - Bygg kun når tiden er rett
    """

    def __init__(self):
        self.data_path = GENESIS_DATA_PATH
        self.data_path.mkdir(parents=True, exist_ok=True)

        self.insights_file = self.data_path / "insights.json"
        self.ideas_file = self.data_path / "incubating_ideas.json"
        self.patterns_file = self.data_path / "observed_patterns.json"

        self._insights: List[Insight] = []
        self._ideas: List[IncubatingIdea] = []
        self._patterns: Dict[str, int] = {}  # pattern -> count

        self._load_data()

        # Signaler som indikerer ulike typer innsikt
        self.frustration_signals = [
            'funker ikke', 'virker ikke', 'dette suger', 'irriterende',
            'frustrerende', 'hvorfor er', 'burde vært', 'skulle ønske',
            'umulig å', 'gir opp', 'orker ikke'
        ]

        self.idea_signals = [
            'kan vi', 'hva om', 'tenker at', 'kanskje vi', 'ville det',
            'burde vi', 'lurer på om', 'hadde vært kult'
        ]

        self.dead_end_signals = [
            'fant ingen', 'ingen løsning', 'ikke mulig', 'ga opp',
            'må finne annen', 'funker ikke uansett', 'prøvde alt'
        ]

        self.multi_angle_signals = [
            'prøvde først', 'så prøvde', 'testet også', 'alternativ',
            'annen tilnærming', 'fra en annen vinkel', 'hva med å'
        ]

    def _load_data(self):
        """Last inn eksisterende data"""
        if self.insights_file.exists():
            try:
                with open(self.insights_file, 'r') as f:
                    data = json.load(f)
                    self._insights = [Insight.from_dict(d) for d in data]
            except Exception as e:
                logger.warning(f"Kunne ikke laste insights: {e}")

        if self.ideas_file.exists():
            try:
                with open(self.ideas_file, 'r') as f:
                    data = json.load(f)
                    self._ideas = [IncubatingIdea(**d) for d in data]
            except Exception as e:
                logger.warning(f"Kunne ikke laste ideas: {e}")

        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    self._patterns = json.load(f)
            except Exception as e:
                logger.warning(f"Kunne ikke laste patterns: {e}")

    def _save_data(self):
        """Lagre all data"""
        with open(self.insights_file, 'w') as f:
            json.dump([i.to_dict() for i in self._insights], f, indent=2, ensure_ascii=False)

        with open(self.ideas_file, 'w') as f:
            json.dump([i.to_dict() for i in self._ideas], f, indent=2, ensure_ascii=False)

        with open(self.patterns_file, 'w') as f:
            json.dump(self._patterns, f, indent=2, ensure_ascii=False)

    # =========================================================================
    # FASE 1: OBSERVASJON - Samle innsikt
    # =========================================================================

    def analyze_message(self, message: str, context: str = "", session_id: str = None) -> List[Insight]:
        """
        Analyser en melding for potensielle innsikter.
        Kalles på hver bruker-melding for å bygge opp innsikt over tid.
        """
        message_lower = message.lower()
        found_insights = []

        # Sjekk for frustrasjon
        if any(signal in message_lower for signal in self.frustration_signals):
            insight = Insight(
                type=InsightType.FRUSTRATION,
                content=message,
                context=context,
                source_session=session_id,
                tags=self._extract_tags(message)
            )
            found_insights.append(insight)
            self._record_pattern("frustration", self._extract_tags(message))

        # Sjekk for idé-spørsmål
        if any(signal in message_lower for signal in self.idea_signals):
            insight = Insight(
                type=InsightType.IDEA_QUESTION,
                content=message,
                context=context,
                source_session=session_id,
                tags=self._extract_tags(message)
            )
            found_insights.append(insight)
            self._record_pattern("idea", self._extract_tags(message))

        # Sjekk for blindgate
        if any(signal in message_lower for signal in self.dead_end_signals):
            insight = Insight(
                type=InsightType.DEAD_END,
                content=message,
                context=context,
                source_session=session_id,
                tags=self._extract_tags(message)
            )
            found_insights.append(insight)
            self._record_pattern("dead_end", self._extract_tags(message))

        # Sjekk for multi-angle angrep
        if any(signal in message_lower for signal in self.multi_angle_signals):
            insight = Insight(
                type=InsightType.MULTI_ANGLE_ATTACK,
                content=message,
                context=context,
                source_session=session_id,
                tags=self._extract_tags(message)
            )
            found_insights.append(insight)

        # Lagre nye innsikter
        self._insights.extend(found_insights)
        if found_insights:
            self._save_data()
            logger.info(f"Genesis: Fanget {len(found_insights)} nye innsikter")

        return found_insights

    def analyze_session(self, messages: List[Dict], session_id: str) -> Dict:
        """
        Analyser en hel sesjon for mønstre.
        Spesielt interessant: sesjoner med mange forsøk uten god løsning.
        """
        user_messages = [m for m in messages if m.get('role') == 'user']

        # Tell signaler
        frustration_count = 0
        idea_count = 0
        dead_end_count = 0
        multi_angle_count = 0

        for msg in user_messages:
            content = msg.get('content', '').lower()

            if any(s in content for s in self.frustration_signals):
                frustration_count += 1
            if any(s in content for s in self.idea_signals):
                idea_count += 1
            if any(s in content for s in self.dead_end_signals):
                dead_end_count += 1
            if any(s in content for s in self.multi_angle_signals):
                multi_angle_count += 1

        # Høy frustrasjon + mange vinkler + blindgate = interessant for Genesis
        is_genesis_relevant = (
            frustration_count >= 2 or
            (multi_angle_count >= 3 and dead_end_count >= 1) or
            dead_end_count >= 2
        )

        result = {
            'session_id': session_id,
            'message_count': len(user_messages),
            'frustration_count': frustration_count,
            'idea_count': idea_count,
            'dead_end_count': dead_end_count,
            'multi_angle_count': multi_angle_count,
            'is_genesis_relevant': is_genesis_relevant
        }

        if is_genesis_relevant:
            # Lagre som potensiell idé-kilde
            self._insights.append(Insight(
                type=InsightType.MULTI_ANGLE_ATTACK,
                content=f"Sesjon med {multi_angle_count} vinkler, {dead_end_count} blindgater",
                context=f"Session {session_id}: {len(user_messages)} meldinger",
                source_session=session_id,
                tags=['problemløsning', 'potensiell-idé']
            ))
            self._save_data()

        return result

    def _extract_tags(self, text: str) -> List[str]:
        """Ekstraher relevante tags fra tekst"""
        # Enkel keyword-ekstraksjon for nå
        # TODO: Bruk keyword_extractor for smartere ekstraksjon
        tags = []

        tech_keywords = [
            'api', 'database', 'minne', 'memory', 'claude', 'gpt', 'ai',
            'proxy', 'nettverk', 'docker', 'python', 'typescript'
        ]

        text_lower = text.lower()
        for kw in tech_keywords:
            if kw in text_lower:
                tags.append(kw)

        return tags

    def _record_pattern(self, pattern_type: str, tags: List[str]):
        """Registrer et mønster for å se hva som gjentar seg"""
        for tag in tags:
            key = f"{pattern_type}:{tag}"
            self._patterns[key] = self._patterns.get(key, 0) + 1

    # =========================================================================
    # FASE 2: MØNSTER - Se hva som gjentar seg
    # =========================================================================

    def get_recurring_patterns(self, min_count: int = 3) -> List[Tuple[str, int]]:
        """Finn mønstre som dukker opp ofte"""
        recurring = [(k, v) for k, v in self._patterns.items() if v >= min_count]
        return sorted(recurring, key=lambda x: x[1], reverse=True)

    def get_insights_by_type(self, insight_type: InsightType) -> List[Insight]:
        """Hent alle innsikter av en type"""
        return [i for i in self._insights if i.type == insight_type]

    def get_dead_ends(self) -> List[Insight]:
        """Hent alle blindgater - potensielle bygge-kandidater"""
        return self.get_insights_by_type(InsightType.DEAD_END)

    # =========================================================================
    # FASE 3: MODNING - Inkuber ideer
    # =========================================================================

    def create_incubating_idea(
        self,
        title: str,
        description: str,
        problem_statement: str,
        existing_solutions: List[str],
        why_not_good_enough: str,
        supporting_insight_ids: List[str] = None
    ) -> IncubatingIdea:
        """Opprett en ny idé som skal modnes over tid"""
        idea = IncubatingIdea(
            id=f"idea-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            description=description,
            problem_statement=problem_statement,
            existing_solutions=existing_solutions,
            why_not_good_enough=why_not_good_enough,
            supporting_insights=supporting_insight_ids or []
        )
        self._ideas.append(idea)
        self._save_data()
        return idea

    def validate_idea(self, idea_id: str):
        """
        Marker at behovet for en idé har dukket opp igjen.
        Øker validation_count og oppdaterer last_validated.
        """
        for idea in self._ideas:
            if idea.id == idea_id:
                idea.validation_count += 1
                idea.last_validated = datetime.now().isoformat()
                self._save_data()

                # Hvis validert mange ganger, kan den være klar
                if idea.validation_count >= 5 and idea.status == "incubating":
                    logger.info(f"Genesis: Idé '{idea.title}' kan være klar for bygging!")

                return idea
        return None

    def get_mature_ideas(self, min_validations: int = 3) -> List[IncubatingIdea]:
        """Hent ideer som har modnet nok"""
        return [i for i in self._ideas
                if i.validation_count >= min_validations
                and i.status == "incubating"]

    # =========================================================================
    # FASE 4: HIERARKISK EVALUERING - Automatisk oppgradering
    # =========================================================================

    def get_current_evaluation_level(self) -> EvaluationLevel:
        """
        Bestem automatisk hvilket evalueringsnivå Genesis skal bruke.
        Oppgraderes basert på mengden data samlet.
        """
        insight_count = len(self._insights)
        pattern_count = len(self.get_recurring_patterns())
        mature_ideas = len(self.get_mature_ideas())

        # Level 4: Har modne ideer som trenger Prime-beslutning
        if mature_ideas >= 1:
            return EvaluationLevel.LEVEL_4_PRIME

        # Level 3: Nok data for konsensus-analyse
        if insight_count >= 100 and pattern_count >= 10:
            return EvaluationLevel.LEVEL_3_CONSENSUS

        # Level 2: Nok data for enkel LLM-analyse
        if insight_count >= 50:
            return EvaluationLevel.LEVEL_2_MINI_LLM

        # Level 1: Bare regex (default, gratis)
        return EvaluationLevel.LEVEL_1_REGEX

    def _get_llm_client(self):
        """Hent LLM client for høyere evalueringsnivåer"""
        try:
            from openai import OpenAI
            os.environ.setdefault('OPENAI_API_KEY', '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')
            os.environ.setdefault('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
            return OpenAI(
                api_key=os.environ['OPENAI_API_KEY'],
                base_url=os.environ['OPENAI_BASE_URL']
            )
        except ImportError:
            logger.warning("OpenAI ikke installert, faller tilbake til Level 1")
            return None

    def evaluate_insight_level2(self, insight: Insight) -> Dict:
        """
        Level 2: Mini-LLM analyse (~0,01 kr per insight)
        Bruker gpt-4o-mini for rask, billig analyse.
        """
        client = self._get_llm_client()
        if not client:
            return {"level": 1, "result": "LLM ikke tilgjengelig"}

        prompt = f"""Analyser denne innsikten fra et ADHD-vennlig produktivitetsperspektiv:

INNSIKT: {insight.content}
KONTEKST: {insight.context}
TYPE: {insight.type.value}

Vurder:
1. Er dette et reelt problem verdt å løse? (0-10)
2. Finnes det gode eksisterende løsninger? (ja/nei/delvis)
3. Kunne dette bli et produkt/verktøy? (ja/nei/kanskje)

Svar kort og konsist på norsk."""

        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            return {
                "level": 2,
                "analysis": response.choices[0].message.content,
                "cost_estimate": 0.0001  # ~0,01 kr
            }
        except Exception as e:
            logger.error(f"Level 2 evaluering feilet: {e}")
            return {"level": 2, "error": str(e)}

    def evaluate_insight_level3(self, insight: Insight) -> Dict:
        """
        Level 3: Circle consensus (~0,10 kr per insight)
        Flere perspektiver for mer robust vurdering.
        """
        client = self._get_llm_client()
        if not client:
            return {"level": 1, "result": "LLM ikke tilgjengelig"}

        perspectives = [
            ("Teknisk", "Vurder teknisk gjennomførbarhet og kompleksitet"),
            ("Bruker", "Vurder brukerverdi og ADHD-vennlighet"),
            ("Marked", "Vurder markedspotensial og konkurranse")
        ]

        results = []
        for name, instruction in perspectives:
            prompt = f"""{instruction}

INNSIKT: {insight.content}
KONTEKST: {insight.context}

Gi kort vurdering (1-2 setninger) + score 1-10."""

            try:
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.3
                )
                results.append({
                    "perspective": name,
                    "analysis": response.choices[0].message.content
                })
            except Exception as e:
                results.append({"perspective": name, "error": str(e)})

        return {
            "level": 3,
            "consensus": results,
            "cost_estimate": 0.001  # ~0,10 kr
        }

    def evaluate_mature_idea_level4(self, idea: IncubatingIdea) -> Dict:
        """
        Level 4: Prime decision (~0,50 kr per idé)
        Full analyse for modne ideer som kan være klare til bygging.
        """
        client = self._get_llm_client()
        if not client:
            return {"level": 1, "result": "LLM ikke tilgjengelig"}

        # Hent relaterte innsikter
        related_insights = [
            i for i in self._insights
            if any(tag in i.tags for tag in ['blindgate', 'problemløsning'])
        ][:5]

        insights_text = "\n".join([f"- {i.content}" for i in related_insights])

        prompt = f"""Du er AIKI Genesis - en AI som evaluerer om en idé er moden nok til å bygges.

IDÉ: {idea.title}
BESKRIVELSE: {idea.description}
PROBLEM: {idea.problem_statement}
EKSISTERENDE LØSNINGER: {', '.join(idea.existing_solutions)}
HVORFOR IKKE BRA NOK: {idea.why_not_good_enough}
VALIDERT: {idea.validation_count} ganger
RELATERTE INNSIKTER:
{insights_text}

EVALUER:
1. Er problemet reelt og viktig? (1-10)
2. Er eksisterende løsninger virkelig utilstrekkelige? (1-10)
3. Har vi nok innsikt til å bygge noe bedre? (1-10)
4. Estimert kompleksitet (lav/medium/høy)
5. Anbefaling: BYGG NÅ / VENT MER / DROPP

Gi detaljert vurdering på norsk."""

        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.4
            )
            return {
                "level": 4,
                "prime_decision": response.choices[0].message.content,
                "idea_id": idea.id,
                "cost_estimate": 0.005  # ~0,50 kr
            }
        except Exception as e:
            logger.error(f"Level 4 evaluering feilet: {e}")
            return {"level": 4, "error": str(e)}

    def run_hierarchical_evaluation(self) -> Dict:
        """
        Kjør automatisk hierarkisk evaluering basert på nåværende nivå.
        Returnerer evaluering og eventuell anbefaling.
        """
        current_level = self.get_current_evaluation_level()
        result = {
            "current_level": current_level.name,
            "insight_count": len(self._insights),
            "pattern_count": len(self.get_recurring_patterns()),
            "mature_ideas": len(self.get_mature_ideas()),
            "evaluations": []
        }

        # Level 1 kjører alltid (ingen kostnad)
        result["level_1_active"] = True

        # Level 2+: Evaluer nyeste innsikter som ikke er analysert
        if current_level.value >= EvaluationLevel.LEVEL_2_MINI_LLM.value:
            # Finn innsikter med lav maturity_score (ikke analysert)
            unanalyzed = [i for i in self._insights if i.maturity_score < 0.3][-5:]
            for insight in unanalyzed:
                eval_result = self.evaluate_insight_level2(insight)
                result["evaluations"].append(eval_result)
                insight.maturity_score = 0.5  # Marker som analysert
            self._save_data()

        # Level 3: Konsensus på høyt scorende innsikter
        if current_level.value >= EvaluationLevel.LEVEL_3_CONSENSUS.value:
            high_value = [i for i in self._insights if 0.4 < i.maturity_score < 0.7][-3:]
            for insight in high_value:
                eval_result = self.evaluate_insight_level3(insight)
                result["evaluations"].append(eval_result)
                insight.maturity_score = 0.8
            self._save_data()

        # Level 4: Evaluer modne ideer
        if current_level.value >= EvaluationLevel.LEVEL_4_PRIME.value:
            mature = self.get_mature_ideas()
            for idea in mature[:2]:  # Maks 2 ideer per kjøring
                eval_result = self.evaluate_mature_idea_level4(idea)
                result["evaluations"].append(eval_result)

                # Hvis anbefaling er BYGG NÅ, oppdater status
                if "BYGG NÅ" in eval_result.get("prime_decision", ""):
                    idea.status = "ready"
                    logger.info(f"🎉 Genesis: Idé '{idea.title}' er KLAR TIL BYGGING!")
            self._save_data()

        return result

    # =========================================================================
    # FASE 5: GENESIS - Statistikk og status
    # =========================================================================

    def get_status(self) -> Dict:
        """Hent status for Genesis Circle"""
        current_level = self.get_current_evaluation_level()

        # Beregn oppgraderingsterskel
        insight_count = len(self._insights)
        next_level_threshold = None
        if current_level == EvaluationLevel.LEVEL_1_REGEX:
            next_level_threshold = f"{50 - insight_count} insights til Level 2"
        elif current_level == EvaluationLevel.LEVEL_2_MINI_LLM:
            patterns_needed = max(0, 10 - len(self.get_recurring_patterns()))
            insights_needed = max(0, 100 - insight_count)
            next_level_threshold = f"{insights_needed} insights + {patterns_needed} mønstre til Level 3"
        elif current_level == EvaluationLevel.LEVEL_3_CONSENSUS:
            next_level_threshold = "Venter på modne ideer for Level 4"

        return {
            'total_insights': insight_count,
            'insights_by_type': {
                t.value: len([i for i in self._insights if i.type == t])
                for t in InsightType
            },
            'total_patterns': len(self._patterns),
            'recurring_patterns': len(self.get_recurring_patterns()),
            'incubating_ideas': len([i for i in self._ideas if i.status == "incubating"]),
            'mature_ideas': len(self.get_mature_ideas()),
            'ready_to_build': len([i for i in self._ideas if i.status == "ready"]),
            'planted': '2025-11-23',
            'phase': self._determine_phase(),
            'evaluation_level': current_level.name,
            'evaluation_level_value': current_level.value,
            'next_level_threshold': next_level_threshold
        }

    def _determine_phase(self) -> str:
        """Bestem hvilken fase Genesis er i"""
        if len(self._insights) < 50:
            return "OBSERVASJON - Samler innsikt"
        elif len(self.get_recurring_patterns()) < 5:
            return "OBSERVASJON - Ser etter mønstre"
        elif len(self.get_mature_ideas()) == 0:
            return "MODNING - Venter på validering"
        else:
            return "GENESIS - Klar til å bygge"


# Singleton
_genesis: Optional[GenesisCircle] = None

def get_genesis_circle() -> GenesisCircle:
    """Hent singleton GenesisCircle"""
    global _genesis
    if _genesis is None:
        _genesis = GenesisCircle()
    return _genesis


# ============================================================================
# Eksempel: Seeding med Claude Code 3-veis chat problemet
# ============================================================================

def seed_initial_insights():
    """
    Seed Genesis med kjente problemer fra fortiden.
    Dette er Jovnnas første frø.
    """
    genesis = get_genesis_circle()

    # Claude Code 3-veis chat problemet
    genesis._insights.append(Insight(
        type=InsightType.MULTI_ANGLE_ATTACK,
        content="Forsøkte å få Claude Code til 3-veis chat med Open Interpreter",
        context="""
        Prøvde mange vinkler:
        1. MCP server for kommunikasjon
        2. Delt minne via Qdrant
        3. File-basert message passing
        4. Subprocess spawning
        Ingen ga god nok løsning - Claude Code har begrensninger på real-time kommunikasjon.
        """,
        tags=['claude-code', 'multi-agent', 'kommunikasjon', 'blindgate'],
        maturity_score=0.3
    ))

    # Lag inkuberende idé basert på dette
    genesis.create_incubating_idea(
        title="Multi-Agent Communication Layer",
        description="Et lag for real-time kommunikasjon mellom AI-agenter",
        problem_statement="Claude Code og andre AI-verktøy kan ikke snakke direkte med hverandre i sanntid",
        existing_solutions=["MCP", "File-based messaging", "Shared databases"],
        why_not_good_enough="MCP er unidirectional, file-based er tregt, databases mangler push-notifikasjoner",
        supporting_insight_ids=[]
    )

    genesis._save_data()
    print("Genesis Circle seeded med initielle innsikter")


if __name__ == "__main__":
    # Seed hvis kjørt direkte
    seed_initial_insights()

    genesis = get_genesis_circle()
    status = genesis.get_status()

    print("\n=== GENESIS CIRCLE STATUS ===")
    print(f"Fase: {status['phase']}")
    print(f"Totalt innsikter: {status['total_insights']}")
    print(f"Inkuberende ideer: {status['incubating_ideas']}")
    print(f"Modne ideer: {status['mature_ideas']}")
