import time
from core.sanitizer import SanitizerEngine

engine = SanitizerEngine()

# Sample log lines for benchmarking
log_lines = [
    "User logged in from 192.168.1.1",
    "Contact us at support@example.com",
    "Generated UUID: 550e8400-e29b-41d4-a716-446655440000",
    "Transaction hash: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
    "MD5 checksum: 5d41402abc4b2a76b9719d911017c592",
    "JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
] * 1000  # Repeat for larger dataset

start_time = time.time()

sanitized_lines = engine.sanitize_lines(log_lines)

end_time = time.time()

print(f"Processed {len(log_lines)} lines in {end_time - start_time:.2f} seconds.")
