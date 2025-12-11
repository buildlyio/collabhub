# Developer Level Assessment System

## Overview

This system provides a comprehensive assessment for evaluating software developers' skill levels through:
- **15 Multiple Choice Questions** (Technical competency assessment)
- **3 Essay Questions** (Technical depth and problem-solving assessment)
- **AI Detection** (Identify potential AI-assisted answers)
- **Automated Scoring** (Rubric-based evaluation)
- **Human Review** (Final evaluation and interview scheduling)

## Scoring Rubric

### Multiple Choice Questions (Q1-Q15)

Each question is scored as follows:
- **A = 1 point** (Beginner/Basic understanding)
- **B = 2 points** (Developing/Some experience)
- **C = 3 points** (Proficient/Solid experience)
- **D = 4 points** (Expert/Advanced experience)

**Total Score Range:** 15-60 points

### Level Thresholds

| Score Range | Level | Description |
|-------------|-------|-------------|
| 15-24 | **Junior** | Entry-level developer, requires mentorship |
| 25-36 | **Mid-Level** | Solid technical foundation, can work independently |
| 37-48 | **Senior** | Strong technical depth, can lead features |
| 49-60 | **Lead/Architect** | Advanced expertise, can design systems |

### Essay Questions (Q16-Q18)

Essays are evaluated for:
1. **AI Detection Score** (0-100): Likelihood the answer was AI-generated
   - 0-30: Low AI likelihood (appears human)
   - 31-49: Uncertain
   - 50-69: Moderate AI likelihood
   - 70-100: High AI likelihood

2. **Skill Level Assessment**: Technical depth demonstrated in answer
   - Junior: Basic understanding
   - Mid-Level: Solid competency
   - Senior: Strong technical depth
   - Lead: Advanced expertise

3. **Human Evaluation**: Final review by interviewer with notes

## Setup Instructions

### 1. Run Migration

```bash
cd /Users/greglind/Projects/buildly/collabhub
source venv/bin/activate
DJANGO_SETTINGS_MODULE=mysite.settings.dev python manage.py migrate onboarding
```

### 2. Create the Quiz

```bash
# Create quiz with default admin owner
python manage.py create_developer_level_quiz

# Or specify a different owner
python manage.py create_developer_level_quiz --owner-username=yourusername

# Customize the quiz URL
python manage.py create_developer_level_quiz --quiz-url=https://collab.buildly.io/assessment/dev
```

This creates:
- 1 Quiz: "Developer Level Assessment"
- 15 Multiple choice questions
- 3 Essay questions
- All questions assigned to team_member_type='all'

## Usage Workflow

### For Candidates

1. **Take the Assessment** (Honor System)
   - Answer all 15 multiple choice questions honestly
   - Write detailed essay answers to 3 questions
   - Submit responses through the system

2. **Follow-up Interview**
   - Scheduled based on assessment results
   - Technical verification questions
   - Discussion of essay answers

### For Evaluators

#### Step 1: Generate Assessment Report

```bash
python manage.py assess_developer_quiz <team_member_id>
```

This displays:
- Multiple choice score and level
- Essay answer previews
- Overall assessment

#### Step 2: Run AI Detection (Optional)

```bash
python manage.py assess_developer_quiz <team_member_id> --run-ai-detection
```

Adds to report:
- AI detection score for each essay
- Analysis of AI usage indicators
- Recommendations for follow-up

#### Step 3: Assess Essay Skills (Optional)

```bash
python manage.py assess_developer_quiz <team_member_id> --assess-essays
```

Adds to report:
- Skill level assessment for each essay
- Technical depth analysis
- Quality indicators

#### Step 4: Run Complete Assessment

```bash
python manage.py assess_developer_quiz <team_member_id> --run-ai-detection --assess-essays
```

Generates complete report with all analyses.

## Admin Interface

### Viewing Answers

1. Navigate to **Django Admin** → **Onboarding** → **Quiz Answers**
2. Filter by:
   - Quiz name
   - Submission date
   - Evaluation status

### Running AI Detection

1. Select essay answers in admin
2. Choose action: **"Run AI detection on essay answers"**
3. Review AI detection scores and analysis

### Manual Evaluation

For each answer, you can add:
- **Evaluator Score** (1-4 for multiple choice scale)
- **Evaluator Notes** (Comments and observations)
- **Evaluated By** (Automatically set to current user)
- **Evaluated At** (Timestamp of evaluation)

## AI Detection Explained

### How It Works

The AI detection system analyzes essay text for patterns common in AI-generated content:

