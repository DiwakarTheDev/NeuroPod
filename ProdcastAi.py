import fitz # PDF text extraction
import speech_recognition as sr # Speech Recognition
from transformers import pipeline # AI Response Generation & Summarization
from gtts import gTTS # Google Text-to-Speech
import pygame # Background music & sound effects
import time # Timing transitions
import os # File handling

# File paths (Updated)
INTRO_SOUND = "intro.wav"
OUTRO_SOUND = "outro.wav"
BACKGROUND_MUSIC = "background_music.mp3"
QNA_SOUND = "background_music.mp3"
PDF_FILE = "article.pdf"

# Load AI Models for summarization & Q&A
summarizer = pipeline("summarization", model="t5-small")
qa_pipeline = pipeline("text2text-generation", model="t5-small")

# Initialize Pygame for audio management
pygame.mixer.init()
bgm_channel = pygame.mixer.Channel(0) # Separate channel for BGM
voice_channel = pygame.mixer.Channel(1) # Separate channel for AI voice

def play_background_music():
    """Plays background music with fade-in effect."""
    bgm_sound = pygame.mixer.Sound(BACKGROUND_MUSIC)
    bgm_channel.play(bgm_sound, loops=-1, fade_ms=2000) # 2s fade-in
    bgm_channel.set_volume(0.6) # Set default volume

def fade_out_bgm():
    """Fades out background music smoothly."""
    for i in range(10, 5, -1):  
        bgm_channel.set_volume(i / 10)
        time.sleep(0.2)

def fade_in_bgm():
    """Fades in background music smoothly."""
    for i in range(6, 11):  
        bgm_channel.set_volume(i / 10)
        time.sleep(0.2)

def play_sound_effect(effect_file):
    """Plays sound effects with fade-in."""
    fade_out_bgm()
    effect = pygame.mixer.Sound(effect_file)
    voice_channel.play(effect, fade_ms=500)  
    while voice_channel.get_busy():
        time.sleep(0.5)
    fade_in_bgm()

def generate_voice(text, voice_gender="male"):
    """Generates AI voice using gTTS."""
    voice_file = f"ai_voice_{voice_gender}.mp3"
    
    # Adjust speed for a natural effect
    tts = gTTS(text=text, lang="en", tld="co.in", slow=True if voice_gender == "female" else False)
    tts.save(voice_file)

    fade_out_bgm()  

    # Play AI voice on a separate channel
    ai_voice = pygame.mixer.Sound(voice_file)
    voice_channel.play(ai_voice, fade_ms=500)  
    while voice_channel.get_busy():
        time.sleep(0.5)

    os.remove(voice_file)  
    fade_in_bgm()  

def extract_text_from_pdf():
    """Extracts text from PDF."""
    doc = fitz.open(PDF_FILE)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def generate_podcast_script(full_text):
    """Generates an interactive podcast script with a natural conversation flow."""
    summary = summarizer(full_text, max_length=500, min_length=200, do_sample=False)[0]["summary_text"]

    discussion_points = summary.split(". ")[:5] # Pick 5 key points to discuss

    script = [
        "🎙️ Welcome to our AI-powered podcast! Today, we have a fascinating topic to discuss!",
        f"👨 Male AI: Hey, did you know? {discussion_points[0]}",
        f"👩 Female AI: Wow, that's interesting! But how does that connect with {discussion_points[1]}?",
        f"👨 Male AI: Great question! It turns out that {discussion_points[2]}.",
        f"👩 Female AI: That reminds me of something related. {discussion_points[3]}! What do you think?",
        f"👨 Male AI: I think it's fascinating. But there's another perspective to this: {discussion_points[4]}",
        "👩 Female AI: This discussion is getting deep! Let's take a pause for any listener questions!",
    ]
    
    return script

def listen_for_question():
    """Listens for user questions."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Ask a question or say 'continue' to resume.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        question = recognizer.recognize_google(audio).lower()
        print(f"🗣️ You asked: {question}")
        return question
    except sr.UnknownValueError:
        print("❌ Could not understand. Try again.")
        return None
    except sr.RequestError:
        print("❌ Speech Recognition service unavailable.")
        return None

def answer_question(context, question):
    """Generates an AI answer based on user question."""
    response = qa_pipeline(f"question: {question} context: {context}")[0]["generated_text"]
    return response

def interactive_qna(context):
    """Handles real-time Q&A and resumes podcast."""
    while True:
        question = listen_for_question()
        if question is None:
            continue
        if "exit" in question:
            print("🔴 Ending podcast. Goodbye!")
            return False
        if "continue" in question:
            print("🎙️ Resuming discussion...")
            return True  

        play_sound_effect(QNA_SOUND)  

        answer = answer_question(context, question)

        print(f"👨 Male AI: {answer}")
        generate_voice(answer, "male")

        print("👩 Female AI: Yes, and to add to that...")
        generate_voice(f"Yes, and to add to that... {answer}", "female")

        print("\n🔄 Ask another question or say 'continue'.")
        generate_voice("Would you like to ask another question or continue the discussion?", "male")

def main():
    """Main function to run AI podcast."""
    full_text = extract_text_from_pdf()
    podcast_script = generate_podcast_script(full_text)

    play_background_music()

    play_sound_effect(INTRO_SOUND)  
    time.sleep(2)  

    print("\n🎙️ AI Podcast Begins 🎙️\n")

    for line in podcast_script:
        if "👨" in line:
            generate_voice(line.replace("👨", ""), "male")
        elif "👩" in line:
            generate_voice(line.replace("👩", ""), "female")
        else:
            generate_voice(line, "male")

        print("🔵 (Pause for possible questions)")
        generate_voice("Do you have any questions about this?", "female")

        if not interactive_qna(full_text):
            break

    play_sound_effect(OUTRO_SOUND)  
    time.sleep(3)  

    print("🎙️ AI Podcast Ended. Thank you for listening!")
    bgm_channel.fadeout(3000)  

if __name__ == "__main__":
    main()