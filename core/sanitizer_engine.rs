use regex::Regex;
use std::collections::HashMap;

#[no_mangle]
pub extern "C" fn sanitize_line(line: *const libc::c_char) -> *const libc::c_char {
    use std::ffi::{CStr, CString};

    let c_str = unsafe { CStr::from_ptr(line) };
    let input = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null(),
    };

    let patterns: HashMap<&str, Regex> = HashMap::from([
        ("ip", Regex::new(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b").unwrap()),
        ("email", Regex::new(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b").unwrap()),
        ("uuid", Regex::new(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b").unwrap()),
        ("sha256", Regex::new(r"\b[a-fA-F0-9]{64}\b").unwrap()),
        ("md5", Regex::new(r"\b[a-fA-F0-9]{32}\b").unwrap()),
        ("jwt", Regex::new(r"\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b").unwrap()),
    ]);

    let mut sanitized = input.to_string();

    for (label, regex) in &patterns {
        sanitized = regex.replace_all(&sanitized, format!("[REDACTED_{}]", label).as_str()).to_string();
    }

    let c_string = CString::new(sanitized).unwrap();
    c_string.into_raw()
}

#[no_mangle]
pub extern "C" fn free_string(s: *mut libc::c_char) {
    unsafe {
        if s.is_null() { return; }
        CString::from_raw(s);
    }
}
