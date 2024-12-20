use std::time::{Duration, Instant};

pub struct Animation {
    start_time: Instant,
    duration: Duration,
    elapsed: Duration,
    easing: EasingFunction,
}

pub enum EasingFunction {
    Linear,
    EaseIn,
    EaseOut,
    EaseInOut,
    Bounce,
    Elastic,
}

impl Animation {
    pub fn new(duration: Duration, easing: EasingFunction) -> Self {
        Self {
            start_time: Instant::now(),
            duration,
            elapsed: Duration::from_secs(0),
            easing,
        }
    }
    
    pub fn progress(&self) -> f64 {
        let progress = self.elapsed.as_secs_f64() / self.duration.as_secs_f64();
        match self.easing {
            EasingFunction::Linear => progress,
            EasingFunction::EaseIn => progress * progress,
            EasingFunction::EaseOut => -(progress * (progress - 2.0)),
            EasingFunction::EaseInOut => {
                if progress < 0.5 {
                    2.0 * progress * progress
                } else {
                    -1.0 + (4.0 - 2.0 * progress) * progress
                }
            },
            EasingFunction::Bounce => {
                let t = 1.0 - progress;
                1.0 - (t * t * t - t * f64::sin(t * std::f64::consts::PI))
            },
            EasingFunction::Elastic => {
                let t = progress - 1.0;
                -(2.0f64.powf(-10.0 * t) * f64::sin((t - 0.075) * 2.0 * std::f64::consts::PI / 0.3))
            },
        }
    }
    
    pub fn update(&mut self) {
        self.elapsed = Instant::now().duration_since(self.start_time);
    }
    
    pub fn is_complete(&self) -> bool {
        self.elapsed >= self.duration
    }
}

pub struct AnimationManager {
    animations: Vec<Animation>,
}

impl AnimationManager {
    pub fn new() -> Self {
        Self {
            animations: Vec::new(),
        }
    }
    
    pub fn add_animation(&mut self, duration: Duration, easing: EasingFunction) {
        self.animations.push(Animation::new(duration, easing));
    }
    
    pub fn update(&mut self) {
        for animation in &mut self.animations {
            animation.update();
        }
        self.animations.retain(|a| !a.is_complete());
    }
    
    pub fn get_progress(&self, index: usize) -> Option<f64> {
        self.animations.get(index).map(|a| a.progress())
    }
}

