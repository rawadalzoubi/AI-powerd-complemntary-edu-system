import pdfplumber
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    """Filter to parse PDF files and extract text."""
    
    def process(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        import os
        current_cwd = os.getcwd()
        logger.info(f"PDFParser Current Working Directory: {current_cwd}")
        print(f"DEBUG PDFParser CWD: {current_cwd}")
        """
        Process the files by parsing PDFs and extracting text.
        
        Args:
            files (List[Dict]): List of dictionaries containing document data.
                                 Expected keys from MySQLLoader: 'id', 'title', 
                                 'file' (containing the file path).
                                 
        Returns:
            List[Dict]: List of dictionaries with parsed text content.
        """
        parsed_files = []
        # temp_dir = "temp_pdfs" # لا حاجة لملفات مؤقتة إذا كان بإمكاننا فتح المسار مباشرة
        
        if not files:
            logger.info("No files provided to PDFParser.") # استخدام logger أفضل من print
            return parsed_files

        for item_data in files: # تم تغيير اسم المتغير من file إلى item_data لتجنب الالتباس
            file_id = None # تعريف المتغيرات خارج try لضمان وجودها في except
            actual_file_path = None
            display_title = item_data.get('title', "Unknown Title") # استخدام .get مع قيمة افتراضية

            try:
                file_id = item_data.get('id')
                actual_file_path = item_data.get('file') # هذا هو المسار الفعلي للملف من عمود 'file'

                if not actual_file_path or not isinstance(actual_file_path, str):
                    logger.warning(f"Skipping item with ID {file_id} (Title: {display_title}) due to missing or invalid file path.")
                    continue

                # Define the base path to your media files
                # TODO: Move this to a configuration file or environment variable
                media_base_path = "C:/Users/Rawad/Desktop/Complementary_Education_System/backend/Education/Educational_system/media"
                
                # Construct the full path
                full_file_path = os.path.join(media_base_path, actual_file_path)

                # الآن، استخدم full_file_path للتحقق من الامتداد ولفتح الملف
                if actual_file_path.lower().endswith('.pdf'): # Keep original actual_file_path for extension check
                    if not os.path.exists(full_file_path):
                        logger.error(f"PDF file not found at path: {full_file_path} for ID: {file_id} (Title: {display_title})")
                        continue
                    
                    text = ""
                    with pdfplumber.open(full_file_path) as pdf: # افتح المسار الأصلي مباشرة
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    
                    parsed_files.append({
                        'id': file_id,
                        'file_name': actual_file_path, # يمكنك الاحتفاظ بالمسار كـ file_name
                        'title': display_title,        # الاحتفاظ بالعنوان الأصلي
                        'text': text.strip()
                    })
                    logger.info(f"Successfully parsed PDF: {full_file_path} (ID: {file_id}, Title: {display_title})")

                elif actual_file_path.lower().endswith(('.txt', '.md')): # Keep original actual_file_path for extension check
                    # The original code already used abspath, let's ensure it's based on the full_file_path logic
                    # However, the original debug log used `os.path.abspath(actual_file_path)` which would be relative to CWD.
                    # We should use full_file_path for consistency.
                    logger.info(f"PDFParser is checking text file path: {full_file_path}")
                    print(f"DEBUG PDFParser is checking text file path: {full_file_path}") # Keep for user's debug if needed
                    if not os.path.exists(full_file_path):
                        logger.error(f"Text file not found at path: {full_file_path} for ID: {file_id} (Title: {display_title})")
                        continue

                    with open(full_file_path, "r", encoding='utf-8', errors='ignore') as f_text:
                        text_content = f_text.read()
                    
                    parsed_files.append({
                        'id': file_id,
                        'file_name': actual_file_path, # Keep original relative path as file_name
                        'title': display_title,
                        'text': text_content.strip()
                    })
                    logger.info(f"Successfully parsed text file: {full_file_path} (ID: {file_id}, Title: {display_title})")
                else:
                    logger.info(f"Skipping unsupported file type: {actual_file_path} (ID: {file_id}, Title: {display_title})") # Path for log might be better as full_file_path
                
            except Exception as e:
                # استخدام القيم المعرفة مسبقًا في رسالة الخطأ
                path_for_log = actual_file_path if actual_file_path else "Unknown Path"
                id_for_log = file_id if file_id else "Unknown ID"
                title_for_log = display_title
                logger.error(f"Error processing file {path_for_log} (ID: {id_for_log}, Title: {title_for_log}): {e}", exc_info=True)
                continue # انتقل إلى الملف التالي في حالة حدوث خطأ
            
        return parsed_files

    # دالة parse هذه تبدو غير مستخدمة في منطق process الأساسي
    # إذا كنت تخزن المحتوى الثنائي مباشرة في قاعدة البيانات في عمود آخر
    # وتحتاج إلى تحليل هذا المحتوى الثنائي، فستحتاج إلى تعديل MySQLLoader لجلب هذا العمود
    # ثم استدعاء هذه الدالة. الكود الحالي لـ process يعتمد على قراءة الملفات من مسارات.
    def parse(self, content: bytes) -> str:
        """
        Parse the content from a document.
        
        Args:
            content: The document content as bytes
            
        Returns:
            The parsed text content
        """
        try:
            text = content.decode('utf-8')
            logger.info("Successfully parsed document content")
            return text
        except Exception as e:
            logger.error(f"Error parsing document content: {str(e)}")
            raise