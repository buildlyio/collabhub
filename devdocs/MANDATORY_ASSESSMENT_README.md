# Mandatory Developer Skill Assessment

## Overview

Every new developer who registers on Buildly CollabHub must complete a mandatory skill assessment. This assessment helps us understand each developer's current skill level so we can provide personalized support, training, mentorship, and appropriate project opportunities.

## Purpose

The assessment is designed to:
- **Identify skill gaps** so we can provide targeted learning resources
- **Match developers** with appropriate projects based on their experience level
- **Create personalized learning paths** tailored to individual needs
- **Connect developers** with mentors who can help them grow
- **Track progress** over time as developers level up their skills

**This is NOT a gatekeeping mechanism.** It's a support tool to help developers succeed.

## User Experience Flow

### 1. Registration
- New users create an account and complete their profile
- After registration, they are automatically redirected to the assessment landing page

### 2. Assessment Landing Page
- Shows clear explanation of:
  - **Honor system rules** (no AI, no help, no research)
  - **Purpose** (helps us provide better support)
  - **What to expect** (18 questions: 15 MC, 3 essay)
  - **What happens next** (review, interview, personalized plan)
- Displays warning banner for returning users showing reminder count

### 3. Taking the Assessment
- Question-by-question interface with progress tracking
- Sticky reminder banner about honor system
- Three action options:
  - **Save & Continue Later** - saves answer and returns to dashboard
  - **Next Question** - saves answer and moves forward
  - **Submit Assessment** - completes the assessment (final question only)
- Unsaved changes warning when navigating away

### 4. Assessment Complete
- Congratulations page explaining next steps
- Timeline for review and follow-up interview
- Full access to CollabHub features granted

### 5. Enforcement & Reminders
- **Middleware** redirects unauthenticated users to assessment landing page
- **Persistent banner** shows at top of every page until assessment completed
- **Reminder count** increments each time user sees landing page
- **Exemptions**: admin users, static/media URLs, auth pages, assessment pages

## Technical Architecture

### Models

#### TeamMember (Assessment Tracking Fields)
```python
has_completed_assessment = BooleanField(default=False)
assessment_completed_at = DateTimeField(null=True, blank=True)
assessment_reminder_count = IntegerField(default=0)
assessment_last_reminded = DateTimeField(null=True, blank=True)
```

#### QuizAnswer (AI Detection Fields)
```python
ai_detection_score = FloatField(null=True, blank=True)
ai_detection_analysis = TextField(blank=True)
evaluator_score = IntegerField(null=True, blank=True, choices=1-4)
evaluator_notes = TextField(blank=True)
evaluated_by = ForeignKey(User, null=True)
evaluated_at = DateTimeField(null=True)
```

### Views

1. **assessment_landing** - Landing page with honor system explanation
2. **take_assessment** - Question-by-question quiz interface
3. **assessment_complete** - Completion congratulations page

### Middleware

**AssessmentRequiredMiddleware** - Enforces assessment completion
- Checks if user is authenticated and has completed assessment
- Redirects to landing page if not completed
- Exempts admin users and specific URL patterns

### Context Processor

**assessment_status** - Makes assessment status globally available
- `needs_assessment` - Boolean for incomplete assessments
- `assessment_reminder_count` - Number of reminders shown

### Templates

1. **assessment_landing.html** - Landing page with honor system rules
2. **take_assessment.html** - Quiz question interface
3. **assessment_complete.html** - Success page
4. **includes/assessment_banner.html** - Persistent notification banner

### URLs

```python
path('assessment/', views.assessment_landing, name='assessment_landing')
path('assessment/quiz/', views.take_assessment, name='take_assessment')
path('assessment/complete/', views.assessment_complete, name='assessment_complete')
```

## Assessment Content

### 15 Multiple Choice Questions (4-point rubric: A=1, B=2, C=3, D=4)

Topics covered:
1. Git/version control experience
2. Code review experience
3. Testing practices
4. Database knowledge
5. API development
6. Frontend frameworks
7. DevOps/deployment
8. Design patterns
9. Problem-solving approach
10. Security awareness
11. Scalability considerations
12. Team collaboration
13. Documentation habits
14. Learning approach
15. Debugging skills

### 3 Essay Questions

1. **Project Challenge** - Describe a complex technical problem you solved
2. **System Design** - Explain how you'd build a scalable web application
3. **Learning & Growth** - What skills are you actively working to improve and why?

