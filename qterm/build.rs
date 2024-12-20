use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

#[cfg(target_os = "macos")]
fn compile_metal_shaders(source_path: &Path, output_dir: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let xcrun = Command::new("xcrun")
        .args(&[
            "-sdk", "macosx", "metal",
            "-c", source_path.to_str().unwrap(),
            "-o", output_dir.join("shader.air").to_str().unwrap()
        ])
        .output()?;

    if !xcrun.status.success() {
        return Err(format!(
            "Failed to compile metal shader: {}",
            String::from_utf8_lossy(&xcrun.stderr)
        ).into());
    }

    let metallib = Command::new("xcrun")
        .args(&[
            "-sdk", "macosx", "metallib",
            output_dir.join("shader.air").to_str().unwrap(),
            "-o", output_dir.join("shader.metallib").to_str().unwrap()
        ])
        .output()?;

    if !metallib.status.success() {
        return Err(format!(
            "Failed to create metallib: {}",
            String::from_utf8_lossy(&metallib.stderr)
        ).into());
    }

    Ok(())
}

fn copy_shaders(src_dir: &Path, dst_dir: &Path) -> Result<(), Box<dyn std::error::Error>> {
    fs::create_dir_all(dst_dir)?;
    
    for entry in fs::read_dir(src_dir)? {
        let entry = entry?;
        let path = entry.path();
        
        if path.extension().map_or(false, |ext| ext == "metal") {
            fs::copy(&path, dst_dir.join(path.file_name().unwrap()))?;
        }
    }
    
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let out_dir = PathBuf::from(env::var("OUT_DIR")?);
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR")?);
    
    // Source and resource directories
    let shader_src = manifest_dir.join("Sources/Resources");
    let shader_dst = out_dir.join("shaders");
    
    // Ensure shader source directory exists
    if !shader_src.exists() {
        fs::create_dir_all(&shader_src)?;
        println!("Created shader source directory at {:?}", shader_src);
    }
    
    // Copy shaders to build directory
    copy_shaders(&shader_src, &shader_dst)?;
    println!("cargo:rerun-if-changed=Sources/Resources");
    
    #[cfg(target_os = "macos")]
    {
        // Compile Metal shaders on macOS
        println!("cargo:warning=Compiling Metal shaders...");
        for entry in fs::read_dir(&shader_src)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.extension().map_or(false, |ext| ext == "metal") {
                compile_metal_shaders(&path, &shader_dst)?;
                println!("cargo:rerun-if-changed={}", path.display());
            }
        }
    }
    
    // Set linker flags for Metal framework on macOS
    #[cfg(target_os = "macos")]
    {
        println!("cargo:rustc-link-lib=framework=Metal");
        println!("cargo:rustc-link-lib=framework=CoreGraphics");
        println!("cargo:rustc-link-lib=framework=Foundation");
    }
    
    Ok(())
}

