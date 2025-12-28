import os
import torch
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import CrossEncoder
from pipelines.text_pipeline import TextPipeline
from pipelines.image_pipeline import ImagePipeline
from utils.ai_corrector import AICorrector
from config import Config

try:
    from pipelines.video_pipeline import VideoPipeline
except:
    VideoPipeline = None

class RAGService:
    def __init__(self):
        print("=== INITIALIZING RAG ORCHESTRATOR ===")
        
        self.text_pipeline = TextPipeline(Config)
        self.image_pipeline = ImagePipeline(Config)
        
        # ===> تهيئة المصحح <===
        self.ai_helper = AICorrector()
        
        if VideoPipeline:
            try:
                self.video_pipeline = VideoPipeline(Config)
            except: self.video_pipeline = None
        else: self.video_pipeline = None

        # Re-ranker
        reranker_model = getattr(Config, "RERANKER_MODEL_NAME", "BAAI/bge-reranker-base")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.reranker = CrossEncoder(reranker_model, device=device)
        except:
            self.reranker = None
        
        # LLM
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL_NAME,
            api_key=Config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7
        )
        self.qa_chain_template = None

    def load_resources(self):
        print("--- Loading Indexes ---")
        self.text_pipeline.load_index()
        self.image_pipeline.load_index()
        self._setup_generation_chain()

    def _setup_generation_chain(self):
        template = """
        أنت مساعد واجبات ذكي. أجب بناءً على السياق فقط.
        السياق:
        {context}
        السؤال:
        {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        self.qa_chain_template = (prompt | self.llm | StrOutputParser())

    def rerank_documents(self, query, docs):
        if not docs or not self.reranker: return docs
        pairs = [[query, doc.page_content] for doc in docs]
        scores = self.reranker.predict(pairs)
        scored_docs = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:getattr(Config, "FINAL_TOP_K", 3)]]

    def answer_text_question(self, question: str):
        if not self.text_pipeline.vectorstore: return "System not ready."

        # ===> تصحيح سؤال الطالب قبل البحث <===
        final_q = question
        if self.ai_helper.client and len(question.split()) > 3:
            corrected = self.ai_helper.correct_text(question)
            if corrected != question:
                print(f"✨ Query Corrected (Llama): {question} -> {corrected}")
                final_q = corrected
        
        # 1. Retrieval
        initial_docs = self.text_pipeline.vectorstore.similarity_search(final_q, k=10)
        if not initial_docs: return "No documents found."
        
        # 2. Re-ranking
        refined_docs = self.rerank_documents(final_q, initial_docs) if self.reranker else initial_docs[:3]
        
        context = "\n\n".join([d.page_content for d in refined_docs])
        
        # 3. Generation
        return self.qa_chain_template.invoke({"context": context, "question": final_q})

    def search_image(self, img): return self.image_pipeline.search(img)

def transcribe_audio_file(self, path):
        if self.video_pipeline and self.video_pipeline.video_processor:
            try:
                segs = self.video_pipeline.video_processor.transcribe_video(path)
                if segs:
                    raw_text = " ".join([s['text'] for s in segs])
                    
                    # ===> تصحيح النص الصوتي <===
                    if self.ai_helper.client:
                        final_text = self.ai_helper.correct_text(raw_text)
                        print(f"🎤 Voice Corrected: {raw_text} -> {final_text}")
                        return final_text
                    return raw_text
            except Exception as e: print(f"Error: {e}")
        return ""

rag_service = RAGService()