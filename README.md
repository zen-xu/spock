# spock

<div align="center">
  <a href="https://github.com/zen-xu/spock/actions">
    <img src="https://github.com/zen-xu/spock/actions/workflows/main.yaml/badge.svg" alt="CI"/>
  </a>
  <a href="https://codecov.io/gh/zen-xu/spock">
    <img src="https://codecov.io/gh/zen-xu/spock/branch/main/graph/badge.svg?token=WPG2V9w16r"/>
  </a>
  <a href="https://pypi.org/project/pyspock">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/pyspock">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/pyspock">
  <a href="https://github.com/zen-xu/spock/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/MIT%202.0-blue.svg" alt="License">
  </a>
</div>
<div align="center">
  <a href="https://results.pre-commit.ci/latest/github/zen-xu/spock/main">
    <img src="https://results.pre-commit.ci/badge/github/zen-xu/spock/main.svg">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg">
  </a>
  <a href="https://deepsource.io/gh/zen-xu/spock/?ref=repository-badge}" target="_blank">
    <img alt="DeepSource" title="DeepSource" src="https://deepsource.io/gh/zen-xu/spock.svg/?label=active+issues&show_trend=true&token=mgZ7FgiJDAxSt9Ilav9vLFEo"/>
  </a>
</div>

`pyspock` is a BDD-style developer testing and specification framework for Python, and this is an implementation of the [`spock`](https://github.com/spockframework/spock).

An example of simple bdd test:

```python
import pytest


@pytest.mark.spock("maximum of {a} and {b} is {c}")
def test_maximum():
    def expect(a, b, c):
        assert max(a, b) == c

    def where(_, a, b, c):
        _ | a | b | c
        _ | 3 | 7 | 7
        _ | 5 | 4 | 5
        _ | 9 | 9 | 9
```

If you are using vscode, you can find there will be 3 test cases.

![vscode-test-discovery](doc/en/img/vscode-testing-discovery.png)
