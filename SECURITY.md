# Security Policy

## Supported Versions

LogVeil follows semantic versioning. Security updates are provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | Fully supported |
| 1.x.x   | Critical fixes only |
| < 1.0   | No longer supported |

## Reporting a Vulnerability

### Responsible Disclosure

We take security seriously. If you discover a security vulnerability in LogVeil, please report it responsibly by emailing our security team at [security@logveil.dev](mailto:security@logveil.dev).

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include

When reporting a vulnerability, please include:

1. **Description**: Clear description of the vulnerability
2. **Impact**: Potential impact and affected components
3. **Reproduction**: Step-by-step instructions to reproduce
4. **Environment**: LogVeil version, OS, and relevant configuration
5. **Proof of Concept**: Code or logs demonstrating the issue (if applicable)

### Response Timeline

- **Initial Response**: 24 hours
- **Triage and Assessment**: 3-5 business days
- **Fix Development**: Varies by severity (1-30 days)
- **Release**: Coordinated disclosure after fix is ready

### Severity Levels

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Remote code execution, data exfiltration | 1-3 days |
| **High** | Privilege escalation, authentication bypass | 5-10 days |
| **Medium** | Information disclosure, denial of service | 10-20 days |
| **Low** | Minor information leaks | 20-30 days |

## Security Features

### Data Protection

LogVeil implements multiple layers of protection:

- **No Data Retention**: Processed data is never permanently stored
- **Memory Safety**: Rust components prevent buffer overflows
- **Input Validation**: All inputs are validated before processing
- **Configurable Policies**: Fine-grained control over data handling

### Audit and Compliance

- **Trace Logging**: Optional audit trails for compliance
- **Pattern Validation**: Regex patterns are validated before use
- **Configuration Security**: Secure defaults for all settings
- **Access Controls**: Role-based access in API mode

### Deployment Security

- **Container Security**: Minimal attack surface in Docker images
- **Network Security**: HTTPS/TLS support for API endpoints
- **Authentication**: Multiple authentication methods supported
- **Rate Limiting**: Protection against abuse and DoS

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest stable version
2. **Validate Inputs**: Verify log files before processing
3. **Secure Configuration**: Use secure settings in production
4. **Monitor Access**: Log and monitor API access
5. **Regular Audits**: Review redaction policies regularly

### For Developers

1. **Code Review**: All changes require security review
2. **Static Analysis**: Automated security scanning in CI/CD
3. **Dependency Scanning**: Regular updates and vulnerability checks
4. **Secure Coding**: Follow OWASP guidelines
5. **Testing**: Include security tests in test suite

## Known Security Considerations

### Log Data Handling

- **Partial Redaction**: Some patterns may have edge cases
- **Context Preservation**: Balancing security with log utility
- **Performance vs Security**: Trade-offs in real-time processing

### Engine Security

- **Regex Complexity**: Complex patterns may cause ReDoS
- **Memory Usage**: Large files may consume significant memory
- **Process Isolation**: Different engines have different isolation levels

### API Security

- **Input Validation**: All API inputs are validated
- **Rate Limiting**: Built-in protection against abuse
- **Authentication**: Optional but recommended for production
- **CORS**: Configurable cross-origin resource sharing

## Cryptographic Disclosure

LogVeil uses cryptographic functions for:

- **Hash Detection**: Identifying cryptographic hashes in logs
- **Entropy Analysis**: Statistical analysis for secret detection
- **API Authentication**: Optional JWT token validation

We do not implement custom cryptography and rely on well-established libraries.

## Third-Party Dependencies

LogVeil regularly audits dependencies for vulnerabilities:

- **Python**: Using `pip-audit` and `safety`
- **Rust**: Using `cargo-audit`
- **Go**: Using `govulncheck`

Critical vulnerabilities in dependencies trigger immediate updates.

## Security Contact

For security-related inquiries:

- **Email**: [security@logveil.dev](mailto:security@logveil.dev)
- **PGP Key**: Available on request
- **Response Time**: 24 hours for critical issues

## Bug Bounty

We currently do not offer a formal bug bounty program, but we recognize and credit security researchers who responsibly disclose vulnerabilities.

---

Last updated: August 2025
