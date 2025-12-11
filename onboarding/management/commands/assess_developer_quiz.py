# onboarding/management/commands/assess_developer_quiz.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from onboarding.models import Quiz, QuizAnswer, TeamMember
from onboarding.ai_detection import calculate_rubric_score, detect_ai_usage, assess_essay_skill_level


class Command(BaseCommand):
    help = "Generate assessment report for a team member's Developer Level Assessment"

    def add_arguments(self, parser):
        parser.add_argument(
            'team_member_id',
            type=int,
            help='Team member ID to assess',
        )
        parser.add_argument(
            '--run-ai-detection',
            action='store_true',
            help='Run AI detection on essay answers',
        )
        parser.add_argument(
            '--assess-essays',
            action='store_true',
            help='Run skill level assessment on essay answers',
        )

    def handle(self, *args, **options):
        team_member_id = options['team_member_id']
        run_ai = options['run_ai_detection']
        assess_essays = options['assess_essays']
        
        try:
            team_member = TeamMember.objects.get(id=team_member_id)
        except TeamMember.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Team member {team_member_id} not found"))
            return
        
        # Get the Developer Level Assessment quiz
        try:
            quiz = Quiz.objects.get(name="Developer Level Assessment")
        except Quiz.DoesNotExist:
            self.stderr.write(self.style.ERROR("Developer Level Assessment quiz not found"))
            self.stdout.write("Run: python manage.py create_developer_level_quiz")
            return
        
        # Get all answers for this team member
        answers = QuizAnswer.objects.filter(
            team_member=team_member,
            question__quiz=quiz
        ).select_related('question').order_by('question__id')
        
        if not answers.exists():
            self.stderr.write(self.style.ERROR(f"No answers found for {team_member}"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*80}"))
        self.stdout.write(self.style.SUCCESS(f"DEVELOPER LEVEL ASSESSMENT REPORT"))
        self.stdout.write(self.style.SUCCESS(f"{'='*80}"))
        self.stdout.write(f"\nCandidate: {team_member.first_name} {team_member.last_name}")
        self.stdout.write(f"Email: {team_member.email}")
        self.stdout.write(f"Team Member Type: {team_member.team_member_type}")
        self.stdout.write(f"Total Answers: {answers.count()}")
        
        # Separate multiple choice and essay answers
        mc_answers = {}
        essay_answers = []
        
        for answer in answers:
            if answer.question.question_type == 'multiple_choice':
                mc_answers[answer.question.id] = answer.answer
            else:
                essay_answers.append(answer)
        
        # Calculate multiple choice score
        self.stdout.write(f"\n{'-'*80}")
        self.stdout.write(self.style.SUCCESS("MULTIPLE CHOICE ASSESSMENT (Questions 1-15)"))
        self.stdout.write(f"{'-'*80}")
        
        if mc_answers:
            rubric = calculate_rubric_score(mc_answers)
            self.stdout.write(f"\n📊 Score: {rubric['total_score']}/60 ({rubric['percentage']}%)")
            self.stdout.write(f"📊 Average per question: {rubric['average_score']:.2f}/4")
            self.stdout.write(f"📊 Questions answered: {rubric['question_count']}")
            self.stdout.write(f"\n🎯 Assessed Level: {rubric['level']}")
            self.stdout.write(f"💡 Recommendation: {rubric['recommendation']}")
        else:
            self.stdout.write(self.style.WARNING("No multiple choice answers found"))
        
        # Process essay answers
        if essay_answers:
            self.stdout.write(f"\n{'-'*80}")
            self.stdout.write(self.style.SUCCESS(f"ESSAY ANSWERS (Questions 16-18)"))
            self.stdout.write(f"{'-'*80}")
            
            for idx, answer in enumerate(essay_answers, 1):
                self.stdout.write(f"\n{'='*80}")
                self.stdout.write(f"Essay Question {idx}")
                self.stdout.write(f"{'='*80}")
                
                # Show question
                question_preview = answer.question.question[:150]
                if len(answer.question.question) > 150:
                    question_preview += "..."
                self.stdout.write(f"\nQuestion: {question_preview}")
                
                # Show answer preview
                answer_preview = answer.answer[:200]
                if len(answer.answer) > 200:
                    answer_preview += "..."
                self.stdout.write(f"\nAnswer: {answer_preview}")
                self.stdout.write(f"Word count: {len(answer.answer.split())} words")
                
                # Run AI detection if requested
                if run_ai:
                    self.stdout.write(f"\n{'-'*40}")
                    self.stdout.write("Running AI Detection...")
                    self.stdout.write(f"{'-'*40}")
                    
                    score, analysis = detect_ai_usage(answer.answer)
                    answer.ai_detection_score = score
                    answer.ai_detection_analysis = analysis
                    answer.save(update_fields=['ai_detection_score', 'ai_detection_analysis'])
                    
                    self.stdout.write(f"\n🤖 AI Detection Score: {score:.1f}/100")
                    
                    if score >= 70:
                        self.stdout.write(self.style.ERROR("⚠️  HIGH likelihood of AI assistance"))
                    elif score >= 50:
                        self.stdout.write(self.style.WARNING("⚡ MODERATE likelihood of AI assistance"))
                    elif score >= 30:
                        self.stdout.write("❓ UNCERTAIN - Could be human or AI")
                    else:
                        self.stdout.write(self.style.SUCCESS("✓ LOW likelihood of AI (appears human)"))
                    
                    # Show brief analysis
                    self.stdout.write("\nBrief Analysis:")
                    for line in analysis.split('\n')[:10]:  # First 10 lines
                        if line.strip():
                            self.stdout.write(f"  {line}")
                
                # Run skill assessment if requested
                if assess_essays:
                    self.stdout.write(f"\n{'-'*40}")
                    self.stdout.write("Assessing Technical Skill Level...")
                    self.stdout.write(f"{'-'*40}")
                    
                    skill_level, skill_analysis = assess_essay_skill_level(answer.answer)
                    
                    self.stdout.write(f"\n🎓 Skill Level: {skill_level}")
                    self.stdout.write("\nSkill Assessment:")
                    for line in skill_analysis.split('\n')[:15]:  # First 15 lines
                        if line.strip():
                            self.stdout.write(f"  {line}")
        
        # Overall summary
        self.stdout.write(f"\n{'='*80}")
        self.stdout.write(self.style.SUCCESS("SUMMARY & NEXT STEPS"))
        self.stdout.write(f"{'='*80}")
        
        if mc_answers:
            self.stdout.write(f"\n✓ Multiple Choice: {rubric['level']} ({rubric['total_score']}/60)")
        
        if essay_answers:
            self.stdout.write(f"\n✓ Essay Answers: {len(essay_answers)} questions answered")
            
            if run_ai:
                avg_ai_score = sum(a.ai_detection_score or 0 for a in essay_answers) / len(essay_answers)
                self.stdout.write(f"✓ Average AI Detection Score: {avg_ai_score:.1f}/100")
                
                if avg_ai_score >= 60:
                    self.stdout.write(self.style.WARNING(
                        "\n⚠️  CAUTION: High AI usage detected. Recommend follow-up interview "
                        "with technical deep-dive questions."
                    ))
                elif avg_ai_score >= 40:
                    self.stdout.write(
                        "\n⚡ MODERATE AI signals. Conduct standard technical interview."
                    )
                else:
                    self.stdout.write(self.style.SUCCESS(
                        "\n✓ Low AI signals. Answers appear authentic."
                    ))
        
        self.stdout.write("\n📋 Recommended Next Steps:")
        self.stdout.write("  1. Review this assessment report")
        self.stdout.write("  2. Schedule follow-up interview (honor system + verification)")
        self.stdout.write("  3. Ask specific technical questions related to essay answers")
        self.stdout.write("  4. Assess cultural fit and communication skills")
        
        self.stdout.write(f"\n{'='*80}\n")
