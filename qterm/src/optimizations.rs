use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use metal::Device;

pub struct ResourceOptimizer {
    device: Arc<Device>,
    particle_budget: AtomicU64,
    compute_budget: AtomicU64,
}

impl ResourceOptimizer {
    pub fn new(device: Arc<Device>) -> Self {
        Self {
            device,
            particle_budget: AtomicU64::new(1000000),
            compute_budget: AtomicU64::new(1000),
        }
    }

    pub fn adjust_particle_budget(&self, coherence: f32) {
        let new_budget = (coherence * 2000000.0) as u64;
        self.particle_budget.store(new_budget, Ordering::Relaxed);
    }

    pub fn get_particle_budget(&self) -> u64 {
        self.particle_budget.load(Ordering::Relaxed)
    }

    pub fn optimize_compute(&self, workload: f32) {
        let base_budget = 1000;
        let scaled_budget = (workload * base_budget as f32) as u64;
        self.compute_budget.store(scaled_budget, Ordering::Relaxed);
    }

    pub fn get_compute_budget(&self) -> u64 {
        self.compute_budget.load(Ordering::Relaxed)
    }

    pub fn monitor_resources(&self) -> ResourceStats {
        ResourceStats {
            memory_available: self.device.recommended_max_working_set_size() as f64,
            compute_units: self.device.max_threads_per_threadgroup(0) as u32,
            current_particle_budget: self.get_particle_budget(),
            current_compute_budget: self.get_compute_budget(),
        }
    }
}

pub struct ResourceStats {
    pub memory_available: f64,
    pub compute_units: u32,
    pub current_particle_budget: u64,
    pub current_compute_budget: u64,
}

