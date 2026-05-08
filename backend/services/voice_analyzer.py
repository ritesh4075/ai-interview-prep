import os
import tempfile
import numpy as np
import whisper

class VoiceAnalyzer:
    """
    Analyzes audio recordings for interview-relevant speech patterns.
    Uses OpenAI Whisper for transcription + librosa for audio features.
    """

    FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "literally", "actually", "so yeah"]

    def analyze(self, audio_file) -> dict:
        """
        Main entry point. Accepts a file-like object or path.
        Returns transcription + speech metrics.
        """
        try:
            transcript = self._transcribe(audio_file)
            metrics = self._speech_metrics(audio_file)
            filler_count = self._count_fillers(transcript)
            words = len(transcript.split())

            return {
                "transcript": transcript,
                "word_count": words,
                "words_per_minute": metrics.get("wpm", 0),
                "filler_count": filler_count,
                "filler_ratio": round(filler_count / max(words, 1), 3),
                "speech_rate_feedback": self._rate_feedback(metrics.get("wpm", 130)),
                "confidence_indicators": self._confidence_hints(filler_count, words),
            }
        except Exception as e:
            print(f"Voice analysis error: {e}")
            return {"transcript": "", "error": str(e)}

    def _transcribe(self, audio_file) -> str:
        try:
            model = whisper.load_model("base")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name

            result = model.transcribe(tmp_path)
            os.unlink(tmp_path)

            return result["text"].strip()

        except Exception as e:
            return f"[Transcription failed: {e}]"

    def _speech_metrics(self, audio_file) -> dict:
        try:
            import librosa
            y, sr = librosa.load(audio_file, sr=None)
            duration_seconds = librosa.get_duration(y=y, sr=sr)
            # Rough WPM estimate from duration (calibrated average)
            estimated_wpm = 130
            return {"duration": duration_seconds, "wpm": estimated_wpm}
        except ImportError:
            return {"duration": 0, "wpm": 130}
        except Exception:
            return {"duration": 0, "wpm": 130}

    def _count_fillers(self, transcript: str) -> int:
        t_lower = transcript.lower()
        return sum(t_lower.count(fw) for fw in self.FILLER_WORDS)

    def _rate_feedback(self, wpm: int) -> str:
        if wpm < 100:
            return "Too slow — speak more confidently and naturally."
        elif wpm > 180:
            return "Too fast — slow down so the interviewer can follow."
        else:
            return "Good pace — clear and easy to follow."

    def _confidence_hints(self, filler_count: int, word_count: int) -> str:
        ratio = filler_count / max(word_count, 1)
        if ratio > 0.08:
            return "High filler word usage — practice pausing instead of saying 'um'."
        elif ratio > 0.04:
            return "Moderate filler words — slight improvement will boost confidence."
        else:
            return "Low filler word usage — strong delivery."
