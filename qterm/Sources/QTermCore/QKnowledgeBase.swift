import Foundation
import Metal

public class QKnowledgeBase {
    private let device: MTLDevice
    private var embeddings: [String: [Float]] = [:]
    private var documents: [String: String] = [:]
    
    public init(device: MTLDevice) throws {
        self.device = device
    }
    
    public func addDocument(_ text: String, embeddings: [Float]) throws {
        let id = UUID().uuidString
        self.documents[id] = text
        self.embeddings[id] = embeddings
    }
    
    public func search(query: [Float], limit: Int = 5) -> [(String, Double)] {
        var results: [(String, Double)] = []
        
        for (id, docEmbeddings) in embeddings {
            let similarity = cosineSimilarity(query, docEmbeddings)
            if let text = documents[id] {
                results.append((text, similarity))
            }
        }
        
        return results
            .sorted { $0.1 > $1.1 }
            .prefix(limit)
            .map { ($0.0, $0.1) }
    }
    
    private func cosineSimilarity(_ a: [Float], _ b: [Float]) -> Double {
        guard a.count == b.count else { return 0.0 }
        
        var dotProduct: Float = 0.0
        var normA: Float = 0.0
        var normB: Float = 0.0
        
        for i in 0..<a.count {
            dotProduct += a[i] * b[i]
            normA += a[i] * a[i]
            normB += b[i] * b[i]
        }
        
        normA = sqrt(normA)
        normB = sqrt(normB)
        
        guard normA > 0 && normB > 0 else { return 0.0 }
        return Double(dotProduct / (normA * normB))
    }
}
