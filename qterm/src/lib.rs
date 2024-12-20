use std::ffi::{c_void, CString};
use tokio::runtime::Runtime;

mod ui;
mod quantum;
mod compute;
mod effects;
mod optimizations;
mod gpu;

pub use quantum::*;
pub use compute::metal::MetalCompute;
pub use effects::quantum::QuantumEffect;
pub use optimizations::ResourceOptimizer;
pub use gpu::*;
pub use ui::QuantumUI;
#[repr(C)]
pub struct QuantumState {
    amplitudes: *mut f32,
    phases: *mut f32,
    size: usize,
}

static RUNTIME: std::sync::OnceLock<Runtime> = std::sync::OnceLock::new();

fn get_runtime() -> &'static Runtime {
    RUNTIME.get_or_init(|| {
        Runtime::new().expect("Failed to create Tokio runtime")
    })
}

#[no_mangle]
pub extern "C" fn quantum_init() -> *mut c_void {
    let runtime = get_runtime();
    Box::into_raw(Box::new(runtime)) as *mut c_void
}

#[no_mangle]
pub extern "C" fn quantum_create_state(size: usize) -> *mut QuantumState {
    let state = QuantumState {
        amplitudes: Box::into_raw(vec![0.0f32; size].into_boxed_slice()) as *mut f32,
        phases: Box::into_raw(vec![0.0f32; size].into_boxed_slice()) as *mut f32,
        size,
    };
    Box::into_raw(Box::new(state))
}

#[no_mangle]
pub extern "C" fn quantum_destroy_state(state: *mut QuantumState) {
    if !state.is_null() {
        unsafe {
            let state = Box::from_raw(state);
            let _ = Box::from_raw(state.amplitudes as *mut [f32]);
            let _ = Box::from_raw(state.phases as *mut [f32]);
        }
    }
}

#[no_mangle]
pub extern "C" fn quantum_apply_gate(state: *mut QuantumState, gate_type: u32, qubit: u32) -> bool {
    if state.is_null() {
        return false;
    }
    // TODO: Implement gate application using Metal
    true
}

#[no_mangle]
pub extern "C" fn quantum_measure_state(state: *const QuantumState) -> f32 {
    if state.is_null() {
        return 0.0;
    }
    unsafe {
        let state = &*state;
        // Return the first amplitude as a simple measurement
        *state.amplitudes
    }
}

#[no_mangle]
pub extern "C" fn quantum_get_last_error() -> *mut i8 {
    CString::new("No error").unwrap().into_raw()
}
