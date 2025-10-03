#!/usr/bin/env python3
"""
Headphone Jack Test Script for Linux
Tests 3.5mm audio jack functionality with test tones and device detection.
Compatible with RISC-V, ARM, and x86_64 Linux systems.
"""

import sys
import time
import subprocess
from typing import Optional, List, Tuple


def check_audio_backend() -> str:
    """
    Check which audio library is available.
    Returns: 'sounddevice', 'pyaudio', or 'fallback'
    """
    try:
        import sounddevice as sd
        import numpy
        return 'sounddevice'
    except ImportError:
        pass

    try:
        import pyaudio
        return 'pyaudio'
    except ImportError:
        pass

    return 'fallback'


def list_alsa_devices() -> List[str]:
    """List audio devices using aplay command."""
    try:
        result = subprocess.run(
            ['aplay', '-l'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.split('\n')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def list_pulse_devices() -> List[str]:
    """List PulseAudio output devices."""
    try:
        result = subprocess.run(
            ['pactl', 'list', 'short', 'sinks'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.split('\n')
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def get_current_volume() -> Optional[str]:
    """Get current system volume level."""
    try:
        # Try PulseAudio first
        result = subprocess.run(
            ['pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    try:
        # Try ALSA mixer
        result = subprocess.run(
            ['amixer', 'get', 'Master'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def check_audio_muted() -> bool:
    """Check if audio is muted."""
    try:
        result = subprocess.run(
            ['pactl', 'get-sink-mute', '@DEFAULT_SINK@'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'yes' in result.stdout.lower():
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    try:
        result = subprocess.run(
            ['amixer', 'get', 'Master'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if '[off]' in result.stdout.lower():
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return False


def generate_sine_wave(frequency: float, duration: float, sample_rate: int = 44100):
    """Generate a sine wave tone."""
    import numpy as np
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Apply fade in/out to avoid clicks
    fade_samples = int(sample_rate * 0.05)  # 50ms fade
    wave = np.sin(2 * np.pi * frequency * t)

    # Apply fade envelope
    envelope = np.ones_like(wave)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

    return (wave * envelope * 0.3).astype(np.float32)  # Reduced amplitude for safety


def test_with_sounddevice(device_id: Optional[int] = None) -> bool:
    """Test audio using sounddevice library."""
    try:
        import sounddevice as sd
        import numpy as np

        print("\n" + "=" * 70)
        print("Testing with sounddevice library")
        print("=" * 70)

        # List available devices
        devices = sd.query_devices()
        print("\nAvailable audio devices:")
        print("-" * 70)
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                default_marker = " [DEFAULT]" if i == sd.default.device[1] else ""
                print(f"  [{i}] {dev['name']}{default_marker}")
                print(f"      Channels: {dev['max_output_channels']}, "
                      f"Sample Rate: {dev['default_samplerate']} Hz")
        print("-" * 70)

        # Select device
        if device_id is None:
            device_input = input("\nEnter device number (press Enter for default): ").strip()
            if device_input:
                device_id = int(device_input)
            else:
                device_id = sd.default.device[1]

        selected_device = devices[device_id]
        print(f"\nSelected device: {selected_device['name']}")

        # Test tones
        sample_rate = int(selected_device['default_samplerate'])

        print("\n" + "=" * 70)
        print("PLAYING TEST TONES")
        print("=" * 70)
        print("\nPlease listen for the following tones on your headphones:")
        print("  1. 440 Hz (A4 - musical note A) for 2 seconds")
        print("  2. 880 Hz (A5 - one octave higher) for 2 seconds")
        print("\nEnsure your headphones are plugged into the 3.5mm jack!")
        input("\nPress Enter to start the test...")

        # Play 440 Hz tone
        print("\nPlaying 440 Hz tone...")
        tone_440 = generate_sine_wave(440, 2.0, sample_rate)
        sd.play(tone_440, sample_rate, device=device_id, blocking=True)
        time.sleep(0.5)

        # Play 880 Hz tone
        print("Playing 880 Hz tone...")
        tone_880 = generate_sine_wave(880, 2.0, sample_rate)
        sd.play(tone_880, sample_rate, device=device_id, blocking=True)

        print("\nTest tones completed!")
        return True

    except ImportError:
        return False
    except Exception as e:
        print(f"\nError during sounddevice test: {e}")
        return False


def test_with_pyaudio(device_id: Optional[int] = None) -> bool:
    """Test audio using PyAudio library."""
    try:
        import pyaudio
        import numpy as np

        print("\n" + "=" * 70)
        print("Testing with PyAudio library")
        print("=" * 70)

        p = pyaudio.PyAudio()

        # List available devices
        print("\nAvailable audio devices:")
        print("-" * 70)
        default_device = p.get_default_output_device_info()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxOutputChannels'] > 0:
                default_marker = " [DEFAULT]" if i == default_device['index'] else ""
                print(f"  [{i}] {dev['name']}{default_marker}")
                print(f"      Channels: {dev['maxOutputChannels']}, "
                      f"Sample Rate: {dev['defaultSampleRate']} Hz")
        print("-" * 70)

        # Select device
        if device_id is None:
            device_input = input("\nEnter device number (press Enter for default): ").strip()
            if device_input:
                device_id = int(device_input)
            else:
                device_id = default_device['index']

        selected_device = p.get_device_info_by_index(device_id)
        print(f"\nSelected device: {selected_device['name']}")

        sample_rate = int(selected_device['defaultSampleRate'])

        print("\n" + "=" * 70)
        print("PLAYING TEST TONES")
        print("=" * 70)
        print("\nPlease listen for the following tones on your headphones:")
        print("  1. 440 Hz (A4 - musical note A) for 2 seconds")
        print("  2. 880 Hz (A5 - one octave higher) for 2 seconds")
        print("\nEnsure your headphones are plugged into the 3.5mm jack!")
        input("\nPress Enter to start the test...")

        # Open stream
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sample_rate,
            output=True,
            output_device_index=device_id
        )

        # Play 440 Hz tone
        print("\nPlaying 440 Hz tone...")
        tone_440 = generate_sine_wave(440, 2.0, sample_rate)
        stream.write(tone_440.tobytes())
        time.sleep(0.5)

        # Play 880 Hz tone
        print("Playing 880 Hz tone...")
        tone_880 = generate_sine_wave(880, 2.0, sample_rate)
        stream.write(tone_880.tobytes())

        stream.stop_stream()
        stream.close()
        p.terminate()

        print("\nTest tones completed!")
        return True

    except ImportError:
        return False
    except Exception as e:
        print(f"\nError during PyAudio test: {e}")
        return False


def test_with_fallback() -> bool:
    """Test audio using system commands (fallback method)."""
    print("\n" + "=" * 70)
    print("Testing with system commands (fallback method)")
    print("=" * 70)
    print("\nPython audio libraries not found. Using system commands...")

    # Try speaker-test
    try:
        print("\nAttempting to use speaker-test utility...")
        print("You should hear pink noise from your headphones.")
        print("The test will run for 5 seconds.")
        input("\nPress Enter to start the test...")

        subprocess.run(
            ['speaker-test', '-t', 'sine', '-f', '440', '-l', '1'],
            timeout=3
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Try aplay with beep
    try:
        print("\nAttempting to use aplay with beep...")
        print("Generating a test beep file...")

        # Generate beep using sox if available
        subprocess.run(
            ['sox', '-n', '/tmp/test_beep.wav', 'synth', '2', 'sine', '440'],
            timeout=5,
            check=True
        )

        print("Playing beep through headphones...")
        input("\nPress Enter to play...")

        subprocess.run(['aplay', '/tmp/test_beep.wav'], timeout=5)
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        pass

    print("\nCould not find suitable audio playback tools.")
    return False


def show_troubleshooting_tips():
    """Display troubleshooting information."""
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING TIPS")
    print("=" * 70)

    print("\nIf you didn't hear any sound, try the following:\n")

    print("1. CHECK VOLUME LEVELS:")
    print("   - PulseAudio: pactl set-sink-volume @DEFAULT_SINK@ 50%")
    print("   - ALSA: amixer set Master 50%")
    print("   - Or use: alsamixer (interactive)")

    print("\n2. CHECK IF MUTED:")
    print("   - PulseAudio: pactl set-sink-mute @DEFAULT_SINK@ 0")
    print("   - ALSA: amixer set Master unmute")

    print("\n3. LIST AUDIO DEVICES:")
    print("   - ALSA: aplay -l")
    print("   - PulseAudio: pactl list sinks")

    print("\n4. CHECK HEADPHONE JACK DETECTION:")
    print("   - Some systems auto-switch when headphones are plugged in")
    print("   - Try unplugging and re-plugging the headphones")
    print("   - Check: pactl list sinks | grep -i analog")

    print("\n5. SELECT CORRECT OUTPUT:")
    print("   - PulseAudio: pactl set-default-sink <sink-name>")
    print("   - Check available sinks: pactl list short sinks")

    print("\n6. TEST WITH SYSTEM BEEP:")
    print("   - speaker-test -t sine -f 440 -l 1")
    print("   - aplay /usr/share/sounds/alsa/Front_Center.wav")

    print("\n7. CHECK KERNEL MESSAGES:")
    print("   - dmesg | grep -i audio")
    print("   - dmesg | grep -i sound")

    print("\n8. VERIFY AUDIO DRIVERS:")
    print("   - lsmod | grep snd")
    print("   - cat /proc/asound/cards")

    print("\n9. INSTALL REQUIRED LIBRARIES (if needed):")
    print("   - pip install sounddevice numpy")
    print("   - pip install pyaudio")
    print("   - apt install python3-sounddevice python3-numpy")

    print("\n10. ARCHITECTURE-SPECIFIC NOTES:")
    print("   - RISC-V: Ensure audio drivers are loaded (snd_soc_*)")
    print("   - ARM: Some boards need specific device tree overlays")
    print("   - Check board documentation for audio setup")

    print("\n" + "=" * 70)


def show_system_info():
    """Display relevant system audio information."""
    print("\n" + "=" * 70)
    print("SYSTEM AUDIO INFORMATION")
    print("=" * 70)

    # Current volume
    volume = get_current_volume()
    if volume:
        print("\nCurrent Volume:")
        print(volume)

    # Mute status
    if check_audio_muted():
        print("\n⚠ WARNING: Audio appears to be MUTED!")
        print("   Unmute with: pactl set-sink-mute @DEFAULT_SINK@ 0")
    else:
        print("\nMute Status: Not muted")

    # ALSA devices
    print("\nALSA Devices:")
    alsa_devices = list_alsa_devices()
    if alsa_devices:
        for line in alsa_devices[:10]:  # Show first 10 lines
            if line.strip():
                print(f"  {line}")
    else:
        print("  Could not retrieve ALSA devices")

    # PulseAudio devices
    print("\nPulseAudio Sinks:")
    pulse_devices = list_pulse_devices()
    if pulse_devices:
        for line in pulse_devices[:10]:  # Show first 10 lines
            if line.strip():
                print(f"  {line}")
    else:
        print("  PulseAudio not available or no sinks found")

    print("\n" + "=" * 70)


def main():
    """Main function to run headphone jack test."""
    print("=" * 70)
    print("HEADPHONE JACK TEST UTILITY")
    print("Linux Audio Output Testing Tool")
    print("=" * 70)

    # Check backend
    backend = check_audio_backend()
    print(f"\nDetected audio backend: {backend}")

    if backend == 'fallback':
        print("\n⚠ WARNING: No Python audio libraries found!")
        print("   For best results, install: pip install sounddevice numpy")

    # Show system info
    show_system_info()

    # Run test
    success = False

    if backend == 'sounddevice':
        success = test_with_sounddevice()
    elif backend == 'pyaudio':
        success = test_with_pyaudio()
    else:
        success = test_with_fallback()

    # Get user feedback
    print("\n" + "=" * 70)
    print("TEST RESULT")
    print("=" * 70)

    response = input("\nDid you hear the test tones in your headphones? (y/n): ").strip().lower()

    if response == 'y' or response == 'yes':
        print("\n✓ SUCCESS! Your headphone jack is working correctly.")
        print("  Audio output through 3.5mm jack is functional.")
        return 0
    else:
        print("\n✗ Test failed or sound not heard.")
        show_troubleshooting_tips()

        # Offer to show more help
        show_more = input("\nWould you like to see detailed device information? (y/n): ").strip().lower()
        if show_more == 'y' or show_more == 'yes':
            print("\nRunning detailed device scan...")
            subprocess.run(['aplay', '-L'], capture_output=False)

        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
