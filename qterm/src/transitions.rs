use std::time::{Duration, Instant};
use metal;
use crate::emotions::EmotionalState;

pub struct Transition {
    start_time: Instant,
    duration: Duration,
    from_state: TransitionState,
    to_state: TransitionState,
    interpolator: Box<dyn Fn(f32) -> f32>,
}

impl Transition {
    pub fn new(
        from_state: TransitionState,
        to_state: TransitionState,
        duration: Duration,
    ) -> Self {
        Self {
            start_time: Instant::now(),
            duration,
            from_state,
            to_state,
            interpolator: Box::new(|t| t * t * (3.0 - 2.0 * t)), // Smooth step
        }
    }

    pub fn progress(&self) -> f32 {
        let elapsed = self.start_time.elapsed();
        if elapsed >= self.duration {
            1.0
        } else {
            (elapsed.as_secs_f32() / self.duration.as_secs_f32()).min(1.0)
        }
    }

    pub fn current_state(&self) -> TransitionState {
        let t = (self.interpolator)(self.progress());
        self.from_state.interpolate(&self.to_state, t)
    }
}

pub struct TransitionState {
    pub emotional_state: EmotionalState,
    pub field_intensity: f32,
    pub color_palette: ColorPalette,
}

impl TransitionState {
    fn interpolate(&self, other: &TransitionState, t: f32) -> TransitionState {
        TransitionState {
            emotional_state: self.emotional_state.interpolate(&other.emotional_state, t),
            field_intensity: self.field_intensity * (1.0 - t) + other.field_intensity * t,
            color_palette: self.color_palette.interpolate(&other.color_palette, t),
        }
    }
}

pub struct ColorPalette {
    primary: [f32; 4],
    secondary: [f32; 4],
    accent: [f32; 4],
}

impl ColorPalette {
    fn interpolate(&self, other: &ColorPalette, t: f32) -> ColorPalette {
        ColorPalette {
            primary: interpolate_color(self.primary, other.primary, t),
            secondary: interpolate_color(self.secondary, other.secondary, t),
            accent: interpolate_color(self.accent, other.accent, t),
        }
    }
}

fn interpolate_color(c1: [f32; 4], c2: [f32; 4], t: f32) -> [f32; 4] {
    [
        c1[0] * (1.0 - t) + c2[0] * t,
        c1[1] * (1.0 - t) + c2[1] * t,
        c1[2] * (1.0 - t) + c2[2] * t,
        c1[3] * (1.0 - t) + c2[3] * t,
    ]
}

