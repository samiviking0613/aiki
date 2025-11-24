#!/usr/bin/env mojo
"""
🔥 MOJO TASK CLASSIFIER - Phase 2
Fast pattern matching and task classification for AIKI
"""

from algorithm import vectorize, parallelize
from memory import UnsafePointer, alloc
from python import Python


# =============================================================================
# CONSTANTS - Task Patterns
# =============================================================================

alias MAX_PATTERNS = 14
alias MAX_TASKS = 12
alias MAX_TEXT_LEN = 10000


# Task types (matching Python version)
# Note: Simplified without patterns pointer for now
struct TaskType:
    var name: String
    var weight: Int
    var num_patterns: Int

    fn __init__(out self, name: String, weight: Int):
        self.name = name
        self.weight = weight
        self.num_patterns = 0


# =============================================================================
# STRING UTILITIES - SIMD Optimized
# =============================================================================

fn vectorized_lowercase(text: String) raises -> String:
    """Convert string to lowercase using SIMD operations."""

    var py = Python.import_module("builtins")
    return String(py.str(text).lower())


fn substring_search_simple(haystack: String, needle: String) raises -> Bool:
    """Simple substring search - Python interop for now."""

    # For Phase 2A, using Python's 'in' operator
    # Phase 2B will implement native Mojo SIMD version
    var py_str = Python.import_module("builtins").str
    var hay = py_str(haystack)
    var need = py_str(needle)

    return Bool(need in hay)


fn count_pattern_matches(text: String, patterns: List[String]) raises -> Int:
    """Count how many patterns match in text."""

    var count = 0

    for i in range(len(patterns)):
        if substring_search_simple(text, patterns[i]):
            count += 1

    return count


# =============================================================================
# TASK CLASSIFICATION - Core Functions
# =============================================================================

struct TaskScore:
    var task_name: String
    var score: Float32
    var matches: Int

    fn __init__(out self, name: String, score: Float32, matches: Int):
        self.task_name = name
        self.score = score
        self.matches = matches


