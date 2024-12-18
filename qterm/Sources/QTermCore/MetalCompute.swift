import Foundation
import Metal

/// Metal-accelerated quantum computations
public class MetalCompute {
    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private let library: MTLLibrary
    private let computePipelineState: MTLComputePipelineState
    
    public var isMetalAvailable: Bool { true }
    
    public init() throws {
        guard let device = MTLCreateSystemDefaultDevice() else {
            throw QuantumError.metalNotAvailable
        }
        self.device = device
        
        guard let queue = device.makeCommandQueue() else {
            throw QuantumError.metalNotAvailable
        }
        self.commandQueue = queue
        
        // Load metal shader library
        let libraryPath = Bundle.module.path(forResource: "default", ofType: "metallib")
        guard let libraryPath = libraryPath,
              let library = try? device.makeLibrary(filepath: libraryPath) else {
            throw QuantumError.metalLibraryNotFound
        }
        self.library = library
        
        // Create compute pipeline
        guard let function = library.makeFunction(name: "quantum_gate") else {
            throw QuantumError.metalFunctionNotFound
        }
        
        self.computePipelineState = try device.makeComputePipelineState(function: function)
    }
    
    /// Process quantum state using Metal
    public func processQuantumState(_ state: QuantumVector, gate: QuantumGate) throws -> QuantumVector {
        // Create Metal buffers
        let inputBuffer = device.makeBuffer(bytes: state.metalBuffer,
                                          length: MemoryLayout<Float>.stride * 4,
                                          options: .storageModeShared)
        
        let outputBuffer = device.makeBuffer(length: MemoryLayout<Float>.stride * 4,
                                           options: .storageModeShared)
        
        let gateMatrix = gate.matrix
        var metalGateMatrix = [Float](repeating: 0, count: 8)
        for i in 0..<2 {
            for j in 0..<2 {
                metalGateMatrix[i * 4 + j * 2] = gateMatrix[i][j].real
                metalGateMatrix[i * 4 + j * 2 + 1] = gateMatrix[i][j].imag
            }
        }
        
        let gateBuffer = device.makeBuffer(bytes: metalGateMatrix,
                                         length: MemoryLayout<Float>.stride * 8,
                                         options: .storageModeShared)
        
        guard let commandBuffer = commandQueue.makeCommandBuffer(),
              let computeEncoder = commandBuffer.makeComputeCommandEncoder(),
              let inputBuffer = inputBuffer,
              let outputBuffer = outputBuffer,
              let gateBuffer = gateBuffer else {
            throw QuantumError.metalBufferCreationFailed
        }
        
        computeEncoder.setComputePipelineState(computePipelineState)
        computeEncoder.setBuffer(inputBuffer, offset: 0, index: 0)
        computeEncoder.setBuffer(outputBuffer, offset: 0, index: 1)
        computeEncoder.setBuffer(gateBuffer, offset: 0, index: 2)
        
        let gridSize = MTLSize(width: 1, height: 1, depth: 1)
        let threadGroupSize = MTLSize(width: 1, height: 1, depth: 1)
        computeEncoder.dispatchThreadgroups(gridSize, threadsPerThreadgroup: threadGroupSize)
        
        computeEncoder.endEncoding()
        commandBuffer.commit()
        commandBuffer.waitUntilCompleted()
        
        let result = outputBuffer.contents().bindMemory(to: Float.self, capacity: 4)
        let components = [result[0], result[1]]
        
        return QuantumVector(components: components)
    }
}
