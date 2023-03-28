# Token Bucket Rate Limiter

## Motivation

Apply theoretical learning to implement a functional rate limiter service using the [token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket)  in Python. Iterate on multiple versions until reach a near-production-worthy working implementation.

## Requirements

### Functional

* Allow 4 tokens (requests) per 60s
* Track requests per IPV4 address
* Refill bucket to max tokens every 60s
  * Refill occurs 60s after the initial request for a IPV4 adddress is served e.g:
    * 127.0.0.1 first request at 01:01:32
    * 127.0.0.1 will have a bucket refil at 01:02:32 (60s later)

### Infra
* Self-healing
* Highly available
* Configs/secrets externally stored
* Deploy to public cloud

### Extra
* Unit tests & coverage reporting