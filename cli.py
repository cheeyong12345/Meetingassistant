#!/usr/bin/env python3
"""
Meeting Assistant CLI
Command-line interface for the meeting assistant
"""

import click
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

from src.meeting import MeetingAssistant
from src.config import config

console = Console()

@click.group()
def cli():
    """Meeting Assistant - AI-powered meeting transcription and summarization"""
    pass

@cli.command()
def devices():
    """List available audio input devices"""
    assistant = MeetingAssistant()
    if not assistant.initialize():
        console.print("[red]Failed to initialize meeting assistant[/red]")
        return

    devices = assistant.audio_recorder.list_input_devices()

    table = Table(title="Available Audio Input Devices")
    table.add_column("Index", style="cyan")
    table.add_column("Device Name", style="magenta")
    table.add_column("Sample Rate", style="green")

    for device in devices:
        table.add_row(
            str(device['index']),
            device['name'],
            f"{device['sample_rate']} Hz"
        )

    console.print(table)
    assistant.cleanup()

@cli.command()
def status():
    """Show current engine status"""
    assistant = MeetingAssistant()
    if not assistant.initialize():
        console.print("[red]Failed to initialize meeting assistant[/red]")
        return

    status_info = assistant.get_engine_status()

    # STT Engine Status
    stt_info = status_info['stt']
    console.print(Panel(
        f"Engine: {stt_info['name']}\n"
        f"Initialized: {stt_info['initialized']}\n"
        f"Config: {stt_info.get('config', {})}",
        title="STT Engine Status",
        border_style="blue"
    ))

    # Summarization Engine Status
    sum_info = status_info['summarization']
    console.print(Panel(
        f"Engine: {sum_info['name']}\n"
        f"Initialized: {sum_info['initialized']}\n"
        f"Config: {sum_info.get('config', {})}",
        title="Summarization Engine Status",
        border_style="green"
    ))

    assistant.cleanup()

@cli.command()
@click.option('--stt-engine', default=None, help='STT engine to use (whisper, vosk)')
@click.option('--sum-engine', default=None, help='Summarization engine to use (qwen3, ollama)')
def engines(stt_engine, sum_engine):
    """List available engines or switch engines"""
    assistant = MeetingAssistant()
    if not assistant.initialize():
        console.print("[red]Failed to initialize meeting assistant[/red]")
        return

    if stt_engine:
        if assistant.switch_stt_engine(stt_engine):
            console.print(f"[green]Switched to STT engine: {stt_engine}[/green]")
        else:
            console.print(f"[red]Failed to switch to STT engine: {stt_engine}[/red]")

    if sum_engine:
        if assistant.switch_summarization_engine(sum_engine):
            console.print(f"[green]Switched to summarization engine: {sum_engine}[/green]")
        else:
            console.print(f"[red]Failed to switch to summarization engine: {sum_engine}[/red]")

    if not stt_engine and not sum_engine:
        # List available engines
        console.print("[bold]Available STT Engines:[/bold]")
        for engine in assistant.get_available_stt_engines():
            console.print(f"  • {engine}")

        console.print("\n[bold]Available Summarization Engines:[/bold]")
        for engine in assistant.get_available_summarization_engines():
            console.print(f"  • {engine}")

    assistant.cleanup()

@cli.command()
@click.option('--title', '-t', help='Meeting title')
@click.option('--participants', '-p', help='Comma-separated list of participants')
@click.option('--device', '-d', type=int, help='Audio input device index')
def record(title, participants, device):
    """Start a new meeting recording"""
    assistant = MeetingAssistant()
    if not assistant.initialize():
        console.print("[red]Failed to initialize meeting assistant[/red]")
        return

    # Set audio device if specified
    if device is not None:
        config.audio.input_device = device
        assistant.audio_recorder.config['input_device'] = device

    # Parse participants
    participant_list = []
    if participants:
        participant_list = [p.strip() for p in participants.split(',')]

    # Start meeting
    result = assistant.start_meeting(title, participant_list)

    if not result['success']:
        console.print(f"[red]Failed to start meeting: {result.get('error', 'Unknown error')}[/red]")
        assistant.cleanup()
        return

    console.print(f"[green]Meeting started: {result['title']}[/green]")
    console.print("[yellow]Press Ctrl+C to stop recording[/yellow]")

    try:
        # Live status display
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                status = assistant.get_current_meeting_status()
                if not status['active']:
                    break

                duration = status['duration']
                minutes = duration // 60
                seconds = duration % 60

                panel = Panel(
                    f"Meeting: {status['title']}\n"
                    f"Duration: {minutes:02d}:{seconds:02d}\n"
                    f"Transcript Length: {status['transcript_length']} characters\n"
                    f"Participants: {', '.join(status['participants']) if status['participants'] else 'None'}",
                    title="[bold green]Recording in Progress[/bold green]",
                    border_style="green"
                )
                live.update(panel)
                time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping recording...[/yellow]")

    # Stop meeting
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing meeting...", total=None)

        result = assistant.stop_meeting()

        if result['success']:
            console.print(f"\n[green]Meeting saved successfully![/green]")
            console.print(f"Meeting ID: {result['meeting_id']}")
            console.print(f"Audio file: {result.get('audio_file', 'N/A')}")
            console.print(f"Meeting file: {result.get('meeting_file', 'N/A')}")

            if 'summary' in result:
                summary = result['summary']
                console.print(Panel(
                    summary.get('summary', 'No summary available'),
                    title="Meeting Summary",
                    border_style="cyan"
                ))

                if summary.get('key_points'):
                    console.print("\n[bold]Key Points:[/bold]")
                    for point in summary['key_points']:
                        console.print(f"  • {point}")

                if summary.get('action_items'):
                    console.print("\n[bold]Action Items:[/bold]")
                    for item in summary['action_items']:
                        console.print(f"  • {item}")
        else:
            console.print(f"[red]Failed to save meeting: {result.get('error', 'Unknown error')}[/red]")

    assistant.cleanup()

