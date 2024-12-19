import Foundation

/// Quantum-aware model selector for NLP processing
public class QModelSelector {
    private let processManager = ProcessManager()
    private var availableModels: [Q.ModelInfo] = []
    private var modelCapabilities: [String: Q.ModelCapabilities] = [:]
    private var lastUpdateTime: Date = .distantPast
    
    public init() {}
    
    /// Select best model for given prompt using quantum decision making
    public func selectModel(for prompt: Q.NLPPrompt, state: inout Q.NeuralState) async throws -> Q.ModelSelection {
        // Update model cache if needed
        if needsUpdate {
            try await updateAvailableModels()
        }
        
        // Calculate quantum superposition of model suitability
        var modelScores: [(Q.ModelInfo, Double)] = []
        
        for model in availableModels {
            let capabilities = modelCapabilities[model.name] ?? Q.ModelCapabilities()
            
            // Quantum probability amplitude for model selection
            let amplitude = try calculateModelAmplitude(
                model: model,
                capabilities: capabilities,
                prompt: prompt,
                state: &state
            )
            
            modelScores.append((model, amplitude))
        }
        
        // Collapse superposition to select best model
        let selectedModel = try collapseModelSuperposition(
            scores: modelScores,
            state: &state
        )
        
        return Q.ModelSelection(
            model: selectedModel,
            confidence: selectedModel.quantumScore,
            reasoning: selectedModel.selectionReasoning
        )
    }
    
    /// Check if available models need updating
    private var needsUpdate: Bool {
        Date().timeIntervalSince(lastUpdateTime) > 300 // Update every 5 minutes
    }
    
    /// Update available models from Ollama and JAN
    private func updateAvailableModels() async throws {
        // Get Ollama models
        let ollamaModels = try await listOllamaModels()
        
        // Get JAN models
        let janModels = try await listJANModels()
        
        // Merge and update capabilities
        availableModels = ollamaModels + janModels
        try await updateModelCapabilities()
        
        lastUpdateTime = Date()
    }
    
    /// List available Ollama models
    private func listOllamaModels() async throws -> [Q.ModelInfo] {
        let output = try await processManager.run("ollama list")
        return try parseOllamaOutput(output)
    }
    
    /// List available JAN models
    private func listJANModels() async throws -> [Q.ModelInfo] {
        // Query JAN server for available models
        let janClient = try JANClient()
        return try await janClient.listModels()
    }
    
    /// Update capabilities for all models
    private func updateModelCapabilities() async throws {
        for model in availableModels {
            modelCapabilities[model.name] = try await analyzeModelCapabilities(model)
        }
    }
    
    /// Analyze capabilities of a specific model
    private func analyzeModelCapabilities(_ model: Q.ModelInfo) async throws -> Q.ModelCapabilities {
        // Analyze model parameters and performance characteristics
        let capabilities = Q.ModelCapabilities(
            contextLength: model.contextLength,
            specializations: try await detectSpecializations(model),
            quantumCompatibility: model.quantumCompatible,
            performance: try await benchmarkModel(model)
        )
        
        return capabilities
    }
    
    /// Calculate quantum amplitude for model selection
    private func calculateModelAmplitude(
        model: Q.ModelInfo,
        capabilities: Q.ModelCapabilities,
        prompt: Q.NLPPrompt,
        state: inout Q.NeuralState
    ) throws -> Double {
        // Base score from classical features
        var score = evaluateClassicalFeatures(model, capabilities, prompt)
        
        // Apply quantum interference effects
        score *= cos(state.phase) * state.amplitude
        
        // Consider quantum entanglement with prompt
        if capabilities.quantumCompatibility {
            score *= state.coherence
        }
        
        // Reality anchoring
        score *= state.reality
        
        return score
    }
    
    /// Evaluate classical features for model selection
    private func evaluateClassicalFeatures(
        _ model: Q.ModelInfo,
        _ capabilities: Q.ModelCapabilities,
        _ prompt: Q.NLPPrompt
    ) -> Double {
        var score = 1.0
        
        // Context length compatibility
        let promptLength = prompt.text.count
        if promptLength > capabilities.contextLength {
            score *= 0.5
        }
        
        // Specialization match
        if capabilities.specializations.contains(where: { prompt.task.contains($0) }) {
            score *= 1.5
        }
        
        // Performance requirements
        if prompt.config.requiresFastResponse && capabilities.performance.latency > 1.0 {
            score *= 0.7
        }
        
        return score
    }
    
