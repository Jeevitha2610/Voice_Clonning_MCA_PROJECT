# 🎙️ VoiceStudio

> **Your Local-First Neural Voice Cloning & Speech Production Studio**  
> 100% Pure Python • Runs on your CPU • Zero Cloud Required • Studio-Grade Audio

VoiceStudio is a desktop-grade audio workstation that runs completely on your own computer. You can type any sentence and hear it spoken aloud, clone any voice from a short audio sample, or choose from ready-to-use studio voices. Because everything runs locally, your voice recordings and text stay 100% private.

---

## 🚀 Quick Start (In 60 Seconds)

You don't need any complex setup or cloud accounts. Follow these two simple steps:

### Step 1: Open Your Terminal
Open PowerShell or Command Prompt on your computer, and navigate to the project folder:
```powershell
cd "C:\Users\Jeevitha J R\Desktop\project"
```

### Step 2: Start the Studio
Run the launcher command:
```powershell
python run.py
```

You will see the studio banner appear in your terminal. Next, open your web browser (Chrome, Edge, Firefox, or Brave) and go to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧭 Visual Studio Layout (Where Everything Is)

When you open the application in your browser, the screen is organized into **four distinct areas**:

```
+-------------------------------------------------------------------------+
| [TOP] Session Bar: System Status & Hardware Telemetry                   |
+------------------------------------+------------------------------------+
| [LEFT SIDEBAR]                     | [CENTER WORKSPACE]                 |
|                                    |                                    |
| 1. Voice Profiles (Select a Voice) | 3. Speech Script (Type your text)  |
|    • Aria Prime (Narrator)         |                                    |
|    • Atlas Echo (Deep Radio)       | 4. Tuning Sliders                  |
|    • Nova Clarity (Tech)           |    • Speed Slider (0.5x - 2.0x)    |
|    • Orion Warmth (Story)          |    • Pitch Slider (-6st to +6st)   |
|                                    |                                    |
| 2. Audio Dropzone (Clone a Voice)  | 5. [ Synthesize Speech ] Button    |
|    [ Drag & Drop Audio Here ]      |                                    |
+------------------------------------+------------------------------------+
| [BOTTOM DOCK] Audio Transport & Waveform Monitor                       |
|   [▶ Play/Pause]   [⬇ Download WAV]   |   ~~~~~ Sound Waveform ~~~~~    |
+-------------------------------------------------------------------------+
```

---

## 📖 Step-by-Step User Guide (For Beginners)

### Workflow 1: How to Turn Text into Speech (Using a Preset Voice)

1. **Look to the Left Side of the Screen:**  
   Under **"Voice Profiles"**, you will see a list of pre-calibrated voices. Click on any voice to highlight it:
   - **Aria Prime** – A balanced, natural studio narrator (great for general voiceovers).
   - **Atlas Echo** – A deep, resonant radio broadcaster voice.
   - **Nova Clarity** – A crisp, bright voice ideal for instructions and tutorials.
   - **Orion Warmth** – A calm, gentle storytelling voice.

2. **Look to the Center of the Screen:**  
   Find the big text box labeled **"Speech Script"**. Click inside it and type whatever you want the voice to say:
   > *"Hello everyone! Welcome to my podcast. Today we are talking about sound design."*

3. **Adjust the Sound (Optional):**  
   Right below the text box are two adjustment sliders:
   - **Speech Speed:** Slide left to speak slower (down to 0.5x), or slide right to speak faster (up to 2.0x).
   - **Pitch Modulation:** Slide left to make the voice deeper, or slide right to make it higher.

4. **Click the Blue Button:**  
   Click the **"Synthesize Speech"** button (or press `Ctrl + Enter` on your keyboard).
   - You will see a blue progress bar fill across the screen as the neural engine creates your audio.

5. **Listen to the Result (Bottom of the Screen):**  
   Once synthesis finishes, look at the **bottom dock**:
   - The green sound wave will light up with your newly created speech.
   - Click the **Play button (`▶`)** or press the **Spacebar** to listen.
   - Click the **Download button (`⬇`)** to save the audio file (`.wav`) directly to your computer!

