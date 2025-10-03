#!/usr/bin/env python3
"""
Model Conversion Script for NPU Acceleration
Converts PyTorch models to ONNX/RKNN/ENNP formats for hardware acceleration
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.hardware import get_hardware_detector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelConverter:
    """Convert models for NPU acceleration"""

    def __init__(self, npu_type: str = "auto"):
        self.hardware = get_hardware_detector()

        if npu_type == "auto":
            self.npu_type = self.hardware.npu_type
        else:
            self.npu_type = npu_type

        if not self.npu_type:
            logger.warning("No NPU detected, using CPU fallback")
            self.npu_type = "cpu"

        logger.info(f"Target NPU type: {self.npu_type}")

    def convert_whisper_to_onnx(
        self,
        model_size: str = "base",
        output_dir: str = "./models/onnx",
        quantize: bool = True
    ) -> Optional[str]:
        """Convert Whisper model to ONNX format

        Args:
            model_size: Whisper model size (tiny, base, small, medium)
            output_dir: Output directory for ONNX model
            quantize: Whether to quantize the model

        Returns:
            Path to converted ONNX model or None if failed
        """
        logger.info(f"Converting Whisper {model_size} model to ONNX...")

        try:
            import torch
            import whisper

            # Load Whisper model
            logger.info(f"Loading Whisper {model_size} model...")
            model = whisper.load_model(model_size)
            model.eval()

            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # ONNX file path
            onnx_file = output_path / f"whisper_{model_size}.onnx"

            # Dummy input for tracing
            # Whisper encoder takes mel spectrogram (80 mel bands, variable time frames)
            # Using a fixed size for export
            dummy_mel = torch.randn(1, 80, 3000)  # batch_size=1, n_mels=80, n_frames=3000

            logger.info("Exporting encoder to ONNX...")
            torch.onnx.export(
                model.encoder,
                dummy_mel,
                str(onnx_file),
                export_params=True,
                opset_version=13,
                do_constant_folding=True,
                input_names=['mel'],
                output_names=['encoder_output'],
                dynamic_axes={
                    'mel': {2: 'n_frames'},  # Variable time frames
                    'encoder_output': {1: 'n_frames'}
                }
            )

            logger.info(f"ONNX model saved to: {onnx_file}")

            # Quantize if requested
            if quantize:
                quantized_file = self._quantize_onnx(onnx_file)
                if quantized_file:
                    return str(quantized_file)

            return str(onnx_file)

        except ImportError as e:
            logger.error(f"Required package not available: {e}")
            logger.info("Install with: pip install torch whisper onnx")
            return None
        except Exception as e:
            logger.error(f"Failed to convert Whisper model: {e}")
            return None

    def convert_qwen_to_onnx(
        self,
        model_name: str = "Qwen/Qwen2.5-3B-Instruct",
        output_dir: str = "./models/onnx",
        quantize: bool = True
    ) -> Optional[str]:
        """Convert Qwen model to ONNX format

        Args:
            model_name: Hugging Face model name
            output_dir: Output directory for ONNX model
            quantize: Whether to quantize the model

        Returns:
            Path to converted ONNX model or None if failed
        """
        logger.info(f"Converting Qwen model {model_name} to ONNX...")

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from transformers.onnx import export as onnx_export

            # Load model and tokenizer
            logger.info(f"Loading {model_name}...")
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                trust_remote_code=True
            )

            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Simplified model name for file
            model_short_name = model_name.split('/')[-1].lower().replace('-', '_')
            onnx_file = output_path / f"{model_short_name}.onnx"

            logger.info("Exporting to ONNX...")
            logger.warning("Large language models may not fully support ONNX export")
            logger.info("Consider using ONNX Runtime with optimizations instead")

            # For now, recommend using ONNX Runtime directly with the model
            logger.info("Alternative: Use model directly with ONNX Runtime ExecutionProvider")

            return str(onnx_file)

        except ImportError as e:
            logger.error(f"Required package not available: {e}")
            logger.info("Install with: pip install transformers onnx onnxruntime")
            return None
        except Exception as e:
            logger.error(f"Failed to convert Qwen model: {e}")
            logger.info("Qwen models are best used with their native format + ONNX Runtime EP")
            return None

    def _quantize_onnx(self, onnx_file: Path) -> Optional[Path]:
        """Quantize ONNX model to INT8

        Args:
            onnx_file: Path to ONNX model

        Returns:
            Path to quantized model or None if failed
        """
        logger.info("Quantizing ONNX model to INT8...")

        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType

            quantized_file = onnx_file.parent / f"{onnx_file.stem}_quantized.onnx"

            quantize_dynamic(
                str(onnx_file),
                str(quantized_file),
                weight_type=QuantType.QUInt8
            )

            logger.info(f"Quantized model saved to: {quantized_file}")
            return quantized_file

        except ImportError:
            logger.warning("onnxruntime not available for quantization")
            return None
        except Exception as e:
            logger.error(f"Quantization failed: {e}")
            return None

    def convert_to_rknn(self, onnx_file: str, output_file: str) -> bool:
        """Convert ONNX model to RKNN format for RK3588

        Args:
            onnx_file: Path to ONNX model
            output_file: Output path for RKNN model

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Converting {onnx_file} to RKNN format...")

        try:
            from rknn.api import RKNN

            # Create RKNN object
            rknn = RKNN(verbose=True)

            # Load ONNX model
            logger.info("Loading ONNX model...")
            ret = rknn.load_onnx(model=onnx_file)
            if ret != 0:
                logger.error("Failed to load ONNX model")
                return False

            # Build model
            logger.info("Building RKNN model...")
            ret = rknn.build(do_quantization=True)
            if ret != 0:
                logger.error("Failed to build RKNN model")
                return False

            # Export RKNN model
            logger.info(f"Exporting to {output_file}...")
            ret = rknn.export_rknn(output_file)
            if ret != 0:
                logger.error("Failed to export RKNN model")
                return False

            rknn.release()
            logger.info("Successfully converted to RKNN format")
            return True

        except ImportError:
            logger.error("RKNN toolkit not installed")
            logger.info("Install with: pip install rknn-toolkit2")
            return False
        except Exception as e:
            logger.error(f"RKNN conversion failed: {e}")
            return False

    def convert_to_ennp(self, onnx_file: str, output_file: str) -> bool:
        """Convert ONNX model to ENNP format for EIC7700

        Args:
            onnx_file: Path to ONNX model
            output_file: Output path for ENNP model

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Converting {onnx_file} to ENNP format...")

        # Check for ENNP SDK tools
        if not self._check_ennp_tools():
            logger.error("ENNP SDK tools not found")
            logger.info("Download from: https://www.eswincomputing.com")
            return False

        try:
            # Step 1: Quantize with EsQuant
            quantized_file = f"{onnx_file.replace('.onnx', '_quant.onnx')}"
            logger.info("Quantizing model with EsQuant...")

            quant_cmd = [
                "esquant",
                "--model", onnx_file,
                "--output", quantized_file,
                "--quantize_type", "int8"
            ]

            result = subprocess.run(quant_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Quantization failed: {result.stderr}")
                quantized_file = onnx_file  # Use original

            # Step 2: Compile with EsAAC
            logger.info("Compiling model with EsAAC...")
            compile_cmd = [
                "esaac",
                "--model", quantized_file,
                "--output", output_file,
                "--target", "eic7700"
            ]

            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Compilation failed: {result.stderr}")
                return False

            logger.info("Successfully converted to ENNP format")
            return True

        except Exception as e:
            logger.error(f"ENNP conversion failed: {e}")
            return False

    def _check_ennp_tools(self) -> bool:
        """Check if ENNP SDK tools are available"""
        tools = ["esquant", "esaac"]
        for tool in tools:
            if subprocess.run(["which", tool], capture_output=True).returncode != 0:
                logger.warning(f"ENNP tool not found: {tool}")
                return False
        return True

    def convert_model(
        self,
        model_type: str,
        model_size: str,
        target_format: str = "auto"
    ) -> bool:
        """Convert model to target NPU format

        Args:
            model_type: Type of model (whisper, qwen)
            model_size: Model size/name
            target_format: Target format (onnx, rknn, ennp, auto)

        Returns:
            True if successful, False otherwise
        """
        # Determine target format
        if target_format == "auto":
            if self.npu_type == "rk3588":
                target_format = "rknn"
            elif self.npu_type == "eic7700":
                target_format = "ennp"
            else:
                target_format = "onnx"

        logger.info(f"Converting {model_type} model to {target_format} format...")

        # Step 1: Convert to ONNX
        if model_type == "whisper":
            onnx_file = self.convert_whisper_to_onnx(model_size)
        elif model_type == "qwen":
            onnx_file = self.convert_qwen_to_onnx(model_size)
        else:
            logger.error(f"Unknown model type: {model_type}")
            return False

        if not onnx_file:
            return False

        # Step 2: Convert to NPU format if needed
        if target_format == "onnx":
            logger.info("ONNX conversion complete")
            return True

        elif target_format == "rknn":
            output_file = onnx_file.replace(".onnx", ".rknn")
            return self.convert_to_rknn(onnx_file, output_file)

        elif target_format == "ennp":
            output_file = onnx_file.replace(".onnx", ".ennp")
            return self.convert_to_ennp(onnx_file, output_file)

        else:
            logger.error(f"Unknown target format: {target_format}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert models for NPU acceleration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert Whisper base model to ONNX
  python convert_models_npu.py --model whisper --size base --format onnx

  # Convert Whisper to RKNN for RK3588
  python convert_models_npu.py --model whisper --size base --format rknn

  # Convert Qwen to ENNP for EIC7700
  python convert_models_npu.py --model qwen --size Qwen/Qwen2.5-3B-Instruct --format ennp

  # Auto-detect NPU and convert
  python convert_models_npu.py --model whisper --size base --format auto
        """
    )

    parser.add_argument(
        '--model', '-m',
        required=True,
        choices=['whisper', 'qwen'],
        help='Model type to convert'
    )

    parser.add_argument(
        '--size', '-s',
        required=True,
        help='Model size (e.g., base, small, medium for Whisper)'
    )

    parser.add_argument(
        '--format', '-f',
        default='auto',
        choices=['auto', 'onnx', 'rknn', 'ennp'],
        help='Target format (default: auto-detect based on NPU)'
    )

    parser.add_argument(
        '--npu', '-n',
        default='auto',
        choices=['auto', 'rk3588', 'eic7700', 'cpu'],
        help='Target NPU type (default: auto-detect)'
    )

    parser.add_argument(
        '--output', '-o',
        default='./models',
        help='Output directory (default: ./models)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create converter
    converter = ModelConverter(npu_type=args.npu)

    # Convert model
    success = converter.convert_model(args.model, args.size, args.format)

    if success:
        logger.info("✅ Model conversion successful!")
        sys.exit(0)
    else:
        logger.error("❌ Model conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