struct TaskPatterns:
    """All task patterns - mirrors Python TaskClassifier.TASK_PATTERNS."""

    var search_patterns: List[String]
    var code_patterns: List[String]
    var analysis_patterns: List[String]
    var creative_patterns: List[String]
    var math_patterns: List[String]
    var reasoning_patterns: List[String]
    var conversation_patterns: List[String]
    var translation_patterns: List[String]
    var summary_patterns: List[String]
    var complex_patterns: List[String]
    var planning_patterns: List[String]
    var optimization_patterns: List[String]

    fn __init__(out self):
        # Search patterns
        self.search_patterns = List[String]()
        self.search_patterns.append("search")
        self.search_patterns.append("find")
        self.search_patterns.append("lookup")
        self.search_patterns.append("what is")
        self.search_patterns.append("hva er")
        self.search_patterns.append("who is")
        self.search_patterns.append("current")
        self.search_patterns.append("latest")
        self.search_patterns.append("recent")
        self.search_patterns.append("news")
        self.search_patterns.append("google")
        self.search_patterns.append("wikipedia")

        # Code patterns
        self.code_patterns = List[String]()
        self.code_patterns.append("code")
        self.code_patterns.append("program")
        self.code_patterns.append("function")
        self.code_patterns.append("debug")
        self.code_patterns.append("fix")
        self.code_patterns.append("implement")
        self.code_patterns.append("algorithm")
        self.code_patterns.append("python")
        self.code_patterns.append("javascript")
        self.code_patterns.append("html")
        self.code_patterns.append("css")
        self.code_patterns.append("sql")
        self.code_patterns.append("git")

        # Analysis patterns
        self.analysis_patterns = List[String]()
        self.analysis_patterns.append("analyze")
        self.analysis_patterns.append("analyser")
        self.analysis_patterns.append("examine")
        self.analysis_patterns.append("evaluate")
        self.analysis_patterns.append("assess")
        self.analysis_patterns.append("review")
        self.analysis_patterns.append("compare")
        self.analysis_patterns.append("study")
        self.analysis_patterns.append("research")
        self.analysis_patterns.append("investigate")

        # Creative patterns
        self.creative_patterns = List[String]()
        self.creative_patterns.append("write")
        self.creative_patterns.append("create")
        self.creative_patterns.append("story")
        self.creative_patterns.append("poem")
        self.creative_patterns.append("essay")
        self.creative_patterns.append("creative")
        self.creative_patterns.append("generate")
        self.creative_patterns.append("compose")
        self.creative_patterns.append("brainstorm")
        self.creative_patterns.append("imagine")

        # Math patterns
        self.math_patterns = List[String]()
        self.math_patterns.append("calculate")
        self.math_patterns.append("solve")
        self.math_patterns.append("equation")
        self.math_patterns.append("formula")
        self.math_patterns.append("math")
        self.math_patterns.append("arithmetic")
        self.math_patterns.append("algebra")
        self.math_patterns.append("geometry")
        self.math_patterns.append("statistics")
        self.math_patterns.append("probability")

        # Reasoning patterns
        self.reasoning_patterns = List[String]()
        self.reasoning_patterns.append("explain")
        self.reasoning_patterns.append("why")
        self.reasoning_patterns.append("how")
        self.reasoning_patterns.append("because")
        self.reasoning_patterns.append("reason")
        self.reasoning_patterns.append("logic")
        self.reasoning_patterns.append("think")
        self.reasoning_patterns.append("conclude")
        self.reasoning_patterns.append("understand")
        self.reasoning_patterns.append("clarify")

        # Conversation patterns
        self.conversation_patterns = List[String]()
        self.conversation_patterns.append("hello")
        self.conversation_patterns.append("hi")
        self.conversation_patterns.append("chat")
        self.conversation_patterns.append("talk")
        self.conversation_patterns.append("discuss")
        self.conversation_patterns.append("opinion")
        self.conversation_patterns.append("what do you think")
        self.conversation_patterns.append("hei")
        self.conversation_patterns.append("snakke")

        # Translation patterns
        self.translation_patterns = List[String]()
        self.translation_patterns.append("translate")
        self.translation_patterns.append("oversett")
        self.translation_patterns.append("convert")
        self.translation_patterns.append("language")
        self.translation_patterns.append("språk")
        self.translation_patterns.append("from english")
        self.translation_patterns.append("to norwegian")
        self.translation_patterns.append("til norsk")

        # Summary patterns
        self.summary_patterns = List[String]()
        self.summary_patterns.append("summarize")
        self.summary_patterns.append("summary")
        self.summary_patterns.append("brief")
        self.summary_patterns.append("overview")
        self.summary_patterns.append("outline")
        self.summary_patterns.append("key points")
        self.summary_patterns.append("sammendrag")
        self.summary_patterns.append("oppsummer")

        # Complex patterns
        self.complex_patterns = List[String]()
        self.complex_patterns.append("complex")
        self.complex_patterns.append("detailed")
        self.complex_patterns.append("comprehensive")
        self.complex_patterns.append("thorough")
        self.complex_patterns.append("deep")
        self.complex_patterns.append("advanced")
        self.complex_patterns.append("sophisticated")
        self.complex_patterns.append("intricate")

        # Planning patterns
        self.planning_patterns = List[String]()
        self.planning_patterns.append("plan")
        self.planning_patterns.append("strategy")
        self.planning_patterns.append("roadmap")
        self.planning_patterns.append("schedule")
        self.planning_patterns.append("organize")
        self.planning_patterns.append("structure")
        self.planning_patterns.append("framework")
        self.planning_patterns.append("approach")

        # Optimization patterns
        self.optimization_patterns = List[String]()
        self.optimization_patterns.append("optimize")
        self.optimization_patterns.append("improve")
        self.optimization_patterns.append("enhance")
        self.optimization_patterns.append("better")
        self.optimization_patterns.append("efficient")
        self.optimization_patterns.append("performance")
        self.optimization_patterns.append("speed")
        self.optimization_patterns.append("cost")


struct TaskWeights:
    """Task priority weights - mirrors Python TaskClassifier.TASK_WEIGHTS."""

    var search: Int
    var code: Int
    var math: Int
    var translation: Int
    var analysis: Int
    var creative: Int
    var planning: Int
    var optimization: Int
    var reasoning: Int
    var summary: Int
    var complex: Int
    var conversation: Int

    fn __init__(out self):
        self.search = 10
        self.code = 9
        self.math = 9
        self.translation = 8
        self.analysis = 7
        self.creative = 6
        self.planning = 6
        self.optimization = 6
        self.reasoning = 5
        self.summary = 5
        self.complex = 3
        self.conversation = 2