1. **Formal Language** - AI tends to use formal transitions ("Furthermore", "Moreover")
2. **Sentence Structure** - AI writes longer, more complex sentences
3. **Personal Pronouns** - Humans use "I", "we", "my" more frequently
4. **Perfect Grammar** - AI avoids contractions and informal language
5. **Generic Phrases** - AI uses templated responses
6. **Specific Details** - Humans include dates, versions, names
7. **Structure** - AI over-uses bullet points and numbered lists

### Interpreting Scores

- **70-100**: High likelihood - Schedule deeper technical interview
- **50-69**: Moderate likelihood - Standard technical interview
- **30-49**: Uncertain - Review content manually
- **0-29**: Low likelihood - Appears authentic

**Important**: AI detection is a tool, not a definitive answer. Always:
- Review the content yourself
- Ask follow-up questions in interview
- Use it to guide discussion, not disqualify candidates

## Skill Level Assessment

Essay answers are also assessed for technical skill demonstrated:

### Indicators

- **Technical Vocabulary**: Use of appropriate technical terms
- **Problem-Solving Depth**: Structured approach to problems
- **Leadership/Collaboration**: Mentions of teamwork, mentoring
- **Specific Examples**: Concrete details vs vague statements
- **Response Quality**: Length and comprehensiveness

### Output

Each essay receives:
- Skill level: Junior, Mid-Level, Senior, or Lead
- Analysis of detected indicators
- Detailed breakdown of assessment

## Example Workflow

### Scenario: Evaluating John Doe (Team Member ID: 42)

```bash
# Step 1: Generate basic report
python manage.py assess_developer_quiz 42

# Output shows:
# - Multiple Choice: 38/60 (Senior level)
# - 3 essay answers submitted

# Step 2: Run full analysis
python manage.py assess_developer_quiz 42 --run-ai-detection --assess-essays

# Output shows:
# - MC Score: 38/60 (Senior)
# - Essay 1: AI Score 25/100 (Low), Skill: Senior
# - Essay 2: AI Score 68/100 (Moderate), Skill: Mid-Level
# - Essay 3: AI Score 42/100 (Uncertain), Skill: Senior
# - Average AI: 45/100 (Moderate)
# - Recommendation: Conduct standard technical interview
```

### Step 3: Review in Admin

1. Go to Admin → Quiz Answers
2. Filter by John Doe
3. Review essay #2 (moderate AI score)
4. Add evaluator notes
5. Schedule interview with focus on that topic

### Step 4: Interview

Ask John to:
- Explain essay #2 answer in more detail
- Write code live that demonstrates the concept
- Discuss trade-offs they mentioned

## Best Practices

### For Creating Fair Assessments

1. **Honor System First** - Trust candidates, verify in interview
2. **Use AI Detection as Guide** - Not as disqualification
3. **Focus on Technical Depth** - Ask follow-up questions
4. **Consider Context** - ESL speakers may have different patterns
5. **Combine Methods** - Use MC scores + essays + interview

### For Conducting Interviews

1. **Reference Specific Answers** - "You mentioned X in your essay..."
2. **Ask for Elaboration** - "Can you explain that approach in more detail?"
3. **Live Coding** - Verify practical skills
4. **Discussion** - Gauge communication and collaboration
5. **Growth Mindset** - Assess learning ability

### Red Flags

- **High AI + Low MC Score** - Possible AI overuse
- **Generic Essays** - Lack of specific examples
- **Perfect Grammar + No Detail** - Possible AI templates
- **Contradictory Levels** - MC says Junior but essays say Senior

## Files Created

```
onboarding/
├── management/
│   └── commands/
│       ├── create_developer_level_quiz.py  # Quiz creation
│       └── assess_developer_quiz.py        # Assessment reports
├── ai_detection.py                         # AI detection & scoring
└── models.py                               # Updated with evaluation fields
```

## Database Schema

### QuizAnswer Model (Enhanced)

```python
class QuizAnswer:
    question: ForeignKey
    team_member: ForeignKey
    answer: TextField
    submitted_at: DateTimeField
    
    # AI Detection
    ai_detection_score: Float (0-100)
    ai_detection_analysis: Text
    
    # Human Evaluation
    evaluator_score: Integer (1-4)
    evaluator_notes: Text
    evaluated_by: ForeignKey(User)
    evaluated_at: DateTimeField
```

## Support & Questions

For issues or questions:
1. Check this README
2. Review the AI detection analysis output
3. Contact development team
4. Review candidate in follow-up interview

## Future Enhancements

Potential additions:
- [ ] Automated interview scheduling
- [ ] Integration with external AI detection APIs
- [ ] Candidate dashboard for viewing results
- [ ] Comparative analytics across candidates
- [ ] Custom rubrics per role type
- [ ] Video interview integration
- [ ] Code challenge integration
