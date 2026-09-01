import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


# ============================================================
# NetSentinel — Groq Benchmark
# ============================================================

GROQ_MODEL = "openai/gpt-oss-20b"

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


def build_benchmark_prompt():

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
"""


def run_groq_benchmark():

    print("=" * 60)
    print("  NetSentinel — Groq AI Benchmark")
    print(
        f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 60)

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Please check your .env file."
        )

    client = Groq(api_key=api_key)

    prompt = build_benchmark_prompt()

    print("\nTesting Groq + Llama/GPT OSS model...")
    print(f"Model: {GROQ_MODEL}")

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

    elapsed_time = time.perf_counter() - start_time

    result = response.choices[0].message.content

    # --------------------------------------------------------
    # Token information
    # --------------------------------------------------------

    usage = getattr(response, "usage", None)

    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

    if usage:

        prompt_tokens = getattr(
            usage,
            "prompt_tokens",
            0,
        )

        completion_tokens = getattr(
            usage,
            "completion_tokens",
            0,
        )

        total_tokens = getattr(
            usage,
            "total_tokens",
            0,
        )

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("  BENCHMARK RESULT")
    print("=" * 60)

    print(f"\nInference Time: {elapsed_time:.3f} seconds")
    print(f"Prompt Tokens: {prompt_tokens}")
    print(f"Completion Tokens: {completion_tokens}")
    print(f"Total Tokens: {total_tokens}")

    print("\nAI Analysis:")
    print("-" * 60)
    print(result)
    print("-" * 60)

    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    output_directory = "monitoring/reports"

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

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

    output_file = (
        "monitoring/reports/"
        "benchmark_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            benchmark_result,
            file,
            indent=2,
        )

    print(
        f"\n✅ Benchmark saved to: {output_file}"
    )

    return benchmark_result


if __name__ == "__main__":

    try:

        run_groq_benchmark()

    except Exception as error:

        print(
            f"\n❌ Benchmark failed: {error}"
        )

        raise