---

### Workflow 2: How to Clone Any Voice from an Audio File

You can teach VoiceStudio to speak with any voice using a short recording (5 to 30 seconds of clear talking).

1. **Prepare Your Audio Sample:**
   - Record a short clip on your phone or computer, or use an existing audio file (`.wav`, `.mp3`, `.flac`, or `.ogg`).
   - For best results, use a clip with clean speech and no loud background music.

2. **Look to the Bottom of the Left Sidebar:**  
   Find the dashed box with the microphone icon that says **"Drop reference WAV/MP3 to clone voice"**.

3. **Add Your File:**
   - **Option A:** Drag your audio file from your folder and drop it right into the box.
   - **Option B:** Click inside the box, and a file browser window will pop up. Select your audio file and click **Open**.

4. **Name the Voice:**
   - A prompt will ask you for a name (for example: *"Uncle Robert"* or *"Conference Speaker"*).
   - Type the name and press **OK**.

5. **Done!**
   - The studio will analyze the acoustic timbre, calculate a 128-dimensional voiceprint, and add your new voice to the top of the **Voice Profiles** list.
   - Click on your new voice card, type your text in the center box, and click **"Synthesize Speech"**!

---

### Workflow 3: Scrubbing and Exploring the Sound Wave

At the bottom of your screen is the **Studio Monitor Waveform**:
- **Play / Pause:** Press the `▶` button on the left or tap your keyboard's **Spacebar**.
- **Scrub / Jump to a Part:** Click anywhere directly on the green sound waveform to jump the playback head immediately to that exact syllable.
- **Audio Telemetry (Bottom Right):**
  - **Signal SNR:** Shows the cleanliness of the audio signal (above 20 dB is studio quality).
  - **Integrated LUFS:** Measures broadcast loudness (normalized to standard -23 LUFS).
  - **Duration:** Shows the exact length in seconds.

---

## ⌨️ Helpful Keyboard Shortcuts

| Shortcut | Action | Where to Use |
| :--- | :--- | :--- |
| `Ctrl + Enter` | Instantly generates speech | Inside the Speech Script box |
| `Spacebar` | Plays or Pauses the audio | Anywhere in the studio |
| `Click on Waveform` | Jumps playback to that exact spot | In the bottom waveform area |

---

## 💻 Headless Mode (Command Line for Power Users)

If you prefer using the command line without opening a browser, VoiceStudio provides complete terminal commands:

- **List all voices:**
  ```powershell
  python -m VoiceStudio list-voices
  ```

- **Clone a voice directly from a file:**
  ```powershell
  python -m VoiceStudio clone-voice --name "David" --file "my_sample.wav"
  ```

- **Generate speech straight to a WAV file:**
  ```powershell
  python -m VoiceStudio synthesize --text "Welcome to the studio." --out "output.wav"
  ```

- **Inspect the sound quality of any audio file:**
  ```powershell
  python -m VoiceStudio assess --file "output.wav"
  ```

---

## ❓ Frequently Asked Questions (FAQ)

### How do I stop the application?
Go back to the terminal window where you ran `python run.py`, and press `Ctrl + C` on your keyboard.

### Where are my generated audio files stored on my hard drive?
All audio files are safely stored inside the project folder at:
```
project\data\outputs\
```
Your uploaded voice samples are stored at:
```
project\data\uploads\
```

### Can VoiceStudio work without an internet connection?
**Yes, 100%.** VoiceStudio runs entirely on your local machine using PyTorch and local signal processing. It does not send any audio or text over the internet.

### Does it require an expensive graphics card (GPU)?
No. VoiceStudio is optimized specifically for standard **CPU** processing. It runs smoothly on any modern laptop or desktop computer.

---

## 🛠️ Verification & Testing

To verify that all 35 internal automated tests are passing:
```powershell
python -m pytest -v
```

Enjoy creating your custom voices with **VoiceStudio**! 🎙️✨
