use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};
use tokio::sync::RwLock;
use tracing::{debug, error, info};

#[derive(Debug, Default)]
pub struct MetalMetrics {
    compute_time: AtomicU64,
    memory_usage: AtomicU64,
    gpu_utilization: AtomicU64,
}

#[derive(Debug, Default)]
pub struct StateMetrics {
    transitions: AtomicU64,
    sync_time: AtomicU64,
    state_size: AtomicU64,
}

#[derive(Debug)]
pub struct PerformanceMetrics {
    metal: MetalMetrics,
    state: StateMetrics,
    start_time: Instant,
    samples: RwLock<Vec<Duration>>,
}

impl PerformanceMetrics {
    pub fn new() -> Self {
        Self {
            metal: MetalMetrics::default(),
            state: StateMetrics::default(),
            start_time: Instant::now(),
            samples: RwLock::new(Vec::with_capacity(1000)),
        }
    }

    pub async fn record_compute_time(&self, duration: Duration) {
        self.metal.compute_time.fetch_add(duration.as_micros() as u64, Ordering::Relaxed);
        let mut samples = self.samples.write().await;
        samples.push(duration);
        if samples.len() >= 1000 {
            samples.remove(0);
        }
    }

    pub fn update_gpu_metrics(&self, memory: u64, utilization: u64) {
        self.metal.memory_usage.store(memory, Ordering::Relaxed);
        self.metal.gpu_utilization.store(utilization, Ordering::Relaxed);
    }

    pub fn record_state_transition(&self, duration: Duration, size: u64) {
        self.state.transitions.fetch_add(1, Ordering::Relaxed);
        self.state.sync_time.fetch_add(duration.as_micros() as u64, Ordering::Relaxed);
        self.state.state_size.store(size, Ordering::Relaxed);
    }

    pub async fn get_performance_summary(&self) -> String {
        let uptime = self.start_time.elapsed();
        let samples = self.samples.read().await;
        let avg_compute = if !samples.is_empty() {
            samples.iter().sum::<Duration>().as_micros() as f64 / samples.len() as f64
        } else {
            0.0
        };

        format!(
            "Performance Metrics:\n\
            Uptime: {:?}\n\
            Avg Compute Time: {:.2}µs\n\
            GPU Memory: {}MB\n\
            GPU Utilization: {}%\n\
            State Transitions: {}\n\
            Avg Sync Time: {:.2}µs",
            uptime,
            avg_compute,
            self.metal.memory_usage.load(Ordering::Relaxed) / (1024 * 1024),
            self.metal.gpu_utilization.load(Ordering::Relaxed),
            self.state.transitions.load(Ordering::Relaxed),
            self.state.sync_time.load(Ordering::Relaxed) as f64 /
                self.state.transitions.load(Ordering::Relaxed).max(1) as f64
        )
    }
}

