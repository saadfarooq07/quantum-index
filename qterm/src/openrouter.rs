use reqwest::{Client, Error as ReqwestError};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::RwLock;

const OPENROUTER_API_URL: &str = "https://openrouter.ai/api/v1";
const CACHE_DURATION: Duration = Duration::from_secs(3600); // 1 hour

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelInfo {
    pub id: String,
    pub name: String,
    pub max_tokens: usize,
    pub pricing: ModelPricing,
    pub performance_metrics: PerformanceMetrics,
    pub last_used: Option<Instant>,
    pub cached_until: Option<Instant>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelPricing {
    pub prompt_tokens: f64,
    pub completion_tokens: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub avg_latency_ms: f64,
    pub success_rate: f64,
    pub total_requests: usize,
    pub last_error: Option<String>,
}

#[derive(Clone)]
pub struct OpenRouterClient {
    client: Client,
    api_key: String,
    models_cache: Arc<RwLock<HashMap<String, ModelInfo>>>,
    current_model: Arc<RwLock<Option<String>>>,
    metrics: Arc<RwLock<HashMap<String, PerformanceMetrics>>>,
}

impl OpenRouterClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
            models_cache: Arc::new(RwLock::new(HashMap::new())),
            current_model: Arc::new(RwLock::new(None)),
            metrics: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub async fn list_models(&self) -> Result<Vec<ModelInfo>, ReqwestError> {
        let cached = self.get_cached_models().await;
        if !cached.is_empty() {
            return Ok(cached);
        }

        let response = self.client
            .get(&format!("{}/models", OPENROUTER_API_URL))
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await?
            .json::<Vec<ModelInfo>>()
            .await?;

        self.update_cache(response.clone()).await;
        Ok(response)
    }

    pub async fn select_model(&self, model_id: &str) -> Result<(), String> {
        let models = self.list_models().await
            .map_err(|e| format!("Failed to fetch models: {}", e))?;

        if !models.iter().any(|m| m.id == model_id) {
            return Err(format!("Model {} not found", model_id));
        }

        let mut current = self.current_model.write().await;
        *current = Some(model_id.to_string());
        Ok(())
    }

    pub async fn get_current_model(&self) -> Option<ModelInfo> {
        let current = self.current_model.read().await;
        if let Some(model_id) = &*current {
            let cache = self.models_cache.read().await;
            return cache.get(model_id).cloned();
        }
        None
    }

    pub async fn get_model_metrics(&self, model_id: &str) -> Option<PerformanceMetrics> {
        let metrics = self.metrics.read().await;
        metrics.get(model_id).cloned()
    }

    async fn get_cached_models(&self) -> Vec<ModelInfo> {
        let cache = self.models_cache.read().await;
        let now = Instant::now();
        
        cache.values()
            .filter(|m| m.cached_until.map_or(false, |t| t > now))
            .cloned()
            .collect()
    }

    async fn update_cache(&self, models: Vec<ModelInfo>) {
        let mut cache = self.models_cache.write().await;
        let now = Instant::now();
        
        for model in models {
            let mut model = model;
            model.cached_until = Some(now + CACHE_DURATION);
            cache.insert(model.id.clone(), model);
        }
    }

    pub async fn update_metrics(&self, model_id: &str, latency: Duration, success: bool, error: Option<String>) {
        let mut metrics = self.metrics.write().await;
        let model_metrics = metrics.entry(model_id.to_string())
            .or_insert(PerformanceMetrics {
                avg_latency_ms: 0.0,
                success_rate: 1.0,
                total_requests: 0,
                last_error: None,
            });

        let total = model_metrics.total_requests as f64;
        model_metrics.avg_latency_ms = (model_metrics.avg_latency_ms * total + latency.as_millis() as f64) / (total + 1.0);
        model_metrics.total_requests += 1;
        model_metrics.success_rate = ((model_metrics.success_rate * total + if success { 1.0 } else { 0.0 }) / (total + 1.0));
        model_metrics.last_error = error;
    }
}

