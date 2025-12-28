import os
import torch
from transformers import pipeline
from moviepy import VideoFileClip

class VideoProcessor:
    def __init__(self, model_id="openai/whisper-small"):
        """
        تهيئة نموذج Whisper من Hugging Face (نسخة متوافقة مع Modal).
        """
        print(f"Loading Hugging Face Whisper model: {model_id}...")
        
        # اكتشاف ما إذا كان الجهاز يدعم GPU
        # في Modal T4، سيكون cuda:0 متاحاً
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Running Whisper on: {self.device}")

        # إعداد خط الأنابيب (Pipeline)
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            chunk_length_s=30,
            device=self.device,
        )

    def extract_audio(self, video_path, output_audio_path="temp_audio.mp3"):
        try:
            with VideoFileClip(video_path) as video:
                video.audio.write_audiofile(output_audio_path, logger=None)
            return output_audio_path
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    def transcribe_video(self, video_path):
        print(f"Processing video/audio: {video_path}...")
        
        # التحقق إذا كان الملف صوتي مباشرة (wav, mp3, webm) أو فيديو
        audio_extensions = ['.wav', '.mp3', '.webm', '.ogg', '.flac', '.m4a']
        file_ext = os.path.splitext(video_path)[1].lower()
        
        if file_ext in audio_extensions:
            # الملف صوتي مباشرة - لا حاجة لاستخراج الصوت
            audio_path = video_path
            should_delete_audio = False
            print(f"  -> Direct audio file detected: {file_ext}")
        else:
            # الملف فيديو - نستخرج الصوت منه
            audio_path = self.extract_audio(video_path)
            should_delete_audio = True
            if not audio_path:
                return None

        try:
            # التشغيل عبر Pipeline
            prediction = self.pipe(
                audio_path, 
                return_timestamps=True,
                generate_kwargs={"language": "arabic"}
            )
            
            if should_delete_audio and os.path.exists(audio_path):
                os.remove(audio_path)

            segments = []
            # التعامل مع اختلاف صيغ المخرجات
            chunks = prediction.get("chunks", [])
            
            if not chunks:
                segments.append({
                    "text": prediction["text"].strip(),
                    "start": 0.0,
                    "end": 0.0
                })
            else:
                for chunk in chunks:
                    timestamp = chunk.get("timestamp", (0.0, 0.0))
                    start, end = timestamp if timestamp else (0.0, 0.0)
                    
                    text = chunk["text"].strip()
                    if len(text) < 2: continue

                    segments.append({
                        "text": text,
                        "start": start,
                        "end": end
                    })
            
            return segments

        except Exception as e:
            print(f"Error during transcription: {e}")
            if should_delete_audio and os.path.exists(audio_path): 
                os.remove(audio_path)
            return None