use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct EmotionalState {
    intensity: f32,
    calmness: f32,
    energy: f32,
    coherence: f32,
    primary_color: [f32; 4],
    secondary_color: [f32; 4],
    last_update: Arc<AtomicU64>,
}

impl EmotionalState {
    pub fn new() -> Self {
        Self {
            intensity: 0.5,
            calmness: 0.5,
            energy: 0.5,
            coherence: 0.5,
            primary_color: [0.2, 0.6, 1.0, 1.0],
            secondary_color: [0.8, 0.3, 0.9, 1.0],
            last_update: Arc::new(AtomicU64::new(0)),
        }
    }

    pub fn update(&mut self, delta_time: f32) {
        // Update emotional state based on system events and user interaction
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        
        self.last_update.store(current_time, Ordering::SeqCst);
        
        // Smooth transitions for emotional parameters
        self.intensity = smooth_transition(self.intensity, target_intensity(), delta_time);
        self.calmness = smooth_transition(self.calmness, target_calmness(), delta_time);
        self.energy = smooth_transition(self.energy, target_energy(), delta_time);
        self.coherence = smooth_transition(self.coherence, target_coherence(), delta_time);
        
        // Update colors based on emotional state
        self.update_colors();
    }

    fn update_colors(&mut self) {
        // Adjust colors based on emotional parameters
        let hue = (self.energy * 360.0).fract();
        let saturation = self.intensity;
        let value = self.coherence;
        
        self.primary_color = hsv_to_rgb(hue, saturation, value);
        self.secondary_color = hsv_to_rgb((hue + 0.5).fract(), 
                                        saturation * 0.8,
                                        value * 1.2);
    }
    
    pub fn get_shader_uniforms(&self) -> EmotionalUniforms {
        EmotionalUniforms {
            intensity: self.intensity,
            calmness: self.calmness,
            energy: self.energy,
            coherence: self.coherence,
            primary_color: self.primary_color,
            secondary_color: self.secondary_color,
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct EmotionalUniforms {
    pub intensity: f32,
    pub calmness: f32,
    pub energy: f32,
    pub coherence: f32,
    pub primary_color: [f32; 4],
    pub secondary_color: [f32; 4],
}

fn smooth_transition(current: f32, target: f32, delta_time: f32) -> f32 {
    current + (target - current) * (1.0 - (-5.0 * delta_time).exp())
}

fn target_intensity() -> f32 {
    // Implement based on system state and user interaction
    0.7
}

fn target_calmness() -> f32 {
    // Implement based on system load and stability
    0.6
}

fn target_energy() -> f32 {
    // Implement based on computation intensity and activity
    0.8
}

fn target_coherence() -> f32 {
    // Implement based on system consistency and predictability
    0.9
}

fn hsv_to_rgb(h: f32, s: f32, v: f32) -> [f32; 4] {
    let c = v * s;
    let x = c * (1.0 - ((h * 6.0) % 2.0 - 1.0).abs());
    let m = v - c;

    let (r, g, b) = match (h * 6.0).floor() as i32 {
        0 => (c, x, 0.0),
        1 => (x, c, 0.0),
        2 => (0.0, c, x),
        3 => (0.0, x, c),
        4 => (x, 0.0, c),
        _ => (c, 0.0, x),
    };

    [r + m, g + m, b + m, 1.0]
}

