from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Any


# Log format (simplified):
#   <ip> - - [date] "<METHOD> <PATH> HTTP/1.1" <status>
#
# Example:
#   10.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.1" 200
#
# Requirements:
# - Ignore blank lines and lines starting with '#'
# - Parse IP, method, path, status
# - Count requests per IP
# - Count requests per HTTP method
# - Count responses by status class: 2xx, 3xx, 4xx, 5xx
# - Return a dict with the exact shape described in the docstring


LOG_RE = re.compile(
    r'^(?P<ip>\S+)\s+-\s+-\s+\[(?P<ts>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+HTTP/\d\.\d"\s+(?P<status>\d{3})\s*$'
)


def summarize_access_log(text: str) -> Dict[str, Any]:
    """
    Parse a newline-separated access log string and return a summary dict.

    Input:
      text: a single string containing zero or more newline-separated log lines.

    Output: dict with exactly these keys:
      - "total_requests": int
      - "requests_by_ip": dict[str, int]
      - "requests_by_method": dict[str, int]
      - "status_classes": dict[str, int]  # keys: "2xx","3xx","4xx","5xx"

    Rules:
      - Ignore blank lines
      - Ignore lines starting with '#'
      - If a non-ignored line does not match the log format, raise ValueError
        with a message that includes the 1-based line number: "Invalid log line at <n>"

    TODO: implement.
    """
    lines = text.splitlines()
    total_requests = 0
    requests_by_ip = Counter()
    requests_by_method = Counter()
    status_classes = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
    line_num = 0
    for line in lines:
        line_num += 1
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = LOG_RE.match(line)
        if not match:
            raise ValueError(f"Invalid log line at {line_num}")
        ip = match.group('ip')
        method = match.group('method')
        status = int(match.group('status'))
        total_requests += 1
        requests_by_ip[ip] += 1
        requests_by_method[method] += 1
        status_class = f"{status // 100}xx"
        status_classes[status_class] += 1
    return {
        "total_requests": total_requests,
        "requests_by_ip": dict(requests_by_ip),
        "requests_by_method": dict(requests_by_method),
        "status_classes": status_classes,
    }