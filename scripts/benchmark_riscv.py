#!/usr/bin/env python3
"""
RISC-V/NPU Performance Benchmarking Script
Measures inference performance on different hardware backends
"""

import os
import sys
import time
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.hardware import get_hardware_detector


class PerformanceBenchmark:
    """Benchmark inference performance on different backends"""

    def __init__(self):
        self.hardware = get_hardware_detector()
        self.results = {}

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")

    def print_result(self, name: str, value: str):
        """Print formatted result"""
        print(f"  {name:40s}: {value}")

    def get_system_info(self) -> Dict:
        """Get system information"""
        self.print_header("System Information")

        info = self.hardware.get_system_info()

        self.print_result("Architecture", info['architecture'])
        self.print_result("SoC Type", info['soc_type'])
        self.print_result("CPU Count", str(info['cpu_info']['cpu_count']))

        if info['cpu_info'].get('max_freq_mhz'):
            self.print_result("CPU Max Freq", f"{info['cpu_info']['max_freq_mhz']:.0f} MHz")

        # NPU Info
        npu_info = info['npu_info']
        if npu_info['available']:
            self.print_result("NPU", npu_info['description'])
            self.print_result("NPU TOPS", f"{npu_info['tops']:.1f}")
        else:
            self.print_result("NPU", "Not Available")

        self.print_result("Optimal Device", info['optimal_device'])

        return info

    def benchmark_whisper(self, model_size: str = "base", iterations: int = 5) -> Dict:
        """Benchmark Whisper STT performance

        Args:
            model_size: Whisper model size
            iterations: Number of test iterations

        Returns:
            Benchmark results dict
        """
        self.print_header(f"Benchmarking Whisper ({model_size})")

        try:
            from src.stt.whisper_engine import WhisperEngine

            # Create dummy audio (30 seconds of silence)
            sample_rate = 16000
            duration = 30  # seconds
            audio_data = np.zeros(sample_rate * duration, dtype=np.float32)

            # Test PyTorch backend
            results = {}
            config_cpu = {
                'model_size': model_size,
                'device': 'cpu',
                'use_npu': False
            }

            print("Testing CPU backend...")
            engine = WhisperEngine(config_cpu)

            if engine.initialize():
                times = []
                for i in range(iterations):
                    start = time.time()
                    result = engine.transcribe(audio_data)
                    elapsed = time.time() - start
                    times.append(elapsed)
                    print(f"  Iteration {i+1}/{iterations}: {elapsed:.2f}s")

                avg_time = np.mean(times)
                std_time = np.std(times)

                results['cpu'] = {
                    'avg_time': avg_time,
                    'std_time': std_time,
                    'throughput': duration / avg_time  # audio seconds per real second
                }

                self.print_result("CPU Avg Time", f"{avg_time:.2f}s ± {std_time:.2f}s")
                self.print_result("CPU Throughput", f"{results['cpu']['throughput']:.2f}x realtime")

                engine.cleanup()
            else:
                print("  ⚠️  Failed to initialize CPU backend")

            # Test NPU backend if available
            if self.hardware.supports_npu_acceleration():
                print("\nTesting NPU backend...")
                config_npu = {
                    'model_size': model_size,
                    'device': 'cpu',
                    'use_npu': True
                }

                engine = WhisperEngine(config_npu)
                if engine.initialize() and engine.using_npu:
                    times = []
                    for i in range(iterations):
                        start = time.time()
                        result = engine.transcribe(audio_data)
                        elapsed = time.time() - start
                        times.append(elapsed)
                        print(f"  Iteration {i+1}/{iterations}: {elapsed:.2f}s")

                    avg_time = np.mean(times)
                    std_time = np.std(times)

                    results['npu'] = {
                        'avg_time': avg_time,
                        'std_time': std_time,
                        'throughput': duration / avg_time
                    }

                    self.print_result("NPU Avg Time", f"{avg_time:.2f}s ± {std_time:.2f}s")
                    self.print_result("NPU Throughput", f"{results['npu']['throughput']:.2f}x realtime")

                    # Calculate speedup
                    if 'cpu' in results:
                        speedup = results['cpu']['avg_time'] / results['npu']['avg_time']
                        self.print_result("NPU Speedup", f"{speedup:.2f}x")
                        results['npu']['speedup'] = speedup

                    engine.cleanup()
                else:
                    print("  ⚠️  NPU backend not available or model not converted")

            return results

        except ImportError as e:
            print(f"  ❌ Whisper not available: {e}")
            return {}
        except Exception as e:
            print(f"  ❌ Benchmark failed: {e}")
            return {}

    def benchmark_qwen(self, model_name: str = "Qwen/Qwen2.5-3B-Instruct", iterations: int = 3) -> Dict:
        """Benchmark Qwen summarization performance

        Args:
            model_name: Qwen model name
            iterations: Number of test iterations

        Returns:
            Benchmark results dict
        """
        self.print_header(f"Benchmarking Qwen")

        try:
            from src.summarization.qwen_engine import QwenEngine

            # Test prompt
            test_text = """
            This is a test meeting transcript. We discussed several important topics today.
            First, we reviewed the project timeline and identified key milestones.
            Second, we discussed resource allocation and team assignments.
            Third, we addressed technical challenges and proposed solutions.
            Finally, we set action items for the next sprint.
            """ * 10  # Make it longer for realistic test

            results = {}

            # Test CPU backend
            config_cpu = {
                'model_name': model_name,
                'device': 'cpu',
                'use_npu': False,
                'max_tokens': 500
            }

            print("Testing CPU backend...")
            engine = QwenEngine(config_cpu)

            if engine.initialize():
                times = []
                for i in range(iterations):
                    start = time.time()
                    result = engine.summarize(test_text)
                    elapsed = time.time() - start
                    times.append(elapsed)
                    print(f"  Iteration {i+1}/{iterations}: {elapsed:.2f}s")

                avg_time = np.mean(times)
                std_time = np.std(times)

                results['cpu'] = {
                    'avg_time': avg_time,
                    'std_time': std_time,
                    'tokens_per_sec': 500 / avg_time  # approximate
                }

                self.print_result("CPU Avg Time", f"{avg_time:.2f}s ± {std_time:.2f}s")
                self.print_result("CPU Tokens/sec", f"{results['cpu']['tokens_per_sec']:.1f}")

                engine.cleanup()
            else:
                print("  ⚠️  Failed to initialize CPU backend")

            # Test NPU backend if available
            if self.hardware.supports_npu_acceleration():
                print("\nTesting NPU backend...")
                config_npu = {
                    'model_name': model_name,
                    'device': 'cpu',
                    'use_npu': True,
                    'max_tokens': 500
                }

                engine = QwenEngine(config_npu)
                if engine.initialize() and engine.using_npu:
                    times = []
                    for i in range(iterations):
                        start = time.time()
                        result = engine.summarize(test_text)
                        elapsed = time.time() - start
                        times.append(elapsed)
                        print(f"  Iteration {i+1}/{iterations}: {elapsed:.2f}s")

                    avg_time = np.mean(times)
                    std_time = np.std(times)

                    results['npu'] = {
                        'avg_time': avg_time,
                        'std_time': std_time,
                        'tokens_per_sec': 500 / avg_time
                    }

                    self.print_result("NPU Avg Time", f"{avg_time:.2f}s ± {std_time:.2f}s")
                    self.print_result("NPU Tokens/sec", f"{results['npu']['tokens_per_sec']:.1f}")

                    # Calculate speedup
                    if 'cpu' in results:
                        speedup = results['cpu']['avg_time'] / results['npu']['avg_time']
                        self.print_result("NPU Speedup", f"{speedup:.2f}x")
                        results['npu']['speedup'] = speedup

                    engine.cleanup()
                else:
                    print("  ⚠️  NPU backend not available or model not converted")

            return results

        except ImportError as e:
            print(f"  ❌ Qwen not available: {e}")
            return {}
        except Exception as e:
            print(f"  ❌ Benchmark failed: {e}")
            return {}

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file"""
        output_dir = Path("./benchmark_results")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / filename

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Results saved to: {output_file}")

    def run_full_benchmark(self, whisper_size: str = "base", iterations: int = 5):
        """Run complete benchmark suite"""
        print("\n" + "="*60)
        print("  RISC-V / NPU Performance Benchmark")
        print("="*60)

        # System info
        self.results['system'] = self.get_system_info()

        # Benchmark Whisper
        self.results['whisper'] = self.benchmark_whisper(whisper_size, iterations)

        # Benchmark Qwen (fewer iterations as it's slower)
        self.results['qwen'] = self.benchmark_qwen(iterations=min(iterations, 3))

        # Summary
        self.print_header("Benchmark Summary")

        if self.results.get('whisper') and 'npu' in self.results['whisper']:
            whisper_speedup = self.results['whisper']['npu'].get('speedup', 0)
            self.print_result("Whisper NPU Speedup", f"{whisper_speedup:.2f}x")

        if self.results.get('qwen') and 'npu' in self.results['qwen']:
            qwen_speedup = self.results['qwen']['npu'].get('speedup', 0)
            self.print_result("Qwen NPU Speedup", f"{qwen_speedup:.2f}x")

        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.save_results(f"benchmark_{timestamp}.json")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Benchmark Meeting Assistant performance on RISC-V/NPU",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--whisper-size', '-w',
        default='base',
        choices=['tiny', 'base', 'small', 'medium'],
        help='Whisper model size (default: base)'
    )

    parser.add_argument(
        '--iterations', '-i',
        type=int,
        default=5,
        help='Number of iterations per test (default: 5)'
    )

    parser.add_argument(
        '--whisper-only',
        action='store_true',
        help='Benchmark Whisper only'
    )

    parser.add_argument(
        '--qwen-only',
        action='store_true',
        help='Benchmark Qwen only'
    )

    args = parser.parse_args()

    benchmark = PerformanceBenchmark()

    if args.whisper_only:
        benchmark.results['system'] = benchmark.get_system_info()
        benchmark.results['whisper'] = benchmark.benchmark_whisper(args.whisper_size, args.iterations)
        benchmark.save_results()
    elif args.qwen_only:
        benchmark.results['system'] = benchmark.get_system_info()
        benchmark.results['qwen'] = benchmark.benchmark_qwen(iterations=args.iterations)
        benchmark.save_results()
    else:
        benchmark.run_full_benchmark(args.whisper_size, args.iterations)


if __name__ == "__main__":
    main()
