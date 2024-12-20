use std::time::{Duration, Instant};
use ratatui::style::Color;

pub struct Effect {
    start_time: Instant,
    duration: Duration,
    effect_type: EffectType,
    position: (f32, f32),
}

pub enum EffectType {
    Achievement(String),
    ColorTransition(Color, Color),
    ParticleExplosion,
    QuantumWave,
    StateTransition,
}

pub struct EffectSystem {
    active_effects: Vec<Effect>,
    background_particles: Vec<Particle>, 
    quantum_state: f32,
    last_update: Instant,
}

impl EffectSystem {
    pub fn new() -> Self {
        Self {
            active_effects: Vec::new(),
            background_particles: Vec::new(),
            quantum_state: 0.0,
            last_update: Instant::now(),
        }
    }

    pub fn add_achievement(&mut self, message: String) {
        self.active_effects.push(Effect {
            start_time: Instant::now(),
            duration: Duration::from_secs(3),
            effect_type: EffectType::Achievement(message),
            position: (0.5, 0.1), // Top center
        });
    }

    pub fn add_color_transition(&mut self, from: Color, to: Color, pos: (f32, f32)) {
        self.active_effects.push(Effect {
            start_time: Instant::now(),
            duration: Duration::from_millis(500),
            effect_type: EffectType::ColorTransition(from, to),
            position: pos,
        });
    }

    pub fn add_particles(&mut self, pos: (f32, f32)) {
        self.active_effects.push(Effect {
            start_time: Instant::now(),
            duration: Duration::from_millis(1000),
            effect_type: EffectType::ParticleExplosion,
            position: pos,
        });
    }

    pub fn update(&mut self, dt: Duration) -> Vec<Effect> {
        let now = Instant::now();
        self.quantum_state = (self.quantum_state + dt.as_secs_f32() * 2.0) % std::f32::consts::TAU;
        
        // Update background particles
        for particle in &mut self.background_particles {
            particle.update(dt);
        }

        // Remove expired effects
        self.active_effects.retain(|effect| {
            now.duration_since(effect.start_time) < effect.duration
        });

        self.active_effects.clone()
    }

    pub fn get_quantum_color(&self) -> Color {
        let r = ((self.quantum_state).sin() * 127.0 + 128.0) as u8;
        let g = ((self.quantum_state + 2.0*std::f32::consts::PI/3.0).sin() * 127.0 + 128.0) as u8;
        let b = ((self.quantum_state + 4.0*std::f32::consts::PI/3.0).sin() * 127.0 + 128.0) as u8;
        Color::Rgb(r, g, b)
    }
}

