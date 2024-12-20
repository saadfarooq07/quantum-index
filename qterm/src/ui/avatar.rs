use ratatui::{ 
    backend::Backend,
    buffer::Buffer,
    layout::Rect,
    widgets::Widget,
    style::Color
};
use std::time::Instant;

pub struct AvatarState {
    // Visual characteristics driven by embeddings
    energy: f64,
    complexity: f64,
    harmony: f64,
    evolution_stage: f64,
    
    // Animation state
    last_update: Instant,
    transition_progress: f64,
    pattern_phase: f64,
    
    // Pattern generation
    pattern_seeds: Vec<f64>,
    color_palette: Vec<Color>,
}

impl Default for AvatarState {
    fn default() -> Self {
        Self {
            energy: 0.5,
            complexity: 0.5, 
            harmony: 0.5,
            evolution_stage: 0.0,
            
            last_update: Instant::now(),
            transition_progress: 0.0,
            pattern_phase: 0.0,
            
            pattern_seeds: vec![0.0; 8],
            color_palette: vec![
                Color::Rgb(20, 40, 80),   // Deep blue
                Color::Rgb(40, 100, 120), // Teal
                Color::Rgb(80, 160, 200), // Light blue 
                Color::Rgb(160, 200, 220) // Sky blue
            ]
        }
    }
}

impl AvatarState {
    pub fn update_from_embeddings(&mut self, embeddings: &[f64]) {
        let now = Instant::now();
        let dt = now.duration_since(self.last_update).as_secs_f64();
        
        // Map embeddings to visual characteristics
        if embeddings.len() >= 3 {
            let target_energy = embeddings[0].abs();
            let target_complexity = embeddings[1].abs();
            let target_harmony = embeddings[2].abs();
            
            // Smooth transitions
            self.energy += (target_energy - self.energy) * dt;
            self.complexity += (target_complexity - self.complexity) * dt;
            self.harmony += (target_harmony - self.harmony) * dt;
        }
        
        // Update animation state
        self.pattern_phase = (self.pattern_phase + dt * self.energy) % std::f64::consts::PI;
        self.evolution_stage += dt * 0.1 * self.complexity;
        
        // Generate new pattern seeds
        for seed in &mut self.pattern_seeds {
            *seed = (*seed + dt * self.harmony).sin();
        }
        
        self.last_update = now;
    }
    
    fn get_pattern_color(&self, x: f64, y: f64) -> Color {
        // Generate biological-inspired patterns using pattern_seeds
        let px = x * std::f64::consts::PI * 2.0;
        let py = y * std::f64::consts::PI * 2.0;
        
        let pattern_val = self.pattern_seeds.iter().enumerate()
            .map(|(i, &seed)| {
                let freq = (i + 1) as f64 * self.complexity;
                (px * freq + seed).sin() * (py * freq).cos()
            })
            .sum::<f64>() / self.pattern_seeds.len() as f64;
            
        // Blend colors based on pattern value
        let idx = ((pattern_val + 1.0) * 0.5 * (self.color_palette.len() - 1) as f64) as usize;
        self.color_palette[idx.min(self.color_palette.len() - 1)]
    }
}

pub struct Avatar<'a> {
    state: &'a mut AvatarState,
}

impl<'a> Avatar<'a> {
    pub fn new(state: &'a mut AvatarState) -> Self {
        Self { state }
    }
}

impl<'a> Widget for Avatar<'a> {
    fn render(self, area: Rect, buf: &mut Buffer) {
        // Render the generative avatar patterns
        for y in area.top()..area.bottom() {
            for x in area.left()..area.right() {
                let rel_x = (x - area.left()) as f64 / area.width as f64;
                let rel_y = (y - area.top()) as f64 / area.height as f64;
                
                let color = self.state.get_pattern_color(rel_x, rel_y);
                buf.get_mut(x, y).set_bg(color);
            }
        }
    }
}

