import json
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


# ============================================================
# NetSentinel — Groq AI Benchmark
# ============================================================

GROQ_MODEL = "openai/gpt-oss-20b"

OUTPUT_FILE = (
    Path("monitoring")
    / "reports"
    / "benchmark_results.json"
)


# ============================================================
# Benchmark Test Data
# ============================================================

BENCHMARK_DATA = {
    "average_latency_ms": 145.5,
    "p95_latency_ms": 320.0,
    "p99_latency_ms": 480.0,
    "error_rate_percent": 2.5,
    "requests_per_second": 8.5,
    "total_requests": 2550,
    "concurrent_users": 50,
    "test_duration": "5 minutes",
}


# ============================================================
# Build Benchmark Prompt
# ============================================================

def build_benchmark_prompt():
    """
    Build the prompt used for the Groq AI benchmark.
    """

    return f"""
You are a Senior Network Performance Engineer.

Analyze the following NetSentinel load test results.

Average Latency: {BENCHMARK_DATA["average_latency_ms"]} ms
P95 Latency: {BENCHMARK_DATA["p95_latency_ms"]} ms
P99 Latency: {BENCHMARK_DATA["p99_latency_ms"]} ms
Error Rate: {BENCHMARK_DATA["error_rate_percent"]} %
Requests Per Second: {BENCHMARK_DATA["requests_per_second"]}
Total Requests: {BENCHMARK_DATA["total_requests"]}
Concurrent Users: {BENCHMARK_DATA["concurrent_users"]}
Test Duration: {BENCHMARK_DATA["test_duration"]}

Provide the analysis using exactly this structure:

BOTTLENECK: [Primary bottleneck]
SEVERITY: [LOW/MEDIUM/HIGH/CRITICAL]
ROOT CAUSE: [One sentence]
IMMEDIATE ACTION 1: [Recommended action]
IMMEDIATE ACTION 2: [Recommended action]
PERFORMANCE VERDICT: [PASS/FAIL/WARNING]

Keep the response below 150 words.
""".strip()


# ============================================================
# Extract Token Usage
# ============================================================

def extract_token_usage(response):
    """
    Safely extract token usage information from a Groq response.

    Supports both object-style and dictionary-style usage data.
    """

    usage = getattr(response, "usage", None)

    if usage is None:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    if isinstance(usage, dict):
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    return {
        "prompt_tokens": getattr(
            usage,
            "prompt_tokens",
            0,
        ),
        "completion_tokens": getattr(
            usage,
            "completion_tokens",
            0,
        ),
        "total_tokens": getattr(
            usage,
            "total_tokens",
            0,
        ),
    }


# ============================================================
# Save Benchmark Result
# ============================================================

def save_benchmark_result(result):
    """
    Save the benchmark result as JSON.
    """

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
        )


# ============================================================
# Run Groq Benchmark
# ============================================================

def run_groq_benchmark():
    """
    Execute the Groq AI benchmark and save the result.
    """

    print("=" * 60)
    print("  NetSentinel — Groq AI Benchmark")
    print(
        f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Validate API Key
    # --------------------------------------------------------

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Please configure the GROQ_API_KEY environment variable."
        )

    # --------------------------------------------------------
    # Initialize Groq Client
    # --------------------------------------------------------

    client = Groq(
        api_key=api_key
    )

    prompt = build_benchmark_prompt()

    print("\nTesting Groq AI model...")
    print(f"Model: {GROQ_MODEL}")

    # --------------------------------------------------------
    # Execute AI Request
    # --------------------------------------------------------

    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.3,
    )

    elapsed_time = (
        time.perf_counter()
        - start_time
    )

    # --------------------------------------------------------
    # Extract AI Response
    # --------------------------------------------------------

    try:
        result = response.choices[0].message.content
    except (
        AttributeError,
        IndexError,
        TypeError,
    ) as error:

        raise RuntimeError(
            "Groq returned an invalid response."
        ) from error

    if not result:
        raise RuntimeError(
            "Groq returned an empty AI response."
        )

    # --------------------------------------------------------
    # Extract Token Information
    # --------------------------------------------------------

    token_usage = extract_token_usage(
        response
    )

    prompt_tokens = token_usage[
        "prompt_tokens"
    ]

    completion_tokens = token_usage[
        "completion_tokens"
    ]

    total_tokens = token_usage[
        "total_tokens"
    ]

    # --------------------------------------------------------
    # Display Benchmark Result
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("  BENCHMARK RESULT")
    print("=" * 60)

    print(
        f"\nInference Time: "
        f"{elapsed_time:.3f} seconds"
    )

    print(
        f"Prompt Tokens: "
        f"{prompt_tokens}"
    )

    print(
        f"Completion Tokens: "
        f"{completion_tokens}"
    )

    print(
        f"Total Tokens: "
        f"{total_tokens}"
    )

    print("\nAI Analysis:")
    print("-" * 60)
    print(result)
    print("-" * 60)

    # --------------------------------------------------------
    # Prepare Benchmark Result
    # --------------------------------------------------------

    benchmark_result = {
        "benchmark_at": datetime.now().isoformat(),
        "provider": "Groq",
        "model": GROQ_MODEL,
        "test_data": BENCHMARK_DATA,
        "inference_time_seconds": round(
            elapsed_time,
            3,
        ),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "analysis": result,
        "status": "success",
    }

    # --------------------------------------------------------
    # Save Benchmark Result
    # --------------------------------------------------------

    save_benchmark_result(
        benchmark_result
    )

    print(
        f"\n✅ Benchmark saved to: "
        f"{OUTPUT_FILE}"
    )

    return benchmark_result


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":

    try:

        run_groq_benchmark()

    except Exception as error:

        print(
            f"\n❌ Benchmark failed: {error}"
        )

        raise