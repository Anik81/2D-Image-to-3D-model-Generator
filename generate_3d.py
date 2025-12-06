

import os
import sys
import argparse
import glob
import subprocess


def setup_triposr():
    """Clone TripoSR repository if not exists"""
    if not os.path.exists('TripoSR'):
        print("Cloning TripoSR repository...")
        subprocess.run(['git', 'clone', 'https://github.com/VAST-AI-Research/TripoSR.git'], check=True)
        
        # Install dependencies
        print("\nInstalling dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'setuptools'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'huggingface_hub', 'accelerate', 'transformers'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'TripoSR/requirements.txt'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'onnxruntime', 'trimesh'], check=True)
    else:
        print("TripoSR already cloned.")


def generate_3d(input_image: str, output_dir: str = "output"):
    """Generate 3D model from input image"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get absolute paths
    input_path = os.path.abspath(input_image)
    output_path = os.path.abspath(output_dir)
    triposr_path = os.path.abspath('TripoSR')
    
    # Check if input exists
    if not os.path.exists(input_path):
        print(f"Error: Input image not found: {input_path}")
        sys.exit(1)
    
    print(f"\nInput image: {input_path}")
    print(f"Output directory: {output_path}")
    
    # Run TripoSR
    print("\nGenerating 3D model... (this may take a few minutes)")
    cmd = [
        sys.executable, 'run.py',
        input_path,
        '--output-dir', output_path
    ]
    
    subprocess.run(cmd, cwd=triposr_path, check=True)
    
    return output_path


def convert_to_glb(output_dir: str, output_filename: str = "output_model.glb"):
    """Convert generated OBJ to GLB format"""
    import trimesh
    
    # Find generated OBJ file
    obj_files = glob.glob(os.path.join(output_dir, "**/*.obj"), recursive=True)
    
    if not obj_files:
        print("Error: No OBJ file found in output directory")
        return None
    
    obj_path = obj_files[0]
    print(f"\nFound OBJ file: {obj_path}")
    
    # Load mesh
    mesh = trimesh.load(obj_path)
    
    # Export to GLB
    glb_path = os.path.join(output_dir, output_filename)
    mesh.export(glb_path, file_type='glb')
    print(f"Converted to GLB: {glb_path}")
    
    # Print mesh info
    print(f"\n=== 3D Model Info ===")
    print(f"Vertices: {len(mesh.vertices)}")
    print(f"Faces: {len(mesh.faces)}")
    
    return glb_path


def main():
    parser = argparse.ArgumentParser(description='Generate 3D model from 2D image using TripoSR')
    parser.add_argument('input_image', help='Path to input image (PNG, JPG)')
    parser.add_argument('--output', '-o', default='output', help='Output directory (default: output)')
    parser.add_argument('--output-name', '-n', default='output_model.glb', help='Output GLB filename')
    parser.add_argument('--skip-setup', action='store_true', help='Skip TripoSR setup')
    
    args = parser.parse_args()
    
    # Setup TripoSR
    if not args.skip_setup:
        setup_triposr()
    
    # Generate 3D model
    output_dir = generate_3d(args.input_image, args.output)
    
    # Convert to GLB
    glb_path = convert_to_glb(output_dir, args.output_name)
    
    if glb_path:
        print(f"\n[DONE] 3D model is saved at: {glb_path}")


if __name__ == "__main__":
    main()
