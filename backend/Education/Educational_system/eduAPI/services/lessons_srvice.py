from eduAPI.models.lessons_model import Lesson, LessonContent, Quiz, Question, Answer

class LessonService:
    @staticmethod
    def get_teacher_lessons(teacher_id):
        """Get all lessons created by a specific teacher."""
        return Lesson.objects.filter(teacher_id=teacher_id)
    
    @staticmethod
    def get_lesson_by_id(lesson_id, teacher_id=None):
        """Get a specific lesson by ID, optionally filtering by teacher."""
        if teacher_id:
            return Lesson.objects.filter(id=lesson_id, teacher_id=teacher_id).first()
        return Lesson.objects.filter(id=lesson_id).first()
    
    @staticmethod
    def create_lesson(data, teacher_id):
        """Create a new lesson."""
        lesson = Lesson.objects.create(
            name=data['name'],
            subject=data['subject'],
            level=data['level'],
            teacher_id=teacher_id
        )
        return lesson
    
    @staticmethod
    def update_lesson(lesson_id, data, teacher_id):
        """Update an existing lesson."""
        lesson = LessonService.get_lesson_by_id(lesson_id, teacher_id)
        if not lesson:
            return None
        
        if 'name' in data:
            lesson.name = data['name']
        if 'subject' in data:
            lesson.subject = data['subject']
        if 'level' in data:
            lesson.level = data['level']
        
        lesson.save()
        return lesson
    
    @staticmethod
    def delete_lesson(lesson_id, teacher_id):
        """Delete a lesson."""
        lesson = LessonService.get_lesson_by_id(lesson_id, teacher_id)
        if not lesson:
            return False
        
        lesson.delete()
        return True

class LessonContentService:
    @staticmethod
    def get_lesson_contents(lesson_id):
        """Get all content for a specific lesson."""
        return LessonContent.objects.filter(lesson_id=lesson_id)
    
    @staticmethod
    def create_content(lesson_id, data, file):
        """Create new lesson content."""
        content = LessonContent.objects.create(
            lesson_id=lesson_id,
            content_type=data['content_type'],
            title=data['title'],
            file=file
        )
        return content
    
    @staticmethod
    def delete_content(content_id, teacher_id):
        """Delete lesson content."""
        content = LessonContent.objects.filter(id=content_id, lesson__teacher_id=teacher_id).first()
        if not content:
            return False
        
        content.delete()
        return True

class QuizService:
    @staticmethod
    def get_lesson_quizzes(lesson_id):
        """Get all quizzes for a specific lesson."""
        return Quiz.objects.filter(lesson_id=lesson_id)
    
    @staticmethod
    def get_quiz_by_id(quiz_id, teacher_id=None):
        """Get a specific quiz by ID, optionally filtering by teacher."""
        if teacher_id:
            return Quiz.objects.filter(id=quiz_id, lesson__teacher_id=teacher_id).first()
        return Quiz.objects.filter(id=quiz_id).first()
    
    @staticmethod
    def create_quiz(lesson_id, data):
        """Create a new quiz."""
        quiz = Quiz.objects.create(
            lesson_id=lesson_id,
            title=data['title'],
            total_marks=data['total_marks']
        )
        return quiz
    
    @staticmethod
    def update_quiz(quiz_id, data, teacher_id):
        """Update an existing quiz."""
        quiz = QuizService.get_quiz_by_id(quiz_id, teacher_id)
        if not quiz:
            return None
        
        if 'title' in data:
            quiz.title = data['title']
        if 'total_marks' in data:
            quiz.total_marks = data['total_marks']
        
        quiz.save()
        return quiz
    
    @staticmethod
    def delete_quiz(quiz_id, teacher_id):
        """Delete a quiz."""
        quiz = QuizService.get_quiz_by_id(quiz_id, teacher_id)
        if not quiz:
            return False
        
        quiz.delete()
        return True

class QuestionService:
    @staticmethod
    def create_question(quiz_id, data):
        """Create a new question."""
        question = Question.objects.create(
            quiz_id=quiz_id,
            text=data['text'],
            points=data['points']
        )
        return question
    
    @staticmethod
    def get_question_by_id(question_id, teacher_id=None):
        """Get a specific question by ID, optionally filtering by teacher."""
        if teacher_id:
            return Question.objects.filter(id=question_id, quiz__lesson__teacher_id=teacher_id).first()
        return Question.objects.filter(id=question_id).first()
    
    @staticmethod
    def update_question(question_id, data, teacher_id):
        """Update an existing question."""
        question = QuestionService.get_question_by_id(question_id, teacher_id)
        if not question:
            return None
        
        if 'text' in data:
            question.text = data['text']
        if 'points' in data:
            question.points = data['points']
        
        question.save()
        return question
    
    @staticmethod
    def delete_question(question_id, teacher_id):
        """Delete a question."""
        question = QuestionService.get_question_by_id(question_id, teacher_id)
        if not question:
            return False
        
        question.delete()
        return True

class AnswerService:
    @staticmethod
    def create_answer(question_id, data):
        """Create a new answer."""
        answer = Answer.objects.create(
            question_id=question_id,
            text=data['text'],
            is_correct=data.get('is_correct', False)
        )
        return answer
    
    @staticmethod
    def get_answer_by_id(answer_id, teacher_id=None):
        """Get a specific answer by ID, optionally filtering by teacher."""
        if teacher_id:
            return Answer.objects.filter(id=answer_id, question__quiz__lesson__teacher_id=teacher_id).first()
        return Answer.objects.filter(id=answer_id).first()
    
    @staticmethod
    def update_answer(answer_id, data, teacher_id):
        """Update an existing answer."""
        answer = AnswerService.get_answer_by_id(answer_id, teacher_id)
        if not answer:
            return None
        
        if 'text' in data:
            answer.text = data['text']
        if 'is_correct' in data:
            answer.is_correct = data['is_correct']
        
        answer.save()
        return answer
    
    @staticmethod
    def delete_answer(answer_id, teacher_id):
        """Delete an answer."""
        answer = AnswerService.get_answer_by_id(answer_id, teacher_id)
        if not answer:
            return False
        
        answer.delete()
        return True