@cli.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--engine', help='STT engine to use')
def transcribe(audio_file, engine):
    """Transcribe an audio file"""
    assistant = MeetingAssistant()
    if not assistant.initialize():
        console.print("[red]Failed to initialize meeting assistant[/red]")
        return

    if engine and not assistant.switch_stt_engine(engine):
        console.print(f"[red]Failed to switch to engine: {engine}[/red]")
        assistant.cleanup()
        return

    console.print(f"[yellow]Transcribing: {audio_file}[/yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Transcribing audio...", total=None)

        result = assistant.transcribe_audio_file(audio_file)

        if result.get('text'):
            console.print(Panel(
                result['text'],
                title="Transcription",
                border_style="green"
            ))

            # Show additional info
            if 'confidence' in result:
                console.print(f"Confidence: {result['confidence']:.2f}")
            if 'language' in result:
                console.print(f"Language: {result['language']}")
        else:
            console.print(f"[red]Transcription failed: {result.get('error', 'Unknown error')}[/red]")

    assistant.cleanup()

@cli.command()
@click.argument('text_file', type=click.Path(exists=True))
@click.option('--engine', help='Summarization engine to use')
def summarize(text_file, engine):
    """Summarize text from a file"""
    assistant = MeetingAssistant()
    if not assistant.initialize():
        console.print("[red]Failed to initialize meeting assistant[/red]")
        return

    if engine and not assistant.switch_summarization_engine(engine):
        console.print(f"[red]Failed to switch to engine: {engine}[/red]")
        assistant.cleanup()
        return

    # Read text file
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        console.print(f"[red]Failed to read file: {e}[/red]")
        assistant.cleanup()
        return

    console.print(f"[yellow]Summarizing: {text_file}[/yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating summary...", total=None)

        result = assistant.summarize_text(text)

        if result.get('success'):
            console.print(Panel(
                result.get('summary', 'No summary available'),
                title="Summary",
                border_style="cyan"
            ))

            if result.get('key_points'):
                console.print("\n[bold]Key Points:[/bold]")
                for point in result['key_points']:
                    console.print(f"  • {point}")

            if result.get('action_items'):
                console.print("\n[bold]Action Items:[/bold]")
                for item in result['action_items']:
                    console.print(f"  • {item}")
        else:
            console.print(f"[red]Summarization failed: {result.get('error', 'Unknown error')}[/red]")

    assistant.cleanup()

@cli.command()
def test():
    """Test microphone and engines"""
    console.print("[yellow]Testing Meeting Assistant...[/yellow]")

    assistant = MeetingAssistant()
    if not assistant.initialize():
        console.print("[red]Failed to initialize meeting assistant[/red]")
        return

    # Test audio devices
    devices = assistant.audio_recorder.list_input_devices()
    console.print(f"[green]Found {len(devices)} audio input devices[/green]")

    # Test engines
    status = assistant.get_engine_status()
    stt_status = status['stt']['initialized']
    sum_status = status['summarization']['initialized']

    console.print(f"STT Engine: [{'green' if stt_status else 'red'}]{'Ready' if stt_status else 'Failed'}[/]")
    console.print(f"Summarization Engine: [{'green' if sum_status else 'red'}]{'Ready' if sum_status else 'Failed'}[/]")

    if stt_status and sum_status:
        console.print("[green]All systems ready![/green]")
    else:
        console.print("[red]Some systems failed to initialize[/red]")

    assistant.cleanup()

if __name__ == '__main__':
    cli()