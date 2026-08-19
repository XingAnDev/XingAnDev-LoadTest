# XingAnDev-LoadTest
XingAnDev-LoadTest — A lightweight Python HTTP load-testing tool with a Kali-style CLI interface, system information display, concurrent request testing, and HTTP status tracking.

**XingAnDev-LoadTest** is a Python-based command-line HTTP load-testing, request analysis, and concurrency programming tool designed for controlled, authorized testing and practical study of Python networking.

The project combines HTTP communication, thread-pool concurrency, synchronization primitives, exception handling, operating-system information detection, terminal interface customization, HTTP status-code classification, and result aggregation into a single interactive command-line application.

Rather than being a minimal HTTP request script, XingAnDev-LoadTest is structured as a compact network-testing project that demonstrates how multiple Python components can be combined into a complete workflow: collecting user parameters, normalizing target URLs, creating concurrent I/O tasks, processing responses, maintaining thread-safe statistics, classifying failures, and presenting final results through a readable CLI interface.

---

## Core Architecture

At startup, XingAnDev-LoadTest initializes a terminal-oriented user interface and displays a custom ASCII banner.

The banner is dynamically centered according to the current terminal width, allowing the interface to adapt to different console window sizes.

The application then constructs a Kali-inspired command-line prompt containing:

* The current operating-system user name
* A simplified Windows version identifier
* The current working directory
* Color-coded terminal elements
* Interactive configuration prompts

The interface uses `Colorama` for terminal color control on supported Windows environments.

---

## Target URL Handling

The target address is provided interactively by the user.

Before testing begins, the application performs lightweight URL normalization. If the supplied address does not begin with:

```text
http://
https://
```

the program automatically prepends:

```text
https://
```

This allows users to enter either a complete URL or a plain domain name.

Protocol detection is case-insensitive, so values such as:

```text
HTTP://example.com
HTTPS://example.com
http://example.com
https://example.com
```

are recognized correctly.

For example:

```text
Input:
example.com

Normalized:
https://example.com
```

while an already complete URL is left unchanged.

---

## Configurable Concurrency

The application allows the user to specify a concurrency value.

This value is passed to Python's:

```python
ThreadPoolExecutor
```

which manages a pool of worker threads.

Instead of manually creating and controlling individual threads, XingAnDev-LoadTest delegates task scheduling to the executor.

Conceptually:

```text
                 ThreadPoolExecutor
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
     Worker 1         Worker 2         Worker N
        │                │                │
        ▼                ▼                ▼
     HTTP GET         HTTP GET         HTTP GET
```

This architecture demonstrates practical use of Python's high-level concurrency facilities for I/O-bound workloads.

HTTP operations spend a substantial portion of their lifetime waiting for DNS resolution, connection establishment, TLS negotiation, server processing, and response delivery. A thread-based model allows several independent I/O operations to remain in progress concurrently.

---

## Repeated Test Rounds

In addition to concurrency, the application accepts a configurable number of test rounds.

For each round, XingAnDev-LoadTest generates multiple instances of the same target URL and submits them to the thread pool.

The repeated URL sequence is generated using:

```python
itertools.repeat
```

This avoids manually duplicating identical URL strings inside a list.

A simplified execution model is:

```text
Round 1
 ├── Request
 ├── Request
 ├── Request
 └── Request ...

Round 2
 ├── Request
 ├── Request
 ├── Request
 └── Request ...

Round N
 ├── Request
 ├── Request
 ├── Request
 └── Request ...
```

The application calculates the planned number of request operations as:

```text
Total Requests = Concurrency × Rounds
```

Concurrency determines the configured worker level, while rounds determine how many batches are executed.

---

## HTTP Request Layer

The HTTP communication layer is implemented using the Python `requests` library.

Each worker performs an HTTP GET operation similar to:

```python
requests.get(url, timeout=100)
```

The timeout value prevents a worker from waiting indefinitely for a response.

When a response is received, the resulting `Response` object provides information such as:

```text
status_code
headers
content
text
url
```

The current implementation primarily uses the HTTP status code for response classification and statistical reporting.

---

