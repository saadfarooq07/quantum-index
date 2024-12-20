use std::time::Duration;
use ratatui::style::Color;
use rand::{self, Rng};

pub struct Particle {
    pos: (f32, f32),
    vel: (f32, f32),
    color: Color,
    lifetime: Duration,
    age: Duration,
    quantum_state: f32,
}

impl Particle {
    pub fn new(pos: (f32, f32)) -> Self {
        let mut rng = rand::thread_rng();
        let angle = rng.gen_range(0.0..std::f32::consts::TAU);
        let speed = rng.gen_range(0.5..2.0);
        
        Self {
            pos,
            vel: (angle.cos() * speed, angle.sin() * speed),
            color: Color::Rgb(
                rng.gen_range(128..255),
                rng.gen_range(128..255),
                rng.gen_range(128..255)
            ),
            lifetime: Duration::from_millis(rng.gen_range(500..2000)),
            age: Duration::ZERO,
            quantum_state: rng.gen_range(0.0..std::f32::consts::TAU),
        }
    }

    pub fn update(&mut self, dt: Duration) {
        self.age += dt;
        self.quantum_state = (self.quantum_state + dt.as_secs_f32()) % std::f32::consts::TAU;
        
        // Quantum-inspired movement
        let quantum_influence = self.quantum_state.sin() * 0.2;
        self.pos.0 += self.vel.0 * (1.0 + quantum_influence);
        self.pos.1 += self.vel.1 * (1.0 + quantum_influence);
        
        // Update color based on quantum state
        let life_ratio = self.age.as_secs_f32() / self.lifetime.as_secs_f32();
        if let Color::Rgb(r, g, b) = self.color {
            let fade = 1.0 - life_ratio;
            let quantum_color = (self.quantum_state * 127.0 + 128.0) as u8;
            self.color = Color::Rgb(
                (r as f32 * fade) as u8,
                ((g as f32 * 0.8 + quantum_color as f32 * 0.2) * fade) as u8,
                (b as f32 * fade) as u8
            );
        }
    }

    pub fn is_alive(&self) -> bool {
        self.age < self.lifetime
    }
}

pub struct ParticleSystem {
    particles: Vec<Particle>,
    emit_rate: f32,
    emit_timer: f32,
}

impl ParticleSystem {
    pub fn new(emit_rate: f32) -> Self {
        Self {
            particles: Vec::new(),
            emit_rate,
            emit_timer: 0.0,
        }
    }

    pub fn update(&mut self, dt: Duration) {
        // Update existing particles
        self.particles.retain_mut(|p| {
            p.update(dt);
            p.is_alive()
        });

        // Emit new particles
        self.emit_timer += dt.as_secs_f32();
        while self.emit_timer >= 1.0 / self.emit_rate {
            self.emit_timer -= 1.0 / self.emit_rate;
            if self.particles.len() < 1000 {
                let mut rng = rand::thread_rng();
                self.particles.push(Particle::new((
                    rng.gen_range(0.0..1.0),
                    rng.gen_range(0.0..1.0)
                )));
            }
        }
    }
}

