import Foundation
import Metal

/// Bridge between qTerm and local NLP capabilities
public class QNLPBridge {
    private let metalDevice: MTLDevice
    private let commandQueue: MTLCommandQueue
    private let modelSelector: QModelSelector
    private let ollamaClient: QOllamaClient
    private let qortexBridge: QortexBridge
    
    public init() throws {
        // Initialize Metal
        guard let device = MTLCreateSystemDefaultDevice() else {
            throw Q.QError.metalDeviceNotFound
        }
        self.metalDevice = device
        
        guard let queue = device.makeCommandQueue() else {
            throw Q.QError.metalQueueCreationFailed
        }
        self.commandQueue = queue
        
        // Initialize components
        self.modelSelector = QModelSelector()
        self.ollamaClient = QOllamaClient()
        self.qortexBridge = try QortexBridge()
    }
    
    /// Process NLP request with local models
    public func processPrompt(_ prompt: Q.NLPPrompt) async throws -> Q.NLPResponse {
        // Initialize quantum state for processing
        var state = Q.NeuralState(
            amplitude: 1.0,
            phase: 0.0,
            coherence: 1.0,
            reality: 1.0
        )
        
        // Select best model using quantum decision making
        let modelSelection = try await modelSelector.selectModel(
            for: prompt,
            state: &state
        )
        
        // Create Metal command buffer
        guard let commandBuffer = commandQueue.makeCommandBuffer() else {
            throw Q.QError.metalCommandBufferFailed
        }
        
        // Process through Qortex for quantum enhancement
        let qortexResult = try await qortexBridge.process(
            prompt: prompt,
            state: &state,
            commandBuffer: commandBuffer
        )
        
        // Get response from selected model
        let modelResponse = try await getModelResponse(
            prompt: qortexResult.enhancedPrompt,
            selection: modelSelection
        )
        
        // Post-process through quantum circuit
        let finalResponse = try await qortexBridge.postProcess(
            response: modelResponse,
            state: &state,
            commandBuffer: commandBuffer
        )
        
        return Q.NLPResponse(
            text: finalResponse.text,
            quantumState: state,
            metrics: finalResponse.metrics,
            modelInfo: modelSelection
        )
    }
    
    /// Get response from selected model
    private func getModelResponse(
        prompt: String,
        selection: Q.ModelSelection
    ) async throws -> String {
        switch selection.model.source {
        case .ollama:
            return try await ollamaClient.complete(
                prompt: prompt,
                model: selection.model.name
            )
        case .jan:
            return try await qortexBridge.janClient.complete(
                model: selection.model.name,
                prompt: prompt
            )
        }
    }
}

/// Ollama client for local model inference
private class QOllamaClient {
    private let processManager = ProcessManager()
    
    func complete(prompt: String, model: String) async throws -> String {
        let command = "ollama run \(model) \"\(prompt)\""
        return try await processManager.run(command)
    }
}

/// Bridge to Qortex quantum processing
private class QortexBridge {
    let janClient: JANClient
    
    init() throws {
        self.janClient = try JANClient()
    }
    
    func process(
        prompt: Q.NLPPrompt,
        state: inout Q.NeuralState,
        commandBuffer: MTLCommandBuffer
    ) async throws -> QortexResult {
        // Process through quantum circuit
        let result = try await janClient.processQuantum(
            input: prompt.text,
            state: &state,
            commandBuffer: commandBuffer
        )
        
        return QortexResult(
            enhancedPrompt: result.output,
            metrics: result.metrics
        )
    }
    
    func postProcess(
        response: String,
        state: inout Q.NeuralState,
        commandBuffer: MTLCommandBuffer
    ) async throws -> QortexResult {
        // Apply quantum post-processing
        let result = try await janClient.postProcessQuantum(
            input: response,
            state: &state,
            commandBuffer: commandBuffer
        )
        
        return QortexResult(
            text: result.output,
            metrics: result.metrics
        )
    }
}

/// Process manager for shell commands
private class ProcessManager {
    func run(_ command: String) async throws -> String {
        let process = Process()
        let pipe = Pipe()
        
        process.executableURL = URL(fileURLWithPath: "/bin/zsh")
        process.arguments = ["-c", command]
        process.standardOutput = pipe
        
        try process.run()
        process.waitUntilExit()
        
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        return String(data: data, encoding: .utf8) ?? ""
    }
}

/// Result from Qortex processing
private struct QortexResult {
    let text: String
    let metrics: [String: Double]
    
    init(enhancedPrompt: String, metrics: [String: Double]) {
        self.text = enhancedPrompt
        self.metrics = metrics
    }
    
    init(text: String, metrics: [String: Double]) {
        self.text = text
        self.metrics = metrics
    }
}

extension Q {
    public struct NLPPrompt {
        let text: String
        let task: String
        let config: NLPConfig
        
        public init(
            text: String,
            task: String = "general",
            config: NLPConfig = NLPConfig()
        ) {
            self.text = text
            self.task = task
            self.config = config
        }
    }
    
    public struct NLPConfig {
        let temperature: Double
        let maxTokens: Int
        let quantumOptimization: Bool
        let requiresFastResponse: Bool
        
        public init(
            temperature: Double = 0.7,
            maxTokens: Int = 2048,
            quantumOptimization: Bool = true,
            requiresFastResponse: Bool = false
        ) {
            self.temperature = temperature
            self.maxTokens = maxTokens
            self.quantumOptimization = quantumOptimization
            self.requiresFastResponse = requiresFastResponse
        }
    }
    
    public struct NLPResponse {
        let text: String
        let quantumState: NeuralState
        let metrics: [String: Double]
        let modelInfo: ModelSelection
    }
}