## HTTP Status Code Classification

XingAnDev-LoadTest contains an internal HTTP status-code dictionary that maps common HTTP responses to readable English descriptions.

Examples include:

```text
200 → Request successful
201 → Resource created
204 → Request successful, no content
301 → Permanent redirect
302 → Temporary redirect
304 → Resource not modified
400 → Bad request
401 → Unauthorized
403 → Forbidden
404 → Page not found
405 → Method not allowed
408 → Request timeout
409 → Request conflict
412 → Precondition failed
413 → Request content too large
429 → Too many requests
500 → Internal server error
501 → Function not implemented
502 → Bad gateway
503 → Service unavailable
504 → Gateway timeout
```

When a status code is not included in the mapping, the application falls back to:

```text
Unknown status code
```

The dictionary is accessed through `.get()` so that unexpected or uncommon status codes do not cause a lookup exception.

---

## Success and Error Aggregation

The application maintains shared statistics for successful responses and other HTTP results.

The primary structures are:

```python
success = 0
errors = {}
```

An HTTP `200` response increments the success counter.

Other HTTP response codes are stored in the error dictionary.

For example:

```text
403 → 4
404 → 2
412 → 7
503 → 1
```

This preserves the distinction between different classes of server responses instead of reducing every non-200 response to one generic failure category.

---

## Thread Synchronization

Because multiple worker threads can complete at nearly the same time, shared counters and dictionaries require synchronized updates.

XingAnDev-LoadTest uses:

```python
threading.Lock
```

to protect shared statistics.

Conceptually:

```text
Worker A ─┐
Worker B ─┼──→ Lock ──→ Update Shared Statistics
Worker C ─┘
```

The lock is only held while shared statistics are being modified. HTTP requests themselves remain outside the protected section.

This demonstrates an important concurrency principle: minimizing the size of critical sections while protecting mutable shared state from race conditions.

---

## Exception Handling

Not every failed request produces an HTTP status code.

A request can fail before an HTTP response is available because of conditions such as:

```text
ConnectionError
ReadTimeout
ProxyError
SSLError
DNS failures
Socket failures
```

The application catches:

```python
requests.RequestException
```

and records these events separately as:

```text
Request exception
```

The program also prints the exception class and detailed error message, allowing users to distinguish between network-level failures and actual HTTP responses.

This distinction is important:

```text
HTTP 503
```

means the client successfully received an HTTP response from a server or intermediary.

By comparison:

```text
ReadTimeout
ConnectionError
ProxyError
```

indicates that the request failed during the communication process and did not produce a usable HTTP response.

---

## System Information Display

Before the test begins, XingAnDev-LoadTest displays information about the local execution environment.

The program reports:

```text
CPU
RAM
OS
Version
```

CPU information is obtained through Python's `platform` module.

RAM capacity is retrieved through:

```python
psutil.virtual_memory()
```

and converted from bytes into gigabytes for display.

System information provides useful context when comparing test sessions performed on different machines or configurations.

---

## Windows Version Detection

The CLI prompt includes a simplified Windows operating-system label.

The application reads:

```text
SOFTWARE\Microsoft\Windows NT\CurrentVersion
```

from the Windows registry and retrieves:

```text
CurrentBuild
```

The build number is then classified approximately as:

```text
Build >= 22000
    ↓
Windows11

10240 <= Build < 22000
    ↓
Windows10

Older builds
    ↓
Windows
```

The resulting label is inserted into the custom prompt.

For example:

```text
┌──(admin㉿Windows11)-[D:\Projects\XingAnDev-LoadTest]
└─#
```

---

## Custom CLI Interface

The command-line interface is intentionally inspired by the visual structure of a Kali Linux terminal while remaining usable as a Windows console application.

The prompt follows this format:

```text
┌──(USER㉿OS)-[PATH]
└─#
```

The individual elements are color-coded:

```text
Blue
 ├── Terminal structure
 ├── Brackets
 ├── Separators
 └── Path delimiters

Red
 ├── Username
 ├── ㉿ symbol
 ├── Operating-system label
 ├── #
 └── Interactive input

White
 └── Current working-directory path
```

