"""
AI Detection System for Essay Answers

This module provides functionality to detect if an essay answer was likely 
written with AI assistance. It uses multiple heuristics and can optionally 
integrate with external AI detection services.
"""

import re
from typing import Tuple


def detect_ai_usage(text: str) -> Tuple[float, str]:
    """
    Detect likelihood of AI usage in text.
    
    Returns:
        Tuple of (score, analysis) where:
        - score: 0-100 indicating likelihood of AI usage (higher = more likely AI)
        - analysis: Detailed explanation of the detection
    """
    if not text or len(text.strip()) < 50:
        return 0.0, "Text too short for meaningful analysis"
    
    analysis_parts = []
    indicators = []
    
    # 1. Check for overly formal language patterns common in AI
    formal_phrases = [
        r'\bIt is important to note that\b',
        r'\bIn conclusion\b',
        r'\bFurthermore\b',
        r'\bMoreover\b',
        r'\bIn summary\b',
        r'\bIt should be noted\b',
        r'\bIt is worth mentioning\b',
    ]
    
    formal_count = sum(1 for phrase in formal_phrases if re.search(phrase, text, re.IGNORECASE))
    if formal_count >= 3:
        indicators.append(('High formal language density', 20))
        analysis_parts.append(f"Contains {formal_count} formal transition phrases (AI models tend to overuse these)")
    
    # 2. Check for AI-typical sentence structures
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) > 0:
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_length > 25:
            indicators.append(('Long average sentence length', 15))
            analysis_parts.append(f"Average sentence length: {avg_sentence_length:.1f} words (AI tends to write longer sentences)")
    
    # 3. Check for lack of personal pronouns (AI often avoids "I", "my", "we")
    personal_pronouns = len(re.findall(r'\b(I|my|we|our|me)\b', text, re.IGNORECASE))
    word_count = len(text.split())
    personal_pronoun_ratio = personal_pronouns / word_count if word_count > 0 else 0
    
    if personal_pronoun_ratio < 0.01:
        indicators.append(('Very low personal pronoun usage', 25))
        analysis_parts.append(f"Personal pronouns only {personal_pronoun_ratio*100:.1f}% of text (human answers typically use more)")
    elif personal_pronoun_ratio > 0.05:
        # High personal pronoun usage is typically human
        indicators.append(('High personal pronoun usage (likely human)', -20))
        analysis_parts.append(f"Good personal pronoun usage {personal_pronoun_ratio*100:.1f}% (typical of human writing)")
    
    # 4. Check for overly perfect grammar (no typos, perfect punctuation)
    # Simple heuristic: check for common human errors that AI avoids
    has_contractions = bool(re.search(r"\b(don't|can't|won't|I'm|I've|wasn't|weren't|didn't)\b", text, re.IGNORECASE))
    has_informal_words = bool(re.search(r"\b(yeah|yep|nope|gonna|wanna|kinda|sorta|gotta)\b", text, re.IGNORECASE))
    
    if not has_contractions and not has_informal_words and word_count > 100:
        indicators.append(('Overly formal/perfect grammar', 20))
        analysis_parts.append("No contractions or informal language (AI tends to be overly formal)")
    elif has_contractions or has_informal_words:
        indicators.append(('Natural informal language (likely human)', -15))
        analysis_parts.append("Uses contractions/informal language (typical human trait)")
    
    # 5. Check for generic/templated responses
    generic_phrases = [
        r'\bFor example\b',
        r'\bFor instance\b',
        r'\bSuch as\b',
        r'\bIncluding but not limited to\b',
        r'\bAmong other things\b',
    ]
    
    generic_count = sum(1 for phrase in generic_phrases if re.search(phrase, text, re.IGNORECASE))
    if generic_count >= 2:
        indicators.append(('Generic phrase patterns', 15))
        analysis_parts.append(f"Contains {generic_count} generic transition phrases")
    
    # 6. Check for specific technical details vs. vague statements
    # Humans typically include specific names, versions, dates
    specific_details = len(re.findall(r'\b(version|v\d|20\d{2}|January|February|March|April|May|June|July|August|September|October|November|December)\b', text, re.IGNORECASE))
    
    if specific_details >= 2:
        indicators.append(('Contains specific details (likely human)', -20))
        analysis_parts.append("Includes specific dates/versions/details (human trait)")
    
    # 7. Check for structured bullet points or numbered lists (AI loves structure)
    has_structure = bool(re.search(r'^\s*[\d\-\*•]', text, re.MULTILINE))
    structure_count = len(re.findall(r'^\s*[\d\-\*•]', text, re.MULTILINE))
    
    if structure_count >= 5:
        indicators.append(('Highly structured format', 15))
        analysis_parts.append(f"Contains {structure_count} structured list items (AI tends to over-structure)")
    
    # Calculate final score
    base_score = 30  # Baseline uncertainty
    adjustment = sum(score for _, score in indicators)
    final_score = max(0, min(100, base_score + adjustment))
    
    # Build analysis report
    analysis = "=== AI Detection Analysis ===\n\n"
    
    if final_score >= 70:
        analysis += "⚠️ HIGH LIKELIHOOD of AI assistance\n\n"
    elif final_score >= 50:
        analysis += "⚡ MODERATE LIKELIHOOD of AI assistance\n\n"
    elif final_score >= 30:
        analysis += "❓ UNCERTAIN - Could be human or AI\n\n"
    else:
        analysis += "✓ LOW LIKELIHOOD of AI assistance (appears human-written)\n\n"
    
    analysis += "Detected Indicators:\n"
    for indicator, score in indicators:
        sign = "+" if score > 0 else ""
        analysis += f"  • {indicator}: {sign}{score} points\n"
    
    analysis += "\nDetailed Analysis:\n"
    for part in analysis_parts:
        analysis += f"  • {part}\n"
    
    analysis += f"\n📊 Word count: {word_count}\n"
    analysis += f"📊 Sentence count: {len(sentences)}\n"
    analysis += f"📊 Final AI likelihood score: {final_score:.1f}/100\n"
    
    analysis += "\n⚠️ Note: This is a heuristic analysis. Always review the content manually."
    
    return final_score, analysis