    /// Collapse quantum superposition to select final model
    private func collapseModelSuperposition(
        scores: [(Q.ModelInfo, Double)],
        state: inout Q.NeuralState
    ) throws -> Q.ModelInfo {
        // Normalize scores to create probability distribution
        let total = scores.reduce(0.0) { $0 + $1.1 }
        let probabilities = scores.map { ($0.0, $0.1 / total) }
        
        // Apply quantum measurement
        let measurement = Double.random(in: 0...1) * state.reality
        
        var accumulator = 0.0
        for (model, probability) in probabilities {
            accumulator += probability
            if measurement <= accumulator {
                // Update quantum state after measurement
                state.phase += .pi / 4
                state.coherence *= 0.9
                
                return model
            }
        }
        
        // Fallback to highest scoring model
        return scores.max(by: { $0.1 < $1.1 })?.0 ?? availableModels[0]
    }
    
    /// Parse Ollama CLI output
    private func parseOllamaOutput(_ output: String) throws -> [Q.ModelInfo] {
        let lines = output.components(separatedBy: .newlines)
        return try lines.compactMap { line in
            let components = line.split(separator: " ")
            guard components.count >= 2 else { return nil }
            
            return Q.ModelInfo(
                name: String(components[0]),
                source: .ollama,
                size: String(components[1]),
                contextLength: 4096, // Default, will be updated during capability analysis
                quantumCompatible: false // Will be determined during analysis
            )
        }
    }
    
    /// Detect model specializations
    private func detectSpecializations(_ model: Q.ModelInfo) async throws -> Set<String> {
        // Analyze model architecture and training data
        var specializations: Set<String> = []
        
        // Add known specializations based on model name and metadata
        if model.name.contains("code") {
            specializations.insert("code")
        }
        if model.name.contains("chat") {
            specializations.insert("conversation")
        }
        
        return specializations
    }
    
    /// Benchmark model performance
    private func benchmarkModel(_ model: Q.ModelInfo) async throws -> Q.ModelPerformance {
        // Run quick benchmark if not already cached
        let benchmarkPrompt = "Test prompt for latency measurement"
        let startTime = Date()
        
        if model.source == .ollama {
            _ = try await processManager.run("ollama run \(model.name) \"\(benchmarkPrompt)\"")
        } else {
            let janClient = try JANClient()
            _ = try await janClient.complete(model: model.name, prompt: benchmarkPrompt)
        }
        
        let latency = Date().timeIntervalSince(startTime)
        
        return Q.ModelPerformance(
            latency: latency,
            throughput: 1.0 / latency
        )
    }
}

extension Q {
    public struct ModelInfo {
        let name: String
        let source: ModelSource
        let size: String
        let contextLength: Int
        let quantumCompatible: Bool
        var quantumScore: Double = 0.0
        var selectionReasoning: String = ""
    }
    
    public enum ModelSource {
        case ollama
        case jan
    }
    
    public struct ModelCapabilities {
        let contextLength: Int
        let specializations: Set<String>
        let quantumCompatibility: Bool
        let performance: ModelPerformance
        
        init(
            contextLength: Int = 4096,
            specializations: Set<String> = [],
            quantumCompatibility: Bool = false,
            performance: ModelPerformance = ModelPerformance()
        ) {
            self.contextLength = contextLength
            self.specializations = specializations
            self.quantumCompatibility = quantumCompatibility
            self.performance = performance
        }
    }
    
    public struct ModelPerformance {
        let latency: Double
        let throughput: Double
        
        init(latency: Double = 0.0, throughput: Double = 0.0) {
            self.latency = latency
            self.throughput = throughput
        }
    }
    
    public struct ModelSelection {
        let model: ModelInfo
        let confidence: Double
        let reasoning: String
    }
}
