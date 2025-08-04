use regex::Regex;
use std::collections::HashMap;
use std::ffi::{CStr, CString};
use std::sync::OnceLock;
use libc::c_char;

static PATTERNS: OnceLock<HashMap<&'static str, Regex>> = OnceLock::new();

fn get_patterns() -> &'static HashMap<&'static str, Regex> {
    PATTERNS.get_or_init(|| {
        let mut map = HashMap::new();
        map.insert("ip", Regex::new(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b").expect("Invalid regex"));
        map.insert("email", Regex::new(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b").expect("Invalid regex"));
        map.insert("uuid", Regex::new(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b").expect("Invalid regex"));
        map.insert("sha256", Regex::new(r"\b[a-fA-F0-9]{64}\b").expect("Invalid regex"));
        map.insert("md5", Regex::new(r"\b[a-fA-F0-9]{32}\b").expect("Invalid regex"));
        map.insert("jwt", Regex::new(r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b").expect("Invalid regex"));
        map
    })
}

#[no_mangle]
pub extern "C" fn sanitize_line(line: *const c_char) -> *const c_char {
    if line.is_null() {
        return std::ptr::null();
    }

    let c_str = unsafe { CStr::from_ptr(line) };
    let input = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null(),
    };

    let patterns = get_patterns();

    let mut sanitized = input.to_string();

    for (label, regex) in patterns.iter() {
        sanitized = regex.replace_all(&sanitized, format!("[REDACTED_{}]", label).as_str()).to_string();
    }

    match CString::new(sanitized) {
        Ok(c_string) => c_string.into_raw(),
        Err(_) => std::ptr::null(),
    }
}

#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    unsafe {
        if s.is_null() { return; }
        CString::from_raw(s);
    }
}