fn classify_task_mojo(text: String) raises -> String:
    """
    Classify task based on text content.

    Returns primary task type (highest scoring).
    """

    # Lowercase text
    var lower_text = vectorized_lowercase(text)

    # Initialize patterns and weights
    var patterns = TaskPatterns()
    var weights = TaskWeights()

    # Count matches for each task type
    var search_matches = count_pattern_matches(lower_text, patterns.search_patterns)
    var code_matches = count_pattern_matches(lower_text, patterns.code_patterns)
    var analysis_matches = count_pattern_matches(lower_text, patterns.analysis_patterns)
    var creative_matches = count_pattern_matches(lower_text, patterns.creative_patterns)
    var math_matches = count_pattern_matches(lower_text, patterns.math_patterns)
    var reasoning_matches = count_pattern_matches(lower_text, patterns.reasoning_patterns)
    var conversation_matches = count_pattern_matches(lower_text, patterns.conversation_patterns)
    var translation_matches = count_pattern_matches(lower_text, patterns.translation_patterns)
    var summary_matches = count_pattern_matches(lower_text, patterns.summary_patterns)
    var complex_matches = count_pattern_matches(lower_text, patterns.complex_patterns)
    var planning_matches = count_pattern_matches(lower_text, patterns.planning_patterns)
    var optimization_matches = count_pattern_matches(lower_text, patterns.optimization_patterns)

    # Calculate scores
    var search_score = search_matches * weights.search
    var code_score = code_matches * weights.code
    var analysis_score = analysis_matches * weights.analysis
    var creative_score = creative_matches * weights.creative
    var math_score = math_matches * weights.math
    var reasoning_score = reasoning_matches * weights.reasoning
    var conversation_score = conversation_matches * weights.conversation
    var translation_score = translation_matches * weights.translation
    var summary_score = summary_matches * weights.summary
    var complex_score = complex_matches * weights.complex
    var planning_score = planning_matches * weights.planning
    var optimization_score = optimization_matches * weights.optimization

    # Find max score
    var max_score = search_score
    var primary_task = "search"

    if code_score > max_score:
        max_score = code_score
        primary_task = "code"

    if math_score > max_score:
        max_score = math_score
        primary_task = "math"

    if translation_score > max_score:
        max_score = translation_score
        primary_task = "translation"

    if analysis_score > max_score:
        max_score = analysis_score
        primary_task = "analysis"

    if creative_score > max_score:
        max_score = creative_score
        primary_task = "creative"

    if planning_score > max_score:
        max_score = planning_score
        primary_task = "planning"

    if optimization_score > max_score:
        max_score = optimization_score
        primary_task = "optimization"

    if reasoning_score > max_score:
        max_score = reasoning_score
        primary_task = "reasoning"

    if summary_score > max_score:
        max_score = summary_score
        primary_task = "summary"

    if complex_score > max_score:
        max_score = complex_score
        primary_task = "complex"

    if conversation_score > max_score:
        max_score = conversation_score
        primary_task = "conversation"

    # Return "general" if no matches
    if max_score == 0:
        return "general"

    return primary_task


# =============================================================================
# MAIN - Testing & Benchmarking
# =============================================================================

fn main() raises:
    print("🔥 MOJO TASK CLASSIFIER - Phase 2")
    print("=" * 70)
    print()

    # Test cases (same as Python version)
    var test_cases = List[String]()
    test_cases.append("Can you help me debug this Python code?")
    test_cases.append("What is the latest news about AI?")
    test_cases.append("Write a creative story about a dragon")
    test_cases.append("Calculate the area of a circle with radius 5")
    test_cases.append("Translate this to Norwegian")
    test_cases.append("Summarize this article for me")

    print("📋 Test Cases:")
    print()

    for i in range(len(test_cases)):
        var text = test_cases[i]
        var task = classify_task_mojo(text)
        print(i+1, ".", text)
        print("   → Task:", task)
        print()

    print("=" * 70)
    print("✅ MOJO Task Classifier Phase 2A Complete!")
    print()
    print("Phase 2B Next:")
    print("  - Native SIMD string matching")
    print("  - Parallelized pattern matching")
    print("  - Batch classification")
    print("  - Benchmark vs Python")
