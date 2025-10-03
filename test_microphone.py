#!/usr/bin/env python3
"""
Microphone Testing Script
Tests local device microphone with support for multiple audio libraries.
Compatible with RISC-V, ARM, and x86 Linux systems.
"""

import sys
import time
import wave
import struct
from pathlib import Path
from typing import Optional, Tuple, List
import platform


class MicrophoneTest:
    """Microphone testing utility with multiple backend support."""

    def __init__(self):
        self.audio_backend = None
        self.sample_rate = 44100
        self.channels = 1
        self.chunk_size = 1024
        self.record_duration = 5
        self.output_file = "test_recording.wav"

    def print_system_info(self):
        """Display system information."""
        print("\n" + "="*60)
        print("MICROPHONE TEST UTILITY")
        print("="*60)
        print(f"System: {platform.system()}")
        print(f"Machine: {platform.machine()}")
        print(f"Platform: {platform.platform()}")
        print("="*60 + "\n")

    def check_available_libraries(self) -> str:
        """Check which audio library is available."""
        print("Checking available audio libraries...")

        # Try sounddevice first (generally more compatible)
        try:
            import sounddevice as sd
            import numpy as np
            print("✓ sounddevice library found")
            return "sounddevice"
        except ImportError:
            print("✗ sounddevice not available")

        # Try PyAudio
        try:
            import pyaudio
            print("✓ PyAudio library found")
            return "pyaudio"
        except ImportError:
            print("✗ PyAudio not available")

        return None

    def install_instructions(self):
        """Display installation instructions for audio libraries."""
        print("\n" + "!"*60)
        print("ERROR: No audio library found!")
        print("!"*60)
        print("\nPlease install one of the following:\n")
        print("Option 1 - sounddevice (Recommended):")
        print("  pip install sounddevice numpy scipy")
        print("  or")
        print("  sudo apt-get install python3-sounddevice python3-numpy\n")
        print("Option 2 - PyAudio:")
        print("  pip install pyaudio")
        print("  or")
        print("  sudo apt-get install python3-pyaudio\n")
        print("For RISC-V/ARM systems, you may also need:")
        print("  sudo apt-get install portaudio19-dev python3-dev")
        print("  pip install pyaudio --no-binary :all:")
        print("="*60 + "\n")

    def list_devices_sounddevice(self):
        """List audio devices using sounddevice."""
        import sounddevice as sd

        print("\n" + "-"*60)
        print("AVAILABLE AUDIO INPUT DEVICES (sounddevice)")
        print("-"*60)

        devices = sd.query_devices()
        default_input = sd.default.device[0]

        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                marker = " [DEFAULT]" if i == default_input else ""
                print(f"\nDevice {i}: {device['name']}{marker}")
                print(f"  Input Channels: {device['max_input_channels']}")
                print(f"  Sample Rate: {device['default_samplerate']} Hz")
                print(f"  Host API: {sd.query_hostapis(device['hostapi'])['name']}")

        print("-"*60 + "\n")
        return default_input

    def list_devices_pyaudio(self):
        """List audio devices using PyAudio."""
        import pyaudio

        print("\n" + "-"*60)
        print("AVAILABLE AUDIO INPUT DEVICES (PyAudio)")
        print("-"*60)

        p = pyaudio.PyAudio()
        default_input = p.get_default_input_device_info()['index']

        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                marker = " [DEFAULT]" if i == default_input else ""
                print(f"\nDevice {i}: {info['name']}{marker}")
                print(f"  Input Channels: {info['maxInputChannels']}")
                print(f"  Sample Rate: {int(info['defaultSampleRate'])} Hz")
                print(f"  Host API: {p.get_host_api_info_by_index(info['hostapi'])['name']}")

        p.terminate()
        print("-"*60 + "\n")
        return default_input

    def get_audio_level(self, data, backend: str) -> float:
        """Calculate audio level from data."""
        if backend == "sounddevice":
            import numpy as np
            # Data is already numpy array
            return float(np.abs(data).mean())
        else:  # pyaudio
            # Convert bytes to amplitude
            import array
            count = len(data) // 2
            shorts = struct.unpack(f"{count}h", data)
            return sum(abs(s) for s in shorts) / count if count > 0 else 0

    def display_audio_level(self, level: float, backend: str, max_level: float = None):
        """Display audio level as a visual bar."""
        if backend == "sounddevice":
            # Normalize for sounddevice (0.0 to 1.0 range)
            normalized = min(level * 10, 1.0)
        else:  # pyaudio
            # Normalize for pyaudio (16-bit audio)
            max_val = max_level if max_level else 32768
            normalized = min(level / max_val, 1.0)

        bar_length = 50
        filled = int(normalized * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        percent = int(normalized * 100)

        # Use carriage return to update same line
        sys.stdout.write(f"\rAudio Level: [{bar}] {percent:3d}%")
        sys.stdout.flush()

    def record_sounddevice(self, device_id: Optional[int] = None) -> bool:
        """Record audio using sounddevice."""
        import sounddevice as sd
        import numpy as np
        from scipy.io.wavfile import write

        print("\n" + "="*60)
        print(f"RECORDING FOR {self.record_duration} SECONDS...")
        print("="*60)
        print("Speak into your microphone!\n")

        try:
            # Record audio
            recording_data = []

            def callback(indata, frames, time_info, status):
                if status:
                    print(f"\nStatus: {status}")
                recording_data.append(indata.copy())
                level = self.get_audio_level(indata, "sounddevice")
                self.display_audio_level(level, "sounddevice")

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                device=device_id,
                blocksize=self.chunk_size
            ):
                sd.sleep(self.record_duration * 1000)

            print("\n\nRecording complete!")

            # Concatenate and save
            recording = np.concatenate(recording_data, axis=0)
            write(self.output_file, self.sample_rate, recording)

            return True

        except Exception as e:
            print(f"\n\nERROR during recording: {e}")
            return False

    def record_pyaudio(self, device_id: Optional[int] = None) -> bool:
        """Record audio using PyAudio."""
        import pyaudio

        print("\n" + "="*60)
        print(f"RECORDING FOR {self.record_duration} SECONDS...")
        print("="*60)
        print("Speak into your microphone!\n")

        p = pyaudio.PyAudio()

        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_id,
                frames_per_buffer=self.chunk_size
            )

            frames = []
            num_chunks = int(self.sample_rate / self.chunk_size * self.record_duration)

            for _ in range(num_chunks):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                level = self.get_audio_level(data, "pyaudio")
                self.display_audio_level(level, "pyaudio")

            print("\n\nRecording complete!")

            stream.stop_stream()
            stream.close()

            # Save to WAV file
            wf = wave.open(self.output_file, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()

            return True

        except Exception as e:
            print(f"\n\nERROR during recording: {e}")
            return False
        finally:
            p.terminate()

    def verify_recording(self) -> bool:
        """Verify the recording was successful."""
        print("\n" + "-"*60)
        print("VERIFYING RECORDING")
        print("-"*60)

        try:
            file_path = Path(self.output_file)

            if not file_path.exists():
                print("✗ Recording file not found!")
                return False

            file_size = file_path.stat().st_size
            print(f"✓ File exists: {self.output_file}")
            print(f"✓ File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

            # Check WAV file
            with wave.open(str(file_path), 'rb') as wf:
                n_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                duration = n_frames / framerate

                print(f"✓ Channels: {n_channels}")
                print(f"✓ Sample Width: {sample_width} bytes")
                print(f"✓ Sample Rate: {framerate} Hz")
                print(f"✓ Duration: {duration:.2f} seconds")
                print(f"✓ Total Frames: {n_frames:,}")

            if file_size < 1000:
                print("\n⚠ WARNING: File size is very small. Recording may have failed.")
                return False

            print("\n✓ Recording verification PASSED!")
            print("-"*60 + "\n")
            return True

        except Exception as e:
            print(f"✗ Error verifying recording: {e}")
            return False

    def run(self):
        """Run the complete microphone test."""
        self.print_system_info()

        # Check for available libraries
        backend = self.check_available_libraries()

        if backend is None:
            self.install_instructions()
            return 1

        print(f"\nUsing audio backend: {backend}\n")
        self.audio_backend = backend

        # List available devices
        try:
            if backend == "sounddevice":
                default_device = self.list_devices_sounddevice()
            else:
                default_device = self.list_devices_pyaudio()
        except Exception as e:
            print(f"ERROR listing devices: {e}")
            return 1

        # Perform recording
        try:
            if backend == "sounddevice":
                success = self.record_sounddevice()
            else:
                success = self.record_pyaudio()

            if not success:
                print("\n✗ Recording failed!")
                return 1

        except KeyboardInterrupt:
            print("\n\nRecording interrupted by user.")
            return 1
        except Exception as e:
            print(f"\nUnexpected error during recording: {e}")
            import traceback
            traceback.print_exc()
            return 1

        # Verify recording
        if not self.verify_recording():
            print("✗ Recording verification failed!")
            return 1

        # Success
        print("="*60)
        print("MICROPHONE TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\nRecording saved to: {Path(self.output_file).absolute()}")
        print("\nYou can play it back with:")
        print(f"  aplay {self.output_file}")
        print(f"  or")
        print(f"  ffplay {self.output_file}")
        print("\n" + "="*60 + "\n")

        return 0


def main():
    """Main entry point."""
    tester = MicrophoneTest()
    return tester.run()


if __name__ == "__main__":
    sys.exit(main())
