#[cfg(feature = "metal")]
use metal::{Device, CommandQueue, Buffer, ComputePipelineState};
use std::sync::Arc;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum GPUError {
    #[error("GPU device not available")]
    DeviceNotAvailable,
    #[error("Shader compilation failed: {0}")]
    ShaderCompilationError(String),
    #[error("Pipeline creation failed: {0}")]
    PipelineError(String),
    #[error("Buffer allocation failed: {0}")]
    BufferError(String),
    #[error("Compute operation failed: {0}")]
    ComputeError(String),
}

pub type Result<T> = std::result::Result<T, GPUError>;

/// Platform-specific GPU context
#[cfg(feature = "metal")]
pub struct MetalContext {
    device: Device,
    command_queue: CommandQueue,
    pipeline_state: ComputePipelineState,
}

#[cfg(feature = "metal")]
impl Drop for MetalContext {
    fn drop(&mut self) {
        // Metal handles cleanup automatically through reference counting
    }
}

#[cfg(feature = "metal")]
impl MetalContext {
    /// Creates a new Metal context for GPU computations
    ///
    /// # Errors
    /// - Returns DeviceNotAvailable if no Metal-capable GPU is found
    /// - Returns ShaderCompilationError if quantum shader compilation fails
    /// - Returns PipelineError if compute pipeline creation fails
    pub fn new() -> Result<Self> {
        let device = Device::system_default()
            .ok_or(GPUError::DeviceNotAvailable)?;
        let command_queue = device.new_command_queue();
        
        // Load and compile quantum compute shader
        let shader_src = include_str!("../Sources/Resources/Shaders.metal");
        let options = metal::CompileOptions::new();
        let library = device.new_library_with_source(shader_src, &options)
            .map_err(|e| GPUError::ShaderCompilationError(e.to_string()))?;
        let function = library.get_function("quantum_evolve", None)
            .ok_or_else(|| GPUError::ShaderCompilationError("quantum_evolve function not found".into()))?;
        let pipeline_state = device.new_compute_pipeline_state_with_function(&function)
            .map_err(|e| GPUError::PipelineError(e.to_string()))?;
        
        Ok(Self {
            device,
            command_queue,
            pipeline_state,
        })
    }
    
    /// Process quantum state using GPU acceleration
    ///
    /// # Errors
    /// - Returns BufferError if GPU memory allocation fails
    /// - Returns ComputeError if compute operation fails
    pub fn process_quantum_state(&self, state: &mut QuantumState, gate_type: u32) -> Result<()> {
        let command_buffer = self.command_queue.new_command_buffer();
        let compute_encoder = command_buffer.new_compute_command_encoder();
        
        // Set up buffers and dispatch compute shader
        let amplitudes_buffer = self.device.new_buffer_with_data(
            unsafe { std::slice::from_raw_parts(state.amplitudes, state.size) } as *const _ as *const _,
            (state.size * std::mem::size_of::<f32>()) as u64,
            metal::MTLResourceOptions::StorageModeShared,
        );
        
        compute_encoder.set_compute_pipeline_state(&self.pipeline_state);
        compute_encoder.set_buffer(0, Some(&amplitudes_buffer), 0);
        
        // Configure thread groups
        let thread_group_size = metal::MTLSize::new(256, 1, 1);
        let thread_groups = metal::MTLSize::new(
            (state.size as u64 + 255) / 256,
            1,
            1
        );
        
        compute_encoder.dispatch_thread_groups(thread_groups, thread_group_size);
        compute_encoder.end_encoding();
        
        command_buffer.commit();
        command_buffer.wait_until_completed();
        
        Ok(())
    }
}

#[cfg(not(any(feature = "metal", feature = "cuda", feature = "opencl")))]
mod cpu_fallback {
    use super::*;
    
    pub struct CpuContext;
    
    impl CpuContext {
        pub fn new() -> Result<Self> {
            Ok(Self)
        }
        
        pub fn process_quantum_state(&self, state: &mut QuantumState, gate_type: u32) -> Result<()> {
            // CPU fallback implementation for quantum state evolution
            // Basic single-threaded implementation for platforms without GPU support
            match gate_type {
                0 => { /* Implement Hadamard gate */ }
                1 => { /* Implement CNOT gate */ }
                2 => { /* Implement Phase gate */ }
                _ => return Err(GPUError::ComputeError("Invalid gate type".into()))
            }
            Ok(())
        }
    }
}
}

/// High-level quantum device bridge that provides platform-agnostic GPU acceleration
pub struct QDeviceBridge {
    #[cfg(feature = "metal")]
    context: Arc<MetalContext>,
    #[cfg(not(any(feature = "metal", feature = "cuda", feature = "opencl")))]
    context: Arc<cpu_fallback::CpuContext>,
}

impl QDeviceBridge {
    /// Creates a new quantum device bridge with the best available GPU backend
    ///
    /// # Errors
    /// - Returns DeviceNotAvailable if no compatible GPU is found
    /// - Returns other GPU-specific errors during initialization
    pub fn new() -> Result<Self> {
        #[cfg(feature = "metal")]
        {
            Ok(Self {
                context: Arc::new(MetalContext::new()?)
            })
        }
        
        #[cfg(not(any(feature = "metal", feature = "cuda", feature = "opencl")))]
        {
            Ok(Self {
                context: Arc::new(cpu_fallback::CpuContext::new()?)
            })
        }
    }
    
    /// Evolves quantum state using the configured backend
    ///
    /// # Errors
    /// - Returns GPU-specific errors during computation
    pub async fn evolve_state(&self, state: &mut QuantumState, gate: u32) -> Result<()> {
        self.context.process_quantum_state(state, gate)
    }
}
}

