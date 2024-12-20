#[cfg(feature = "metal")]
use metal;
use std::sync::Arc;
use std::error::Error;
use std::fmt;
use crate::monitor::MetalResourceMonitor;

#[derive(Debug)]
pub enum QuantumRenderError {
    DeviceError(String),
    PipelineError(String),
    StateError(String),
    RenderError(String),
}

impl fmt::Display for QuantumRenderError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::DeviceError(msg) => write!(f, "Device error: {}", msg),
            Self::PipelineError(msg) => write!(f, "Pipeline error: {}", msg),
            Self::StateError(msg) => write!(f, "State error: {}", msg),
            Self::RenderError(msg) => write!(f, "Render error: {}", msg),
        }
    }
}

impl Error for QuantumRenderError {}

pub type Result<T> = std::result::Result<T, QuantumRenderError>;

pub struct QuantumRenderer {
    device: Arc<metal::Device>,
    pipeline_state: metal::RenderPipelineState,
    emotion_weight: f32,
    command_queue: metal::CommandQueue,
}

/// Represents the quantum state for visualization
#[derive(Debug, Clone)]
pub struct QuantumState {
    /// Wave function amplitude (must be between 0 and 1)
    amplitude: f32,
    /// Phase angle in radians
    phase: f32,
    /// Entanglement factor (0 = none, 1 = fully entangled)
    entanglement: f32,
    /// Emotional influence factor
    emotional_influence: f32,
}

impl QuantumState {
    pub fn new(amplitude: f32, phase: f32, entanglement: f32, emotional_influence: f32) -> Result<Self> {
        if !(0.0..=1.0).contains(&amplitude) {
            return Err(QuantumRenderError::StateError("Amplitude must be between 0 and 1".into()));
        }
        if !(-std::f32::consts::PI..=std::f32::consts::PI).contains(&phase) {
            return Err(QuantumRenderError::StateError("Phase must be between -π and π".into()));
        }
        if !(0.0..=1.0).contains(&entanglement) {
            return Err(QuantumRenderError::StateError("Entanglement must be between 0 and 1".into()));
        }
        if !(0.0..=1.0).contains(&emotional_influence) {
            return Err(QuantumRenderError::StateError("Emotional influence must be between 0 and 1".into()));
        }

        Ok(Self {
            amplitude,
            phase,
            entanglement,
            emotional_influence,
        })
    }
}

impl QuantumRenderer {
    /// Creates a new quantum renderer instance
    #[cfg(feature = "metal")]
    pub fn new(monitor: &MetalResourceMonitor) -> Result<Self> {
        let device = monitor.get_device();
        let command_queue = device.new_command_queue().ok_or_else(|| 
            QuantumRenderError::DeviceError("Failed to create command queue".into())
        )?;
        
        // Create Metal pipeline for quantum visualization
        let pipeline_desc = metal::RenderPipelineDescriptor::new();
        let vertex_func = device.new_function("quantum_vertex", None)
            .ok_or_else(|| QuantumRenderError::PipelineError("Failed to create vertex function".into()))?;
        let fragment_func = device.new_function("quantum_fragment", None)
            .ok_or_else(|| QuantumRenderError::PipelineError("Failed to create fragment function".into()))?;
        
        pipeline_desc.set_vertex_function(Some(&vertex_func));
        pipeline_desc.set_fragment_function(Some(&fragment_func));
        
        let pipeline_state = device.new_render_pipeline_state(&pipeline_desc)
            .map_err(|e| QuantumRenderError::PipelineError(format!("Failed to create pipeline state: {:?}", e)))?;
        
        Ok(Self {
            device,
            pipeline_state,
            emotion_weight: 0.5,
            command_queue,
        })
    }

    #[cfg(not(feature = "metal"))]
    pub fn new(_monitor: &MetalResourceMonitor) -> Result<Self> {
        Err(QuantumRenderError::DeviceError("Metal rendering is not available on this platform".into()))
    }

    #[cfg(feature = "metal")]
    pub fn render_quantum_state(&mut self, state: QuantumState) -> Result<()> {
        let pool = unsafe { cocoa::foundation::NSAutoreleasePool::new(cocoa::base::nil) };
        let command_buffer = self.command_queue.new_command_buffer()
            .ok_or_else(|| QuantumRenderError::RenderError("Failed to create command buffer".into()))?;
        
        // Set up render pass
        let desc = metal::RenderPassDescriptor::new();
        let encoder = command_buffer.new_render_command_encoder(desc)
            .ok_or_else(|| QuantumRenderError::RenderError("Failed to create render command encoder".into()))?;

        encoder.set_render_pipeline_state(&self.pipeline_state);
        
        // Update quantum state uniforms
        let uniforms = [
            state.amplitude,
            state.phase,
            state.entanglement,
            state.emotional_influence * self.emotion_weight,
        ];
        
        // SAFETY: The uniforms array is properly aligned and valid for the duration of the encoding
        encoder.set_vertex_bytes(0, std::mem::size_of_val(&uniforms) as u64, uniforms.as_ptr() as *const _);
        
        encoder.draw_primitives(metal::MTLPrimitiveType::Triangle, 0, 3);
        encoder.end_encoding();
        
        command_buffer.commit();
        
        // Clean up Objective-C autorelease pool
        unsafe { pool.drain() };
        
        Ok(())
    }

    #[cfg(not(feature = "metal"))]
    pub fn render_quantum_state(&mut self, _state: QuantumState) -> Result<()> {
        Err(QuantumRenderError::RenderError("Metal rendering is not available on this platform".into()))
    }

    pub fn update_emotional_state(&mut self, emotion: f32) {
        self.emotion_weight = emotion.max(0.0).min(1.0);
    }
}

