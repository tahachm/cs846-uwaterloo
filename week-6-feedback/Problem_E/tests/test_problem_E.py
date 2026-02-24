import pytest
from problems.problem_E import summarize_access_log


VALID_LOG = """\
# comment line should be ignored
10.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.1" 200
10.0.0.2 - - [10/Oct/2000:13:55:37 -0700] "POST /api/login HTTP/1.1" 401

10.0.0.1 - - [10/Oct/2000:13:55:38 -0700] "GET /about HTTP/1.1" 302
10.0.0.3 - - [10/Oct/2000:13:55:39 -0700] "DELETE /danger HTTP/1.1" 503
"""


def test_summary_counts():
    out = summarize_access_log(VALID_LOG)

    assert out["total_requests"] == 4

    assert out["requests_by_ip"] == {
        "10.0.0.1": 2,
        "10.0.0.2": 1,
        "10.0.0.3": 1,
    }

    assert out["requests_by_method"] == {
        "GET": 2,
        "POST": 1,
        "DELETE": 1,
    }

    assert out["status_classes"] == {
        "2xx": 1,
        "3xx": 1,
        "4xx": 1,
        "5xx": 1,
    }


def test_empty_input():
    out = summarize_access_log("")
    assert out == {
        "total_requests": 0,
        "requests_by_ip": {},
        "requests_by_method": {},
        "status_classes": {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0},
    }


def test_invalid_line_raises_with_line_number():
    bad = '10.0.0.1 - - [x] "GET / HTTP/1.1" TWOHUNDRED\n'
    with pytest.raises(ValueError) as e:
        summarize_access_log(bad)
    assert "Invalid log line at 1" in str(e.value)


def test_ignores_blank_and_comments_only():
    out = summarize_access_log("\n# hi\n\n")
    assert out["total_requests"] == 0