import os
import openai
import instructor
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class AnalysisResult(BaseModel):
    summary: str = Field(description="A brief summary of the session")
    topics: list[str] = Field(description="Key topics discussed")
    action_items: list[str] = Field(description="List of action items")
    questions_asked: list[str] = Field(description="Questions asked during the session")
    talk_listen_ratios: dict[str, float] = Field(description="Ratios of talk/listen per speaker if identifiable, otherwise general ratios. Example: {'Speaker 1': 0.6, 'Speaker 2': 0.4}")

class AIService:
    @staticmethod
    def generate_transcript(audio_file_path: str) -> str:
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
        
    @staticmethod
    def generate_semantic_analysis(transcript: str) -> dict:
        client = instructor.from_openai(openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY")))
        
        response = client.chat.completions.create(
            model="gpt-4o",
            response_model=AnalysisResult,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that analyzes meeting transcripts. Extract the summary, key topics, action items, questions asked, and estimate the talk/listen ratio."},
                {"role": "user", "content": f"Analyze the following transcript:\n\n{transcript}"}
            ]
        )
        return response.model_dump()
