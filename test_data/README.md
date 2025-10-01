# Test Data for Meeting Assistant

This directory contains sample files for testing the Meeting Assistant functionality.

## Audio Files

### test_speech.wav
- **Description**: Female speaker reading Harvard sentences
- **Format**: 16-bit PCM WAV, 8kHz
- **Duration**: ~33 seconds
- **Use**: Basic STT engine testing
- **Content**: Clear, professional speech samples

### test_meeting.wav
- **Description**: Second speech sample with Harvard sentences
- **Format**: 16-bit PCM WAV, 8kHz
- **Duration**: ~32 seconds
- **Use**: Additional STT testing and comparison

## Text Files

### sample_meeting_transcript.txt
- **Description**: Realistic meeting transcript from a software engineering standup
- **Use**: Testing summarization engines
- **Content**: Includes participants, discussion topics, and action items
- **Features**:
  - Multiple speakers
  - Technical discussion
  - Clear action items
  - Meeting structure

## Testing Commands

### CLI Testing

**Test STT with audio file:**
```bash
python3 run_cli.py transcribe test_data/test_speech.wav
```

**Test summarization with text:**
```bash
python3 run_cli.py summarize test_data/sample_meeting_transcript.txt
```

**Test different engines:**
```bash
python3 run_cli.py engines --stt-engine whisper
python3 run_cli.py transcribe test_data/test_speech.wav
```

### Web Interface Testing

1. Start web interface: `python3 run_web.py`
2. Go to http://localhost:8000/transcribe
3. Upload `test_speech.wav` or `test_meeting.wav`
4. Test summarization with content from `sample_meeting_transcript.txt`

## Expected Results

### STT Output (test_speech.wav)
Should transcribe Harvard sentences like:
- "The birch canoe slid on the smooth planks"
- "Glue the sheet to the dark blue background"
- "It's easy to tell the depth of a well"

### Summarization Output (sample_meeting_transcript.txt)
Should extract:
- **Summary**: Daily standup with progress updates and planning
- **Key Points**: Authentication module completion, testing progress, demo preparation
- **Action Items**: Staging access, test data refresh, API completion, testing tasks

## File Sources

- Audio files: VoIP Troubleshooter (https://www.voiptroubleshooter.com/open_speech/)
- Meeting transcript: Generated sample based on typical software engineering standup
- License: Public domain / freely available for testing purposes