def calculate_rubric_score(answers_dict: dict) -> dict:
    """
    Calculate rubric score based on multiple choice answers.
    
    Scoring for 15 multiple-choice questions:
    - A = 1 point, B = 2 points, C = 3 points, D = 4 points
    - Score range: 15-60
    - Thresholds:
      * 15-24: Junior
      * 25-36: Mid-Level
      * 37-48: Senior
      * 49-60: Lead/Architect/CTO Track
    
    Args:
        answers_dict: Dictionary mapping question_id to answer (A/B/C/D)
    
    Returns:
        Dictionary with scoring breakdown and recommended level
    """
    # Scoring rubric: A=1, B=2, C=3, D=4
    score_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
    
    scores = []
    for answer in answers_dict.values():
        # Extract the letter from answer (could be "A", "A.", "A. text", etc.)
        match = re.match(r'^([A-D])', answer.strip().upper())
        if match:
            letter = match.group(1)
            scores.append(score_map.get(letter, 0))
    
    if not scores:
        return {
            'total_score': 0,
            'average_score': 0,
            'max_possible': 0,
            'percentage': 0,
            'level': 'Unknown',
            'recommendation': 'Unable to calculate score',
            'question_count': 0
        }
    
    total = sum(scores)
    average = total / len(scores)
    max_possible = len(scores) * 4
    percentage = (total / max_possible) * 100
    
    # Determine level based on total score (15 questions expected)
    # Thresholds: 15-24 Junior, 25-36 Mid, 37-48 Senior, 49-60 Lead
    if total >= 49:
        level = 'Lead/Architect/CTO Track'
        recommendation = (
            'Exceptional candidate for lead or architect positions. '
            'Strong technical depth and breadth. Schedule leadership interview.'
        )
    elif total >= 37:
        level = 'Senior'
        recommendation = (
            'Strong candidate for senior-level positions. '
            'Demonstrates solid technical expertise. Schedule technical interview.'
        )
    elif total >= 25:
        level = 'Mid-Level'
        recommendation = (
            'Good candidate for mid-level positions. '
            'Shows competency in core areas. Schedule technical interview.'
        )
    elif total >= 15:
        level = 'Junior'
        recommendation = (
            'Suitable for junior positions with mentorship. '
            'Schedule interview to assess growth potential and learning attitude.'
        )
    else:
        level = 'Entry-Level'
        recommendation = (
            'Entry-level candidate. Consider for junior roles with significant support. '
            'May need additional training or guidance.'
        )
    
    return {
        'total_score': total,
        'average_score': round(average, 2),
        'max_possible': max_possible,
        'percentage': round(percentage, 1),
        'level': level,
        'recommendation': recommendation,
        'question_count': len(scores),
        'score_breakdown': f'{total}/60 ({percentage:.1f}%)'
    }


