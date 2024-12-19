import XCTest
@testable import QTermCore

final class QTermTests: XCTestCase {
    var stateManager: QuantumStateManager!
    var interface: QInterface!
    
    override func setUp() async throws {
        try await super.setUp()
        stateManager = try QuantumStateManager(enableMetal: true)
        interface = try QInterface(enableNeural: true)
    }
    
    override func tearDown() async throws {
        stateManager = nil
        interface = nil
        try await super.tearDown()
    }
    
    // MARK: - Quantum SDLC Tests
    
    func testSDLCRoleTransitions() throws {
        // Test Product Manager to Architect transition
        try stateManager.switchRole(.productManager)
        XCTAssertEqual(try stateManager.getCurrentRole(), .productManager)
        
        try stateManager.switchRole(.architect)
        XCTAssertEqual(try stateManager.getCurrentRole(), .architect)
        
        // Test Architect to Engineer transition
        try stateManager.switchRole(.engineer)
        XCTAssertEqual(try stateManager.getCurrentRole(), .engineer)
        
        // Verify state history
        let history = stateManager.getStateHistory()
        XCTAssertEqual(history.count, 3)
        XCTAssertEqual(history[0].0, .productManager)
    }
    
    func testSDLCPhaseProgression() throws {
        // Test phase transitions
        XCTAssertEqual(try stateManager.getCurrentPhase(), .requirements)
        
        try stateManager.advancePhase()
        XCTAssertEqual(try stateManager.getCurrentPhase(), .design)
        
        try stateManager.advancePhase()
        XCTAssertEqual(try stateManager.getCurrentPhase(), .implementation)
        
        try stateManager.advancePhase()
        XCTAssertEqual(try stateManager.getCurrentPhase(), .testing)
        
        try stateManager.advancePhase()
        XCTAssertEqual(try stateManager.getCurrentPhase(), .deployment)
        
        // Test invalid phase transition
        XCTAssertThrowsError(try stateManager.advancePhase()) { error in
            XCTAssertEqual(error as? QuantumError, .invalidPhaseTransition)
        }
    }
    
    func testQuantumStateCoherence() throws {
        // Test quantum state preservation during role transitions
        try stateManager.setState(.plus)
        let initialState = try stateManager.measure()
        
        try stateManager.switchRole(.architect)
        let postRoleState = try stateManager.measure()
        
        // Verify quantum coherence is maintained
        XCTAssertEqual(abs(Double(initialState)! - Double(postRoleState)!), 0.0, accuracy: 0.01)
    }
    
    func testCompleteSDLCWorkflow() throws {
        var observedMessages: [String] = []
        interface.stateObserver = { message in
            observedMessages.append(message)
        }
        
        // Test complete workflow
        try interface.switchRole(.productManager)
        try interface.advancePhase() // Requirements -> Design
        try interface.switchRole(.architect)
        try interface.advancePhase() // Design -> Implementation
        try interface.switchRole(.engineer)
        try interface.advancePhase() // Implementation -> Testing
        try interface.switchRole(.qaEngineer)
        try interface.advancePhase() // Testing -> Deployment
        
        // Verify workflow progression
        XCTAssertGreaterThan(observedMessages.count, 0)
        XCTAssertTrue(observedMessages.contains { $0.contains("Role transition") })
        XCTAssertTrue(observedMessages.contains { $0.contains("Phase transition") })
    }
    
    // MARK: - Error Cases and Edge Cases
    
    func testInvalidRoleTransitions() throws {
        // Test invalid role transition during critical phase
        try stateManager.switchRole(.engineer)
        try stateManager.advancePhase() // To implementation
        
        XCTAssertThrowsError(try stateManager.switchRole(.productManager)) { error in
            XCTAssertEqual(error as? QuantumError, .invalidRoleTransition)
        }
    }
    
    func testConcurrentRolePhaseOperations() async throws {
        // Test concurrent role and phase changes
        async let roleChange = stateManager.switchRole(.architect)
        async let phaseChange = stateManager.advancePhase()
        
        // Both operations should complete successfully
        try await [roleChange, phaseChange].reduce(into: ()) { _, operation in
            _ = try await operation
        }
        
        // Verify final state
        XCTAssertEqual(try stateManager.getCurrentRole(), .architect)
        XCTAssertEqual(try stateManager.getCurrentPhase(), .design)
    }
    
    func testQuantumStateRecovery() throws {
        // Save initial state
        try stateManager.setState(.plus)
        let initialState = try stateManager.measure()
        
        // Simulate system interruption
        stateManager = try QuantumStateManager(enableMetal: true)
        try stateManager.setState(.plus)
        let recoveredState = try stateManager.measure()
        
        // Verify state recovery
        XCTAssertEqual(abs(Double(initialState)! - Double(recoveredState)!), 0.0, accuracy: 0.01)
    }
    
    func testMetalFailover() throws {
        // Test fallback when Metal is unavailable
        let fallbackManager = try QuantumStateManager(enableMetal: false)
        
        // Should still work without Metal
        try fallbackManager.setState(.plus)
        let state = try fallbackManager.measure()
        XCTAssertNotNil(state)
    }
    
    func testStateHistoryLimits() throws {
        // Test state history size limits
        for _ in 0..<100 {
            try stateManager.switchRole(.engineer)
            try stateManager.switchRole(.architect)
        }
        
        let history = stateManager.getStateHistory()
        XCTAssertLessThanOrEqual(history.count, 50) // Assuming 50 is max history size
    }
    
    // MARK: - Neural Interface Tests
    
    func testNeuralCommands() throws {
        let commands = ["qDeepBreathe", "qStretch", "qFeedOnEverything", "qDocReviewMDs"]
        
        for command in commands {
            let result = try interface.processNeuralCommand(command)
            XCTAssertFalse(result.isEmpty)
        }
        
        // Test invalid command
        XCTAssertThrowsError(try interface.processNeuralCommand("invalidCommand")) { error in
            XCTAssertEqual(error as? QuantumError, .invalidCommand)
        }
    }
    
    // MARK: - Metal Acceleration Tests
    
    func testMetalAcceleration() throws {
        let compute = try MetalCompute()
        XCTAssertTrue(compute.isMetalAvailable)
        
        // Test quantum operations with Metal
        let result = try compute.applyQuantumGate(.hadamard, to: [1.0, 0.0])
        XCTAssertEqual(result.count, 2)
        XCTAssertEqual(result[0], Float(1.0 / sqrt(2.0)), accuracy: 0.0001)
    }
}

// MARK: - Integration Tests

final class QTermIntegrationTests: XCTestCase {
    func testSDLCIntegration() async throws {
        let interface = try QInterface(enableNeural: true)
        var messages: [String] = []
        
        interface.stateObserver = { message in
            messages.append(message)
        }
        
        // Simulate complete development cycle
        try interface.switchRole(.productManager)
        try interface.processNeuralCommand("qDeepBreathe")
        try interface.advancePhase()
        
        try interface.switchRole(.architect)
        try interface.processNeuralCommand("qStretch")
        try interface.advancePhase()
        
        try interface.switchRole(.engineer)
        try interface.processNeuralCommand("qFeedOnEverything")
        try interface.advancePhase()
        
        try interface.switchRole(.qaEngineer)
        try interface.processNeuralCommand("qDocReviewMDs")
        
        // Verify integration points
        XCTAssertTrue(messages.contains { $0.contains("Neural Interface") })
        XCTAssertTrue(messages.contains { $0.contains("Quantum Bridge") })
    }
}
