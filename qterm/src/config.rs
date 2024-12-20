use std::path::PathBuf;
use metal::DeviceRef;
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("Invalid quantum state parameters: {0}")]
    InvalidQuantumState(String),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Invalid configuration: {0}")]
    ValidationError(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub gpu: GpuConfig,
    pub quantum: QuantumConfig,
    pub visualization: VisualizationConfig,
    pub performance: PerformanceConfig,
    pub paths: PathConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuConfig {
    pub backend: GpuBackend,
    pub metal: Option<MetalConfig>,
    pub cuda: Option<CudaConfig>,
    pub opencl: Option<OpenClConfig>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum GpuBackend {
    Metal,
    Cuda,
    OpenCL,
    CPU,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetalConfig {
    pub max_buffer_length: usize,
    pub preferred_device: Option<String>,
    pub threading_model: ThreadingModel,
    pub transition_quality: TransitionQuality,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CudaConfig {
    pub device_id: Option<i32>,
    pub max_memory_mb: usize,
    pub stream_count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)] 
pub struct OpenClConfig {
    pub platform_id: Option<i32>,
    pub device_id: Option<i32>,
    pub queue_size: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuantumConfig {
    pub state_vector_size: usize,
    pub precision: Precision,
    pub max_entanglement: usize,
    pub measurement_strategy: MeasurementStrategy,
    pub noise_model: Option<NoiseModel>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VisualizationConfig {
    pub render_mode: RenderMode,
    pub color_scheme: ColorScheme,
    pub animation_speed: f32,
    pub phase_visualization: bool,
    pub probability_threshold: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceConfig {
    pub threading_model: ThreadingModel,
    pub transition_quality: TransitionQuality,
    pub batch_size: usize,
    pub cache_size_mb: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PathConfig {
    pub shader_dir: PathBuf,
    pub cache_dir: PathBuf,
    pub log_dir: PathBuf,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum ThreadingModel {
    Single,
    Multi(usize),
    Adaptive,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum TransitionQuality {
    Low,
    Medium,
    High,
    Adaptive,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum Precision {
    Single,
    Double,
    Mixed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MeasurementStrategy {
    Standard,
    Weak,
    Continuous,
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NoiseModel {
    pub decoherence_rate: f64,
    pub gate_error_rates: std::collections::HashMap<String, f64>,
    pub custom_parameters: std::collections::HashMap<String, f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RenderMode {
    Bloch,
    StateVector,
    DensityMatrix,
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ColorScheme {
    Standard,
    Scientific,
    Accessible,
    Custom(Vec<String>),
}

impl Default for Config {
    fn default() -> Self {
        Self {
            gpu: GpuConfig {
                backend: GpuBackend::CPU,
                metal: Some(MetalConfig {
                    max_buffer_length: 1024 * 1024,
                    preferred_device: None,
                    threading_model: ThreadingModel::Adaptive,
                    transition_quality: TransitionQuality::Adaptive,
                }),
                cuda: None,
                opencl: None,
            },
            quantum: QuantumConfig {
                state_vector_size: 1024,
                precision: Precision::Double,
                max_entanglement: 16,
                measurement_strategy: MeasurementStrategy::Standard,
                noise_model: None,
            },
            visualization: VisualizationConfig {
                render_mode: RenderMode::Bloch,
                color_scheme: ColorScheme::Standard,
                animation_speed: 1.0,
                phase_visualization: true,
                probability_threshold: 1e-6,
            },
            performance: PerformanceConfig {
                threading_model: ThreadingModel::Adaptive,
                transition_quality: TransitionQuality::Adaptive,
                batch_size: 1000,
                cache_size_mb: 512,
            },
            paths: PathConfig {
                shader_dir: PathBuf::from("resources/shaders"),
                cache_dir: PathBuf::from("cache"),
                log_dir: PathBuf::from("logs"),
            },
        }
    }
}

impl Config {
    pub fn load(path: impl AsRef<std::path::Path>) -> Result<Self, ConfigError> {
        let file = std::fs::File::open(path)?;
        let config: Config = serde_json::from_reader(file)?;
        config.validate()?;
        Ok(config)
    }

    pub fn save(&self, path: impl AsRef<std::path::Path>) -> Result<(), ConfigError> {
        let file = std::fs::File::create(path)?;
        serde_json::to_writer_pretty(file, self)?;
        Ok(())
    }

    pub fn validate(&self) -> Result<(), ConfigError> {
        if self.quantum.state_vector_size == 0 {
            return Err(ConfigError::ValidationError(
                "State vector size must be greater than 0".to_string(),
            ));
        }
        if self.visualization.probability_threshold <= 0.0 
            || self.visualization.probability_threshold > 1.0 {
            return Err(ConfigError::ValidationError(
                "Probability threshold must be between 0 and 1".to_string(),
            ));
        }
        Ok(())
    }

    pub fn optimize_for_device(&mut self, device: &DeviceRef) {
        if let Some(metal_config) = &mut self.gpu.metal {
            let name = device.name().to_string();
            metal_config.preferred_device = Some(name);
            
            let recommended_threads = device.recommended_max_working_threads();
            metal_config.threading_model = if recommended_threads > 1 {
                ThreadingModel::Multi(recommended_threads)
            } else {
                ThreadingModel::Single
            };
        }
    }
}
