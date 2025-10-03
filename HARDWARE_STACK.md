# ESWIN NPU Hardware Stack - Integration Guide

## Hardware Platform
- **Board**: ESWIN NPU-enabled hardware
- **Model**: Qwen2 7B (int8 quantized, 1024 token context)
- **Accelerator**: NPU Device 0 (28 transformer blocks)

## Software Stack

### NPU Binary
- **Path**: `/opt/eswin/sample-code/npu_sample/qwen_sample/bin/es_qwen2`
- **Interface**: stdin/stdout text-based protocol
- **Execution**: Single instance, single-threaded

### Required Files
```
Model Directory: /opt/eswin/sample-code/npu_sample/qwen_sample/models/qwen2_7b_1k_int8/
├── modified_block_0_npu_b1.model through modified_block_27_npu_b1.model (28 blocks)
├── lm_npu_b1.model (language model head)
└── embedding.bin

Tokenizer: /opt/eswin/sample-code/npu_sample/qwen_sample/src/qwen2_7b_1k_int8/qwen.tiktoken
```

### Configuration File
Location: `config.json` (pass as argument to binary)

## Integration Protocol

### 1. Starting the NPU Process
```python
import subprocess

process = subprocess.Popen(
    ["/opt/eswin/sample-code/npu_sample/qwen_sample/bin/es_qwen2", "config.json"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1  # Line buffered
)
```

### 2. Initialization Sequence
The binary loads the model and outputs progress to stdout:
- Monitor stdout for "100.00%" to detect ready state
- Typical load time: varies by hardware (10-60 seconds)
- STDERR contains debug/diagnostic information

### 3. Sending Prompts

**Input Protocol (via stdin):**
```
3\n                    # Mode selector: custom prompt
<your_prompt_text>\n  # Your actual prompt
```

**Predefined Prompts (alternative):**
```
0\n  # Uses prompts.0 from config.json
1\n  # Uses prompts.1 from config.json
2\n  # Uses prompts.2 from config.json
```

### 4. Reading Responses

**Output Protocol (from stdout):**
- Character-by-character streaming
- No line buffering - each character arrives individually
- Termination marker: `-------` (7 hyphens)
- Special sequences may appear in first few characters (skip counter=0-6 in qwen_runner.py:119)

**Example Reading Loop:**
```python
output = []
while True:
    char = process.stdout.read(1)
    if not char:
        break
    output.append(char)

    # Check for termination
    if "-------" in ''.join(output):
        break

response = ''.join(output)
```

### 5. Thread Safety
- **Critical**: Only ONE prompt can be processed at a time
- Use mutex/lock when sending prompts from multiple threads
- Queue-based architecture recommended for concurrent requests

## Quick Integration Code

### Minimal Working Example
```python
import subprocess
import threading

class NPUInterface:
    def __init__(self):
        self.process = subprocess.Popen(
            ["/opt/eswin/sample-code/npu_sample/qwen_sample/bin/es_qwen2", "config.json"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.lock = threading.Lock()
        self._wait_ready()

    def _wait_ready(self):
        """Wait for model to load (detect 100.00%)"""
        buffer = ""
        while "100.00%" not in buffer:
            char = self.process.stdout.read(1)
            if not char:
                raise RuntimeError("Process died during startup")
            buffer += char
            if len(buffer) > 10000:
                buffer = buffer[-1000:]  # Sliding window

    def generate(self, prompt):
        """Send prompt and return response"""
        with self.lock:
            # Send prompt
            self.process.stdin.write("3\n")
            self.process.stdin.flush()
            self.process.stdin.write(f"{prompt}\n")
            self.process.stdin.flush()

            # Read response
            output = []
            while True:
                char = self.process.stdout.read(1)
                if not char:
                    break
                output.append(char)
                if "-------" in ''.join(output):
                    break

            return ''.join(output)

    def close(self):
        self.process.terminate()
        self.process.wait()

# Usage
npu = NPUInterface()
response = npu.generate("What is quantum computing?")
print(response)
npu.close()
```

