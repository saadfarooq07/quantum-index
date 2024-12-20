use std::time::{Instant, Duration};

pub struct Achievement {
    pub title: String,
    pub description: String,
    pub shown_at: Instant,
    pub icon: Option<String>,
    pub category: AchievementCategory,
}

pub enum AchievementCategory {
    Command,
    ModelSelection, 
    Quantum,
    Debug,
    Expert
}

pub struct AchievementManager {
    achievements: Vec<Achievement>,
    notification_duration: Duration,
    max_notifications: usize,
}

impl AchievementManager {
    pub fn new() -> Self {
        Self {
            achievements: Vec::new(),
            notification_duration: Duration::from_secs(5),
            max_notifications: 3,
        }
    }
    
    pub fn add_achievement(&mut self, title: &str, description: &str, category: AchievementCategory) {
        self.achievements.push(Achievement {
            title: title.to_string(),
            description: description.to_string(),
            shown_at: Instant::now(),
            icon: None,
            category,
        });
        
        // Trim old notifications
        if self.achievements.len() > self.max_notifications {
            self.achievements.remove(0);
        }
    }
    
    pub fn get_active_notifications(&self) -> Vec<&Achievement> {
        let now = Instant::now();
        self.achievements.iter()
            .filter(|a| now.duration_since(a.shown_at) < self.notification_duration)
            .collect()
    }
    
    pub fn clear_old_notifications(&mut self) {
        let now = Instant::now();
        self.achievements.retain(|a| now.duration_since(a.shown_at) < self.notification_duration);
    }
}

