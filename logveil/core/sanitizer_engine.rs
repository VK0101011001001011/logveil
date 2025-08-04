use regex::Regex;
use std::collections::HashMap;
use std::ffi::{CStr, CString};
use std::sync::OnceLock;
use libc::c_char;
use std::panic;

static PATTERNS: OnceLock<HashMap<&'static str, Regex>> = OnceLock::new();

/// Initialize sanitization patterns with safe regex compilation
fn get_patterns() -> &'static HashMap<&'static str, Regex> {
    PATTERNS.get_or_init(|| {
        let mut map = HashMap::new();
        
        // Use safe regex compilation with proper error handling
        let patterns = [
            ("ip", r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
            ("email", r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
            ("uuid", r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"),
            ("sha256", r"\b[a-fA-F0-9]{64}\b"),
            ("md5", r"\b[a-fA-F0-9]{32}\b"),
            ("jwt", r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b"),
        ];
        
        for (name, pattern) in patterns {
            match Regex::new(pattern) {
                Ok(regex) => {
                    map.insert(name, regex);
                }
                Err(e) => {
                    eprintln!("Failed to compile regex pattern '{}': {}", name, e);
                    // Continue with other patterns rather than panicking
                }
            }
        }
        
        map
    })
}

/// Sanitize a single line of text, replacing sensitive patterns with redaction markers
/// 
/// # Safety
/// This function is intended to be called from C/FFI contexts.
/// The input must be a valid null-terminated C string.
/// The returned pointer must be freed using free_string().
/// 
/// # Arguments
/// * `line` - A null-terminated C string to sanitize
/// 
/// # Returns
/// A pointer to a newly allocated C string containing the sanitized text,
/// or null pointer if an error occurs.
#[no_mangle]
pub extern "C" fn sanitize_line(line: *const c_char) -> *const c_char {
    // Validate input pointer
    if line.is_null() {
        eprintln!("sanitize_line: null input pointer");
        return std::ptr::null();
    }

    // Convert C string to Rust string with proper error handling
    let c_str = unsafe { CStr::from_ptr(line) };
    let input = match c_str.to_str() {
        Ok(s) => s,
        Err(e) => {
            eprintln!("sanitize_line: invalid UTF-8 input: {}", e);
            return std::ptr::null();
        }
    };

    // Catch any panics during processing
    let result = panic::catch_unwind(|| {
        let patterns = get_patterns();
        let mut sanitized = input.to_string();

        // Apply each pattern, handling potential regex errors
        for (label, regex) in patterns.iter() {
            match panic::catch_unwind(|| {
                regex.replace_all(&sanitized, format!("[REDACTED_{}]", label.to_uppercase()).as_str()).to_string()
            }) {
                Ok(new_sanitized) => sanitized = new_sanitized,
                Err(_) => {
                    eprintln!("sanitize_line: panic during pattern '{}' application", label);
                    // Continue with other patterns
                }
            }
        }
        
        sanitized
    });

    let sanitized = match result {
        Ok(s) => s,
        Err(_) => {
            eprintln!("sanitize_line: panic during sanitization");
            return std::ptr::null();
        }
    };

    // Convert back to C string with error handling
    match CString::new(sanitized) {
        Ok(c_string) => c_string.into_raw(),
        Err(e) => {
            eprintln!("sanitize_line: failed to create C string: {}", e);
            std::ptr::null()
        }
    }
}

/// Free a string allocated by sanitize_line
/// 
/// # Safety
/// This function is intended to be called from C/FFI contexts.
/// The pointer must have been returned by sanitize_line() and must not be used after calling this function.
/// 
/// # Arguments
/// * `s` - A pointer to a C string allocated by sanitize_line
#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    if s.is_null() {
        return;
    }
    
    unsafe {
        // Convert back to CString to ensure proper deallocation
        let _ = CString::from_raw(s);
    }
}
        if s.is_null() { return; }
        CString::from_raw(s);
    }
}