### Integration with MQTT (Production Pattern)
```python
import paho.mqtt.client as mqtt

npu = NPUInterface()
client = mqtt.Client()

def on_message(client, userdata, msg):
    prompt = msg.payload.decode()
    response = npu.generate(prompt)
    client.publish("response/topic", response)

client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("prompt/topic")
client.loop_forever()
```

### Streaming Integration (Character-by-Character)
```python
import queue

class StreamingNPU:
    def __init__(self):
        self.process = subprocess.Popen([...])  # Same as above
        self.output_queue = queue.Queue()
        threading.Thread(target=self._stream_reader, daemon=True).start()

    def _stream_reader(self):
        """Continuously read stdout to queue"""
        while True:
            char = self.process.stdout.read(1)
            if not char:
                break
            self.output_queue.put(char)

    def generate_streaming(self, prompt, callback):
        """callback(char) called for each character"""
        # Clear queue
        while not self.output_queue.empty():
            self.output_queue.get()

        # Send prompt
        self.process.stdin.write("3\n")
        self.process.stdin.flush()
        self.process.stdin.write(f"{prompt}\n")
        self.process.stdin.flush()

        # Stream output
        output = []
        while True:
            char = self.output_queue.get(timeout=30)
            output.append(char)
            callback(char)  # Real-time callback

            if "-------" in ''.join(output):
                break

        return ''.join(output)
```

## Model Parameters (from config.json)

```python
PARAMS = {
    "vocab_size": 152064,
    "embedding_size": 3584,
    "max_tokens": 1024,
    "response_max_len": 1024,
    "repetition_penalty": 1.05,
    "top_k": 1,  # Greedy sampling
    "special_tokens": ["<|endoftext|>", "<|im_start|>", "<|im_end|>"],
    "eos_tokens": ["<|endoftext|>", "<|im_end|>", "<|im_start|>"]
}
```

## Performance Characteristics

- **Latency**: First token ~200-500ms (hardware dependent)
- **Throughput**: ~20-50 tokens/second (hardware dependent)
- **Context**: 1024 tokens maximum
- **Concurrent Requests**: 1 (single-threaded NPU binary)

## Error Handling

```python
def safe_generate(self, prompt, timeout=30):
    try:
        with self.lock:
            self.process.stdin.write("3\n")
            self.process.stdin.flush()
            self.process.stdin.write(f"{prompt}\n")
            self.process.stdin.flush()

            output = []
            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError("NPU response timeout")

                # Non-blocking read with select/poll recommended
                char = self.process.stdout.read(1)
                if not char:
                    if self.process.poll() is not None:
                        raise RuntimeError("NPU process died")
                    break

                output.append(char)
                if "-------" in ''.join(output):
                    break

            return ''.join(output)

    except Exception as e:
        # Consider process restart on critical errors
        print(f"Error: {e}")
        return None
```

## Integration Checklist

- [ ] Verify NPU binary path exists: `/opt/eswin/sample-code/npu_sample/qwen_sample/bin/es_qwen2`
- [ ] Verify model files exist in `/opt/eswin/sample-code/npu_sample/qwen_sample/models/qwen2_7b_1k_int8/`
- [ ] Create valid `config.json` (see config.json in repo)
- [ ] Implement thread-safe prompt queue if handling concurrent requests
- [ ] Add timeout handling for hung processes
- [ ] Monitor STDERR for hardware errors
- [ ] Implement process restart logic for production
- [ ] Clear stdout queue before sending new prompts (avoid stale data)

## Notes

- The binary outputs additional control characters in first 6-7 characters (skip these)
- Use `bufsize=1` for line buffering or `bufsize=0` for unbuffered
- Character-by-character reading is intentional - enables real-time streaming
- Do not use `process.communicate()` - blocks until process exit
- The "3\n" mode selector MUST be sent before custom prompts
