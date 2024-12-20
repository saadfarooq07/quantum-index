use std::sync::Arc;
use tokio::sync::RwLock;
use log::{info, warn, error, debug};
use anyhow::{Result, Context};

use crate::error::QuantumError;
use crate::config::Config;
use crate::quantum_state::QuantumState;
use crate::quantum_bridge::QuantumBridge;
use crate::quantum_renderer::QuantumRenderer;

pub struct InitializationGuard {
    quantum_bridge: Arc<RwLock<QuantumBridge>>,
    quantum_renderer: Arc<RwLock<QuantumRenderer>>,
    config: Arc<RwLock<Config>>,
}

impl Drop for InitializationGuard {
    fn drop(&mut self) {
        info!("Shutting down quantum terminal...");
        if let Err(e) = self.cleanup() {
            error!("Error during cleanup: {}", e);
        }
    }
}

impl InitializationGuard {
    async fn cleanup(&self) -> Result<(), QuantumError> {
        debug!("Starting cleanup sequence");
        
        // Acquire write locks for cleanup
        let mut bridge = self.quantum_bridge.write().await;
        let mut renderer = self.quantum_renderer.write().await;
        
        renderer.cleanup().await?;
        bridge.cleanup().await?;
        
        debug!("Cleanup completed successfully");
        Ok(())
    }
}

pub async fn initialize() -> Result<InitializationGuard, QuantumError> {
    info!("Initializing quantum terminal...");
    
    // Initialize logging
    setup_logging()?;
    
    // Load configuration
    let config = Arc::new(RwLock::new(Config::load()
        .context("Failed to load configuration")?));
    
    // Initialize GPU
    let gpu_info = detect_gpu().await?;
    info!("Detected GPU: {:?}", gpu_info);
    
    // Initialize quantum bridge with GPU support
    let quantum_bridge = Arc::new(RwLock::new(QuantumBridge::new(
        gpu_info,
        config.clone(),
    ).await?));
    
    // Initialize quantum renderer
    let quantum_renderer = Arc::new(RwLock::new(QuantumRenderer::new(
        gpu_info,
        config.clone(),
    ).await?));
    
    // Initialize quantum state
    let initial_state = QuantumState::new_default()
        .context("Failed to initialize quantum state")?;
    
    // Configure visualization pipeline
    {
        let mut renderer = quantum_renderer.write().await;
        renderer.configure_pipeline(&initial_state)
            .context("Failed to configure visualization pipeline")?;
    }
    
    info!("Initialization completed successfully");
    
    Ok(InitializationGuard {
        quantum_bridge,
        quantum_renderer,
        config,
    })
}

async fn detect_gpu() -> Result<GpuInfo, QuantumError> {
    #[cfg(feature = "metal")]
    {
        if let Ok(info) = detect_metal_gpu().await {
            return Ok(info);
        }
    }
    
    #[cfg(feature = "cuda")]
    {
        if let Ok(info) = detect_cuda_gpu().await {
            return Ok(info);
        }
    }
    
    #[cfg(feature = "opencl")]
    {
        if let Ok(info) = detect_opencl_gpu().await {
            return Ok(info);
        }
    }
    
    warn!("No GPU acceleration available, falling back to CPU");
    Ok(GpuInfo::cpu_fallback())
}

fn setup_logging() -> Result<(), QuantumError> {
    let log_config = log4rs::config::Config::builder()
        .appender(
            log4rs::config::Appender::builder()
                .build("stdout", Box::new(log4rs::append::console::ConsoleAppender::builder().build()))
        )
        .build(log4rs::config::Root::builder().appender("stdout").build(log::LevelFilter::Info))
        .context("Failed to build logging config")?;
    
    log4rs::init_config(log_config)
        .context("Failed to initialize logging")?;
    
    Ok(())
}

#[derive(Debug)]
pub struct GpuInfo {
    device_type: GpuType,
    device_name: String,
    compute_units: u32,
    memory_size: u64,
}

#[derive(Debug)]
pub enum GpuType {
    Metal,
    Cuda,
    OpenCL,
    CPU,
}

impl GpuInfo {
    fn cpu_fallback() -> Self {
        GpuInfo {
            device_type: GpuType::CPU,
            device_name: "CPU Fallback".to_string(),
            compute_units: num_cpus::get() as u32,
            memory_size: sys_info::mem_info()
                .map(|info| info.total * 1024)
                .unwrap_or(0),
        }
    }
}

