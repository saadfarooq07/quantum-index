import XCTest
@testable import QTermCore

final class Q0rtexDeepSeekTests: XCTestCase {
    var processor: QWorkflowProcessor!
    var stateManager: QuantumStateManager!
    
    override func setUp() {
        super.setUp()
        processor = try! QWorkflowProcessor()
        stateManager = try! QuantumStateManager()
    }
    
    override func tearDown() {
        processor = nil
        stateManager = nil
        super.tearDown()
    }
    
    // MARK: - DeepSeek Integration Tests
    
    func testDeepSeekPromptProcessing() async throws {
        let prompt = "Create a quantum circuit with Hadamard gate"
        let result = try await processor.processWithDeepSeek(prompt: prompt)
        XCTAssertNotNil(result.circuit)
        XCTAssertTrue(result.circuit.contains(.hadamard))
    }
    
    func testMultiModalProcessing() async throws {
        let imageData = // Test image data
        let textPrompt = "Analyze this quantum circuit diagram"
        let result = try await processor.processMultiModal(
            imageData: imageData,
            textPrompt: textPrompt
        )
        XCTAssertNotNil(result.analysis)
        XCTAssertNotNil(result.suggestedOperations)
    }
    
    func testLocalModelChainExecution() async throws {
        let workflow = QWorkflow(
            steps: [
                .modelSelection(criteria: ["task": "quantum_circuit_design"]),
                .circuitGeneration(gates: [.hadamard, .cnot]),
                .statePreparation(initialState: .superposition),
                .measurement
            ]
        )
        
        let result = try await processor.executeLocalModelChain(workflow: workflow)
        XCTAssertNotNil(result.finalState)
        XCTAssertTrue(result.metrics.executionTime > 0)
    }
    
    func testMetalAcceleratedQuantumOps() async throws {
        let state = QuantumNamespace.NeuralState(
            amplitude: 1.0,
            phase: 0.0,
            isEntangled: false
        )
        
        let result = try await processor.executeMetalAcceleratedOp(
            state: state,
            gate: .hadamard
        )
        
        XCTAssertEqual(result.amplitude, 1.0 / sqrt(2), accuracy: 1e-6)
    }
    
    func testModelSwitching() async throws {
        let result = try await processor.switchModel(
            to: .local(name: "jan-7b-chat.gguf"),
            context: ["task": "quantum_circuit_optimization"]
        )
        XCTAssertTrue(result.success)
        XCTAssertNotNil(result.modelConfig)
    }
    
    func testAgenticWorkflow() async throws {
        let workflow = QAgenticWorkflow(
            steps: [
                .analyzeRequirement(prompt: "Optimize this quantum circuit"),
                .proposeChanges(context: ["optimization_target": "gate_count"]),
                .executeChanges,
                .validateResults
            ]
        )
        
        let result = try await processor.executeAgenticWorkflow(workflow)
        XCTAssertTrue(result.success)
        XCTAssertNotNil(result.optimizedCircuit)
    }
    
    // MARK: - Error Handling Tests
    
    func testInvalidModelConfiguration() async throws {
        do {
            _ = try await processor.switchModel(
                to: .invalid,
                context: [:]
            )
            XCTFail("Should throw an error")
        } catch {
            XCTAssertTrue(error is QModelError)
        }
    }
    
    func testCircuitValidation() async throws {
        let invalidCircuit = QCircuit(gates: [])
        do {
            _ = try await processor.validateCircuit(invalidCircuit)
            XCTFail("Should throw an error")
        } catch {
            XCTAssertTrue(error is QCircuitError)
        }
    }
}

// MARK: - Test Support Types

extension Q0rtexDeepSeekTests {
    struct QWorkflow {
        enum Step {
            case modelSelection(criteria: [String: String])
            case circuitGeneration(gates: [QuantumNamespace.Gate])
            case statePreparation(initialState: QuantumState)
            case measurement
        }
        
        let steps: [Step]
    }
    
    struct QAgenticWorkflow {
        enum Step {
            case analyzeRequirement(prompt: String)
            case proposeChanges(context: [String: String])
            case executeChanges
            case validateResults
        }
        
        let steps: [Step]
    }
    
    enum QuantumState {
        case superposition
        case entangled
        case classical
    }
    
    enum QModelError: Error {
        case invalidConfiguration
        case initializationFailed
    }
    
    enum QCircuitError: Error {
        case invalidGateSequence
        case emptyCircuit
    }
}
