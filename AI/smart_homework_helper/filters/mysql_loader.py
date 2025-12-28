import mysql.connector
from langchain_core.documents import Document
from config import Config

class MySQLLoader:
    def __init__(self):
        self.config = Config.mysql_config
    
    def get_connection(self):
        return mysql.connector.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database'],
            port=self.config['port']
        )

    def load_data(self):
        """
        سحب المحتوى التعليمي من جداول متعددة وتحويلها لمستندات
        """
        documents = []
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            print("🔌 Connected to MySQL. Fetching content...")

            # 1. سحب محتوى الدروس (Lesson Content)
            # نركز على الأعمدة التي تحتوي نصوصاً مفيدة
            query_lessons = """
                SELECT 
                    lc.title, 
                    lc.text_content, 
                    lc.description,
                    l.name as lesson_name,
                    l.subject,
                    l.level
                FROM eduapi_lessoncontent lc
                JOIN eduapi_lesson l ON lc.lesson_id = l.id
                WHERE lc.text_content IS NOT NULL AND lc.text_content != ''
            """
            cursor.execute(query_lessons)
            for row in cursor.fetchall():
                # دمج النصوص لتكوين محتوى غني
                full_text = f"المادة: {row['subject']}\nالدرس: {row['lesson_name']}\nالعنوان: {row['title']}\n\n{row['description'] or ''}\n\n{row['text_content']}"
                
                meta = {
                    "source": "database",
                    "type": "lesson",
                    "title": row['title'],
                    "subject": row['subject'],
                    "level": row['level']
                }
                documents.append(Document(page_content=full_text, metadata=meta))

            print(f"   -> Loaded {len(documents)} lesson contents.")

            # 2. سحب الأسئلة والأجوبة والشروحات (Q&A Bank)
            # هذا مفيد جداً للمساعد ليفهم كيفية حل المسائل
            query_qa = """
                SELECT 
                    q.question_text,
                    a.answer_text,
                    a.explanation,
                    a.is_correct
                FROM eduapi_question q
                JOIN eduapi_answer a ON a.question_id = q.id
                WHERE a.explanation IS NOT NULL AND a.explanation != ''
            """
            cursor.execute(query_qa)
            qa_count = 0
            for row in cursor.fetchall():
                # صياغة النص كنموذج سؤال وجواب تعليمي
                status = "إجابة صحيحة" if row['is_correct'] else "إجابة خاطئة"
                full_text = f"سؤال: {row['question_text']}\n{status}: {row['answer_text']}\nالشرح والتعليل: {row['explanation']}"
                
                meta = {
                    "source": "database",
                    "type": "qa_explanation",
                    "is_correct": row['is_correct']
                }
                documents.append(Document(page_content=full_text, metadata=meta))
                qa_count += 1
            
            print(f"   -> Loaded {qa_count} Q&A explanations.")

            return documents

        except Exception as e:
            print(f"❌ MySQL Error: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()