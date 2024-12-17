import PackagePlugin
import Foundation

@main
struct MetalCompiler: BuildToolPlugin {
    func createBuildCommands(context: PluginContext, target: Target) throws -> [Command] {
        let inputFiles = target.directory
            .filter { $0.extension == "metal" }
        
        return try inputFiles.map { inputFile in
            let outputPath = context.pluginWorkDirectory.appending(["default.metallib"])
            
            return .buildCommand(
                displayName: "Compiling Metal shaders",
                executable: try context.tool(named: "xcrun").path,
                arguments: [
                    "metal",
                    "-c", inputFile.string,
                    "-o", outputPath.string
                ],
                inputFiles: [inputFile],
                outputFiles: [outputPath]
            )
        }
    }
}