### Scoring System

**Multiple Choice Total**: 15-60 points (15 questions × 1-4 points each)

**Skill Levels**:
- **15-24 points** - Junior (Learning fundamentals, needs guidance)
- **25-36 points** - Mid-Level (Can work independently with oversight)
- **37-48 points** - Senior (Strong technical depth, can mentor)
- **49-60 points** - Lead (Expert level, architectural decision maker)

**Essay Questions**: Evaluated by human reviewers with AI detection analysis

## AI Detection System

### Detection Algorithm (Heuristic-Based)

Located in `onboarding/ai_detection.py`:

1. **Overly formal patterns** - Detects academic/formal language
2. **Generic phrasing** - Identifies vague, non-specific responses
3. **Perfect grammar** - Flags suspiciously perfect text
4. **Structure patterns** - Detects AI-style organization
5. **Length and repetition** - Analyzes text characteristics

**Output**: 0-100 score with analysis text

### Human Evaluation

Evaluators can:
- Review AI detection scores in admin interface
- Assign scores 1-4 based on content quality
- Add evaluation notes
- Flag suspicious responses for follow-up interview

## Management Commands

### Create Quiz
```bash
python manage.py create_developer_level_quiz
```
Creates/updates the 18-question developer assessment quiz.

### Assess Developer
```bash
python manage.py assess_developer_quiz <team_member_id> [--run-ai-detection] [--assess-essays]
```
Generate comprehensive assessment report with scores and recommendations.

## Admin Interface

### QuizAnswer Admin

**Bulk Actions**:
- Run AI detection on selected answers
- Mark as manually evaluated

**List Display**:
- Team member, question, answer preview
- AI detection score, evaluator score
- Submission and evaluation dates

**Filters**:
- Question type (MC/essay)
- AI detection score ranges
- Evaluation status
- Team member

**Fieldsets**:
- Basic info, answer text
- AI detection results (collapsed)
- Human evaluation (collapsed)

### TeamMember Admin

**Assessment Status**:
- Shows completion status in list view
- Filter by assessment completion
- Display assessment tracking fields in collapsed fieldset

## Configuration

### Settings (base.py)

```python
MIDDLEWARE = [
    # ... other middleware ...
    'onboarding.middleware.AssessmentRequiredMiddleware',
]

TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            # ... other processors ...
            'onboarding.context_processors.assessment_status',
        ],
    },
}]
```

## Testing Checklist

- [ ] New user registration redirects to assessment landing
- [ ] Landing page shows honor system disclaimer
- [ ] Quiz displays questions in order with progress bar
- [ ] Save & Continue Later saves answer and returns to dashboard
- [ ] Persistent banner shows on all pages until completion
- [ ] Middleware blocks access for incomplete assessments
- [ ] Submit completes assessment and marks user as complete
- [ ] Completion page shows success message
- [ ] Banner disappears after completion
- [ ] Admin users bypass middleware
- [ ] AI detection runs on essay answers
- [ ] Management command generates assessment report

## Honor System Messaging

The assessment emphasizes:

1. **Trust** - We trust developers to answer honestly
2. **Support** - Purpose is to help, not judge
3. **Accuracy** - Honest answers lead to better support
4. **Growth** - Admitting gaps is the first step to improvement

**Key phrase**: "If you artificially inflate your score, we won't be able to provide you with the right training, mentorship, and resources to help you grow."

## Follow-Up Process

1. **Automated review** - AI detection and scoring within 24-48 hours
2. **Human evaluation** - Team reviews essay responses and flags
3. **Follow-up interview** - 15-20 minute conversation scheduled within 3-5 days
4. **Personalized plan** - Learning path created within 1 week
5. **Ongoing support** - Regular check-ins and progress tracking

## Future Enhancements

- [ ] Email notifications for assessment completion
- [ ] Dashboard widget showing assessment status
- [ ] Periodic reassessments (every 6 months)
- [ ] Skill progression tracking over time
- [ ] Automated learning resource recommendations
- [ ] Integration with project assignment system
- [ ] Mentor matching based on skill gaps
- [ ] Certificate generation for completed assessments

## Support

For technical issues or questions:
- Email: support@buildly.io
- Documentation: DEVELOPER_ASSESSMENT_README.md
- Admin contact: Check with team lead

---

**Last Updated**: December 2024
**Version**: 1.0
**Status**: Production Ready
