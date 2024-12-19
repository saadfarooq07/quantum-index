import Foundation

public class JANClient {
    private let baseURL: URL
    private let session: URLSession
    
    public init() throws {
        guard let url = URL(string: "http://localhost:8080") else {
            throw QuantumNamespace.QError.invalidConfiguration
        }
        self.baseURL = url
        self.session = URLSession.shared
    }
    
    public func listModels() async throws -> [QuantumNamespace.ModelInfo] {
        let url = baseURL.appendingPathComponent("models")
        let (data, _) = try await session.data(from: url)
        let models = try JSONDecoder().decode([QuantumNamespace.ModelInfo].self, from: data)
        return models
    }
    
    public func complete(model: String, prompt: String) async throws -> String {
        let url = baseURL.appendingPathComponent("complete")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "model": model,
            "prompt": prompt
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await session.data(for: request)
        let response = try JSONDecoder().decode(CompletionResponse.self, from: data)
        return response.text
    }
}

private struct CompletionResponse: Codable {
    let text: String
}