The presentation layer is kept separate from the HTTP request logic, allowing the user interface to be modified without redesigning the request-processing engine.

---

## Execution Flow

The complete program can be summarized as:

```text
Program Start
      │
      ▼
Clear Terminal
      │
      ▼
Render ASCII Banner
      │
      ▼
Detect Terminal Width
      │
      ▼
Detect User / OS / Working Directory
      │
      ▼
Display CLI Prompt
      │
      ├───────────────┬───────────────┐
      ▼               ▼               ▼
 Target URL      Concurrency        Rounds
      │               │               │
      ▼               │               │
Normalize URL         │               │
      │               └───────┬───────┘
      └───────────────────────┘
                              │
                              ▼
                     Display System Info
                              │
                              ▼
                        User Confirmation
                              │
                              ▼
                      Create Thread Pool
                              │
                              ▼
                       Begin Test Rounds
                              │
                              ▼
                       Submit HTTP Tasks
                              │
                              ▼
                        Receive Results
                              │
                       ┌──────┴──────┐
                       │             │
                       ▼             ▼
                  HTTP Response   Exception
                       │             │
                       ▼             ▼
                  Status Check   Error Check
                       │             │
                       └──────┬──────┘
                              │
                              ▼
                     Update Statistics
                              │
                              ▼
                       Next Test Round
                              │
                             ...
                              │
                              ▼
                       Final Statistics
                              │
                              ▼
                         Program Exit
```

---

## Technology Stack

```text
Python
 ├── requests
 │     └── HTTP client
 │
 ├── concurrent.futures
 │     └── ThreadPoolExecutor
 │
 ├── itertools
 │     └── repeat()
 │
 ├── threading
 │     └── Lock
 │
 ├── platform
 │     └── System information
 │
 ├── psutil
 │     └── RAM information
 │
 ├── winreg
 │     └── Windows build detection
 │
 ├── colorama
 │     └── Terminal colors
 │
 └── os / shutil
       └── Terminal and environment utilities
```

---

## Educational Purpose

XingAnDev-LoadTest is intended to provide a practical example of how different Python concepts can be combined into one network-oriented application.

The project demonstrates:

* HTTP client programming
* URL normalization
* Thread-based concurrency
* Thread-pool management
* Shared-state synchronization
* Exception handling
* Dictionary-based aggregation
* Operating-system detection
* System resource inspection
* Terminal UI construction
* ANSI color handling
* Interactive CLI design
* HTTP response classification
* Basic performance-test result collection

The project can also serve as a foundation for studying more advanced topics such as:

* Connection pooling
* Persistent HTTP sessions
* Asynchronous I/O
* Response latency measurement
* Requests-per-second calculations
* Minimum / average / maximum latency
* P95 / P99 latency
* Structured logging
* CSV / JSON result export
* Configurable test profiles
* Cross-platform support
* Result visualization

---

## Responsible Use

XingAnDev-LoadTest is designed for:

* Authorized load testing
* Local development
* Educational experiments
* HTTP protocol research
* Performance evaluation of systems under the user's control
* Testing systems for which explicit authorization has been obtained

The software must not be used to intentionally disrupt, overload, degrade, bypass security controls on, or interfere with services belonging to other parties.

Users are responsible for ensuring that their use of this software complies with applicable laws, network policies, service agreements, and authorization requirements.

---

## Project Status

XingAnDev-LoadTest is an experimental and educational Python networking project.

The current implementation focuses on HTTP request execution, configurable concurrency, response classification, exception reporting, system information display, and terminal-based result aggregation.

Planned areas for future development include:

```text
├── Latency measurement
├── Requests-per-second statistics
├── Minimum / average / maximum response time
├── P95 / P99 latency
├── Structured logging
├── CSV / JSON result export
├── Persistent HTTP sessions
├── Connection reuse
├── Improved cross-platform support
├── Configurable test profiles
└── Result visualization
```

---

## License

See the repository's `LICENSE` file for the terms governing use, modification, and redistribution.

---

**XingAnDev-LoadTest — Explore HTTP, understand concurrency, measure responses, and analyze results.**
