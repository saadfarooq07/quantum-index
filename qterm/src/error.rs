use std::fmt;
use thiserror::Error;

/// Error type for quantum terminal operations
#[derive(Error, Debug)]
pub enum QTermError {
    /// GPU-related errors
    #[error("GPU error: {kind:?} - {message}")]
    GpuError {
        kind: GpuErrorKind,
        message: String,
        #[source]
        source: Option<Box<dyn std::error::Error + Send + Sync>>,
    },

    /// Quantum state errors
    #[error("Quantum state error: {kind:?} - {message}")]
    QuantumStateError {
        kind: QuantumStateErrorKind,
        message: String,
    },

    /// Visualization and rendering errors
    #[error("Rendering error: {kind:?} - {message}")]
    RenderError {
        kind: RenderErrorKind,
        message: String,
    },

    /// Resource management errors
    #[error("Resource error: {kind:?} - {message}")]
    ResourceError {
        kind: ResourceErrorKind,
        message: String,
        path: Option<std::path::PathBuf>,
    },

    /// Shell integration errors
    #[error("Shell error: {kind:?} - {message}")]
    ShellError {
        kind: ShellErrorKind,
        message: String,
    },

    /// Performance measurement errors
    #[error("Metrics error: {kind:?} - {message}")]
    MetricsError {
        kind: MetricsErrorKind,
        message: String,
    },

    /// Command processing errors
    #[error("Command error: {kind:?} - {message}")]
    CommandError {
        kind: CommandErrorKind,
        message: String,
    },

    /// IO operations errors
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    /// Configuration errors
    #[error("Configuration error: {kind:?} - {message}")]
    ConfigError {
        kind: ConfigErrorKind,
        message: String,
    },

    /// Catch-all for unexpected errors
    #[error("Unknown error: {0}")]
    Unknown(String),
}

#[derive(Debug, Clone, PartialEq)]
pub enum GpuErrorKind {
    InitializationFailed,
    ShaderCompilationFailed,
    ResourceAllocationFailed,
    InvalidOperation,
    UnsupportedFeature,
    DeviceLost,
}

#[derive(Debug, Clone, PartialEq)]
pub enum QuantumStateErrorKind {
    InvalidState,
    DecoherenceError,
    MeasurementError,
    EntanglementError,
    EvolutionError,
}

#[derive(Debug, Clone, PartialEq)]
pub enum RenderErrorKind {
    InitializationFailed,
    ResourceCreationFailed,
    PipelineError,
    ValidationError,
    FrameSubmissionFailed,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ResourceErrorKind {
    NotFound,
    AccessDenied,
    InvalidFormat,
    AllocationFailed,
    Corrupted,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ShellErrorKind {
    CommandFailed,
    InvalidInput,
    EnvironmentError,
    PermissionDenied,
}

#[derive(Debug, Clone, PartialEq)]
pub enum MetricsErrorKind {
    CollectionFailed,
    InvalidMetric,
    ProcessingError,
}

#[derive(Debug, Clone, PartialEq)]
pub enum CommandErrorKind {
    InvalidSyntax,
    ExecutionFailed,
    Timeout,
    UnsupportedOperation,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ConfigErrorKind {
    ParseError,
    ValidationError,
    MissingField,
    TypeError,
}

/// Custom Result type for quantum terminal operations
pub type Result<T> = std::result::Result<T, QTermError>;

impl QTermError {
    /// Creates a new GPU error
    pub fn gpu_error<S: Into<String>>(
        kind: GpuErrorKind,
        message: S,
        source: Option<Box<dyn std::error::Error + Send + Sync>>,
    ) -> Self {
        Self::GpuError {
            kind,
            message: message.into(),
            source,
        }
    }

    /// Creates a new quantum state error
    pub fn quantum_error<S: Into<String>>(kind: QuantumStateErrorKind, message: S) -> Self {
        Self::QuantumStateError {
            kind,
            message: message.into(),
        }
    }

    /// Creates a new rendering error
    pub fn render_error<S: Into<String>>(kind: RenderErrorKind, message: S) -> Self {
        Self::RenderError {
            kind,
            message: message.into(),
        }
    }

    /// Creates a new resource error
    pub fn resource_error<S: Into<String>>(
        kind: ResourceErrorKind,
        message: S,
        path: Option<std::path::PathBuf>,
    ) -> Self {
        Self::ResourceError {
            kind,
            message: message.into(),
            path,
        }
    }

    /// Checks if the error is a GPU-related error
    pub fn is_gpu_error(&self) -> bool {
        matches!(self, Self::GpuError { .. })
    }

    /// Checks if the error is recoverable
    pub fn is_recoverable(&self) -> bool {
        !matches!(
            self,
            Self::GpuError {
                kind: GpuErrorKind::DeviceLost,
                ..
            } | Self::ResourceError {
                kind: ResourceErrorKind::Corrupted,
                ..
            }
        )
    }

    /// Returns the error chain as a vector of string messages
    pub fn error_chain(&self) -> Vec<String> {
        let mut chain = vec![self.to_string()];
        if let Self::GpuError { source: Some(err), .. } = self {
            let mut current = err.as_ref();
            while let Some(err) = current.source() {
                chain.push(err.to_string());
                current = err;
            }
        }
        chain
    }
}

/// Error context extension trait for Result
pub trait ErrorContextExt<T, E> {
    fn context<C, F>(self, context: F) -> Result<T>
    where
        C: Into<String>,
        F: FnOnce() -> C;
}

impl<T, E: std::error::Error + Send + Sync + 'static> ErrorContextExt<T, E> for std::result::Result<T, E> {
    fn context<C, F>(self, context: F) -> Result<T>
    where
        C: Into<String>,
        F: FnOnce() -> C,
    {
        self.map_err(|source| QTermError::Unknown(format!("{}: {}", context().into(), source)))
    }
}

/// Formats error messages for display
pub fn format_error(error: &QTermError) -> String {
    match error {
        QTermError::GpuError { kind, message, .. } => {
            format!("GPU Error ({:?}): {}", kind, message)
        }
        QTermError::QuantumStateError { kind, message } => {
            format!("Quantum State Error ({:?}): {}", kind, message)
        }
        QTermError::RenderError { kind, message } => {
            format!("Render Error ({:?}): {}", kind, message)
        }
        QTermError::ResourceError { kind, message, path } => {
            let path_str = path
                .as_ref()
                .map(|p| p.to_string_lossy().into_owned())
                .unwrap_or_default();
            format!("Resource Error ({:?}): {} [{}]", kind, message, path_str)
        }
        QTermError::ShellError { kind, message } => {
            format!("Shell Error ({:?}): {}", kind, message)
        }
        QTermError::MetricsError { kind, message } => {
            format!("Metrics Error ({:?}): {}", kind, message)
        }
        QTermError::CommandError { kind, message } => {
            format!("Command Error ({:?}): {}", kind, message)
        }
        QTermError::IoError(e) => format!("IO Error: {}", e),
        QTermError::ConfigError { kind, message } => {
            format!("Config Error ({:?}): {}", kind, message)
        }
        QTermError::Unknown(msg) => format!("Unknown Error: {}", msg),
    }
}

/// Example conversion implementation for external errors
impl From<metal::MetalError> for QTermError {
    fn from(err: metal::MetalError) -> Self {
        QTermError::gpu_error(
            GpuErrorKind::InvalidOperation,
            err.to_string(),
            Some(Box::new(err)),
        )
    }
}
