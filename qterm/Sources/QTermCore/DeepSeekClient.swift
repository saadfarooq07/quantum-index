import Foundation

public class DeepSeekClient {
    private let apiKey: String
    private let baseURL = "https://api.deepseek.com/v1"
    private let session: URLSession
    
    init() {
        self.apiKey = APIConfig.deepSeekKey
        let config = URLSessionConfiguration.default
        config.httpAdditionalHeaders = [
            "Authorization": "Bearer \(apiKey)",
            "Content-Type": "application/json"
        ]
        self.session = URLSession(configuration: config)
    }
    
    public func process(_ prompt: String) async throws -> DeepSeekResponse {
        let endpoint = "\(baseURL)/completions"
        let parameters: [String: Any] = [
            "model": "deepseek-coder",
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 1000
        ]
        
        return try await sendRequest(to: endpoint, with: parameters)
    }
    
    public func processMultiModal(imageData: Data, prompt: String) async throws -> MultiModalResponse {
        let endpoint = "\(baseURL)/multimodal"
        let boundary = UUID().uuidString
        
        var data = Data()
        
        // Add image data
        data.append("--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"image\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
        data.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        data.append(imageData)
        data.append("\r\n".data(using: .utf8)!)
        
        // Add prompt
        data.append("--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"prompt\"\r\n\r\n".data(using: .utf8)!)
        data.append(prompt.data(using: .utf8)!)
        data.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        return try await sendMultipartRequest(to: endpoint, with: data, boundary: boundary)
    }
    
    // MARK: - Private Methods
    
    private func sendRequest<T: Decodable>(to endpoint: String, with parameters: [String: Any]) async throws -> T {
        guard let url = URL(string: endpoint) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = try JSONSerialization.data(withJSONObject: parameters)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        guard 200...299 ~= httpResponse.statusCode else {
            throw NetworkError.serverError(statusCode: httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    private func sendMultipartRequest<T: Decodable>(to endpoint: String, with data: Data, boundary: String) async throws -> T {
        guard let url = URL(string: endpoint) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.httpBody = data
        
        let (responseData, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        guard 200...299 ~= httpResponse.statusCode else {
            throw NetworkError.serverError(statusCode: httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
}

// MARK: - Response Types

public struct DeepSeekResponse: Codable {
    let id: String
    let choices: [Choice]
    let usage: Usage
    
    struct Choice: Codable {
        let text: String
        let index: Int
        let finishReason: String?
        
        enum CodingKeys: String, CodingKey {
            case text
            case index
            case finishReason = "finish_reason"
        }
    }
    
    struct Usage: Codable {
        let promptTokens: Int
        let completionTokens: Int
        let totalTokens: Int
        
        enum CodingKeys: String, CodingKey {
            case promptTokens = "prompt_tokens"
            case completionTokens = "completion_tokens"
            case totalTokens = "total_tokens"
        }
    }
}

public struct MultiModalResponse: Codable {
    let id: String
    let analysis: String
    let operations: [String]
    let confidence: Double
}

// MARK: - Errors

enum NetworkError: Error {
    case invalidURL
    case invalidResponse
    case serverError(statusCode: Int)
}