def assess_essay_skill_level(essay_text: str) -> Tuple[str, str]:
    """
    Assess the technical skill level demonstrated in an essay answer.
    
    This provides a complementary assessment to the AI detection,
    focusing on the technical depth and quality of the response.
    
    Returns:
        Tuple of (skill_level, analysis) where:
        - skill_level: Junior, Mid-Level, Senior, or Lead
        - analysis: Detailed explanation of the assessment
    """
    if not essay_text or len(essay_text.strip()) < 50:
        return "Insufficient", "Essay too short to assess skill level"
    
    indicators = []
    analysis_parts = []
    
    word_count = len(essay_text.split())
    
    # 1. Check for specific technical terminology
    technical_patterns = [
        r'\b(API|REST|GraphQL|microservice|Docker|Kubernetes|CI/CD|pipeline)\b',
        r'\b(database|SQL|NoSQL|Redis|PostgreSQL|MySQL|MongoDB)\b',
        r'\b(Git|GitHub|branch|merge|pull request|code review)\b',
        r'\b(testing|unit test|integration test|TDD|debugging)\b',
        r'\b(architecture|design pattern|scalability|performance|optimization)\b',
    ]
    
    technical_count = sum(
        len(re.findall(pattern, essay_text, re.IGNORECASE))
        for pattern in technical_patterns
    )
    
    if technical_count >= 5:
        indicators.append(('Strong technical vocabulary', 3))
        analysis_parts.append(f"Uses {technical_count} technical terms appropriately")
    elif technical_count >= 3:
        indicators.append(('Moderate technical vocabulary', 2))
        analysis_parts.append(f"Uses {technical_count} technical terms")
    elif technical_count >= 1:
        indicators.append(('Basic technical vocabulary', 1))
        analysis_parts.append(f"Uses {technical_count} technical terms")
    
    # 2. Check for problem-solving depth
    problem_solving_phrases = [
        r'\b(investigated|debugged|analyzed|identified root cause|traced|isolated)\b',
        r'\b(solution|approach|strategy|alternative|trade-off|considered)\b',
        r'\b(implemented|refactored|optimized|improved|fixed)\b',
    ]
    
    problem_solving_count = sum(
        len(re.findall(pattern, essay_text, re.IGNORECASE))
        for pattern in problem_solving_phrases
    )
    
    if problem_solving_count >= 4:
        indicators.append(('Strong problem-solving depth', 3))
        analysis_parts.append("Demonstrates structured problem-solving approach")
    elif problem_solving_count >= 2:
        indicators.append(('Moderate problem-solving depth', 2))
        analysis_parts.append("Shows basic problem-solving approach")
    
    # 3. Check for leadership/mentoring indicators
    leadership_phrases = [
        r'\b(team|collaborated|mentored|led|guided|taught|shared knowledge)\b',
        r'\b(code review|pair programming|best practices|standards)\b',
        r'\b(architected|designed system|made decision|evaluated options)\b',
    ]
    
    leadership_count = sum(
        len(re.findall(pattern, essay_text, re.IGNORECASE))
        for pattern in leadership_phrases
    )
    
    if leadership_count >= 3:
        indicators.append(('Leadership/mentoring indicators', 3))
        analysis_parts.append("Shows leadership and collaboration experience")
    elif leadership_count >= 1:
        indicators.append(('Some collaboration mentioned', 1))
        analysis_parts.append("Mentions teamwork or collaboration")
    
    # 4. Check for specific examples vs vague statements
    has_specific_examples = bool(re.search(
        r'\b(for example|specifically|in particular|such as|instance where)\b',
        essay_text,
        re.IGNORECASE
    ))
    
    if has_specific_examples:
        indicators.append(('Provides specific examples', 2))
        analysis_parts.append("Uses concrete examples to illustrate points")
    
    # 5. Check response length appropriateness
    if word_count >= 150:
        indicators.append(('Comprehensive response', 2))
        analysis_parts.append(f"Well-developed response ({word_count} words)")
    elif word_count >= 75:
        indicators.append(('Adequate response length', 1))
        analysis_parts.append(f"Adequate response length ({word_count} words)")
    else:
        indicators.append(('Brief response', 0))
        analysis_parts.append(f"Brief response ({word_count} words)")
    
    # Calculate skill level score
    total_indicators = sum(score for _, score in indicators)
    
    # Determine skill level
    if total_indicators >= 10:
        skill_level = "Lead/Senior"
        assessment = "Demonstrates advanced technical knowledge and leadership capabilities"
    elif total_indicators >= 7:
        skill_level = "Senior"
        assessment = "Shows strong technical depth and problem-solving skills"
    elif total_indicators >= 4:
        skill_level = "Mid-Level"
        assessment = "Demonstrates solid technical competency"
    else:
        skill_level = "Junior"
        assessment = "Shows foundational technical understanding"
    
    # Build analysis report
    analysis = f"=== Essay Skill Assessment ===\n\n"
    analysis += f"📊 Assessed Level: {skill_level}\n"
    analysis += f"📝 {assessment}\n\n"
    
    analysis += "Detected Indicators:\n"
    for indicator, score in indicators:
        analysis += f"  • {indicator} ({score} points)\n"
    
    analysis += "\nDetailed Analysis:\n"
    for part in analysis_parts:
        analysis += f"  • {part}\n"
    
    analysis += f"\n📊 Total indicator score: {total_indicators}\n"
    analysis += f"📊 Word count: {word_count}\n"
    
    return skill_level, analysis
